import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FiUsers, FiCamera, FiUpload, FiGrid, FiClock } from 'react-icons/fi';
import { faceRecognitionAPI } from '../api';

const StatCard = ({ icon, label, value, color }) => (
  <div className={`bg-white p-6 rounded-lg shadow-md flex items-center ${color}`}>
    <div className="mr-4">{icon}</div>
    <div>
      <p className="text-lg font-semibold text-gray-700">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  </div>
);

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalFaces: 0,
    recognitionsToday: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [facesResponse, logsResponse] = await Promise.all([
          faceRecognitionAPI.getFaces(),
          faceRecognitionAPI.getLogs()
        ]);
        
        const totalFaces = facesResponse.data.length;
        const today = new Date().toDateString();
        const recognitionsToday = logsResponse.data.filter(log => 
          new Date(log.timestamp).toDateString() === today
        ).length;
        
        setStats({ totalFaces, recognitionsToday });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold text-gray-800">Face Recognition Dashboard</h1>
          <p className="text-lg text-gray-600 mt-2">
            Welcome! Manage your face database and view recognition history.
          </p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <StatCard
            icon={<FiUsers size={32} className="text-blue-500" />}
            label="Total Faces Stored"
            value={loading ? '...' : stats.totalFaces}
            color="bg-blue-50"
          />
          <StatCard
            icon={<FiClock size={32} className="text-green-500" />}
            label="Recognitions Today"
            value={loading ? '...' : stats.recognitionsToday}
            color="bg-green-50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Link to="/live-recognition" className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow text-center">
            <FiCamera size={48} className="mx-auto text-indigo-500 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800">Live Recognition</h2>
            <p className="text-gray-600 mt-2">Use your webcam for real-time face recognition.</p>
          </Link>

          <Link to="/image-upload" className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow text-center">
            <FiUpload size={48} className="mx-auto text-purple-500 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800">Upload Image</h2>
            <p className="text-gray-600 mt-2">Recognize faces from an uploaded image.</p>
          </Link>

          <Link to="/face-gallery" className="bg-white p-8 rounded-lg shadow-md hover:shadow-xl transition-shadow text-center">
            <FiGrid size={48} className="mx-auto text-pink-500 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800">Face Gallery</h2>
            <p className="text-gray-600 mt-2">View and manage all stored faces.</p>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;