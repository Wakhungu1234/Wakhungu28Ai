import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Shield, Lock, Eye, EyeOff } from 'lucide-react';

const PasswordProtection = ({ onAuthSuccess }) => {
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Check if already authenticated
  useEffect(() => {
    const isAuthenticated = localStorage.getItem('wakhungu28ai_authenticated');
    if (isAuthenticated === 'true') {
      onAuthSuccess();
    }
  }, [onAuthSuccess]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Your specified password
    const correctPassword = '($_Wakhungu28_$)';

    if (password === correctPassword) {
      // Store authentication in localStorage
      localStorage.setItem('wakhungu28ai_authenticated', 'true');
      onAuthSuccess();
    } else {
      setError('Incorrect password. Access denied.');
      setPassword('');
    }
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-red-500 to-orange-500 rounded-full">
              <Shield className="w-12 h-12 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Wakhungu28Ai
          </h1>
          <p className="text-blue-200">
            Secure Access Required
          </p>
        </div>

        {/* Password Form */}
        <div className="bg-white rounded-xl shadow-2xl p-8 border border-gray-200">
          <div className="text-center mb-6">
            <Lock className="w-8 h-8 text-blue-600 mx-auto mb-3" />
            <h2 className="text-2xl font-bold text-gray-800">Protected Access</h2>
            <p className="text-gray-600 mt-2">
              Enter your password to access the ULTRA-FAST trading platform
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="password" className="text-sm font-medium text-gray-700">
                Access Password
              </Label>
              <div className="relative mt-1">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full px-3 py-3 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3">
                <div className="flex items-center">
                  <div className="text-red-600 text-sm">
                    🚫 {error}
                  </div>
                </div>
              </div>
            )}

            <Button
              type="submit"
              disabled={isLoading || !password}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white py-3 text-lg font-semibold rounded-md shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
            >
              {isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Authenticating...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span>Access Wakhungu28Ai</span>
                </div>
              )}
            </Button>
          </form>

          {/* Security Notice */}
          <div className="mt-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <div className="text-amber-600">
                🔒
              </div>
              <div>
                <h4 className="font-semibold text-amber-800">Security Notice</h4>
                <p className="text-sm text-amber-700 mt-1">
                  This platform executes real trades on Deriv.com. Ensure you're on a secure network 
                  and never share your access credentials.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-blue-200 text-sm">
            🚀 ULTRA-FAST AI Trading Platform • Authorized Users Only
          </p>
        </div>
      </div>
    </div>
  );
};

export default PasswordProtection;