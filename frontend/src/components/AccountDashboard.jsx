import React, { useState, useEffect } from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  User, 
  DollarSign, 
  RefreshCw, 
  Eye, 
  EyeOff,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Wallet,
  Building
} from 'lucide-react';
import { toast } from './ui/toaster';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const AccountDashboard = ({ linkedAccount, onAccountUpdate }) => {
  const [accounts, setAccounts] = useState([]);
  const [currentAccount, setCurrentAccount] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const [showBalance, setShowBalance] = useState(true);

  useEffect(() => {
    if (linkedAccount?.api_token) {
      fetchAccounts();
      setCurrentAccount(linkedAccount.account_info);
    }
  }, [linkedAccount]);

  const fetchAccounts = async () => {
    if (!linkedAccount?.api_token) return;

    setIsRefreshing(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/deriv-accounts/${encodeURIComponent(linkedAccount.api_token)}`);
      
      if (response.ok) {
        const data = await response.json();
        setAccounts(data.accounts || []);
      } else {
        toast.error('Failed to fetch accounts');
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to fetch account information'
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const switchAccount = async (loginid) => {
    if (!linkedAccount?.api_token) return;

    setIsSwitching(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/switch-deriv-account`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_token: linkedAccount.api_token,
          loginid: loginid
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentAccount(data.account_info);
        
        // Update the linked account data
        onAccountUpdate && onAccountUpdate({
          ...linkedAccount,
          account_info: data.account_info
        });

        toast.success('✅ Account switched successfully', {
          description: `Now using ${loginid}`,
        });
      } else {
        const error = await response.json();
        toast.error('Failed to switch account', {
          description: error.detail || 'Unknown error occurred'
        });
      }
    } catch (error) {
      toast.error('Connection error', {
        description: 'Failed to switch account'
      });
    } finally {
      setIsSwitching(false);
    }
  };

  const refreshBalance = async () => {
    if (!linkedAccount?.api_token) return;

    setIsRefreshing(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/verify-deriv-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          api_token: linkedAccount.api_token
        })
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentAccount(data.account_info);
        
        onAccountUpdate && onAccountUpdate({
          ...linkedAccount,
          account_info: data.account_info
        });

        toast.success('💰 Balance refreshed');
      } else {
        toast.error('Failed to refresh balance');
      }
    } catch (error) {
      toast.error('Connection error');
    } finally {
      setIsRefreshing(false);
    }
  };

  if (!linkedAccount || !currentAccount) {
    return null;
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg">
            <User className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-800">💼 Account Dashboard</h3>
            <p className="text-sm text-gray-600">Manage your Deriv trading accounts</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            onClick={refreshBalance}
            disabled={isRefreshing}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Current Account Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-700">Account ID</span>
            <Building className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-lg font-bold text-blue-800">{currentAccount.loginid}</div>
          <div className="text-xs text-blue-600">
            {currentAccount.is_virtual ? '🎮 Demo Account' : '💰 Real Account'}
          </div>
        </div>

        <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-green-700">Balance</span>
            <div className="flex items-center space-x-2">
              <DollarSign className="w-4 h-4 text-green-600" />
              <button
                onClick={() => setShowBalance(!showBalance)}
                className="text-green-600 hover:text-green-700"
              >
                {showBalance ? <Eye className="w-3 h-3" /> : <EyeOff className="w-3 h-3" />}
              </button>
            </div>
          </div>
          <div className="text-lg font-bold text-green-800">
            {showBalance ? `${currentAccount.balance} ${currentAccount.currency}` : '****'}
          </div>
          <div className="text-xs text-green-600">Available for trading</div>
        </div>

        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-purple-700">Status</span>
            <CheckCircle className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-lg font-bold text-purple-800">Active</div>
          <div className="text-xs text-purple-600">Ready for ULTRA-FAST trading</div>
        </div>
      </div>

      {/* Account Switching */}
      <div className="border-t pt-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-gray-800">🔄 Switch Accounts</h4>
          <Badge className="bg-blue-100 text-blue-800">
            {accounts.length} Account{accounts.length !== 1 ? 's' : ''} Available
          </Badge>
        </div>

        {accounts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {accounts.map((account) => (
              <div
                key={account.loginid}
                className={`p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  currentAccount.loginid === account.loginid
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <Wallet className="w-4 h-4 text-gray-600" />
                    <span className="font-semibold text-gray-800">{account.loginid}</span>
                    {currentAccount.loginid === account.loginid && (
                      <Badge className="bg-green-100 text-green-800 text-xs">Current</Badge>
                    )}
                  </div>
                  <Badge className={`text-xs ${
                    account.is_virtual 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-orange-100 text-orange-800'
                  }`}>
                    {account.is_virtual ? '🎮 Demo' : '💰 Real'}
                  </Badge>
                </div>

                <div className="text-sm text-gray-600 mb-3">
                  <div>Balance: {account.balance} {account.currency}</div>
                  <div>Type: {account.display_name}</div>
                </div>

                {currentAccount.loginid !== account.loginid && (
                  <Button
                    onClick={() => switchAccount(account.loginid)}
                    disabled={isSwitching}
                    size="sm"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {isSwitching ? (
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-3 w-3 border-b border-white"></div>
                        <span>Switching...</span>
                      </div>
                    ) : (
                      <div className="flex items-center space-x-2">
                        <RefreshCw className="w-3 h-3" />
                        <span>Switch to This Account</span>
                      </div>
                    )}
                  </Button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">No additional accounts found</p>
            <p className="text-sm text-gray-500">You can create additional accounts on Deriv.com</p>
          </div>
        )}
      </div>

      {/* Trading Status */}
      <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
        <div className="flex items-center space-x-3">
          <TrendingUp className="w-5 h-5 text-green-600" />
          <div>
            <div className="font-semibold text-green-800">
              🚀 Ready for ULTRA-FAST Trading
            </div>
            <div className="text-sm text-green-600">
              Your account is authorized and ready for 0.5-second interval trading with enhanced martingale recovery
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountDashboard;