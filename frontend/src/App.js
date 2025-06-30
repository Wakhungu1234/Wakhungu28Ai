import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Badge } from "./components/ui/badge";
import QuickStartForm from "./components/QuickStartForm";
import BotDashboard from "./components/BotDashboard";
import { Toaster } from "./components/ui/toaster";
import { 
  Bot, 
  Zap, 
  BarChart3, 
  TrendingUp, 
  Wifi, 
  WifiOff,
  Rocket,
  Activity,
  Settings
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Home = () => {
  const [activeTab, setActiveTab] = useState("quickstart");

  const handleBotCreated = (botData) => {
    // Switch to bot dashboard after creating a bot
    setActiveTab("dashboard");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        
        {/* Main Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-4 mb-4">
            <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full">
              <Bot className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-6xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
              Wakhungu28Ai
            </h1>
            <div className="flex items-center space-x-2">
              <Badge className="bg-green-100 text-green-800 border-green-300">
                <Wifi className="w-3 h-3 mr-1" />
                Live
              </Badge>
              <Badge className="bg-blue-100 text-blue-800 border-blue-300">
                <Activity className="w-3 h-3 mr-1" />
                AI Enhanced
              </Badge>
            </div>
          </div>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Advanced AI Trading Bot for Deriv.com - Target: 88%+ Win Rate through Ultra-Aggressive Pattern Recognition
          </p>
          
          {/* Feature Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-8">
            <div className="bg-white rounded-lg shadow p-4 border">
              <div className="flex items-center justify-center mb-2">
                <Zap className="w-8 h-8 text-yellow-500" />
              </div>
              <h3 className="font-semibold text-gray-800">Ultra-Aggressive</h3>
              <p className="text-sm text-gray-600">3-second trading intervals</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border">
              <div className="flex items-center justify-center mb-2">
                <BarChart3 className="w-8 h-8 text-blue-500" />
              </div>
              <h3 className="font-semibold text-gray-800">AI Enhanced</h3>
              <p className="text-sm text-gray-600">Advanced pattern recognition</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border">
              <div className="flex items-center justify-center mb-2">
                <TrendingUp className="w-8 h-8 text-green-500" />
              </div>
              <h3 className="font-semibold text-gray-800">High Performance</h3>
              <p className="text-sm text-gray-600">Target 88%+ win rate</p>
            </div>
          </div>
        </div>

        {/* Pro Bot Tabs */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <Rocket className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800">⚡ Pro Bot</h2>
            <Badge className="bg-purple-100 text-purple-800 border-purple-300">
              Professional Trading Interface
            </Badge>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8">
              <TabsTrigger 
                value="quickstart" 
                className="flex items-center space-x-2 text-lg py-3"
              >
                <Zap className="w-5 h-5" />
                <span>🚀 QUICK START - Trade NOW!</span>
              </TabsTrigger>
              <TabsTrigger 
                value="dashboard" 
                className="flex items-center space-x-2 text-lg py-3"
              >
                <Settings className="w-5 h-5" />
                <span>🤖 Bot Management</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="quickstart" className="space-y-6">
              <QuickStartForm onBotCreated={handleBotCreated} />
            </TabsContent>

            <TabsContent value="dashboard" className="space-y-6">
              <BotDashboard />
            </TabsContent>
          </Tabs>
        </div>

        {/* API Status Footer */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white rounded-full shadow-md border">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm text-gray-600">
              Connected to Deriv.com WebSocket API - Real-time data streaming
            </span>
          </div>
        </div>

        {/* Warning Disclaimer */}
        <div className="mt-6 max-w-2xl mx-auto">
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="text-amber-600">
                ⚠️
              </div>
              <div>
                <h4 className="font-semibold text-amber-800">Trading Risk Warning</h4>
                <p className="text-sm text-amber-700 mt-1">
                  Trading derivatives carries significant risk. Only trade with money you can afford to lose. 
                  Past performance does not guarantee future results. Monitor your bots closely.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <Toaster />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
