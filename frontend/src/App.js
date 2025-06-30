import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";

// Import components
import TradingDashboard from "./components/TradingDashboard";
import BotControlPanel from "./components/BotControlPanel";
import Navigation from "./components/Navigation";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    // Test API connection on startup
    const testConnection = async () => {
      try {
        const response = await axios.get(`${API}/`);
        setApiStatus(response.data);
        console.log("✅ Connected to Wakhungu28Ai API:", response.data.message);
      } catch (error) {
        console.error("❌ Failed to connect to API:", error);
        setApiStatus({ error: "Connection failed" });
      }
    };

    testConnection();
  }, []);

  return (
    <div className="App">
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
          {/* Header */}
          <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-bold text-sm">W</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white">Wakhungu28Ai</h1>
                  </div>
                  <div className="hidden md:flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${apiStatus?.message ? 'bg-green-500' : 'bg-red-500'}`}></div>
                    <span className="text-sm text-gray-300">
                      {apiStatus?.message ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                </div>
                
                <Navigation currentPage={currentPage} setCurrentPage={setCurrentPage} />
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route 
                path="/" 
                element={<Navigate to="/dashboard" replace />} 
              />
              <Route 
                path="/dashboard" 
                element={<TradingDashboard />} 
              />
              <Route 
                path="/bot" 
                element={<BotControlPanel />} 
              />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-16">
            <div className="container mx-auto px-4 py-6">
              <div className="text-center text-gray-400">
                <p className="text-sm">
                  🤖 Wakhungu28Ai Trading Platform - Target: 88%+ Win Rate
                </p>
                <p className="text-xs mt-2">
                  {apiStatus?.version && `Version ${apiStatus.version} | `}
                  Powered by AI & Advanced Pattern Recognition
                </p>
              </div>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;