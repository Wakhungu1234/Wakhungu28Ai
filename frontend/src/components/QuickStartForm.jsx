import React, { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Zap, Settings, DollarSign, Target, Shield, RotateCcw, AlertTriangle } from 'lucide-react';
import { toast } from './ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const QuickStartForm = ({ onBotCreated }) => {
  const [formData, setFormData] = useState({
    api_token: '',
    stake_amount: 10.0,
    take_profit: 500.0,
    stop_loss: 200.0,
    martingale_multiplier: 2.0,
    max_martingale_steps: 5,
    selected_markets: ['R_100']
  });

  const [isCreating, setIsCreating] = useState(false);

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
          Enhanced Quick Start with comprehensive parameter control for ultra-aggressive trading
        </p>
      </div>

      {/* Ultra-Aggressive Settings Summary */}
      <div className="bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 rounded-xl p-6 mb-8">
        <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center">
          <AlertTriangle className="w-5 h-5 mr-2" />
          Ultra-Aggressive Settings Summary
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="font-semibold text-red-700">🎯 Trade Interval</div>
            <div className="text-red-600">3 seconds</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">📊 Market</div>
            <div className="text-red-600">R_100 (Auto)</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">⚡ Trades/Hour</div>
            <div className="text-red-600">~1,200</div>
          </div>
          <div className="text-center">
            <div className="font-semibold text-red-700">📈 Expected Daily</div>
            <div className="text-red-600">28,800</div>
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
            <input
              id="api_token"
              type="password"
              value={formData.api_token}
              onChange={(e) => handleInputChange('api_token', e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your Deriv API token"
              required
            />
            <p className="text-xs text-gray-500 mt-1">Your API token is encrypted and secure</p>
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
                min="1"
                max="1000"
                step="0.01"
                value={formData.stake_amount}
                onChange={(e) => handleInputChange('stake_amount', parseFloat(e.target.value))}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              />
              <p className="text-xs text-gray-500 mt-1">$10-$50 recommended for testing</p>
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

        {/* Recovery Settings */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
          <h3 className="text-xl font-semibold mb-4 flex items-center text-gray-800">
            <RotateCcw className="w-5 h-5 mr-2 text-purple-600" />
            🔄 Recovery Settings
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
              <p className="text-xs text-gray-500 mt-1">2.0x-3.0x recommended</p>
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
              <p className="text-xs text-gray-500 mt-1">3-5 steps for safety</p>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="text-center pt-6">
          <Button
            type="submit"
            disabled={isCreating || !formData.api_token}
            className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white px-12 py-4 text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            {isCreating ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>🚀 STARTING TRADING...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Zap className="w-6 h-6" />
                <span>🚀 START TRADING NOW</span>
              </div>
            )}
          </Button>
          
          <div className="mt-4 text-sm text-gray-600">
            <p className="font-semibold">⚠️ ULTRA-AGGRESSIVE SETTINGS - Monitor closely!</p>
            <p>Expected completion: Within 10 seconds</p>
          </div>
        </div>
      </form>
    </div>
  );
};

export default QuickStartForm;