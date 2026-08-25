import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center">
      <div className="text-center text-white px-4">
        <h1 className="text-6xl font-bold mb-4">🎓 EduLeap</h1>
        <p className="text-xl mb-8 text-indigo-100">
          AI Tutoring for Learning-Disadvantaged Children
        </p>
        <div className="space-y-4">
          <button 
            onClick={() => navigate('/learn')}
            className="px-8 py-4 bg-white text-indigo-600 rounded-2xl font-bold text-lg hover:scale-105 transition shadow-xl"
          >
            Start Learning
          </button>
          <p className="text-sm text-indigo-200">
            Powered by NVIDIA NIM • Agentrix 2026
          </p>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;