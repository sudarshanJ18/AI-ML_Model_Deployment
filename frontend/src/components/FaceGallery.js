import React, { useState, useEffect } from 'react';
import { faceRecognitionAPI } from '../api';

const FaceGallery = () => {
  const [faces, setFaces] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchFaces = async () => {
      try {
        const response = await faceRecognitionAPI.getFaces();
        setFaces(response.data);
      } catch (error) {
        setError('Error fetching faces');
      } finally {
        setLoading(false);
      }
    };

    fetchFaces();
  }, []);

  const handleDelete = async (faceId) => {
    try {
      await faceRecognitionAPI.deleteFace(faceId);
      setFaces(faces.filter(face => face._id !== faceId));
    } catch (error) {
      setError('Error deleting face');
    }
  };

  const filteredFaces = faces.filter(face =>
    face.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="text-center p-8">Loading...</div>;
  if (error) return <div className="text-red-500 text-center p-8">{error}</div>;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Face Gallery</h1>
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg shadow-sm"
          />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {filteredFaces.map(face => (
            <div key={face._id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                <span className="text-gray-500">Face Image</span>
              </div>
              <div className="p-4">
                <p className="font-semibold text-lg">{face.name}</p>
                <p className="text-sm text-gray-500">Added: {new Date(face.created_at).toLocaleDateString()}</p>
                <button
                  onClick={() => handleDelete(face._id)}
                  className="mt-4 w-full px-4 py-2 font-semibold rounded-lg shadow-md text-white bg-red-500 hover:bg-red-600">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FaceGallery;