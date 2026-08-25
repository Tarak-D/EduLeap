import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import LearningDashboard from './components/LearningDashboard';

function App() {
  const [view, setView] = useState('chat'); // 'chat' | 'dashboard'

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">🎓 EduLeap</h1>
          <div className="space-x-4">
            <button 
              onClick={() => setView('chat')}
              className={`px-4 py-2 rounded-lg ${view === 'chat' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Learn
            </button>
            <button 
              onClick={() => setView('dashboard')}
              className={`px-4 py-2 rounded-lg ${view === 'dashboard' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
            >
              Progress
            </button>
          </div>
        </div>
      </nav>
      
      <main className="max-w-4xl mx-auto p-4">
        {view === 'chat' ? <ChatInterface /> : <LearningDashboard />}
      </main>
    </div>
  );
}

export default App;