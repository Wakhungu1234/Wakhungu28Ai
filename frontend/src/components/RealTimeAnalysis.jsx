import React, { useState, useEffect } from 'react';
import { Badge } from './ui/badge';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Zap,
  BarChart3,
  AlertCircle,
  CheckCircle,
  Clock
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RealTimeAnalysis = () => {
  const [tickData, setTickData] = useState({});
  const [analysis, setAnalysis] = useState({});
  const [recommendations, setRecommendations] = useState({});
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket for real-time updates
    const ws = new WebSocket(BACKEND_URL.replace('https://', 'wss://').replace('http://', 'ws://') + '/api/ws');
    
    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to real-time analysis feed');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'tick_update') {
        setTickData(prev => ({
          ...prev,
          [data.data.symbol]: data.data
        }));
        
        // Trigger analysis update for this symbol
        fetchAnalysis(data.data.symbol);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from real-time analysis feed');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };

    // Fetch initial analysis for all markets
    fetchAllAnalysis();

    return () => {
      ws.close();
    };
  }, []);

  const fetchAnalysis = async (symbol) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/analysis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol,
          contract_type: 'even_odd',
          tick_count: 100
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAnalysis(prev => ({
          ...prev,
          [symbol]: data.analysis
        }));
        
        // Generate recommendations
        generateRecommendations(symbol, data.analysis);
      }
    } catch (error) {
      console.error('Error fetching analysis:', error);
    }
  };

  const fetchAllAnalysis = async () => {
    const symbols = ['R_10', 'R_25', 'R_50', 'R_75', 'R_100', '1HZ10V', '1HZ25V', '1HZ50V', '1HZ75V', '1HZ100V'];
    symbols.forEach(symbol => fetchAnalysis(symbol));
  };

  const generateRecommendations = (symbol, analysisData) => {
    const predictions = analysisData.predictions;
    const recs = [];

    // Even/Odd recommendation
    if (predictions?.even_odd_recommendation?.confidence >= 60) {
      recs.push({
        type: 'EVEN_ODD',
        action: predictions.even_odd_recommendation.trade_type,
        confidence: predictions.even_odd_recommendation.confidence,
        reason: predictions.even_odd_recommendation.reason
      });
    }

    // Over/Under recommendation
    if (predictions?.over_under_recommendation?.confidence >= 60) {
      recs.push({
        type: 'OVER_UNDER',
        action: predictions.over_under_recommendation.trade_type,
        confidence: predictions.over_under_recommendation.confidence,
        reason: predictions.over_under_recommendation.reason
      });
    }

    setRecommendations(prev => ({
      ...prev,
      [symbol]: recs
    }));
  };

  const getDigitColor = (digit) => {
    return digit % 2 === 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
            <BarChart3 className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">📊 Real-Time Analysis</h2>
        </div>
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <Badge className="bg-green-100 text-green-800 border-green-300">
              <CheckCircle className="w-3 h-3 mr-1" />
              Live Feed
            </Badge>
          ) : (
            <Badge className="bg-red-100 text-red-800 border-red-300">
              <AlertCircle className="w-3 h-3 mr-1" />
              Disconnected
            </Badge>
          )}
        </div>
      </div>

      {/* Market Analysis Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {Object.entries(tickData).slice(0, 6).map(([symbol, tick]) => (
          <div key={symbol} className="bg-gray-50 rounded-lg p-4 border">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-800">{symbol}</h3>
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3 text-gray-500" />
                <span className="text-xs text-gray-500">Live</span>
              </div>
            </div>
            
            {/* Current Price and Last Digit */}
            <div className="mb-3">
              <div className="text-sm text-gray-600">Current Price</div>
              <div className="flex items-center space-x-2">
                <span className="text-lg font-bold">{tick?.price}</span>
                <div className={`px-2 py-1 rounded-full text-sm font-bold ${getDigitColor(tick?.last_digit)}`}>
                  {tick?.last_digit}
                </div>
              </div>
            </div>

            {/* Analysis Data */}
            {analysis[symbol] && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>Even/Odd</span>
                  <span className={getConfidenceColor(analysis[symbol].predictions?.even_odd_recommendation?.confidence || 0)}>
                    {analysis[symbol].predictions?.even_odd_recommendation?.confidence?.toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between text-xs">
                  <span>Over/Under</span>
                  <span className={getConfidenceColor(analysis[symbol].predictions?.over_under_recommendation?.confidence || 0)}>
                    {analysis[symbol].predictions?.over_under_recommendation?.confidence?.toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Trading Recommendations */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2 text-green-600" />
          🎯 Live Trading Recommendations
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(recommendations).slice(0, 4).map(([symbol, recs]) => (
            <div key={symbol} className="bg-gradient-to-r from-blue-50 to-green-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-gray-800">{symbol}</h4>
                <Badge className="bg-blue-100 text-blue-800">
                  {recs.length} Signal{recs.length !== 1 ? 's' : ''}
                </Badge>
              </div>
              
              {recs.length > 0 ? (
                <div className="space-y-2">
                  {recs.map((rec, index) => (
                    <div key={index} className="bg-white rounded p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="font-medium text-sm">{rec.type}</span>
                        <span className={`text-sm font-bold ${getConfidenceColor(rec.confidence)}`}>
                          {rec.confidence.toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {rec.confidence >= 70 ? (
                          <TrendingUp className="w-4 h-4 text-green-600" />
                        ) : (
                          <TrendingDown className="w-4 h-4 text-yellow-600" />
                        )}
                        <span className="text-sm font-semibold text-gray-700">{rec.action}</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-1">{rec.reason}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-3">
                  <div className="text-gray-500 text-sm">No strong signals</div>
                  <div className="text-xs text-gray-400">Waiting for better opportunities...</div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Last Digits Color Legend */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-semibold text-gray-700 mb-2">Color Legend</h4>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-100 rounded border border-green-300"></div>
            <span>Even Numbers (0,2,4,6,8)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-100 rounded border border-red-300"></div>
            <span>Odd Numbers (1,3,5,7,9)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RealTimeAnalysis;