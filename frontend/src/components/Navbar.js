import React from 'react';
import { NavLink } from 'react-router-dom';
import { FiHome, FiCamera, FiUpload, FiGrid, FiClock } from 'react-icons/fi';

const Navbar = () => {
  const navLinks = [
    { to: '/', icon: <FiHome />, text: 'Dashboard' },
    { to: '/live-recognition', icon: <FiCamera />, text: 'Live Recognition' },
    { to: '/image-upload', icon: <FiUpload />, text: 'Image Upload' },
    { to: '/face-gallery', icon: <FiGrid />, text: 'Face Gallery' },
    { to: '/history', icon: <FiClock />, text: 'History' },
  ];

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <span className="font-bold text-xl text-gray-800">FaceRec</span>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              {navLinks.map(link => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-700 hover:text-white'}`
                  }
                >
                  {link.icon}
                  <span className="ml-2">{link.text}</span>
                </NavLink>
              ))}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;