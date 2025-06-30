import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Bot, 
  Play, 
  Square, 
  Trash2, 
  TrendingUp, 
  TrendingDown, 
  Activity,
  DollarSign,
  Target,
  Zap,
  Clock,
  BarChart3
} from 'lucide-react';
import { toast } from './ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const BotDashboard = () => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBots();
    const interval = setInterval(fetchBots, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchBots = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bots`);
      const data = await response.json();
      setBots(data);
    } catch (error) {
      console.error('Error fetching bots:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopBot = async (botId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/bots/${botId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Bot stopped successfully');
        fetchBots();
      } else {
        toast.error('Failed to stop bot');
      }
    } catch (error) {
      toast.error('Connection error');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-500';
      case 'STARTING': return 'bg-yellow-500';
      case 'STOPPED': return 'bg-gray-500';
      case 'ERROR': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ACTIVE': return <Badge className="bg-green-100 text-green-800 border-green-300">🟢 Active</Badge>;
      case 'STARTING': return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300">🟡 Starting</Badge>;
      case 'STOPPED': return <Badge className="bg-gray-100 text-gray-800 border-gray-300">⚫ Stopped</Badge>;
      case 'ERROR': return <Badge className="bg-red-100 text-red-800 border-red-300">🔴 Error</Badge>;
      default: return <Badge className="bg-gray-100 text-gray-800 border-gray-300">❓ Unknown</Badge>;
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading bots...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-2">🤖 Bot Management Dashboard</h2>
        <p className="text-gray-600">Monitor and manage your trading bots</p>
      </div>

      {/* Stats Overview */}
      {bots.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Bots</p>
                <p className="text-3xl font-bold text-gray-900">{bots.length}</p>
              </div>
              <Bot className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Bots</p>
                <p className="text-3xl font-bold text-green-600">
                  {bots.filter(bot => bot.status === 'ACTIVE').length}
                </p>
              </div>
              <Activity className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Trades</p>
                <p className="text-3xl font-bold text-purple-600">
                  {bots.reduce((sum, bot) => sum + bot.total_trades, 0)}
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6 border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Avg Win Rate</p>
                <p className="text-3xl font-bold text-orange-600">
                  {bots.length > 0 ? 
                    Math.round(bots.reduce((sum, bot) => sum + bot.win_rate, 0) / bots.length) : 0}%
                </p>
              </div>
              <Target className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>
      )}

      {/* Bots Grid */}
      {bots.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl shadow-lg border border-gray-200">
          <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-600 mb-2">No Trading Bots</h3>
          <p className="text-gray-500 mb-6">Create your first ultra-aggressive trading bot using Quick Start</p>
          <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-lg">
            <Zap className="w-4 h-4 mr-2" />
            Use the "🚀 QUICK START - Trade NOW!" tab to get started
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {bots.map((bot) => (
            <div key={bot.id} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              {/* Bot Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
                    <Bot className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-gray-800">{bot.name}</h3>
                    <p className="text-sm text-gray-500">ID: {bot.id.slice(0, 8)}...</p>
                  </div>
                </div>
                {getStatusBadge(bot.status)}
              </div>

              {/* Performance Metrics */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Balance</span>
                    <DollarSign className="w-4 h-4 text-green-600" />
                  </div>
                  <p className="text-xl font-bold text-gray-800">${bot.current_balance.toFixed(2)}</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Win Rate</span>
                    <Target className="w-4 h-4 text-blue-600" />
                  </div>
                  <p className="text-xl font-bold text-gray-800">{bot.win_rate}%</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Total Trades</span>
                    <BarChart3 className="w-4 h-4 text-purple-600" />
                  </div>
                  <p className="text-xl font-bold text-gray-800">{bot.total_trades}</p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Profit</span>
                    {bot.total_profit >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-600" />
                    )}
                  </div>
                  <p className={`text-xl font-bold ${bot.total_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${bot.total_profit.toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Additional Stats */}
              <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
                <div className="flex items-center space-x-2">
                  <Zap className="w-4 h-4" />
                  <span>Streak: {bot.current_streak}</span>
                </div>
                {bot.uptime && (
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4" />
                    <span>Uptime: {bot.uptime}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                {bot.status === 'ACTIVE' ? (
                  <Button
                    onClick={() => stopBot(bot.id)}
                    variant="destructive"
                    size="sm"
                    className="flex-1"
                  >
                    <Square className="w-4 h-4 mr-2" />
                    Stop Bot
                  </Button>
                ) : (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    disabled
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Restart
                  </Button>
                )}
                
                <Button
                  onClick={() => stopBot(bot.id)}
                  variant="outline"
                  size="sm"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BotDashboard;