import React from 'react';

const DiagnosticQuiz = ({ question, options, onAnswer, progress }) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 max-w-2xl mx-auto">
      <div className="mb-4">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Diagnostic Assessment</span>
          <span>Question {progress?.current || 1} of {progress?.total || 3}</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-indigo-600 h-2 rounded-full transition-all"
            style={{ width: `${((progress?.current || 1) / (progress?.total || 3)) * 100}%` }}
          />
        </div>
      </div>
      
      <h3 className="text-lg font-semibold text-gray-800 mb-6">{question}</h3>
      
      <div className="space-y-3">
        {options?.map((opt, idx) => (
          <button
            key={idx}
            onClick={() => onAnswer(opt)}
            className="w-full p-4 rounded-xl border-2 border-gray-200 hover:border-indigo-500 hover:bg-indigo-50 transition-all text-left font-medium"
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
};

export default DiagnosticQuiz;