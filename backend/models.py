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

# Bot Configuration Models
class BotConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    api_token: str
    stake_amount: float = Field(ge=1, le=1000)
    take_profit: float = Field(ge=10, le=10000)
    stop_loss: float = Field(ge=10, le=5000)
    martingale_multiplier: float = Field(ge=1.1, le=5.0)
    max_martingale_steps: int = Field(ge=1, le=10)
    selected_markets: List[str] = ["R_100"]
    trade_interval: int = 3  # seconds
    is_active: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class BotConfigCreate(BaseModel):
    name: str = "QuickStart-Ultra"
    api_token: str
    stake_amount: float = Field(default=10.0, ge=1, le=1000)
    take_profit: float = Field(default=500.0, ge=10, le=10000)
    stop_loss: float = Field(default=200.0, ge=10, le=5000)
    martingale_multiplier: float = Field(default=2.0, ge=1.1, le=5.0)
    max_martingale_steps: int = Field(default=5, ge=1, le=10)
    selected_markets: List[str] = ["R_100"]

class BotStatus(BaseModel):
    id: str
    name: str
    status: str  # ACTIVE, STOPPED, ERROR
    current_balance: float
    total_trades: int
    winning_trades: int
    win_rate: float
    total_profit: float
    current_streak: int
    last_trade_time: Optional[datetime] = None
    uptime: Optional[str] = None

class TradeRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bot_id: str
    symbol: str
    contract_type: str
    action: str
    stake: float
    confidence: float
    outcome: str  # WIN/LOSS/PENDING
    profit_loss: float
    execution_time: datetime = Field(default_factory=datetime.utcnow)
    contract_id: Optional[str] = None