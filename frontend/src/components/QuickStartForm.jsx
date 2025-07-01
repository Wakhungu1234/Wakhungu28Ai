import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Zap, Settings, DollarSign, Target, Shield, RotateCcw, AlertTriangle, TrendingUp, ExternalLink } from 'lucide-react';
import { toast } from './ui/toaster';
import DerivAccountLinker from './DerivAccountLinker';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const QuickStartForm = ({ onBotCreated }) => {
  const [showAccountLinker, setShowAccountLinker] = useState(false);
  const [linkedAccount, setLinkedAccount] = useState(null);
  const [formData, setFormData] = useState({
    api_token: '',
    stake_amount: 2.0,  // Reduced default to $2 to showcase lower minimum
    take_profit: 500.0,
    stop_loss: 200.0,
    martingale_multiplier: 2.0,
    max_martingale_steps: 5,
    martingale_repeat_attempts: 2,  // New: repeat attempts for recovery
    selected_markets: ['R_100']
  });

  const [isCreating, setIsCreating] = useState(false);
  const [availableMarkets, setAvailableMarkets] = useState([]);

  // Fetch available markets on component mount
  useEffect(() => {
    fetchMarkets();
  }, []);

  const fetchMarkets = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/markets`);
      const markets = await response.json();
      setAvailableMarkets(markets);
    } catch (error) {
      console.error('Error fetching markets:', error);
    }
  };

  const handleAccountLinked = (accountData) => {
    setLinkedAccount(accountData);
    setFormData(prev => ({
      ...prev,
      api_token: accountData.api_token
    }));
    setShowAccountLinker(false);
    toast.success('🔗 Deriv account linked successfully!', {
      description: 'You can now create bots with ULTRA-FAST trading',
    });
  };

  const handleSkipLinking = () => {
    setShowAccountLinker(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/bots/quickstart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        toast.success(`🚀 ${result.message}`, {
          description: `Bot: ${result.bot_name} created successfully!`,
          duration: 5000,
        });
        onBotCreated && onBotCreated(result);
      } else {
        toast.error('Failed to create bot', {
          description: result.detail || 'Unknown error occurred',
        });
      }
    } catch (error) {
      toast.error('Connection Error', {
        description: 'Failed to connect to trading server',
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleMarketToggle = (marketSymbol) => {
    setFormData(prev => ({
      ...prev,
      selected_markets: prev.selected_markets.includes(marketSymbol)
        ? prev.selected_markets.filter(m => m !== marketSymbol)
        : [...prev.selected_markets, marketSymbol]
    }));
  };

  // Show account linker if not linked and no API token
  if (showAccountLinker) {
    return (
      <DerivAccountLinker
        onAccountLinked={handleAccountLinked}
        onSkip={handleSkipLinking}
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="p-3 bg-gradient-to-r from-red-500 to-orange-500 rounded-full">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
            🚀 QUICK START - Trade NOW!
          </h2>
        </div>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Enhanced Quick Start with ULTRA-FAST trading and comprehensive parameter control
        </p>
      </div>

      {/* Account Status */}
      {linkedAccount ? (
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-600 rounded-full">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-green-800">✅ Deriv Account Linked</h3>
                <p className="text-sm text-green-600">Ready for real money ULTRA-FAST trading</p>
              </div>
            </div>
            <Button
              onClick={() => setShowAccountLinker(true)}
              variant="outline"
              size="sm"
              className="text-green-700 border-green-300 hover:bg-green-100"
            >
              Change Account
            </Button>
          </div>
        </div>
      ) : (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-full">
                <ExternalLink className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-blue-800">🔗 Link Your Deriv Account</h3>
                <p className="text-sm text-blue-600">Get guided setup for secure account authorization</p>
              </div>
            </div>
            <Button
              onClick={() => setShowAccountLinker(true)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Link Account
            </Button>
          </div>
        </div>
      )}

      {/* Ultra-Aggressive Settings Summary */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 rounded-xl p-6 mb-8">
        <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          🚀 ULTRA-FAST Trading Settings
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-red-700">⚡ Trade Interval</div>
            <div className="text-red-600 font-bold">0.5 seconds</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">📊 Markets</div>
            <div className="text-red-600">Multi-Select</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">⚡ Trades/Hour</div>
            <div className="text-red-600 font-bold">~7,200</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">📈 Expected Daily</div>
            <div className="text-red-600 font-bold">172,800</div>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <form onSubmit={handleSubmit} className="space-y-8">
        
        {/* Trading Credentials */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
            <Settings className="w-5 h-5 mr-2 text-blue-600" />
            🔑 Trading Credentials
          </h3>
          <div>
            <Label htmlFor="api_token" className="text-sm font-medium text-gray-700">
              Deriv API Token *
            </Label>
            <div className="relative">
              <input
                id="api_token"
                type="password"
                value={formData.api_token}
                onChange={(e) => handleInputChange('api_token', e.target.value)}
                className="mt-1 block w-full px-3 py-2 pr-20 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter your Deriv API token or link your account above"
                required
              />
              {!formData.api_token && (
                <Button
                  type="button"
                  onClick={() => setShowAccountLinker(true)}
                  className="absolute right-1 top-1 h-8 px-3 text-xs bg-blue-600 hover:bg-blue-700"
                >
                  Link Account
                </Button>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              {linkedAccount ? 
                '✅ Using linked Deriv account - secure and authorized' : 
                'Click "Link Account" above for guided setup, or enter your API token manually'
              }
            </p>
          </div>
        </div>

        {/* Rest of the form remains the same... */}
        {/* Market Selection */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            📊 Market Selection
          </h3>
          <div>
            <Label className="text-sm font-medium text-gray-700 mb-3 block">
              Select Markets to Trade (Choose multiple for diversification)
            </Label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {availableMarkets.map((market) => (
                <div key={market.symbol} className="relative">
                  <input
                    type="checkbox"
                    id={market.symbol}
                    checked={formData.selected_markets.includes(market.symbol)}
                    onChange={() => handleMarketToggle(market.symbol)}
                    className="sr-only"
                  />
                  <label
                    htmlFor={market.symbol}
                    className={`cursor-pointer block p-3 rounded-lg border-2 transition-all ${
                      formData.selected_markets.includes(market.symbol)
                        ? 'border-green-500 bg-green-50 text-green-800'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <div className="text-center">
                      <div className="font-semibold">{market.symbol}</div>
                      <div className="text-xs opacity-75">Vol {market.symbol.includes('HZ') ? '1s' : 'Index'}</div>
                    </div>
                  </label>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Selected: {formData.selected_markets.length} market(s) | 
              Recommended: 3-5 markets for optimal diversification
            </p>
          </div>
        </div>

        {/* Risk Management */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
            <DollarSign className="w-5 h-5 mr-2 text-green-600" />
            💰 Risk Management
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="stake_amount" className="text-sm font-medium text-gray-700">
                Stake Amount ($)
              </Label>
              <input
                id="stake_amount"
                type="number"
                min="0.35"
                max="1000"
                step="0.01"
                value={formData.stake_amount}
                onChange={(e) => handleInputChange('stake_amount', parseFloat(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <p className="text-xs text-gray-500 mt-1">$0.35-$25 recommended for ULTRA-FAST trading</p>
            </div>
            <div>
              <Label htmlFor="take_profit" className="text-sm font-medium text-gray-700">
                Take Profit ($)
              </Label>
              <input
                id="take_profit"
                type="number"
                min="10"
                max="10000"
                step="0.01"
                value={formData.take_profit}
                onChange={(e) => handleInputChange('take_profit', parseFloat(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <p className="text-xs text-gray-500 mt-1">Set your profit target (e.g., $500)</p>
            </div>
            <div>
              <Label htmlFor="stop_loss" className="text-sm font-medium text-gray-700">
                Stop Loss ($)
              </Label>
              <input
                id="stop_loss"
                type="number"
                min="10"
                max="5000"
                step="0.01"
                value={formData.stop_loss}
                onChange={(e) => handleInputChange('stop_loss', parseFloat(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
              />
              <p className="text-xs text-gray-500 mt-1">Set your maximum loss (e.g., $200)</p>
            </div>
          </div>
        </div>

        {/* Enhanced Recovery Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
            <RotateCcw className="w-5 h-5 mr-2 text-purple-600" />
            🔄 Enhanced Recovery Settings
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <Label htmlFor="martingale_multiplier" className="text-sm font-medium text-gray-700">
                Martingale Multiplier
              </Label>
              <input
                id="martingale_multiplier"
                type="number"
                min="1.1"
                max="5.0"
                step="0.1"
                value={formData.martingale_multiplier}
                onChange={(e) => handleInputChange('martingale_multiplier', parseFloat(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
              <p className="text-xs text-gray-500 mt-1">1.5x-2.5x recommended for ULTRA-FAST</p>
            </div>
            <div>
              <Label htmlFor="max_martingale_steps" className="text-sm font-medium text-gray-700">
                Max Martingale Steps
              </Label>
              <input
                id="max_martingale_steps"
                type="number"
                min="1"
                max="10"
                value={formData.max_martingale_steps}
                onChange={(e) => handleInputChange('max_martingale_steps', parseInt(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
              />
              <p className="text-xs text-gray-500 mt-1">2-4 steps for ULTRA-FAST safety</p>
            </div>
            <div>
              <Label htmlFor="martingale_repeat_attempts" className="text-sm font-medium text-gray-700">
                Repeat Attempts per Step
              </Label>
              <input
                id="martingale_repeat_attempts"
                type="number"
                min="1"
                max="5"
                value={formData.martingale_repeat_attempts}
                onChange={(e) => handleInputChange('martingale_repeat_attempts', parseInt(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
              <p className="text-xs text-gray-500 mt-1">Repeat same stake for 100% recovery</p>
            </div>
          </div>
          
          {/* Recovery Example */}
          <div className="mt-4 p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg border border-orange-200">
            <h4 className="font-semibold text-orange-800 mb-2">💡 Enhanced Recovery Example:</h4>
            <div className="text-sm text-orange-700 space-y-1">
              <p>• First trade: ${formData.stake_amount} (Loss)</p>
              <p>• Martingale step 1: ${(formData.stake_amount * formData.martingale_multiplier).toFixed(2)} × {formData.martingale_repeat_attempts} attempts</p>
              <p>• If still losing, step 2: ${(formData.stake_amount * Math.pow(formData.martingale_multiplier, 2)).toFixed(2)} × {formData.martingale_repeat_attempts} attempts</p>
              <p className="font-semibold">🎯 Goal: 100% recovery of all losses with repeated stakes!</p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center pt-6">
          <Button
            type="submit"
            disabled={isCreating || !formData.api_token || formData.selected_markets.length === 0}
            className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white px-12 py-4 text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            {isCreating ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>🚀 STARTING ULTRA-FAST TRADING...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Zap className="w-6 h-6" />
                <span>🚀 START ULTRA-FAST TRADING NOW</span>
              </div>
            )}
          </Button>
          
          <div className="mt-4 text-sm text-gray-600">
            <p className="font-semibold">⚡ ULTRA-FAST 0.5-SECOND TRADING - Maximum Speed!</p>
            <p>Expected completion: Within 5 seconds</p>
          </div>
        </div>
      </form>
    </div>
  );
};

export default QuickStartForm;