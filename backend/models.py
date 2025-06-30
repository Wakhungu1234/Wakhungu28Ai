from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

class VolatilityIndex(BaseModel):
    id: str
    name: str
    symbol: str
    description: Optional[str] = None

class TickData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    price: float
    timestamp: datetime
    epoch: int
    last_digit: int
    
class TickAnalysis(BaseModel):
    symbol: str
    tick_count: int
    digit_frequency: List[Dict[str, Any]]
    even_odd_analysis: Dict[str, Any]
    over_under_analysis: Dict[str, Any]
    predictions: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PredictionRequest(BaseModel):
    symbol: str
    contract_type: str  # 'over_under', 'matches_differs', 'even_odd'
    tick_count: int = 1000

# Enhanced Bot Configuration Models for High-Frequency Trading
class TradingParameters(BaseModel):
    """Advanced trading parameters for high-frequency bot"""
    contract_type: str  # "OVER_UNDER", "MATCH_DIFFER", "EVEN_ODD", "AUTO_BEST"
    trade_type: str     # "OVER", "UNDER", "MATCH", "DIFFER", "EVEN", "ODD", "AUTO"
    prediction_number: Optional[int] = None  # For OVER/UNDER/MATCH/DIFFER (0-9)
    stake: float = 10.0
    stop_loss: Optional[float] = None  # Maximum loss before stopping
    take_profit: Optional[float] = None  # Target profit before stopping
    ticks_count: int = 5  # Number of ticks for the trade
    martingale_enabled: bool = True
    martingale_multiplier: float = 2.0
    max_martingale_steps: int = 5
    
class BotConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_name: str = "Wakhungu28Ai-Pro"
    initial_balance: float = 1000.0
    min_confidence: float = 60.0  # Lower for high-frequency
    min_ai_score: float = 55.0
    max_daily_loss: float = 0.15  # 15% max daily loss
    max_single_trade: float = 0.08  # 8% max per trade
    selected_market: str = "R_100"  # Single market focus for speed
    trading_params: TradingParameters = Field(default_factory=TradingParameters)
    deriv_api_token: str = ""
    is_active: bool = False
    
    # High-frequency trading settings
    max_trades_per_hour: int = 500  # Up to 12,000 trades per day
    trade_interval_seconds: float = 0.3  # 300ms between trades (very fast)
    quick_analysis_mode: bool = True  # Use faster analysis
    auto_recovery_mode: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BotStatus(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_id: str
    status: str  # "RUNNING", "STOPPED", "PAUSED", "ERROR", "RECOVERING"
    current_balance: float
    daily_profit_loss: float
    total_trades: int
    winning_trades: int
    win_rate: float
    current_streak: int
    best_streak: int
    martingale_level: int = 0
    last_trade_time: Optional[datetime] = None
    trades_per_hour: float = 0.0
    error_message: Optional[str] = None
    uptime_seconds: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BotTrade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_id: str
    symbol: str
    contract_type: str
    trade_type: str
    prediction_number: Optional[int] = None
    confidence: float
    ai_score: float
    stake: float
    martingale_level: int = 0
    outcome: str  # "WIN", "LOSS", "PENDING"
    profit_loss: float
    contract_id: Optional[str] = None
    ticks_count: int = 5
    execution_time: datetime = Field(default_factory=datetime.utcnow)
    close_time: Optional[datetime] = None

class AdvancedBotCreateRequest(BaseModel):
    """Enhanced bot creation request with all advanced parameters"""
    bot_name: str = "Wakhungu28Ai-Pro"
    initial_balance: float = 1000.0
    deriv_api_token: str
    selected_market: str = "R_100"
    
    # Trading Configuration
    contract_type: str = "AUTO_BEST"  # "OVER_UNDER", "MATCH_DIFFER", "EVEN_ODD", "AUTO_BEST"
    trade_type: str = "AUTO"  # "OVER", "UNDER", "MATCH", "DIFFER", "EVEN", "ODD", "AUTO"
    prediction_number: Optional[int] = None  # 0-9 for specific predictions
    stake: float = 10.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    ticks_count: int = 5
    
    # Advanced Settings
    min_confidence: float = 60.0
    max_trades_per_hour: int = 500
    trade_interval_seconds: float = 0.3
    
    # Martingale Settings
    martingale_enabled: bool = True
    martingale_multiplier: float = 2.0
    max_martingale_steps: int = 5

class BotUpdateRequest(BaseModel):
    """Enhanced bot update request"""
    min_confidence: Optional[float] = None
    min_ai_score: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_single_trade: Optional[float] = None
    selected_market: Optional[str] = None
    deriv_api_token: Optional[str] = None
    
    # Trading parameters
    contract_type: Optional[str] = None
    trade_type: Optional[str] = None
    prediction_number: Optional[int] = None
    stake: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    ticks_count: Optional[int] = None
    
    # High-frequency settings
    max_trades_per_hour: Optional[int] = None
    trade_interval_seconds: Optional[float] = None
    
    # Martingale settings
    martingale_enabled: Optional[bool] = None
    martingale_multiplier: Optional[float] = None
    max_martingale_steps: Optional[int] = None

# Legacy models for backward compatibility
class BotCreateRequest(BaseModel):
    bot_name: str = "Wakhungu28Ai"
    initial_balance: float = 1000.0
    deriv_api_token: str
    min_confidence: float = 65.0
    active_markets: List[str] = ["R_100", "R_25", "R_50"]

# Market configuration
AVAILABLE_MARKETS = [
    {"value": "R_10", "label": "Volatility 10 Index"},
    {"value": "R_25", "label": "Volatility 25 Index"},
    {"value": "R_50", "label": "Volatility 50 Index"},
    {"value": "R_75", "label": "Volatility 75 Index"},
    {"value": "R_100", "label": "Volatility 100 Index"},
    {"value": "1HZ10V", "label": "Volatility 10 (1s) Index"},
    {"value": "1HZ25V", "label": "Volatility 25 (1s) Index"},
    {"value": "1HZ50V", "label": "Volatility 50 (1s) Index"},
    {"value": "1HZ75V", "label": "Volatility 75 (1s) Index"},
    {"value": "1HZ100V", "label": "Volatility 100 (1s) Index"}
]

CONTRACT_TYPES = [
    {"value": "AUTO_BEST", "label": "Auto (Best Confidence)", "description": "AI selects best contract type"},
    {"value": "OVER_UNDER", "label": "Over/Under", "description": "Last digit over or under a number"},
    {"value": "MATCH_DIFFER", "label": "Match/Differ", "description": "Last digit matches or differs from a number"},
    {"value": "EVEN_ODD", "label": "Even/Odd", "description": "Last digit is even or odd"}
]

TRADE_TYPES = {
    "OVER_UNDER": [
        {"value": "AUTO", "label": "Auto (Best)", "description": "AI selects best option"},
        {"value": "OVER", "label": "Over", "description": "Last digit over the prediction number"},
        {"value": "UNDER", "label": "Under", "description": "Last digit under the prediction number"}
    ],
    "MATCH_DIFFER": [
        {"value": "AUTO", "label": "Auto (Best)", "description": "AI selects match or differ"},
        {"value": "MATCH", "label": "Match", "description": "Last digit matches the prediction number"},
        {"value": "DIFFER", "label": "Differ", "description": "Last digit differs from the prediction number"}
    ],
    "EVEN_ODD": [
        {"value": "AUTO", "label": "Auto (Best)", "description": "AI selects even or odd"},
        {"value": "EVEN", "label": "Even", "description": "Last digit is even (0,2,4,6,8)"},
        {"value": "ODD", "label": "Odd", "description": "Last digit is odd (1,3,5,7,9)"}
    ]
}

PREDICTION_NUMBERS = {
    "OVER": [2, 3, 4, 5, 6, 7, 8],  # Over these numbers
    "UNDER": [8, 7, 6, 5, 4, 3, 2, 1],  # Under these numbers  
    "MATCH_DIFFER": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # Exact digits to match/differ
}

TICKS_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]