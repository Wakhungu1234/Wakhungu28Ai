"""
High-Frequency Wakhungu28Ai Trading Engine
Advanced AI for ultra-fast trading with 10,000+ trades per day capability
"""

import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import deque, Counter
from dataclasses import dataclass
import requests

from models import BotConfig, BotStatus, BotTrade, TradingParameters
from analysis import analyze_ticks

logger = logging.getLogger('HighFrequencyAI')

@dataclass
class FastTradingSignal:
    """Ultra-fast trading signal for high-frequency execution"""
    symbol: str
    contract_type: str
    trade_type: str
    prediction_number: Optional[int]
    confidence: float
    ai_score: float
    stake: float
    ticks_count: int
    timestamp: datetime
    execution_priority: int = 1  # 1=highest, 5=lowest
    martingale_level: int = 0

class UltraFastPatternAnalyzer:
    """Optimized pattern analyzer for high-frequency trading"""
    
    def __init__(self):
        self.recent_patterns = deque(maxlen=100)  # Smaller for speed
        self.hot_digits = deque(maxlen=50)
        self.trend_cache = {}
        self.confidence_cache = {}
        
    def quick_analysis(self, recent_digits: List[int], symbol: str) -> Dict:
        """Ultra-fast pattern analysis optimized for speed"""
        if len(recent_digits) < 5:
            return {"confidence_boost": 0, "quick_patterns": {}}
        
        # Cache key for quick lookup
        cache_key = f"{symbol}_{len(recent_digits)}_{hash(tuple(recent_digits[-10:]))}"
        
        if cache_key in self.confidence_cache:
            return self.confidence_cache[cache_key]
        
        # Quick digit frequency (last 20 only for speed)
        recent_20 = recent_digits[-20:]
        digit_counts = Counter(recent_20)
        
        # Fast hot/cold detection
        hot_digits = [d for d, count in digit_counts.items() if count >= 4]
        cold_digits = [d for d, count in digit_counts.items() if count <= 1]
        
        # Quick streak detection
        last_digit = recent_digits[-1]
        streak_length = 1
        for i in range(len(recent_digits) - 2, max(-1, len(recent_digits) - 6), -1):
            if recent_digits[i] % 2 == last_digit % 2:
                streak_length += 1
            else:
                break
        
        # Quick confidence boost calculation
        confidence_boost = 0
        if hot_digits:
            confidence_boost += len(hot_digits) * 3
        if streak_length >= 3:
            confidence_boost += streak_length * 2
        if len(set(recent_20)) <= 6:  # Low variety = pattern
            confidence_boost += 5
            
        result = {
            "confidence_boost": min(confidence_boost, 20),
            "quick_patterns": {
                "hot_digits": hot_digits,
                "cold_digits": cold_digits,
                "streak_length": streak_length,
                "variety_score": len(set(recent_20))
            }
        }
        
        # Cache for 5 seconds
        self.confidence_cache[cache_key] = result
        asyncio.create_task(self._clear_cache_after_delay(cache_key, 5))
        
        return result
    
    async def _clear_cache_after_delay(self, cache_key: str, delay: int):
        """Clear cache entry after delay"""
        await asyncio.sleep(delay)
        self.confidence_cache.pop(cache_key, None)

class MartingaleRecoverySystem:
    """Advanced Martingale recovery system with safeguards"""
    
    def __init__(self, config: TradingParameters):
        self.enabled = config.martingale_enabled
        self.multiplier = config.martingale_multiplier
        self.max_steps = config.max_martingale_steps
        self.current_level = 0
        self.recovery_sequence = []
        self.last_loss_time = None
        
    def get_next_stake(self, base_stake: float, last_outcome: str) -> Tuple[float, int]:
        """Calculate next stake amount and martingale level"""
        if not self.enabled:
            return base_stake, 0
        
        if last_outcome == "WIN":
            # Reset on win
            self.current_level = 0
            self.recovery_sequence = []
            return base_stake, 0
        
        elif last_outcome == "LOSS":
            # Increase stake for recovery
            if self.current_level < self.max_steps:
                self.current_level += 1
                recovery_stake = base_stake * (self.multiplier ** self.current_level)
                self.recovery_sequence.append({
                    "level": self.current_level,
                    "stake": recovery_stake,
                    "timestamp": datetime.now()
                })
                return recovery_stake, self.current_level
            else:
                # Max steps reached, reset
                logger.warning(f"🔴 Martingale max steps ({self.max_steps}) reached. Resetting.")
                self.current_level = 0
                self.recovery_sequence = []
                return base_stake, 0
        
        return base_stake, self.current_level
    
    def is_in_recovery(self) -> bool:
        """Check if currently in recovery mode"""
        return self.current_level > 0
    
    def get_recovery_info(self) -> Dict:
        """Get current recovery information"""
        total_recovery_needed = sum(seq["stake"] for seq in self.recovery_sequence)
        return {
            "is_recovering": self.is_in_recovery(),
            "current_level": self.current_level,
            "max_level": self.max_steps,
            "total_amount_to_recover": total_recovery_needed,
            "recovery_sequence": self.recovery_sequence
        }

class HighFrequencyTradingEngine:
    """Ultra-fast trading engine capable of 10,000+ trades per day"""
    
    def __init__(self, config: BotConfig, analysis_api_url: str, bot_token: str):
        self.config = config
        self.analysis_api_url = analysis_api_url
        self.bot_token = bot_token
        self.headers = {"Authorization": f"Bearer {bot_token}"}
        
        # High-frequency components
        self.fast_analyzer = UltraFastPatternAnalyzer()
        self.martingale_system = MartingaleRecoverySystem(config.trading_params)
        
        # Performance tracking
        self.trades_history: List[BotTrade] = []
        self.last_outcomes = deque(maxlen=10)  # Track recent outcomes
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "win_rate": 0.0,
            "total_profit": 0.0,
            "best_streak": 0,
            "current_streak": 0,
            "trades_per_hour": 0.0,
            "avg_execution_time": 0.0
        }
        
        # Trading state
        self.is_running = False
        self.start_time = None
        self.balance = config.initial_balance
        self.daily_profit_loss = 0.0
        self.trades_today = 0
        self.last_reset_date = datetime.now().date()
        
        # Speed optimization
        self.market_cache = {}
        self.analysis_cache = {}
        self.last_analysis_time = {}
        
        logger.info(f"🚀 High-Frequency Wakhungu28Ai Engine initialized")
        logger.info(f"💰 Target: 10,000+ trades/day with {config.trading_params.martingale_multiplier}x Martingale")
    
    async def start_high_frequency_trading(self) -> bool:
        """Start ultra-fast trading engine"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info(f"🚀 High-Frequency Trading Engine STARTED")
        logger.info(f"📊 Target: {self.config.max_trades_per_hour}/hour ({self.config.max_trades_per_hour * 24}/day)")
        logger.info(f"⚡ Interval: {self.config.trade_interval_seconds}s between trades")
        
        # Start the ultra-fast trading loop
        asyncio.create_task(self._ultra_fast_trading_loop())
        return True
    
    async def stop_trading(self) -> bool:
        """Stop the trading engine"""
        self.is_running = False
        logger.info(f"🛑 High-Frequency Trading Engine STOPPED")
        return True
    
    async def _ultra_fast_trading_loop(self):
        """Main ultra-fast trading loop"""
        trade_count = 0
        hour_start = datetime.now()
        
        while self.is_running:
            try:
                # Reset hourly counter
                current_time = datetime.now()
                if (current_time - hour_start).total_seconds() >= 3600:
                    self.performance_metrics["trades_per_hour"] = trade_count
                    trade_count = 0
                    hour_start = current_time
                
                # Check daily reset
                if current_time.date() != self.last_reset_date:
                    self._reset_daily_counters()
                
                # Rate limiting check
                if trade_count >= self.config.max_trades_per_hour:
                    wait_time = 3600 - (current_time - hour_start).total_seconds()
                    if wait_time > 0:
                        await asyncio.sleep(min(wait_time, 60))  # Wait max 1 minute
                        continue
                
                # Check trading conditions
                if not self._should_continue_trading():
                    await asyncio.sleep(60)  # Wait 1 minute before checking again
                    continue
                
                # Ultra-fast signal generation and execution
                execution_start = time.time()
                
                signal = await self._get_ultra_fast_signal()
                if signal:
                    trade_result = await self._execute_ultra_fast_trade(signal)
                    if trade_result:
                        trade_count += 1
                        self.trades_today += 1
                        
                        # Update Martingale system
                        next_stake, martingale_level = self.martingale_system.get_next_stake(
                            self.config.trading_params.stake, 
                            trade_result.outcome
                        )
                        
                        # Log high-frequency stats
                        execution_time = time.time() - execution_start
                        self.performance_metrics["avg_execution_time"] = (
                            self.performance_metrics["avg_execution_time"] * 0.9 + execution_time * 0.1
                        )
                        
                        if trade_count % 100 == 0:  # Log every 100 trades
                            logger.info(f"⚡ {trade_count} trades/hour | "
                                      f"Win Rate: {self.performance_metrics['win_rate']:.1f}% | "
                                      f"Balance: ${self.balance:.2f} | "
                                      f"Martingale: Level {martingale_level}")
                
                # Ultra-short interval for high frequency
                await asyncio.sleep(self.config.trade_interval_seconds)
                
            except Exception as e:
                logger.error(f"❌ Error in ultra-fast trading loop: {e}")
                await asyncio.sleep(5)  # Short pause on error
    
    async def _get_ultra_fast_signal(self) -> Optional[FastTradingSignal]:
        """Generate ultra-fast trading signal"""
        try:
            symbol = self.config.selected_market
            
            # Get recent ticks (cached for speed)
            recent_ticks = await self._get_cached_ticks(symbol, 30)  # Only last 30 for speed
            if len(recent_ticks) < 10:
                return None
            
            recent_digits = [tick["last_digit"] for tick in recent_ticks[-20:]]
            
            # Ultra-fast pattern analysis
            pattern_analysis = self.fast_analyzer.quick_analysis(recent_digits, symbol)
            
            # Quick decision making based on configuration
            contract_type = self.config.trading_params.contract_type
            trade_type = self.config.trading_params.trade_type
            prediction_number = self.config.trading_params.prediction_number
            
            # Auto-selection logic for best confidence
            if contract_type == "AUTO_BEST" or trade_type == "AUTO":
                signal_options = await self._generate_all_signal_options(recent_digits, pattern_analysis)
                if not signal_options:
                    return None
                
                # Select best signal by confidence
                best_signal = max(signal_options, key=lambda s: s.confidence + s.ai_score)
                return best_signal
            else:
                # Use specific configuration
                confidence = await self._calculate_specific_confidence(
                    recent_digits, contract_type, trade_type, prediction_number
                )
                
                if confidence < self.config.min_confidence:
                    return None
                
                # Calculate stake with Martingale
                base_stake = self.config.trading_params.stake
                last_outcome = self.last_outcomes[-1] if self.last_outcomes else "WIN"
                stake, martingale_level = self.martingale_system.get_next_stake(base_stake, last_outcome)
                
                # Apply balance limits
                max_stake = self.balance * 0.1  # Max 10% of balance
                stake = min(stake, max_stake)
                
                ai_score = confidence + pattern_analysis["confidence_boost"]
                
                return FastTradingSignal(
                    symbol=symbol,
                    contract_type=contract_type,
                    trade_type=trade_type,
                    prediction_number=prediction_number,
                    confidence=confidence,
                    ai_score=ai_score,
                    stake=stake,
                    ticks_count=self.config.trading_params.ticks_count,
                    timestamp=datetime.now(),
                    execution_priority=1,
                    martingale_level=martingale_level
                )
                
        except Exception as e:
            logger.error(f"❌ Error generating ultra-fast signal: {e}")
            return None
    
    async def _generate_all_signal_options(self, recent_digits: List[int], pattern_analysis: Dict) -> List[FastTradingSignal]:
        """Generate all possible signal options for auto-selection"""
        signals = []
        symbol = self.config.selected_market
        base_stake = self.config.trading_params.stake
        
        # Calculate base confidence from recent digits
        digit_counts = Counter(recent_digits[-15:])  # Last 15 for speed
        total = len(recent_digits[-15:])
        
        # Even/Odd signals
        even_count = sum(count for digit, count in digit_counts.items() if digit % 2 == 0)
        odd_count = total - even_count
        even_confidence = (even_count / total) * 100
        odd_confidence = (odd_count / total) * 100
        
        if even_confidence > self.config.min_confidence:
            signals.append(self._create_signal("EVEN_ODD", "EVEN", None, even_confidence, symbol, base_stake, pattern_analysis))
        if odd_confidence > self.config.min_confidence:
            signals.append(self._create_signal("EVEN_ODD", "ODD", None, odd_confidence, symbol, base_stake, pattern_analysis))
        
        # Over/Under signals for different thresholds
        for threshold in [3, 4, 5, 6, 7]:
            over_count = sum(count for digit, count in digit_counts.items() if digit > threshold)
            under_count = sum(count for digit, count in digit_counts.items() if digit < threshold)
            
            over_confidence = (over_count / total) * 100
            under_confidence = (under_count / total) * 100
            
            if over_confidence > self.config.min_confidence:
                signals.append(self._create_signal("OVER_UNDER", "OVER", threshold, over_confidence, symbol, base_stake, pattern_analysis))
            if under_confidence > self.config.min_confidence:
                signals.append(self._create_signal("OVER_UNDER", "UNDER", threshold, under_confidence, symbol, base_stake, pattern_analysis))
        
        # Match/Differ signals for hot/cold digits
        hot_digits = pattern_analysis["quick_patterns"].get("hot_digits", [])
        cold_digits = pattern_analysis["quick_patterns"].get("cold_digits", [])
        
        for digit in hot_digits:
            match_confidence = (digit_counts.get(digit, 0) / total) * 100
            if match_confidence > self.config.min_confidence:
                signals.append(self._create_signal("MATCH_DIFFER", "MATCH", digit, match_confidence, symbol, base_stake, pattern_analysis))
        
        for digit in cold_digits:
            differ_confidence = 100 - (digit_counts.get(digit, 0) / total) * 100
            if differ_confidence > self.config.min_confidence:
                signals.append(self._create_signal("MATCH_DIFFER", "DIFFER", digit, differ_confidence, symbol, base_stake, pattern_analysis))
        
        return signals
    
    def _create_signal(self, contract_type: str, trade_type: str, prediction_number: Optional[int], 
                      confidence: float, symbol: str, base_stake: float, pattern_analysis: Dict) -> FastTradingSignal:
        """Create a trading signal with martingale adjustment"""
        
        # Apply Martingale adjustment
        last_outcome = self.last_outcomes[-1] if self.last_outcomes else "WIN"
        stake, martingale_level = self.martingale_system.get_next_stake(base_stake, last_outcome)
        
        # Apply balance limits
        max_stake = self.balance * 0.1
        stake = min(stake, max_stake)
        
        ai_score = confidence + pattern_analysis["confidence_boost"]
        
        return FastTradingSignal(
            symbol=symbol,
            contract_type=contract_type,
            trade_type=trade_type,
            prediction_number=prediction_number,
            confidence=confidence,
            ai_score=ai_score,
            stake=stake,
            ticks_count=self.config.trading_params.ticks_count,
            timestamp=datetime.now(),
            execution_priority=1 if martingale_level > 0 else 2,  # Recovery trades get priority
            martingale_level=martingale_level
        )
    
    async def _calculate_specific_confidence(self, recent_digits: List[int], contract_type: str, 
                                           trade_type: str, prediction_number: Optional[int]) -> float:
        """Calculate confidence for specific trade configuration"""
        digit_counts = Counter(recent_digits[-15:])
        total = len(recent_digits[-15:])
        
        if contract_type == "EVEN_ODD":
            if trade_type == "EVEN":
                even_count = sum(count for digit, count in digit_counts.items() if digit % 2 == 0)
                return (even_count / total) * 100
            else:  # ODD
                odd_count = sum(count for digit, count in digit_counts.items() if digit % 2 == 1)
                return (odd_count / total) * 100
        
        elif contract_type == "OVER_UNDER" and prediction_number is not None:
            if trade_type == "OVER":
                over_count = sum(count for digit, count in digit_counts.items() if digit > prediction_number)
                return (over_count / total) * 100
            else:  # UNDER
                under_count = sum(count for digit, count in digit_counts.items() if digit < prediction_number)
                return (under_count / total) * 100
        
        elif contract_type == "MATCH_DIFFER" and prediction_number is not None:
            if trade_type == "MATCH":
                match_count = digit_counts.get(prediction_number, 0)
                return (match_count / total) * 100
            else:  # DIFFER
                differ_count = total - digit_counts.get(prediction_number, 0)
                return (differ_count / total) * 100
        
        return 50.0  # Default confidence
    
    async def _get_cached_ticks(self, symbol: str, limit: int = 30) -> List[Dict]:
        """Get cached tick data for ultra-fast access"""
        cache_key = f"{symbol}_{limit}"
        current_time = time.time()
        
        # Check cache (1 second expiry for real-time data)
        if (cache_key in self.market_cache and 
            current_time - self.market_cache[cache_key]["timestamp"] < 1.0):
            return self.market_cache[cache_key]["data"]
        
        try:
            # Fetch fresh data
            url = f"{self.analysis_api_url}/api/ticks/{symbol}"
            params = {"limit": limit}
            
            response = requests.get(url, params=params, timeout=2)  # Short timeout for speed
            response.raise_for_status()
            data = response.json()
            
            ticks = data.get("ticks", [])
            
            # Cache the result
            self.market_cache[cache_key] = {
                "data": ticks,
                "timestamp": current_time
            }
            
            return ticks
            
        except Exception as e:
            # Return cached data if available, even if expired
            if cache_key in self.market_cache:
                logger.warning(f"⚠️ Using cached data due to fetch error: {e}")
                return self.market_cache[cache_key]["data"]
            
            logger.error(f"❌ Error fetching ticks: {e}")
            return []
    
    async def _execute_ultra_fast_trade(self, signal: FastTradingSignal) -> Optional[BotTrade]:
        """Execute trade with ultra-fast processing"""
        try:
            # Simulate ultra-fast trade execution
            # In production, this would call the actual Deriv API
            
            # Calculate win probability based on confidence and AI score
            base_probability = signal.confidence / 100
            ai_boost = signal.ai_score / 1000  # Small boost from AI
            win_probability = min(0.95, base_probability + ai_boost)
            
            # Simulate trade outcome
            outcome = "WIN" if np.random.random() < win_probability else "LOSS"
            
            # Calculate profit/loss
            if outcome == "WIN":
                profit_loss = signal.stake * 0.95  # 95% payout
            else:
                profit_loss = -signal.stake
            
            # Update balance and tracking
            self.balance += profit_loss
            self.daily_profit_loss += profit_loss
            self.last_outcomes.append(outcome)
            
            # Create trade record
            trade_record = BotTrade(
                bot_id=self.config.id,
                symbol=signal.symbol,
                contract_type=signal.contract_type,
                trade_type=signal.trade_type,
                prediction_number=signal.prediction_number,
                confidence=signal.confidence,
                ai_score=signal.ai_score,
                stake=signal.stake,
                martingale_level=signal.martingale_level,
                outcome=outcome,
                profit_loss=profit_loss,
                ticks_count=signal.ticks_count,
                execution_time=signal.timestamp
            )
            
            self.trades_history.append(trade_record)
            self._update_performance_metrics(trade_record)
            
            # Log important trades
            if signal.martingale_level > 0 or abs(profit_loss) > 50:
                logger.info(f"{'🟢' if outcome == 'WIN' else '🔴'} "
                          f"{signal.contract_type} {signal.trade_type} "
                          f"{'(' + str(signal.prediction_number) + ')' if signal.prediction_number is not None else ''} "
                          f"| Conf: {signal.confidence:.1f}% | AI: {signal.ai_score:.1f} "
                          f"| Stake: ${signal.stake:.2f} | P&L: ${profit_loss:.2f} "
                          f"| Martingale: L{signal.martingale_level}")
            
            return trade_record
            
        except Exception as e:
            logger.error(f"❌ Ultra-fast execution error: {e}")
            return None
    
    def _update_performance_metrics(self, trade: BotTrade):
        """Update performance metrics"""
        self.performance_metrics["total_trades"] += 1
        
        if trade.outcome == "WIN":
            self.performance_metrics["winning_trades"] += 1
            self.performance_metrics["current_streak"] += 1
            self.performance_metrics["best_streak"] = max(
                self.performance_metrics["best_streak"],
                self.performance_metrics["current_streak"]
            )
        else:
            self.performance_metrics["current_streak"] = 0
        
        self.performance_metrics["win_rate"] = (
            self.performance_metrics["winning_trades"] / 
            self.performance_metrics["total_trades"] * 100
        )
        
        self.performance_metrics["total_profit"] += trade.profit_loss
        
        # Calculate trades per hour
        if self.start_time:
            hours_running = (datetime.now() - self.start_time).total_seconds() / 3600
            self.performance_metrics["trades_per_hour"] = self.performance_metrics["total_trades"] / max(hours_running, 0.01)
    
    def _should_continue_trading(self) -> bool:
        """Check if trading should continue"""
        # Check daily loss limit
        if self.daily_profit_loss < -self.balance * self.config.max_daily_loss:
            logger.warning(f"🛑 Daily loss limit reached: ${self.daily_profit_loss:.2f}")
            return False
        
        # Check minimum balance
        if self.balance < self.config.initial_balance * 0.1:
            logger.warning(f"🛑 Balance too low: ${self.balance:.2f}")
            return False
        
        # Check take profit
        if (self.config.trading_params.take_profit and 
            self.daily_profit_loss >= self.config.trading_params.take_profit):
            logger.info(f"🎯 Take profit reached: ${self.daily_profit_loss:.2f}")
            return False
        
        # Check stop loss
        if (self.config.trading_params.stop_loss and 
            self.daily_profit_loss <= -self.config.trading_params.stop_loss):
            logger.warning(f"🛑 Stop loss reached: ${self.daily_profit_loss:.2f}")
            return False
        
        return True
    
    def _reset_daily_counters(self):
        """Reset daily trading counters"""
        self.daily_profit_loss = 0
        self.trades_today = 0
        self.last_reset_date = datetime.now().date()
        self.martingale_system.current_level = 0  # Reset Martingale
        logger.info("🔄 Daily counters reset")
    
    def get_status(self) -> BotStatus:
        """Get current bot status"""
        uptime_seconds = 0
        if self.start_time:
            uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
        
        return BotStatus(
            bot_id=self.config.id,
            status="RUNNING" if self.is_running else "STOPPED",
            current_balance=self.balance,
            daily_profit_loss=self.daily_profit_loss,
            total_trades=self.performance_metrics["total_trades"],
            winning_trades=self.performance_metrics["winning_trades"],
            win_rate=self.performance_metrics["win_rate"],
            current_streak=self.performance_metrics["current_streak"],
            best_streak=self.performance_metrics["best_streak"],
            martingale_level=self.martingale_system.current_level,
            trades_per_hour=self.performance_metrics["trades_per_hour"],
            uptime_seconds=uptime_seconds
        )
    
    def get_martingale_info(self) -> Dict:
        """Get detailed Martingale recovery information"""
        return self.martingale_system.get_recovery_info()