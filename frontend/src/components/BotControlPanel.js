import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const BotControlPanel = () => {
  const [bots, setBots] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedBot, setSelectedBot] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [createForm, setCreateForm] = useState({
    bot_name: "Wakhungu28Ai",
    initial_balance: 1000,
    deriv_api_token: "",
    min_confidence: 65,
    active_markets: ["R_100", "R_25", "R_50"]
  });

  useEffect(() => {
    fetchBots();
  }, []);

  useEffect(() => {
    if (selectedBot) {
      fetchBotStatus();
      // Set up periodic status updates
      const interval = setInterval(fetchBotStatus, 5000); // Every 5 seconds
      return () => clearInterval(interval);
    }
  }, [selectedBot]);

  const fetchBots = async () => {
    try {
      const response = await axios.get(`${API}/bots`);
      setBots(response.data.bots || []);
      
      // Auto-select first bot if none selected
      if (!selectedBot && response.data.bots?.length > 0) {
        setSelectedBot(response.data.bots[0]);
      }
    } catch (error) {
      console.error("Error fetching bots:", error);
    }
  };

  const fetchBotStatus = async () => {
    if (!selectedBot) return;
    
    try {
      const response = await axios.get(`${API}/bot/${selectedBot.id}/status`);
      setBotStatus(response.data.bot_status);
    } catch (error) {
      console.error("Error fetching bot status:", error);
    }
  };

  const createBot = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/bot/create`, createForm);
      
      if (response.data.status === "success") {
        await fetchBots();
        setShowCreateForm(false);
        setCreateForm({
          bot_name: "Wakhungu28Ai",
          initial_balance: 1000,
          deriv_api_token: "",
          min_confidence: 65,
          active_markets: ["R_100", "R_25", "R_50"]
        });
        
        // Select the newly created bot
        const newBot = bots.find(bot => bot.id === response.data.bot_id);
        if (newBot) setSelectedBot(newBot);
      }
    } catch (error) {
      console.error("Error creating bot:", error);
      alert("Failed to create bot. Please check your API token and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const startBot = async () => {
    if (!selectedBot) return;
    
    setIsLoading(true);
    try {
      await axios.post(`${API}/bot/${selectedBot.id}/start`);
      await fetchBots();
      await fetchBotStatus();
    } catch (error) {
      console.error("Error starting bot:", error);
      alert("Failed to start bot. Please check your configuration.");
    } finally {
      setIsLoading(false);
    }
  };

  const stopBot = async () => {
    if (!selectedBot) return;
    
    setIsLoading(true);
    try {
      await axios.post(`${API}/bot/${selectedBot.id}/stop`);
      await fetchBots();
      await fetchBotStatus();
    } catch (error) {
      console.error("Error stopping bot:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteBot = async () => {
    if (!selectedBot) return;
    
    if (!window.confirm(`Are you sure you want to delete bot "${selectedBot.bot_name}"?`)) {
      return;
    }
    
    setIsLoading(true);
    try {
      await axios.delete(`${API}/bot/${selectedBot.id}`);
      setSelectedBot(null);
      setBotStatus(null);
      await fetchBots();
    } catch (error) {
      console.error("Error deleting bot:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatUptime = (seconds) => {
    if (!seconds) return "0s";
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) return `${hours}h ${minutes}m`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
  };

  const formatCurrency = (amount) => {
    return `$${amount?.toFixed(2) || '0.00'}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          🤖 Wakhungu28Ai Bot Control Panel
        </h2>
        <p className="text-gray-300">
          Manage your AI trading bot for maximum performance
        </p>
      </div>

      {/* Bot List and Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot Selection */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Your Bots</h3>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              + Create Bot
            </button>
          </div>

          {bots.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">No bots created yet</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium"
              >
                Create Your First Bot
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {bots.map((bot) => (
                <div
                  key={bot.id}
                  onClick={() => setSelectedBot(bot)}
                  className={`
                    p-4 rounded-lg cursor-pointer transition-all duration-200
                    ${selectedBot?.id === bot.id
                      ? 'bg-blue-500/30 border-2 border-blue-500'
                      : 'bg-white/5 border border-white/10 hover:bg-white/10'
                    }
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-white font-semibold">{bot.bot_name}</h4>
                      <p className="text-sm text-gray-400">
                        Balance: {formatCurrency(bot.initial_balance)}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${
                        bot.is_active ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <span className="text-xs text-gray-400">
                        {bot.is_active ? 'Running' : 'Stopped'}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bot Controls */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4">Bot Controls</h3>
          
          {selectedBot ? (
            <div className="space-y-4">
              <div className="text-center">
                <h4 className="text-lg font-medium text-white mb-2">
                  {selectedBot.bot_name}
                </h4>
                <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
                  selectedBot.is_active 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  <div className={`w-2 h-2 rounded-full ${
                    selectedBot.is_active ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                  <span>{selectedBot.is_active ? 'Running' : 'Stopped'}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-3">
                {!selectedBot.is_active ? (
                  <button
                    onClick={startBot}
                    disabled={isLoading}
                    className="bg-green-500 hover:bg-green-600 disabled:opacity-50 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    {isLoading ? "Starting..." : "🚀 Start Bot"}
                  </button>
                ) : (
                  <button
                    onClick={stopBot}
                    disabled={isLoading}
                    className="bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    {isLoading ? "Stopping..." : "🛑 Stop Bot"}
                  </button>
                )}

                <button
                  onClick={deleteBot}
                  disabled={isLoading}
                  className="bg-gray-600 hover:bg-gray-700 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium transition-colors"
                >
                  🗑️ Delete Bot
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">Select a bot to control</p>
            </div>
          )}
        </div>

        {/* Bot Status */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4">Performance</h3>
          
          {botStatus ? (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {formatCurrency(botStatus.current_balance)}
                  </p>
                  <p className="text-sm text-gray-400">Current Balance</p>
                </div>
                <div className="text-center">
                  <p className={`text-2xl font-bold ${
                    botStatus.daily_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(botStatus.daily_profit_loss)}
                  </p>
                  <p className="text-sm text-gray-400">Daily P&L</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-xl font-bold text-blue-400">
                    {botStatus.win_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="text-sm text-gray-400">Win Rate</p>
                </div>
                <div className="text-center">
                  <p className="text-xl font-bold text-purple-400">
                    {botStatus.total_trades || 0}
                  </p>
                  <p className="text-sm text-gray-400">Total Trades</p>
                </div>
              </div>

              <div className="text-center">
                <p className="text-lg font-medium text-white">
                  {formatUptime(botStatus.uptime_seconds)}
                </p>
                <p className="text-sm text-gray-400">Uptime</p>
              </div>

              {botStatus.last_trade_time && (
                <div className="text-center">
                  <p className="text-sm text-gray-400">
                    Last Trade: {new Date(botStatus.last_trade_time).toLocaleString()}
                  </p>
                </div>
              )}
            </div>
          ) : selectedBot ? (
            <div className="text-center py-8">
              <p className="text-gray-400">Loading bot status...</p>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">Select a bot to view performance</p>
            </div>
          )}
        </div>
      </div>

      {/* Create Bot Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-lg p-6 w-full max-w-md border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">Create New Bot</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Bot Name
                </label>
                <input
                  type="text"
                  value={createForm.bot_name}
                  onChange={(e) => setCreateForm({...createForm, bot_name: e.target.value})}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  placeholder="Wakhungu28Ai"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Initial Balance ($)
                </label>
                <input
                  type="number"
                  value={createForm.initial_balance}
                  onChange={(e) => setCreateForm({...createForm, initial_balance: parseFloat(e.target.value)})}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  placeholder="1000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Deriv API Token
                </label>
                <input
                  type="password"
                  value={createForm.deriv_api_token}
                  onChange={(e) => setCreateForm({...createForm, deriv_api_token: e.target.value})}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  placeholder="Your Deriv.com API token"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Get your API token from Deriv.com → Settings → API Token
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Minimum Confidence (%)
                </label>
                <input
                  type="number"
                  min="50"
                  max="95"
                  value={createForm.min_confidence}
                  onChange={(e) => setCreateForm({...createForm, min_confidence: parseFloat(e.target.value)})}
                  className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                />
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateForm(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createBot}
                disabled={isLoading || !createForm.deriv_api_token}
                className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white py-2 px-4 rounded-lg font-medium transition-colors"
              >
                {isLoading ? "Creating..." : "Create Bot"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Getting Started Guide */}
      {bots.length === 0 && !showCreateForm && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-blue-400 mb-4">
            🚀 Getting Started with Wakhungu28Ai
          </h3>
          <div className="space-y-3 text-gray-300">
            <p>
              <strong>1. Get your Deriv API Token:</strong> Visit{" "}
              <a 
                href="https://app.deriv.com/account/api-token" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-400 hover:underline"
              >
                Deriv.com → Settings → API Token
              </a>
            </p>
            <p>
              <strong>2. Create a Bot:</strong> Click "Create Bot" and enter your API token
            </p>
            <p>
              <strong>3. Start Trading:</strong> Launch your bot and monitor its performance
            </p>
            <p>
              <strong>4. Target Performance:</strong> Wakhungu28Ai aims for 88%+ win rates
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default BotControlPanel;