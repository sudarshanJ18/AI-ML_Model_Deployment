import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import LiveRecognition from './components/LiveRecognition';
import ImageUpload from './components/ImageUpload';
import FaceGallery from './components/FaceGallery';
import History from './components/History';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <div className="bg-gray-100 min-h-screen">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/live-recognition" element={<LiveRecognition />} />
            <Route path="/image-upload" element={<ImageUpload />} />
            <Route path="/face-gallery" element={<FaceGallery />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;