import React, { useState } from 'react';

const TOPICS = [
  { id: 'fraction addition', label: 'Fraction Addition', icon: '➕', level: 5 },
  { id: 'common denominators', label: 'Common Denominators', icon: '📊', level: 4 },
  { id: 'equivalent fractions', label: 'Equivalent Fractions', icon: '⚖️', level: 4 },
  { id: 'simplifying fractions', label: 'Simplifying Fractions', icon: '✂️', level: 5 },
];

const TopicSelector = ({ onSelect }) => {
  const [hovered, setHovered] = useState(null);

  return (
    <div className="grid grid-cols-2 gap-4 p-4">
      {TOPICS.map((topic) => (
        <button
          key={topic.id}
          onClick={() => onSelect(topic.id)}
          onMouseEnter={() => setHovered(topic.id)}
          onMouseLeave={() => setHovered(null)}
          className={`p-6 rounded-2xl border-2 transition-all text-left ${
            hovered === topic.id 
              ? 'border-indigo-500 bg-indigo-50 shadow-lg scale-105' 
              : 'border-gray-200 bg-white hover:border-indigo-300'
          }`}
        >
          <div className="text-4xl mb-2">{topic.icon}</div>
          <div className="font-bold text-gray-800">{topic.label}</div>
          <div className="text-sm text-gray-500">Level {topic.level}</div>
        </button>
      ))}
    </div>
  );
};

export default TopicSelector;