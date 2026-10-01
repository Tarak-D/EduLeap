"""
EdNet Processing Pipeline (CORRECTED for real schema).

KT1 schema:      timestamp, solving_id, question_id, user_answer, elapsed_time
questions.csv:   question_id, bundle_id, explanation_id, correct_answer, part, tags, deployed_at
    - tags is semicolon-separated, e.g. "179;181" -> question maps to MULTIPLE skills

This script:
  1. Loads questions.csv ONCE (small, fits in memory).
  2. Derives `correct` for every KT1 interaction by comparing user_answer to correct_answer.
  3. Explodes multi-tag questions into one row per (interaction, skill) pair.
  4. Aggregates into skill_interactions.csv for BKT / prerequisite discovery / DKT.

Run from project root with PYTHONPATH set, e.g.:
    set PYTHONPATH=D:\EduLeap
    python ai_engine\data_pipeline\process_ednet_v2.py
"""

import os
import json
import glob
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List
import pickle

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x


class EdNetProcessorV2:
    def __init__(self, raw_dir: str = "ai_engine/data_pipeline/ednet_raw"):
        self.raw_dir = raw_dir
        self.output_dir = "ai_engine/data_pipeline/outputs/ednet"
        os.makedirs(self.output_dir, exist_ok=True)

        self.kt1_dir = os.path.join(raw_dir, "EdNet-KT1", "KT1")
        self.questions_path = os.path.join(
            raw_dir, "EdNet-Contents-Extracted", "contents", "questions.csv"
        )

        # question_id -> correct_answer
        self.correct_answer_map: Dict[str, str] = {}
        # question_id -> list[int] tags
        self.tag_map: Dict[str, List[int]] = {}
        # question_id -> part
        self.part_map: Dict[str, int] = {}

        self.skill_stats = defaultdict(lambda: {"correct": 0, "total": 0, "students": set()})
        self.total_interactions = 0
        self.total_students = 0

    # ------------------------------------------------------------------ #
    # Step 1: load question metadata (small file, load fully into memory)
    # ------------------------------------------------------------------ #
    def load_questions(self):
        if not os.path.exists(self.questions_path):
            raise FileNotFoundError(
                f"questions.csv not found at {self.questions_path}. "
                "Check that EdNet-Contents.zip was extracted correctly."
            )

        print(f"Loading question metadata from {self.questions_path} ...")
        df = pd.read_csv(self.questions_path)

        for _, row in df.iterrows():
            qid = row["question_id"]
            self.correct_answer_map[qid] = row["correct_answer"]
            self.part_map[qid] = int(row["part"]) if pd.notna(row["part"]) else -1

            tags_raw = row["tags"]
            if pd.isna(tags_raw) or str(tags_raw).strip() in ("", "-1"):
                self.tag_map[qid] = []
            else:
                self.tag_map[qid] = [int(t) for t in str(tags_raw).split(";") if t.strip().isdigit()]

        n_tags = len(set(t for tags in self.tag_map.values() for t in tags))
        print(f"  Loaded {len(df):,} questions, {n_tags} unique skill tags, "
              f"{df['part'].nunique()} distinct parts.")

    # ------------------------------------------------------------------ #
    # Step 2: process one student's KT1 shard -> exploded (interaction, skill) rows
    # ------------------------------------------------------------------ #
    def process_kt1_shard(self, filepath: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(filepath)
        except Exception:
            return pd.DataFrame()

        if "question_id" not in df.columns or "user_answer" not in df.columns:
            return pd.DataFrame()

        # Derive correctness by joining against the real answer key
        df["correct_answer"] = df["question_id"].map(self.correct_answer_map)
        df = df.dropna(subset=["correct_answer"])
        df["correct"] = (df["user_answer"] == df["correct_answer"]).astype(int)

        # Attach tags (list per row) and part
        df["tags"] = df["question_id"].map(self.tag_map)
        df["part"] = df["question_id"].map(self.part_map)

        # Explode: one row per (interaction, skill) so multi-tag questions count for each skill
        df = df[df["tags"].map(lambda t: isinstance(t, list) and len(t) > 0)]
        if df.empty:
            return pd.DataFrame()

        df = df.explode("tags").rename(columns={"tags": "skill"})
        df["skill"] = df["skill"].astype(int)

        return df

    # ------------------------------------------------------------------ #
    # Step 3: iterate all student shards in batches
    # ------------------------------------------------------------------ #
    def process_all_kt1(self, max_shards: int = None, batch_size: int = 2000):
        pattern = os.path.join(self.kt1_dir, "*.csv")
        all_files = sorted(glob.glob(pattern))

        if not all_files:
            raise FileNotFoundError(f"No CSV files found in {self.kt1_dir}")

        if max_shards:
            all_files = all_files[:max_shards]

        self.total_students = len(all_files)
        print(f"Processing {self.total_students:,} student files from KT1 ...")

        batch_dfs = []
        batch_num = 0

        for i, filepath in enumerate(tqdm(all_files, desc="KT1")):
            student_id = os.path.splitext(os.path.basename(filepath))[0]  # e.g. 'u10'
            df = self.process_kt1_shard(filepath)

            if len(df) > 0:
                df["student_id"] = student_id
                batch_dfs.append(df)
                self.total_interactions += len(df)

                for _, row in df.iterrows():
                    skill = row["skill"]
                    self.skill_stats[skill]["total"] += 1
                    self.skill_stats[skill]["correct"] += int(row["correct"])
                    self.skill_stats[skill]["students"].add(student_id)

            if len(batch_dfs) >= batch_size:
                self._write_batch(batch_dfs, batch_num)
                batch_dfs = []
                batch_num += 1

        if batch_dfs:
            self._write_batch(batch_dfs, batch_num)

        print(f"\n✅ Processed {self.total_interactions:,} (interaction, skill) rows "
              f"from {self.total_students:,} students")

    def _write_batch(self, batch_dfs: List[pd.DataFrame], batch_num: int):
        combined = pd.concat(batch_dfs, ignore_index=True)
        keep_cols = ["timestamp", "student_id", "question_id", "skill", "correct", "part", "elapsed_time"]
        keep_cols = [c for c in keep_cols if c in combined.columns]
        combined = combined[keep_cols]

        pq_path = os.path.join(self.output_dir, f"batch_{batch_num}.parquet")
        combined.to_parquet(pq_path, index=False, compression="snappy")

    # ------------------------------------------------------------------ #
    # Step 4: aggregate all batches into the final skill_interactions.csv
    # ------------------------------------------------------------------ #
    def build_skill_interactions(self):
        print("\nAggregating batches into skill_interactions.csv ...")
        batches = sorted(glob.glob(os.path.join(self.output_dir, "batch_*.parquet")))
        if not batches:
            print("No batches found — did process_all_kt1 run successfully?")
            return None

        dfs = [pd.read_parquet(b) for b in tqdm(batches, desc="Reading batches")]
        df = pd.concat(dfs, ignore_index=True)

        out_path = os.path.join(self.output_dir, "skill_interactions.csv")
        df.to_csv(out_path, index=False)

        skill_summary = []
        for skill, stats in self.skill_stats.items():
            if stats["total"] > 0:
                skill_summary.append({
                    "skill": skill,
                    "total_attempts": stats["total"],
                    "correct_count": stats["correct"],
                    "accuracy": stats["correct"] / stats["total"],
                    "unique_students": len(stats["students"]),
                })
        skill_df = pd.DataFrame(skill_summary).sort_values("total_attempts", ascending=False)
        skill_df.to_csv(os.path.join(self.output_dir, "skill_statistics.csv"), index=False)

        print(f"  Skills: {df['skill'].nunique()}")
        print(f"  Students: {df['student_id'].nunique():,}")
        print(f"  (interaction, skill) rows: {len(df):,}")
        print(f"  Overall accuracy: {df['correct'].mean():.2%}")
        print(f"  Saved to {out_path}")

        return df

    # ------------------------------------------------------------------ #
    # Step 5: discover prerequisites from real temporal + correlation data
    # ------------------------------------------------------------------ #
    def build_prerequisites(self, min_correlation: float = 0.1, min_support: int = 50):
        print("\nDiscovering prerequisite relationships from data ...")
        path = os.path.join(self.output_dir, "skill_interactions.csv")
        if not os.path.exists(path):
            print("Run build_skill_interactions first.")
            return []

        df = pd.read_csv(path)
        if len(df) > 2_000_000:
            df = df.sample(n=2_000_000, random_state=42)

        first = (
            df.sort_values("timestamp")
            .groupby(["student_id", "skill"])["correct"]
            .first()
            .reset_index()
        )
        pivot = first.pivot(index="student_id", columns="skill", values="correct")
        corr = pivot.corr()
        skills = corr.columns

        prereqs = []
        for a in skills:
            for b in skills:
                if a == b:
                    continue
                c = corr.loc[a, b]
                if pd.isna(c) or abs(c) < min_correlation:
                    continue

                a_times = df[df["skill"] == a].groupby("student_id")["timestamp"].min()
                b_times = df[df["skill"] == b].groupby("student_id")["timestamp"].min()
                common = a_times.index.intersection(b_times.index)
                if len(common) < min_support:
                    continue

                a_before_b = (a_times[common] < b_times[common]).mean()
                if a_before_b > 0.55:
                    prereqs.append({
                        "prerequisite": int(a),
                        "target": int(b),
                        "correlation": float(c),
                        "precedence": float(a_before_b),
                        "support": int(len(common)),
                    })

        with open(os.path.join(self.output_dir, "prerequisites.json"), "w") as f:
            json.dump(prereqs, f, indent=2)

        print(f"  Found {len(prereqs)} candidate prerequisite pairs")
        return prereqs

    # ------------------------------------------------------------------ #
    # Step 6: build DKT-ready sequences
    # ------------------------------------------------------------------ #
    def generate_dkt_sequences(self, max_seq_len: int = 200, min_seq_len: int = 10):
        print("\nGenerating DKT sequences ...")
        path = os.path.join(self.output_dir, "skill_interactions.csv")
        df = pd.read_csv(path)

        unique_skills = sorted(int(s) for s in df["skill"].unique())
        skill_enc = {s: i for i, s in enumerate(unique_skills)}
        df["skill_enc"] = df["skill"].map(skill_enc)
        df["interaction"] = df["skill_enc"] * 2 + df["correct"]

        sequences = []
        for sid, group in tqdm(df.groupby("student_id"), desc="Building sequences"):
            group = group.sort_values("timestamp")
            if len(group) < min_seq_len:
                continue

            inter = group["interaction"].tolist()
            skl = group["skill_enc"].tolist()
            cor = group["correct"].tolist()

            for start in range(0, len(inter), max_seq_len):
                ci, cs, cc = inter[start:start + max_seq_len], skl[start:start + max_seq_len], cor[start:start + max_seq_len]
                if len(ci) >= min_seq_len:
                    sequences.append({
                        "student_id": sid, "interactions": ci,
                        "skills": cs, "correct": cc, "length": len(ci),
                    })

        students = list(set(s["student_id"] for s in sequences))
        np.random.seed(42)
        np.random.shuffle(students)
        split = int(0.8 * len(students))
        train_ids = set(students[:split])

        train = [s for s in sequences if s["student_id"] in train_ids]
        test = [s for s in sequences if s["student_id"] not in train_ids]

        with open(os.path.join(self.output_dir, "dkt_train.pkl"), "wb") as f:
            pickle.dump(train, f)
        with open(os.path.join(self.output_dir, "dkt_test.pkl"), "wb") as f:
            pickle.dump(test, f)
        with open(os.path.join(self.output_dir, "skill_encoder.json"), "w") as f:
            json.dump(skill_enc, f)

        print(f"  Train: {len(train):,} | Test: {len(test):,} | Skills: {len(unique_skills)}")
        return train, test

    # ------------------------------------------------------------------ #
    def run_pipeline(self, max_shards: int = 10000):
        print("=" * 60)
        print("EdNet Pipeline v2 (real question_id -> tags/correct_answer join)")
        print("=" * 60)

        self.load_questions()
        self.process_all_kt1(max_shards=max_shards)
        self.build_skill_interactions()
        self.build_prerequisites()
        self.generate_dkt_sequences()

        print("\n✅ Done! Outputs in:", self.output_dir)


if __name__ == "__main__":
    processor = EdNetProcessorV2()
    # Start with 10,000 students to validate the pipeline before scaling to all 784K
    processor.run_pipeline(max_shards=10000)