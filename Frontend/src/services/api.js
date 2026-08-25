import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor for auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('eduleap_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  guestLogin: (name) => api.post('/api/auth/guest', { name }),
  getMe: (studentId) => api.get('/api/auth/me', { params: { student_id: studentId } })
};

export const tutoringAPI = {
  startSession: (studentId, topic, name) => 
    api.post('/api/tutoring/start', { student_id: studentId, topic, name }),
  submitAnswer: (sessionId, answer) => 
    api.post('/api/tutoring/answer', { session_id: sessionId, answer }),
  getHistory: (sessionId) => 
    api.get(`/api/tutoring/session/${sessionId}/history`)
};

export const studentAPI = {
  getStudent: (id) => api.get(`/api/students/${id}`),
  getGaps: (id) => api.get(`/api/students/${id}/gaps`)
};

export const analyticsAPI = {
  getSessionAnalytics: (sessionId) => api.get(`/api/analytics/session/${sessionId}`),
  getProgress: (studentId) => api.get(`/api/analytics/student/${studentId}/progress`)
};

export default api;