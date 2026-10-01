"""
Production BKT trainer on real EdNet data.
Handles degenerate skills, adds progress tracking, and uses robust evaluation.
"""

import os
import json
import time
import warnings
import numpy as np
import pandas as pd

# Suppress pyBKT's noisy warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

try:
    from pyBKT.models import Model
except ImportError:
    raise SystemExit("pyBKT not installed. Run: pip install pyBKT")

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss


INPUT_PATH = "ai_engine/data_pipeline/outputs/ednet/skill_interactions.csv"
OUTPUT_DIR = "ai_engine/data_pipeline/outputs/ednet"

# Config
TOP_N_SKILLS = 30
MIN_ROWS_PER_SKILL = 1000      # Raised: needs more data for stable EM
MIN_UNIQUE_STUDENTS = 50       # New: ensure enough students for generalization
TEST_SIZE = 0.2
RANDOM_STATE = 42


def load_and_prepare() -> pd.DataFrame:
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"{INPUT_PATH} not found. Run process_ednet_v2.py first.")
    
    print(f"Loading {INPUT_PATH} ...")
    df = pd.read_csv(INPUT_PATH, usecols=['timestamp', 'student_id', 'skill', 'correct'])
    
    # pyBKT schema
    df = df.rename(columns={
        "student_id": "user_id",
        "skill": "skill_name",
        "correct": "correct",
    })
    
    df["skill_name"] = df["skill_name"].astype(str)
    df = df.dropna(subset=["user_id", "skill_name", "correct"])
    df["correct"] = df["correct"].astype(int)
    
    # CRITICAL FIX: Use dense integer order_id per (user, skill) to prevent ties
    df = df.sort_values(["user_id", "skill_name", "timestamp"])
    df["order_id"] = df.groupby(["user_id", "skill_name"]).cumcount() + 1
    
    # Validate no ties
    tie_check = df.groupby(["user_id", "skill_name"])["order_id"].nunique()
    assert tie_check.eq(df.groupby(["user_id", "skill_name"]).size()).all(), "Tie detected in order_id!"
    
    print(f"  Loaded {len(df):,} rows")
    print(f"  Students: {df['user_id'].nunique():,}")
    print(f"  Skills: {df['skill_name'].nunique()}")
    print(f"  Overall accuracy: {df['correct'].mean():.2%}")
    
    return df


def pick_skills(df: pd.DataFrame, top_n: int, min_rows: int, min_students: int) -> list:
    """Select skills with enough data AND enough unique students."""
    stats = df.groupby("skill_name").agg(
        n_rows=("correct", "count"),
        n_students=("user_id", "nunique"),
        accuracy=("correct", "mean")
    ).reset_index()
    
    # Filter: must have enough rows AND enough students
    eligible = stats[
        (stats["n_rows"] >= min_rows) & 
        (stats["n_students"] >= min_students) &
        (stats["accuracy"] > 0.05) &           # Not 100% correct (degenerate)
        (stats["accuracy"] < 0.95)             # Not 100% incorrect (degenerate)
    ]
    
    # Sort by student count (more students = more reliable)
    eligible = eligible.sort_values("n_students", ascending=False)
    selected = eligible.head(top_n)["skill_name"].tolist()
    
    print(f"\nSkill selection:")
    print(f"  Total skills: {len(stats)}")
    print(f"  Eligible (>{min_rows} rows, >{min_students} students, non-degenerate): {len(eligible)}")
    print(f"  Selected (top {top_n}): {len(selected)}")
    print(f"  Top 5 by volume: {selected[:5]}")
    
    return selected


def student_split(df: pd.DataFrame, test_size: float, seed: int):
    """Split by student to prevent leakage."""
    students = df["user_id"].unique()
    train_ids, test_ids = train_test_split(students, test_size=test_size, random_state=seed)
    return set(train_ids), set(test_ids)


def train_and_evaluate(df: pd.DataFrame, skills: list, train_ids: set, test_ids: set):
    """
    Train BKT per skill with proper error handling and progress tracking.
    """
    results = {}
    model = Model(seed=RANDOM_STATE, num_fits=1)  # num_fits=1 for speed; raise to 3 for production
    
    print(f"\nTraining {len(skills)} skills (train students: {len(train_ids):,}, test: {len(test_ids):,})")
    print("-" * 70)
    
    for i, skill in enumerate(skills, 1):
        start_time = time.time()
        skill_df = df[df["skill_name"] == skill]
        train_df = skill_df[skill_df["user_id"].isin(train_ids)]
        test_df = skill_df[skill_df["user_id"].isin(test_ids)]
        
        n_train_students = train_df["user_id"].nunique()
        n_test_students = test_df["user_id"].nunique()
        n_train_rows = len(train_df)
        n_test_rows = len(test_df)
        
        # Skip if too little data after split
        if n_train_rows < 200 or n_test_rows < 50 or n_test_students < 10:
            print(f"[{i:2d}/{len(skills)}] {skill:>6s}: SKIP (train={n_train_rows}, test={n_test_rows}, test_students={n_test_students})")
            continue
        
        try:
            # Fit BKT
            model.fit(data=train_df, skills=skill)
            
            # Extract parameters safely
            params = model.params()
            skill_params = {}
            try:
                # pyBKT returns multi-index DataFrame
                p = params.xs(skill, level="skill")
                skill_params = {
                    "p_init": float(p.loc[("prior", 0), "value"]) if ("prior", 0) in p.index else None,
                    "p_learn": float(p.loc[("learns", 0), "value"]) if ("learns", 0) in p.index else None,
                    "p_guess": float(p.loc[("guesses", 0), "value"]) if ("guesses", 0) in p.index else None,
                    "p_slip": float(p.loc[("slips", 0), "value"]) if ("slips", 0) in p.index else None,
                }
            except Exception:
                skill_params = {}  # Params extraction failed, but model may still predict
            
            # Predict on test
            preds = model.predict(data=test_df, skills=skill)
            
            # Handle various pyBKT output column names
            pred_col = None
            for col in ["correct_predictions", "state_predictions", preds.columns[-1]]:
                if col in preds.columns:
                    pred_col = col
                    break
            
            if pred_col is None:
                raise ValueError("No prediction column found")
            
            y_true = test_df["correct"].values
            y_pred_prob = preds[pred_col].values
            y_pred_label = (y_pred_prob > 0.5).astype(int)
            
            # Metrics
            acc = accuracy_score(y_true, y_pred_label)
            baseline = max(y_true.mean(), 1 - y_true.mean())
            
            try:
                auc = roc_auc_score(y_true, y_pred_prob)
            except ValueError:
                auc = None  # All one class in test
            
            try:
                ll = log_loss(y_true, np.clip(y_pred_prob, 0.001, 0.999))
            except ValueError:
                ll = None
            
            elapsed = time.time() - start_time
            
            results[skill] = {
                "n_train_rows": int(n_train_rows),
                "n_test_rows": int(n_test_rows),
                "n_train_students": int(n_train_students),
                "n_test_students": int(n_test_students),
                "accuracy": float(acc),
                "baseline_accuracy": float(baseline),
                "lift": float(acc - baseline),
                "auc": float(auc) if auc is not None else None,
                "log_loss": float(ll) if ll is not None else None,
                "params": skill_params,
                "elapsed_seconds": round(elapsed, 2)
            }
            
            auc_str = f"{auc:.3f}" if auc is not None else "N/A"
            print(f"[{i:2d}/{len(skills)}] {skill:>6s}: acc={acc:.3f} (base={baseline:.3f}, lift={acc-baseline:+.3f}) AUC={auc_str} | {n_train_rows:,} rows, {elapsed:.1f}s")
            
        except Exception as e:
            print(f"[{i:2d}/{len(skills)}] {skill:>6s}: FAILED ({str(e)[:60]})")
    
    return results


def print_summary(results: dict):
    """Print formatted summary statistics."""
    if not results:
        print("\n❌ No skills trained successfully.")
        return
    
    accs = [r["accuracy"] for r in results.values()]
    baselines = [r["baseline_accuracy"] for r in results.values()]
    lifts = [r["lift"] for r in results.values()]
    aucs = [r["auc"] for r in results.values() if r["auc"] is not None]
    times = [r["elapsed_seconds"] for r in results.values()]
    
    print("\n" + "=" * 70)
    print("BKT TRAINING SUMMARY")
    print("=" * 70)
    print(f"Skills trained:        {len(results)}")
    print(f"Total training time:   {sum(times):.1f}s (avg {np.mean(times):.1f}s per skill)")
    print(f"\nAccuracy:")
    print(f"  BKT mean:            {np.mean(accs):.3f}")
    print(f"  Baseline mean:       {np.mean(baselines):.3f}")
    print(f"  Mean lift:           {np.mean(lifts):+.3f}")
    print(f"  Skills beating baseline: {sum(1 for l in lifts if l > 0)}/{len(lifts)}")
    if aucs:
        print(f"\nAUC:")
        print(f"  Mean:                {np.mean(aucs):.3f}")
        print(f"  Median:              {np.median(aucs):.3f}")
        print(f"  Min/Max:             {min(aucs):.3f} / {max(aucs):.3f}")
    
    # Best and worst skills
    sorted_by_lift = sorted(results.items(), key=lambda x: x[1]["lift"], reverse=True)
    print(f"\nTop 3 skills by lift:")
    for skill, r in sorted_by_lift[:3]:
        print(f"  {skill}: acc={r['accuracy']:.3f}, lift={r['lift']:+.3f}, AUC={r.get('auc', 'N/A')}")
    
    print(f"\nBottom 3 skills by lift:")
    for skill, r in sorted_by_lift[-3:]:
        print(f"  {skill}: acc={r['accuracy']:.3f}, lift={r['lift']:+.3f}, AUC={r.get('auc', 'N/A')}")
    
    # Save detailed results
    out_path = os.path.join(OUTPUT_DIR, "bkt_evaluation.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Saved to {out_path}")


def main():
    print("=" * 70)
    print("BKT Training v3 - Robust, Progress-Tracked, Production-Ready")
    print("=" * 70)
    
    df = load_and_prepare()
    skills = pick_skills(df, TOP_N_SKILLS, MIN_ROWS_PER_SKILL, MIN_UNIQUE_STUDENTS)
    train_ids, test_ids = student_split(df, TEST_SIZE, RANDOM_STATE)
    
    print(f"\nSplit: {len(train_ids):,} train students / {len(test_ids):,} test students")
    
    results = train_and_evaluate(df, skills, train_ids, test_ids)
    print_summary(results)


if __name__ == "__main__":
    main()