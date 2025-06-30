import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdvancedBotControl = () => {
  const [bots, setBots] = useState([]);
  const [configOptions, setConfigOptions] = useState(null);
  const [selectedBot, setSelectedBot] = useState(null);
  const [botStatus, setBotStatus] = useState(null);
  const [martingaleInfo, setMartingaleInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvancedForm, setShowAdvancedForm] = useState(false);
  
  const [advancedForm, setAdvancedForm] = useState({
    bot_name: "Wakhungu28Ai-Pro",
    initial_balance: 1000,
    deriv_api_token: "",
    selected_market: "R_100",
    
    // Trading Configuration
    contract_type: "AUTO_BEST",
    trade_type: "AUTO",
    prediction_number: null,
    stake: 10.0,
    stop_loss: null,
    take_profit: null,
    ticks_count: 5,
    
    // Advanced Settings
    min_confidence: 60.0,
    max_trades_per_hour: 500,
    trade_interval_seconds: 0.3,
    
    // Martingale Settings
    martingale_enabled: true,
    martingale_multiplier: 2.0,
    max_martingale_steps: 5
  });

  useEffect(() => {
    fetchBots();
    fetchConfigOptions();
  }, []);

  useEffect(() => {
    if (selectedBot) {
      fetchBotStatus();
      fetchMartingaleInfo();
      
      // Set up periodic status updates
      const interval = setInterval(() => {
        fetchBotStatus();
        fetchMartingaleInfo();
      }, 3000); // Every 3 seconds for high-frequency monitoring
      
      return () => clearInterval(interval);
    }
  }, [selectedBot]);

  const fetchBots = async () => {
    try {
      const response = await axios.get(`${API}/bots`);
      setBots(response.data.bots || []);
      
      if (!selectedBot && response.data.bots?.length > 0) {
        setSelectedBot(response.data.bots[0]);
      }
    } catch (error) {
      console.error("Error fetching bots:", error);
    }
  };

  const fetchConfigOptions = async () => {
    try {
      const response = await axios.get(`${API}/bot/configuration-options`);
      setConfigOptions(response.data.options);
    } catch (error) {
      console.error("Error fetching config options:", error);
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

  const fetchMartingaleInfo = async () => {
    if (!selectedBot) return;
    
    try {
      const response = await axios.get(`${API}/bot/${selectedBot.id}/martingale-info`);
      setMartingaleInfo(response.data.martingale_info);
    } catch (error) {
      console.error("Error fetching Martingale info:", error);
    }
  };

  const createAdvancedBot = async () => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/bot/create-advanced`, advancedForm);
      
      if (response.data.status === "success") {
        await fetchBots();
        setShowAdvancedForm(false);
        
        // Reset form
        setAdvancedForm({
          ...advancedForm,
          deriv_api_token: "",
          bot_name: "Wakhungu28Ai-Pro"
        });
        
        // Select the newly created bot
        const newBot = bots.find(bot => bot.id === response.data.bot_id);
        if (newBot) setSelectedBot(newBot);
        
        alert(`🚀 High-Frequency Bot Created!\nMax Trades/Day: ${response.data.features.max_trades_per_day}\nMartingale: ${response.data.features.martingale_recovery ? 'Enabled' : 'Disabled'}`);
      }
    } catch (error) {
      console.error("Error creating advanced bot:", error);
      alert("Failed to create bot. Please check your configuration and API token.");
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
    
    if (!window.confirm(`Delete "${selectedBot.bot_name}"? This cannot be undone.`)) {
      return;
    }
    
    setIsLoading(true);
    try {
      await axios.delete(`${API}/bot/${selectedBot.id}`);
      setSelectedBot(null);
      setBotStatus(null);
      setMartingaleInfo(null);
      await fetchBots();
    } catch (error) {
      console.error("Error deleting bot:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormChange = (field, value) => {
    setAdvancedForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getTradeTypeOptions = (contractType) => {
    if (!configOptions?.trade_types) return [];
    return configOptions.trade_types[contractType] || [];
  };

  const getPredictionNumbers = (tradeType) => {
    if (!configOptions?.prediction_numbers) return [];
    return configOptions.prediction_numbers[tradeType] || [];
  };

  const formatCurrency = (amount) => `$${amount?.toFixed(2) || '0.00'}`;
  
  const formatUptime = (seconds) => {
    if (!seconds) return "0s";
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hours > 0) return `${hours}h ${minutes}m`;
    if (minutes > 0) return `${minutes}m ${secs}s`;
    return `${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          ⚡ High-Frequency Wakhungu28Ai Control
        </h2>
        <p className="text-gray-300">
          Advanced AI trading with 10,000+ trades per day capability
        </p>
      </div>

      {/* Main Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Bot List */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">High-Frequency Bots</h3>
            <button
              onClick={() => setShowAdvancedForm(true)}
              className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all"
            >
              ⚡ Create Pro Bot
            </button>
          </div>

          {bots.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-400 mb-4">No high-frequency bots yet</p>
              <button
                onClick={() => setShowAdvancedForm(true)}
                className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium"
              >
                Create Your First Pro Bot
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
                        bot.is_active ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                      }`}></div>
                      <span className="text-xs text-gray-400">
                        {bot.is_active ? 'Trading' : 'Stopped'}
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
          <h3 className="text-xl font-semibold text-white mb-4">⚡ Bot Controls</h3>
          
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
                    selectedBot.is_active ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                  }`}></div>
                  <span>{selectedBot.is_active ? 'High-Frequency Trading' : 'Stopped'}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-3">
                {!selectedBot.is_active ? (
                  <button
                    onClick={startBot}
                    disabled={isLoading}
                    className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 disabled:opacity-50 text-white py-3 px-4 rounded-lg font-medium transition-all"
                  >
                    {isLoading ? "Starting..." : "🚀 Start High-Frequency Trading"}
                  </button>
                ) : (
                  <button
                    onClick={stopBot}
                    disabled={isLoading}
                    className="bg-red-500 hover:bg-red-600 disabled:opacity-50 text-white py-3 px-4 rounded-lg font-medium transition-colors"
                  >
                    {isLoading ? "Stopping..." : "🛑 Stop Trading"}
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

              {/* Martingale Recovery Info */}
              {martingaleInfo && martingaleInfo.is_recovering && (
                <div className="bg-orange-500/20 border border-orange-500/30 rounded-lg p-3">
                  <h5 className="text-orange-400 font-semibold mb-2">🔄 Recovery Mode</h5>
                  <p className="text-sm text-gray-300">
                    Level: {martingaleInfo.current_level}/{martingaleInfo.max_level}
                  </p>
                  <p className="text-sm text-gray-300">
                    Amount to Recover: {formatCurrency(martingaleInfo.total_amount_to_recover)}
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">Select a bot to control</p>
            </div>
          )}
        </div>

        {/* Performance Dashboard */}
        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
          <h3 className="text-xl font-semibold text-white mb-4">📊 Performance</h3>
          
          {botStatus ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {formatCurrency(botStatus.current_balance)}
                  </p>
                  <p className="text-sm text-gray-400">Current Balance</p>
                </div>
                
                <div className="text-center">
                  <p className={`text-xl font-bold ${
                    botStatus.daily_profit_loss >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {formatCurrency(botStatus.daily_profit_loss)}
                  </p>
                  <p className="text-sm text-gray-400">Daily P&L</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-400">
                    {botStatus.win_rate?.toFixed(1) || 0}%
                  </p>
                  <p className="text-xs text-gray-400">Win Rate</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-purple-400">
                    {botStatus.total_trades || 0}
                  </p>
                  <p className="text-xs text-gray-400">Trades</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-lg font-bold text-yellow-400">
                    {botStatus.trades_per_hour?.toFixed(0) || 0}
                  </p>
                  <p className="text-xs text-gray-400">Trades/Hour</p>
                </div>
                <div className="text-center">
                  <p className="text-lg font-bold text-cyan-400">
                    {botStatus.current_streak || 0}
                  </p>
                  <p className="text-xs text-gray-400">Streak</p>
                </div>
              </div>

              <div className="text-center">
                <p className="text-sm text-white">
                  Uptime: {formatUptime(botStatus.uptime_seconds)}
                </p>
                {botStatus.martingale_level > 0 && (
                  <p className="text-sm text-orange-400">
                    Recovery Level: {botStatus.martingale_level}
                  </p>
                )}
              </div>

              {botStatus.last_trade_time && (
                <div className="text-center">
                  <p className="text-xs text-gray-400">
                    Last Trade: {new Date(botStatus.last_trade_time).toLocaleTimeString()}
                  </p>
                </div>
              )}
            </div>
          ) : selectedBot ? (
            <div className="text-center py-8">
              <div className="animate-pulse text-gray-400">Loading performance...</div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-400">Select a bot to view performance</p>
            </div>
          )}
        </div>
      </div>

      {/* Advanced Bot Creation Form */}
      {showAdvancedForm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-gray-900 rounded-lg p-6 w-full max-w-4xl border border-white/20 max-h-screen overflow-y-auto">
            <h3 className="text-2xl font-semibold text-white mb-6">⚡ Create High-Frequency Trading Bot</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Basic Configuration */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-blue-400">Basic Configuration</h4>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Bot Name</label>
                  <input
                    type="text"
                    value={advancedForm.bot_name}
                    onChange={(e) => handleFormChange('bot_name', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Initial Balance ($)</label>
                  <input
                    type="number"
                    value={advancedForm.initial_balance}
                    onChange={(e) => handleFormChange('initial_balance', parseFloat(e.target.value))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Deriv API Token</label>
                  <input
                    type="password"
                    value={advancedForm.deriv_api_token}
                    onChange={(e) => handleFormChange('deriv_api_token', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                    placeholder="Required for trading"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Market</label>
                  <select
                    value={advancedForm.selected_market}
                    onChange={(e) => handleFormChange('selected_market', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  >
                    {configOptions?.markets?.map(market => (
                      <option key={market.value} value={market.value} className="bg-gray-800">
                        {market.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Trading Configuration */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-green-400">Trading Strategy</h4>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Contract Type</label>
                  <select
                    value={advancedForm.contract_type}
                    onChange={(e) => handleFormChange('contract_type', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  >
                    {configOptions?.contract_types?.map(type => (
                      <option key={type.value} value={type.value} className="bg-gray-800">
                        {type.label} - {type.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Trade Type</label>
                  <select
                    value={advancedForm.trade_type}
                    onChange={(e) => handleFormChange('trade_type', e.target.value)}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  >
                    {getTradeTypeOptions(advancedForm.contract_type).map(type => (
                      <option key={type.value} value={type.value} className="bg-gray-800">
                        {type.label} - {type.description}
                      </option>
                    ))}
                  </select>
                </div>

                {(advancedForm.trade_type === "OVER" || advancedForm.trade_type === "UNDER" || 
                  advancedForm.trade_type === "MATCH" || advancedForm.trade_type === "DIFFER") && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Prediction Number</label>
                    <select
                      value={advancedForm.prediction_number || ""}
                      onChange={(e) => handleFormChange('prediction_number', e.target.value ? parseInt(e.target.value) : null)}
                      className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                    >
                      <option value="" className="bg-gray-800">Select number...</option>
                      {getPredictionNumbers(advancedForm.trade_type).map(num => (
                        <option key={num} value={num} className="bg-gray-800">{num}</option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Stake ($)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={advancedForm.stake}
                      onChange={(e) => handleFormChange('stake', parseFloat(e.target.value))}
                      className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Ticks</label>
                    <select
                      value={advancedForm.ticks_count}
                      onChange={(e) => handleFormChange('ticks_count', parseInt(e.target.value))}
                      className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                    >
                      {configOptions?.ticks_options?.map(tick => (
                        <option key={tick} value={tick} className="bg-gray-800">{tick}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* High-Frequency Settings */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-purple-400">High-Frequency Settings</h4>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Max Trades/Hour (up to 1000)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={advancedForm.max_trades_per_hour}
                    onChange={(e) => handleFormChange('max_trades_per_hour', parseInt(e.target.value))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                  <p className="text-xs text-gray-400 mt-1">
                    Daily potential: {(advancedForm.max_trades_per_hour * 24).toLocaleString()} trades
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Trade Interval (seconds)
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="60"
                    value={advancedForm.trade_interval_seconds}
                    onChange={(e) => handleFormChange('trade_interval_seconds', parseFloat(e.target.value))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Min Confidence (%)
                  </label>
                  <input
                    type="number"
                    min="50"
                    max="95"
                    value={advancedForm.min_confidence}
                    onChange={(e) => handleFormChange('min_confidence', parseFloat(e.target.value))}
                    className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                  />
                </div>
              </div>

              {/* Martingale Settings */}
              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-orange-400">Martingale Recovery</h4>
                
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="martingale_enabled"
                    checked={advancedForm.martingale_enabled}
                    onChange={(e) => handleFormChange('martingale_enabled', e.target.checked)}
                    className="w-4 h-4 text-blue-600 bg-white/10 border-white/20 rounded"
                  />
                  <label htmlFor="martingale_enabled" className="text-sm font-medium text-gray-300">
                    Enable Martingale Recovery
                  </label>
                </div>

                {advancedForm.martingale_enabled && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Multiplier (1.1 - 5.0)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        min="1.1"
                        max="5.0"
                        value={advancedForm.martingale_multiplier}
                        onChange={(e) => handleFormChange('martingale_multiplier', parseFloat(e.target.value))}
                        className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Max Steps (1-10)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="10"
                        value={advancedForm.max_martingale_steps}
                        onChange={(e) => handleFormChange('max_martingale_steps', parseInt(e.target.value))}
                        className="w-full bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white"
                      />
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3 mt-8">
              <button
                onClick={() => setShowAdvancedForm(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-lg font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={createAdvancedBot}
                disabled={isLoading || !advancedForm.deriv_api_token.trim()}
                className="flex-1 bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white py-3 px-4 rounded-lg font-medium transition-all"
              >
                {isLoading ? "Creating..." : "🚀 Create High-Frequency Bot"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Info Cards */}
      {bots.length === 0 && !showAdvancedForm && (
        <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/30 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-blue-400 mb-4">
            ⚡ High-Frequency Trading Features
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
            <div>
              <h4 className="font-semibold text-white">🚀 Ultra-Fast Execution</h4>
              <p className="text-sm">Execute up to 10,000+ trades per day with 300ms intervals</p>
            </div>
            <div>
              <h4 className="font-semibold text-white">🎯 Smart Contract Selection</h4>
              <p className="text-sm">AI selects optimal contract types based on market conditions</p>
            </div>
            <div>
              <h4 className="font-semibold text-white">🔄 Martingale Recovery</h4>
              <p className="text-sm">Advanced recovery system to recover from losing streaks</p>
            </div>
            <div>
              <h4 className="font-semibold text-white">📊 Real-time Monitoring</h4>
              <p className="text-sm">Live performance tracking with detailed analytics</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedBotControl;