import React, { useState, useRef } from 'react';

const VoiceInput = ({ onTranscript, disabled }) => {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      onTranscript(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setIsListening(false);
  };

  return (
    <button
      type="button"
      onClick={isListening ? stopListening : startListening}
      disabled={disabled}
      className={`p-3 rounded-xl transition-all ${
        isListening 
          ? 'bg-red-500 text-white animate-pulse' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      }`}
      title="Voice input"
    >
      {isListening ? '🔴 Listening...' : '🎤'}
    </button>
  );
};

export default VoiceInput;