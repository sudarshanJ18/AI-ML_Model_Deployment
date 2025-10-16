import React, { useState } from 'react';
import { faceRecognitionAPI } from '../api';

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recognitionResult, setRecognitionResult] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setRecognitionResult(null);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await faceRecognitionAPI.recognizeFace(selectedFile);
      setRecognitionResult(response.data);
    } catch (error) {
      console.error('Error recognizing face:', error);
      setError(error.response?.data?.detail || 'Error processing image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Image Upload Recognition</h1>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex flex-col items-center mb-4">
            <input
              accept="image/*"
              style={{ display: 'none' }}
              id="image-upload-file"
              type="file"
              onChange={handleFileChange}
            />
            <label htmlFor="image-upload-file" className="cursor-pointer">
              <div className="w-full max-w-md p-10 border-2 border-dashed border-gray-300 rounded-lg text-center hover:bg-gray-50">
                {previewUrl ? (
                  <img src={previewUrl} alt="Preview" className="max-h-60 mx-auto rounded-lg" />
                ) : (
                  <p className="text-gray-500">Click to select an image</p>
                )}
              </div>
            </label>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || loading}
              className="mt-6 px-6 py-2 font-semibold rounded-lg shadow-md text-white bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400">
              {loading ? 'Recognizing...' : 'Recognize Face'}
            </button>
          </div>
          {error && <div className="text-red-500 text-center my-4">{error}</div>}
          {recognitionResult && (
            <div className="mt-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Recognition Results</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="font-semibold">Faces Detected: {recognitionResult.faces_detected}</h3>
                </div>
                {recognitionResult.recognized_faces.map((face, index) => (
                  <div key={index} className="bg-gray-50 p-4 rounded-lg">
                    <p className="font-semibold text-lg">{face.name}</p>
                    <p>Confidence: {(face.confidence * 100).toFixed(2)}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageUpload;