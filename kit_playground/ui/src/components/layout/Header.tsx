import React from 'react';
import { Link, useLocation } from 'react-router-dom';

export const Header: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Home', path: '/' },
    { name: 'Templates', path: '/templates' },
    { name: 'Jobs', path: '/jobs' },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-dark-card border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-nvidia-green rounded flex items-center justify-center font-bold text-white text-lg">
              K
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Kit App Template</h1>
              <p className="text-xs text-gray-400">NVIDIA Omniverse</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex gap-1">
            {navigation.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all duration-200
                  ${
                    isActive(item.path)
                      ? 'bg-nvidia-green text-white'
                      : 'text-gray-300 hover:bg-dark-hover hover:text-white'
                  }
                `}
              >
                {item.name}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;

