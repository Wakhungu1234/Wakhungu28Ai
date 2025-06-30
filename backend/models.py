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

# Bot Management Models
class BotConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_name: str = "Wakhungu28Ai"
    initial_balance: float = 1000.0
    min_confidence: float = 65.0
    min_ai_score: float = 60.0
    max_daily_loss: float = 0.1  # 10%
    max_single_trade: float = 0.05  # 5%
    active_markets: List[str] = ["R_100", "R_25", "R_50", "R_75", "1HZ100V"]
    deriv_api_token: str = ""
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BotStatus(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_id: str
    status: str  # "RUNNING", "STOPPED", "PAUSED", "ERROR"
    current_balance: float
    daily_profit_loss: float
    total_trades: int
    winning_trades: int
    win_rate: float
    last_trade_time: Optional[datetime] = None
    error_message: Optional[str] = None
    uptime_seconds: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BotTrade(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_id: str
    symbol: str
    contract_type: str
    action: str
    confidence: float
    ai_score: float
    stake: float
    outcome: str  # "WIN", "LOSS", "PENDING"
    profit_loss: float
    contract_id: Optional[str] = None
    execution_time: datetime = Field(default_factory=datetime.utcnow)
    close_time: Optional[datetime] = None

class BotCreateRequest(BaseModel):
    bot_name: str = "Wakhungu28Ai"
    initial_balance: float = 1000.0
    deriv_api_token: str
    min_confidence: float = 65.0
    active_markets: List[str] = ["R_100", "R_25", "R_50"]

class BotUpdateRequest(BaseModel):
    min_confidence: Optional[float] = None
    min_ai_score: Optional[float] = None
    max_daily_loss: Optional[float] = None
    max_single_trade: Optional[float] = None
    active_markets: Optional[List[str]] = None
    deriv_api_token: Optional[str] = None