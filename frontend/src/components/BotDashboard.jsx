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
  BarChart3,
  RefreshCw,
  AlertTriangle
} from 'lucide-react';
import { toast } from './ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const BotDashboard = () => {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState({});

  useEffect(() => {
    fetchBots();
    const interval = setInterval(fetchBots, 3000); // Refresh every 3 seconds for faster updates
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
    setActionLoading(prev => ({ ...prev, [botId]: 'stopping' }));
    try {
      const response = await fetch(`${BACKEND_URL}/api/bots/${botId}/stop`, {
        method: 'PUT'
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message || '🛑 Bot stopped successfully');
        fetchBots();
      } else {
        const error = await response.json();
        toast.error('Failed to stop bot', {
          description: error.detail || 'Unknown error occurred'
        });
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to connect to server'
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [botId]: null }));
    }
  };

  const restartBot = async (botId) => {
    if (!window.confirm('Are you sure you want to restart this bot? This will reset its statistics and start fresh trading.')) {
      return;
    }

    setActionLoading(prev => ({ ...prev, [botId]: 'restarting' }));
    try {
      const response = await fetch(`${BACKEND_URL}/api/bots/${botId}/restart`, {
        method: 'PUT'
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message || '🔄 Bot restarted successfully');
        fetchBots();
      } else {
        const error = await response.json();
        toast.error('Failed to restart bot', {
          description: error.detail || 'Unknown error occurred'
        });
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to connect to server'
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [botId]: null }));
    }
  };

  const deleteBot = async (botId) => {
    if (!window.confirm('⚠️ PERMANENT DELETION WARNING\n\nThis will permanently delete the bot and ALL its trading history. This action cannot be undone.\n\nAre you absolutely sure you want to proceed?')) {
      return;
    }

    setActionLoading(prev => ({ ...prev, [botId]: 'deleting' }));
    try {
      const response = await fetch(`${BACKEND_URL}/api/bots/${botId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(result.message || '🗑️ Bot deleted successfully');
        setBots(prev => prev.filter(bot => bot.id !== botId));
      } else {
        const error = await response.json();
        toast.error('Failed to delete bot', {
          description: error.detail || 'Unknown error occurred'
        });
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to connect to server'
      });
    } finally {
      setActionLoading(prev => ({ ...prev, [botId]: null }));
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

  const getTradingSpeed = (status) => {
    if (status === 'ACTIVE') {
      return (
        <div className="flex items-center space-x-1 text-xs text-green-600">
          <Zap className="w-3 h-3" />
          <span>ULTRA-FAST (0.5s)</span>
        </div>
      );
    }
    return null;
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
        <p className="text-gray-600">Monitor and manage your ULTRA-FAST trading bots</p>
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
          <p className="text-gray-500 mb-6">Create your first ULTRA-FAST trading bot using Quick Start</p>
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
                    <div className="flex items-center space-x-2">
                      <p className="text-sm text-gray-500">ID: {bot.id.slice(0, 8)}...</p>
                      {getTradingSpeed(bot.status)}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {getStatusBadge(bot.status)}
                  {bot.status === 'ACTIVE' && (
                    <div className="flex items-center space-x-1 text-xs text-red-600 mt-1">
                      <AlertTriangle className="w-3 h-3" />
                      <span>ULTRA-FAST MODE</span>
                    </div>
                  )}
                </div>
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
                    disabled={actionLoading[bot.id] === 'stopping'}
                  >
                    {actionLoading[bot.id] === 'stopping' ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-3 w-3 border-b border-white"></div>
                        <span>Stopping...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1">
                        <Square className="w-4 h-4" />
                        <span>Stop Bot</span>
                      </div>
                    )}
                  </Button>
                ) : (
                  <Button
                    onClick={() => restartBot(bot.id)}
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    disabled={actionLoading[bot.id] === 'restarting'}
                  >
                    {actionLoading[bot.id] === 'restarting' ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-3 w-3 border-b border-gray-600"></div>
                        <span>Restarting...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-1">
                        <RefreshCw className="w-4 h-4" />
                        <span>Restart</span>
                      </div>
                    )}
                  </Button>
                )}
                
                <Button
                  onClick={() => deleteBot(bot.id)}
                  variant="outline"
                  size="sm"
                  disabled={actionLoading[bot.id] === 'deleting'}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                >
                  {actionLoading[bot.id] === 'deleting' ? (
                    <div className="animate-spin rounded-full h-4 w-4 border-b border-red-600"></div>
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
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