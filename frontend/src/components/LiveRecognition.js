import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import { faceRecognitionAPI } from '../api';

const LiveRecognition = () => {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [cameraError, setCameraError] = useState(null);
  const webcamRef = useRef(null);

  const handleCameraToggle = () => {
    setIsCameraActive(!isCameraActive);
    setRecognitionResult(null);
    setError(null);
    setCameraError(null);
  };

  const handleCapture = async () => {
    if (!webcamRef.current) {
      setError('Camera not available');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Check if webcam is ready
      if (!webcamRef.current.video || webcamRef.current.video.readyState !== 4) {
        throw new Error('Camera not ready. Please wait a moment and try again.');
      }

      const imageSrc = webcamRef.current.getScreenshot();
      if (!imageSrc) {
        throw new Error('Failed to capture image. Please check camera permissions.');
      }

      const blob = await fetch(imageSrc).then(res => res.blob());
      const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
      
      const response = await faceRecognitionAPI.recognizeFace(file);
      setPreviewUrl(imageSrc);
      setRecognitionResult(response.data);
    } catch (error) {
      console.error('Error capturing and recognizing face:', error);
      setError(error.message || error.response?.data?.detail || 'Error processing image');
    } finally {
      setLoading(false);
    }
  };

  const handleUserMediaError = (error) => {
    console.error('Camera error:', error);
    setCameraError('Camera access denied or not available. Please check your camera permissions.');
    setIsCameraActive(false);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Live Camera Recognition</h1>
        
        {/* Camera Error Message */}
        {cameraError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>Camera Error:</strong> {cameraError}
            <div className="mt-2 text-sm">
              <p>To fix this:</p>
              <ul className="list-disc list-inside ml-4">
                <li>Allow camera access in your browser</li>
                <li>Make sure no other app is using the camera</li>
                <li>Try refreshing the page</li>
                <li>Use Chrome or Firefox for best compatibility</li>
              </ul>
            </div>
          </div>
        )}

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex flex-col items-center mb-4">
            <button
              onClick={handleCameraToggle}
              className={`px-4 py-2 mb-4 font-semibold rounded-lg shadow-md text-white ${isCameraActive ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'}`}>
              {isCameraActive ? 'Turn Off Camera' : 'Turn On Camera'}
            </button>
            
            {isCameraActive && (
              <div className="w-full max-w-2xl mx-auto">
                <Webcam
                  audio={false}
                  ref={webcamRef}
                  screenshotFormat="image/jpeg"
                  className="w-full h-auto rounded-lg shadow-lg"
                  onUserMediaError={handleUserMediaError}
                  videoConstraints={{
                    width: 640,
                    height: 480,
                    facingMode: "user"
                  }}
                />
                <button
                  onClick={handleCapture}
                  disabled={loading}
                  className="mt-4 w-full px-4 py-2 font-semibold rounded-lg shadow-md text-white bg-green-500 hover:bg-green-600 disabled:bg-gray-400">
                  {loading ? 'Recognizing...' : 'Capture & Recognize'}
                </button>
              </div>
            )}
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded my-4">
              <strong>Error:</strong> {error}
            </div>
          )}
          
          {recognitionResult && (
            <div className="mt-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Recognition Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold">Faces Detected: {recognitionResult.faces_detected}</h3>
                </div>
                {recognitionResult.recognized_faces && recognitionResult.recognized_faces.map((face, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg">
                    <p className="font-semibold text-lg">{face.name}</p>
                    <p>Confidence: {(face.confidence * 100).toFixed(2)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Demo Mode Notice */}
          <div className="mt-6 bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded">
            <strong>Demo Mode:</strong> This is a simplified version for testing. Face recognition returns demo results.
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveRecognition;