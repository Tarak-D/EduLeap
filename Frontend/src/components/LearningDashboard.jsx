import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/tutoring';

const LearningDashboard = () => {
  const [history, setHistory] = useState([]);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // For demo, we'll just show a mock session
    // In production, fetch from /api/tutoring/session/{id}/history
    setHistory([
      { type: 'diagnostic', content: 'What is 1/2 + 1/2?', response: 'A) 2/4', evaluation: { correct: true } },
      { type: 'explanation', content: 'Great! Now let\'s learn about common denominators...', response: null },
      { type: 'question', content: 'What is 1/2 + 1/3?', response: 'B) 5/6', evaluation: { correct: true } }
    ]);
  }, []);

  const getTypeColor = (type) => {
    const colors = {
      diagnostic: 'bg-yellow-100 text-yellow-800',
      explanation: 'bg-blue-100 text-blue-800',
      question: 'bg-green-100 text-green-800',
      analysis: 'bg-purple-100 text-purple-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Learning Progress</h2>
        <p className="text-gray-500">Track your adaptive learning journey</p>
        
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="bg-indigo-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-indigo-600">3.5</div>
            <div className="text-sm text-indigo-400">Current Level</div>
          </div>
          <div className="bg-green-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-green-600">12</div>
            <div className="text-sm text-green-400">Questions Answered</div>
          </div>
          <div className="bg-orange-50 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-orange-600">2</div>
            <div className="text-sm text-orange-400">Gaps Identified</div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Session History</h3>
        <div className="space-y-3">
          {history.map((item, idx) => (
            <div key={idx} className="border rounded-xl p-4 hover:shadow-md transition">
              <div className="flex justify-between items-start mb-2">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(item.type)}`}>
                  {item.type.toUpperCase()}
                </span>
                {item.evaluation && (
                  <span className={`text-sm font-medium ${item.evaluation.correct ? 'text-green-600' : 'text-red-600'}`}>
                    {item.evaluation.correct ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                )}
              </div>
              <p className="text-gray-800 font-medium mb-1">{item.content}</p>
              {item.response && (
                <p className="text-gray-500 text-sm">Your answer: {item.response}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl shadow-lg p-6">
        <h3 className="text-lg font-semibold mb-4">Identified Knowledge Gaps</h3>
        <div className="space-y-2">
          <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg border-l-4 border-red-400">
            <span className="text-2xl">⚠️</span>
            <div>
              <div className="font-medium text-red-800">Common Denominators</div>
              <div className="text-sm text-red-600">Needs prerequisite review</div>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-400">
            <span className="text-2xl">🔄</span>
            <div>
              <div className="font-medium text-yellow-800">Equivalent Fractions</div>
              <div className="text-sm text-yellow-600">In progress</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LearningDashboard;