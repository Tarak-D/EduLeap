import React, { createContext, useState, useContext, useCallback } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [student, setStudent] = useState(() => {
    const saved = localStorage.getItem('eduleap_student');
    return saved ? JSON.parse(saved) : null;
  });

  const login = useCallback(async (name) => {
    try {
      const res = await authAPI.guestLogin(name);
      const data = res.data;
      
      localStorage.setItem('eduleap_token', data.access_token);
      localStorage.setItem('eduleap_student', JSON.stringify({
        id: data.student_id,
        name: data.name
      }));
      
      setStudent({ id: data.student_id, name: data.name });
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('eduleap_token');
    localStorage.removeItem('eduleap_student');
    setStudent(null);
  }, []);

  return (
    <AuthContext.Provider value={{ student, login, logout, isAuthenticated: !!student }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};