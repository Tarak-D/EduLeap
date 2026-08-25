import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/tutoring';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    { type: 'bot', content: 'Welcome to EduLeap! 🌟 What topic would you like to learn today? (Try: fraction addition)' }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [studentId] = useState(1); // Demo student
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState('topic_select'); // topic_select | active
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleTopicSelect = async (topic) => {
    setLoading(true);
    setMessages(prev => [...prev, { type: 'user', content: `I want to learn: ${topic}` }]);
    
    try {
      const res = await axios.post(`${API_BASE}/start`, {
        student_id: studentId,
        topic: topic,
        name: "Demo Student"
      });
      
      setSessionId(res.data.progress.session_id);
      setStage('active');
      
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: res.data.content,
        options: res.data.options,
        isQuestion: res.data.type === 'diagnostic' || res.data.type === 'question'
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', content: 'Oops! Something went wrong. Please try again.' }]);
    }
    setLoading(false);
  };

  const handleAnswer = async (answer) => {
    if (!sessionId) return;
    
    setLoading(true);
    setMessages(prev => [...prev, { type: 'user', content: answer }]);
    
    try {
      const res = await axios.post(`${API_BASE}/answer`, {
        session_id: sessionId,
        answer: answer
      });
      
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: res.data.content,
        options: res.data.options,
        isQuestion: res.data.type === 'diagnostic' || res.data.type === 'question',
        progress: res.data.progress
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', content: 'Sorry, I had trouble processing that. Can you try again?' }]);
    }
    setLoading(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    if (stage === 'topic_select') {
      handleTopicSelect(input.trim());
    } else {
      handleAnswer(input.trim());
    }
    setInput('');
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden h-[70vh] flex flex-col">
      {/* Header */}
      <div className="bg-indigo-600 text-white px-6 py-4">
        <h2 className="font-semibold">Your Learning Session</h2>
        <p className="text-indigo-200 text-sm">
          {stage === 'topic_select' ? 'Choose a topic to begin' : 'Adaptive tutoring in progress...'}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 bg-gray-50">
        {messages.map((msg, idx) => (
          <div key={idx}>
            <div className={msg.type === 'user' ? 'message-user' : 'message-bot'}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              
              {/* Options for multiple choice */}
              {msg.options && msg.isQuestion && (
                <div className="mt-4 space-y-2">
                  {msg.options.map((opt, i) => (
                    <button
                      key={i}
                      onClick={() => handleAnswer(opt)}
                      disabled={loading}
                      className="option-btn"
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              )}
              
              {/* Progress indicator */}
              {msg.progress && (
                <div className="mt-3 text-xs text-gray-500 bg-gray-100 rounded px-2 py-1 inline-block">
                  Stage: {msg.progress.stage}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message-bot">
            <span className="loading-dots">Thinking</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={stage === 'topic_select' ? "Enter a topic (e.g., fraction addition)..." : "Type your answer..."}
            className="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium disabled:opacity-50 hover:bg-indigo-700 transition"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;