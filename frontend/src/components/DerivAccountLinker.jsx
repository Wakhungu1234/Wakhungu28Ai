import React, { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { 
  ExternalLink, 
  Shield, 
  Key, 
  CheckCircle, 
  AlertCircle, 
  ArrowRight, 
  Lock,
  Globe,
  Zap,
  DollarSign
} from 'lucide-react';
import { toast } from './ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const DerivAccountLinker = ({ onAccountLinked, onSkip }) => {
  const [step, setStep] = useState(1);
  const [apiToken, setApiToken] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [accountInfo, setAccountInfo] = useState(null);

  const handleVerifyToken = async () => {
    if (!apiToken || apiToken.length < 10) {
      toast.error('Please enter a valid API token');
      return;
    }

    setIsVerifying(true);
    try {
      // Test the API token by trying to get account info
      const response = await fetch(`${BACKEND_URL}/api/verify-deriv-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ api_token: apiToken })
      });

      if (response.ok) {
        const data = await response.json();
        setAccountInfo(data.account_info);
        setStep(4); // Success step
        toast.success('✅ Deriv account linked successfully!');
      } else {
        const error = await response.json();
        toast.error('Token verification failed', {
          description: error.detail || 'Please check your API token and try again'
        });
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to verify token with Deriv.com'
      });
    } finally {
      setIsVerifying(false);
    }
  };

  const handleProceedWithTrading = () => {
    onAccountLinked({
      api_token: apiToken,
      account_info: accountInfo
    });
  };

  const openDerivApiPage = () => {
    window.open('https://app.deriv.com/account/api-token', '_blank');
  };

  const openDerivLoginPage = () => {
    window.open('https://app.deriv.com', '_blank');
  };

  if (step === 1) {
    return (
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-green-500 to-blue-500 rounded-full">
              <Globe className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent mb-4">
            🔗 Link Your Deriv Account
          </h2>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Connect your Deriv.com account to enable ULTRA-FAST AI trading with real money
          </p>
        </div>

        {/* Benefits */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-8 border border-green-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-2" />
            Why Link Your Deriv Account?
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start space-x-3">
              <Zap className="w-5 h-5 text-blue-600 mt-1" />
              <div>
                <div className="font-semibold text-gray-800">ULTRA-FAST Trading</div>
                <div className="text-sm text-gray-600">7,200 trades per hour with 0.5-second intervals</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <DollarSign className="w-5 h-5 text-green-600 mt-1" />
              <div>
                <div className="font-semibold text-gray-800">Real Money Profits</div>
                <div className="text-sm text-gray-600">Trade with real money and earn actual profits</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Shield className="w-5 h-5 text-purple-600 mt-1" />
              <div>
                <div className="font-semibold text-gray-800">Secure Authorization</div>
                <div className="text-sm text-gray-600">Your credentials remain with Deriv.com</div>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <Key className="w-5 h-5 text-orange-600 mt-1" />
              <div>
                <div className="font-semibold text-gray-800">Full Control</div>
                <div className="text-sm text-gray-600">Revoke access anytime from your Deriv account</div>
              </div>
            </div>
          </div>
        </div>

        {/* Account Status Check */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Step 1: Verify Your Deriv Account</h3>
          <p className="text-gray-600 mb-4">
            To enable AI trading, you need an active Deriv.com account. If you don't have one, you can create it for free.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={openDerivLoginPage}
              className="flex-1 bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white"
            >
              <ExternalLink className="w-4 h-4 mr-2" />
              Login to Deriv.com
            </Button>
            <Button
              onClick={() => setStep(2)}
              variant="outline"
              className="flex-1"
            >
              I Have a Deriv Account
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>

        {/* Skip Option */}
        <div className="text-center">
          <Button
            onClick={onSkip}
            variant="ghost"
            className="text-gray-500 hover:text-gray-700"
          >
            Skip Account Linking (Enter API Token Manually)
          </Button>
        </div>
      </div>
    );
  }

  if (step === 2) {
    return (
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-orange-500 to-red-500 rounded-full">
              <Key className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            🔑 Generate API Token
          </h2>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Create an API token on Deriv.com to authorize the AI to trade on your behalf
          </p>
        </div>

        {/* Step-by-step Instructions */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Follow These Steps:</h3>
          
          <div className="space-y-4">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                1
              </div>
              <div>
                <div className="font-semibold text-gray-800">Open Deriv API Token Page</div>
                <div className="text-sm text-gray-600 mb-2">Click the button below to open the API token management page</div>
                <Button
                  onClick={openDerivApiPage}
                  size="sm"
                  className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white"
                >
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Open Deriv API Page
                </Button>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
                2
              </div>
              <div>
                <div className="font-semibold text-gray-800">Create New API Token</div>
                <div className="text-sm text-gray-600">
                  On the API token page, click "Create New Token" and configure it with these permissions:
                </div>
                <div className="mt-2 p-3 bg-gray-50 rounded-lg">
                  <div className="text-xs font-mono space-y-1">
                    <div>✅ <strong>Read:</strong> Account information, balance</div>
                    <div>✅ <strong>Trade:</strong> Buy and sell contracts</div>
                    <div>✅ <strong>Payments:</strong> View payment information</div>
                    <div>⚠️ <strong>Name:</strong> "Wakhungu28Ai Trading Bot"</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
                3
              </div>
              <div>
                <div className="font-semibold text-gray-800">Copy Your API Token</div>
                <div className="text-sm text-gray-600">
                  After creating the token, copy it and paste it in the next step. 
                  <strong className="text-red-600"> Keep it secure!</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-amber-600 mt-1" />
            <div>
              <h4 className="font-semibold text-amber-800">Security Notice</h4>
              <p className="text-sm text-amber-700 mt-1">
                Your API token allows the AI to trade on your behalf. You can revoke access anytime from your Deriv account. 
                Never share your token with anyone else.
              </p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            onClick={() => setStep(1)}
            variant="outline"
          >
            ← Back
          </Button>
          <Button
            onClick={() => setStep(3)}
            className="bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white"
          >
            I Have My Token
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      </div>
    );
  }

  if (step === 3) {
    return (
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full">
              <Lock className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">
            🔐 Authorize AI Trading
          </h2>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Enter your Deriv API token to authorize Wakhungu28Ai to trade on your behalf
          </p>
        </div>

        {/* Token Input */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Enter Your API Token</h3>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="api_token" className="text-sm font-medium text-gray-700">
                Deriv API Token
              </Label>
              <textarea
                id="api_token"
                value={apiToken}
                onChange={(e) => setApiToken(e.target.value)}
                className="mt-1 block w-full px-3 py-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 h-24 resize-none"
                placeholder="Paste your Deriv API token here..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Your token will be encrypted and stored securely. You can revoke access anytime from your Deriv account.
              </p>
            </div>

            <Button
              onClick={handleVerifyToken}
              disabled={isVerifying || !apiToken}
              className="w-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white py-3 text-lg font-semibold"
            >
              {isVerifying ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Verifying with Deriv.com...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Shield className="w-5 h-5" />
                  <span>Verify & Authorize AI Trading</span>
                </div>
              )}
            </Button>
          </div>
        </div>

        {/* What Happens Next */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <h4 className="font-semibold text-blue-800 mb-2">What happens when you authorize?</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• The AI will verify your token with Deriv.com</li>
            <li>• Your account balance and information will be retrieved</li>
            <li>• Trading authorization will be confirmed</li>
            <li>• You'll be able to start ULTRA-FAST AI trading immediately</li>
          </ul>
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <Button
            onClick={() => setStep(2)}
            variant="outline"
          >
            ← Back to Instructions
          </Button>
        </div>
      </div>
    );
  }

  if (step === 4) {
    return (
      <div className="max-w-2xl mx-auto">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full">
              <CheckCircle className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent mb-4">
            ✅ Account Successfully Linked!
          </h2>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Your Deriv account is now authorized for ULTRA-FAST AI trading
          </p>
        </div>

        {/* Account Information */}
        {accountInfo && (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200 mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">📊 Account Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Account ID</div>
                <div className="font-semibold text-gray-800">{accountInfo.loginid || 'Connected'}</div>
              </div>
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Currency</div>
                <div className="font-semibold text-gray-800">{accountInfo.currency || 'USD'}</div>
              </div>
              <div className="p-3 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600">Balance</div>
                <div className="font-semibold text-green-800">${accountInfo.balance || '0.00'}</div>
              </div>
              <div className="p-3 bg-blue-50 rounded-lg">
                <div className="text-sm text-blue-600">Status</div>
                <div className="font-semibold text-blue-800">✅ Authorized</div>
              </div>
            </div>
          </div>
        )}

        {/* Next Steps */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border border-green-200 mb-6">
          <h3 className="text-lg font-semibold text-green-800 mb-4">🚀 Ready for ULTRA-FAST Trading!</h3>
          <div className="space-y-3 text-sm text-green-700">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Account authorized for real money trading</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>ULTRA-FAST 0.5-second trading intervals enabled</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Enhanced martingale recovery system ready</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Multi-market trading across 10 volatility indices</span>
            </div>
          </div>
        </div>

        {/* Start Trading Button */}
        <div className="text-center">
          <Button
            onClick={handleProceedWithTrading}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-8 py-4 text-lg font-bold rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
          >
            <div className="flex items-center space-x-2">
              <Zap className="w-6 h-6" />
              <span>🚀 START AI TRADING NOW</span>
            </div>
          </Button>
          
          <p className="text-sm text-gray-600 mt-4">
            You can start with stakes as low as $0.35 for testing
          </p>
        </div>
      </div>
    );
  }

  return null;
};

export default DerivAccountLinker;