import React, { useState, useEffect } from "react";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const TradingDashboard = () => {
  const [markets, setMarkets] = useState([]);
  const [selectedMarket, setSelectedMarket] = useState("R_100");
  const [analysis, setAnalysis] = useState(null);
  const [recentTicks, setRecentTicks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchMarkets();
    if (selectedMarket) {
      fetchAnalysis();
      fetchRecentTicks();
    }
  }, [selectedMarket]);

  const fetchMarkets = async () => {
    try {
      const response = await axios.get(`${API}/markets`);
      setMarkets(response.data);
    } catch (error) {
      console.error("Error fetching markets:", error);
    }
  };

  const fetchAnalysis = async () => {
    if (!selectedMarket) return;
    
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/analysis`, {
        symbol: selectedMarket,
        contract_type: "over_under",
        tick_count: 100
      });
      setAnalysis(response.data.analysis);
    } catch (error) {
      console.error("Error fetching analysis:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRecentTicks = async () => {
    if (!selectedMarket) return;
    
    try {
      const response = await axios.get(`${API}/ticks/${selectedMarket}?limit=20`);
      setRecentTicks(response.data.ticks || []);
    } catch (error) {
      console.error("Error fetching ticks:", error);
    }
  };

  const formatPercentage = (value) => {
    return `${value?.toFixed(1) || 0}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-white mb-2">
          📊 Deriv Trading Analysis Dashboard
        </h2>
        <p className="text-gray-300">
          Real-time market analysis with AI-powered predictions
        </p>
      </div>

      {/* Market Selector */}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
        <h3 className="text-xl font-semibold text-white mb-4">Select Market</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {markets.map((market) => (
            <button
              key={market.id}
              onClick={() => setSelectedMarket(market.symbol)}
              className={`
                p-3 rounded-lg text-sm font-medium transition-all duration-200
                ${selectedMarket === market.symbol
                  ? 'bg-blue-500 text-white shadow-lg'
                  : 'bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white'
                }
              `}
            >
              {market.symbol}
            </button>
          ))}
        </div>
      </div>

      {/* Analysis Results */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Digit Frequency Chart */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">
              🎯 Last Digit Frequency
            </h3>
            <div className="space-y-3">
              {analysis.digit_frequency?.map((digit) => (
                <div key={digit.digit} className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-blue-500 rounded flex items-center justify-center text-white font-bold">
                    {digit.digit}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-300">
                        Count: {digit.count}
                      </span>
                      <span className={`font-medium ${
                        digit.is_hot ? 'text-red-400' : 
                        digit.is_cold ? 'text-blue-400' : 'text-gray-300'
                      }`}>
                        {formatPercentage(digit.percentage)}
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          digit.is_hot ? 'bg-red-500' :
                          digit.is_cold ? 'bg-blue-500' : 'bg-gray-500'
                        }`}
                        style={{ width: `${Math.min(digit.percentage, 20) * 5}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Trading Recommendations */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
            <h3 className="text-xl font-semibold text-white mb-4">
              🚀 Trading Recommendations
            </h3>
            
            <div className="space-y-4">
              {/* Even/Odd Recommendation */}
              {analysis.predictions?.even_odd_recommendation && (
                <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-green-400 font-semibold">Even/Odd</h4>
                    <span className="text-white font-bold">
                      {formatPercentage(analysis.predictions.even_odd_recommendation.confidence)}
                    </span>
                  </div>
                  <p className="text-white font-medium mb-1">
                    Trade: {analysis.predictions.even_odd_recommendation.trade_type}
                  </p>
                  <p className="text-sm text-gray-300">
                    {analysis.predictions.even_odd_recommendation.reason}
                  </p>
                </div>
              )}

              {/* Over/Under Recommendation */}
              {analysis.predictions?.over_under_recommendation && (
                <div className="bg-purple-500/20 border border-purple-500/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-purple-400 font-semibold">Over/Under 5</h4>
                    <span className="text-white font-bold">
                      {formatPercentage(analysis.predictions.over_under_recommendation.confidence)}
                    </span>
                  </div>
                  <p className="text-white font-medium mb-1">
                    Trade: {analysis.predictions.over_under_recommendation.trade_type}
                  </p>
                  <p className="text-sm text-gray-300">
                    {analysis.predictions.over_under_recommendation.reason}
                  </p>
                </div>
              )}

              {/* Match/Differ Recommendation */}
              {analysis.predictions?.match_differ_recommendation && (
                <div className="bg-orange-500/20 border border-orange-500/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-orange-400 font-semibold">Match/Differ</h4>
                    <span className="text-white font-bold">
                      {formatPercentage(analysis.predictions.match_differ_recommendation.match_confidence)}
                    </span>
                  </div>
                  <p className="text-white font-medium mb-1">
                    Trade: MATCH {analysis.predictions.match_differ_recommendation.match_digit}
                  </p>
                  <p className="text-sm text-gray-300">
                    {analysis.predictions.match_differ_recommendation.match_reason}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Ticks */}
      <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
        <h3 className="text-xl font-semibold text-white mb-4">
          📈 Recent Ticks - {selectedMarket}
        </h3>
        
        {recentTicks.length > 0 ? (
          <div className="grid grid-cols-4 md:grid-cols-10 gap-2">
            {recentTicks.slice(-20).map((tick, index) => (
              <div
                key={index}
                className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-2 text-center"
              >
                <div className="text-white font-bold text-lg">
                  {tick.last_digit}
                </div>
                <div className="text-xs text-gray-400">
                  {new Date(tick.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-gray-400 py-8">
            <p>No recent tick data available</p>
            <p className="text-sm">Waiting for live market data...</p>
          </div>
        )}
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={() => {
            fetchAnalysis();
            fetchRecentTicks();
          }}
          disabled={isLoading}
          className="bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white font-semibold px-6 py-3 rounded-lg transition-colors duration-200"
        >
          {isLoading ? "🔄 Analyzing..." : "🔄 Refresh Analysis"}
        </button>
      </div>
    </div>
  );
};

export default TradingDashboard;