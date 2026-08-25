import React from 'react';
import LearningDashboard from '../components/LearningDashboard';

const Dashboard = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <LearningDashboard />
      </div>
    </div>
  );
};

export default Dashboard;