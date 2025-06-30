"""
Wakhungu28Ai Web Service - Enhanced High-Frequency Bot Management System
Ultra-fast trading with 10,000+ trades per day capability
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
from collections import deque, Counter
from dataclasses import dataclass
import requests

from models import BotConfig, BotStatus, BotTrade, AdvancedBotCreateRequest, TradingParameters
from analysis import analyze_ticks
from high_frequency_ai import HighFrequencyTradingEngine
from ultra_aggressive_ai import UltraAggressiveTradingEngine

logger = logging.getLogger('Wakhungu28AiService')

@dataclass
class TradingSignal:
    """Enhanced trading signal with AI enhancements"""
    symbol: str
    contract_type: str
    action: str
    confidence: float
    winning_digits: List[int]
    reason: str
    timestamp: datetime
    ai_score: float = 0.0
    risk_level: str = "MEDIUM"
    expected_profit: float = 0.0

@dataclass
class TradeResult:
    """Trade execution result tracking"""
    signal: TradingSignal
    contract_id: str
    stake: float
    outcome: str  # WIN/LOSS/PENDING
    profit_loss: float
    execution_time: datetime
    close_time: Optional[datetime] = None

class AdvancedPatternAnalyzer:
    """AI-powered pattern recognition for enhanced predictions"""
    
    def __init__(self):
        self.historical_patterns = deque(maxlen=1000)
        self.digit_sequences = deque(maxlen=200)
        self.winning_patterns = {}
        self.market_cycles = {}
        
    def analyze_digit_patterns(self, recent_digits: List[int]) -> Dict:
        """Advanced pattern analysis beyond basic frequency"""
        if len(recent_digits) < 10:
            return {"confidence_boost": 0, "patterns": []}
        
        patterns = {
            "sequences": self._find_sequences(recent_digits),
            "cycles": self._detect_cycles(recent_digits),
            "streaks": self._analyze_streaks(recent_digits),
            "distributions": self._analyze_distribution_patterns(recent_digits)
        }
        
        # Calculate AI confidence boost based on patterns
        confidence_boost = self._calculate_pattern_confidence(patterns)
        
        return {
            "confidence_boost": confidence_boost,
            "patterns": patterns,
            "prediction_strength": self._get_prediction_strength(patterns)
        }
    
    def _find_sequences(self, digits: List[int]) -> Dict:
        """Find repeating sequences in digit patterns"""
        sequences = {}
        for length in range(2, 6):  # Look for sequences of 2-5 digits
            for i in range(len(digits) - length + 1):
                seq = tuple(digits[i:i+length])
                if seq in sequences:
                    sequences[seq] += 1
                else:
                    sequences[seq] = 1
        
        # Find most frequent sequences
        frequent_sequences = {k: v for k, v in sequences.items() if v >= 2}
        return frequent_sequences
    
    def _detect_cycles(self, digits: List[int]) -> Dict:
        """Detect cyclical patterns in digit appearance"""
        cycles = {}
        
        # Check for even/odd cycles
        even_odd_pattern = [d % 2 for d in digits[-20:]]
        cycles["even_odd_alternation"] = self._calculate_alternation_score(even_odd_pattern)
        
        # Check for over/under 5 cycles
        over_under_pattern = [1 if d > 5 else 0 for d in digits[-20:]]
        cycles["over_under_alternation"] = self._calculate_alternation_score(over_under_pattern)
        
        return cycles
    
    def _analyze_streaks(self, digits: List[int]) -> Dict:
        """Analyze streak patterns for prediction"""
        current_streak = {"type": None, "length": 0, "digit": None}
        
        # Even/Odd streak
        last_type = digits[-1] % 2
        streak_length = 1
        for i in range(len(digits) - 2, -1, -1):
            if digits[i] % 2 == last_type:
                streak_length += 1
            else:
                break
        
        current_streak["even_odd"] = {
            "type": "EVEN" if last_type == 0 else "ODD",
            "length": streak_length,
            "break_probability": min(streak_length * 0.15, 0.8)  # Higher streak = higher break chance
        }
        
        return current_streak
    
    def _analyze_distribution_patterns(self, digits: List[int]) -> Dict:
        """Analyze distribution deviations for prediction"""
        digit_counts = Counter(digits[-50:])  # Last 50 digits
        total = len(digits[-50:])
        
        distributions = {}
        for digit in range(10):
            actual_freq = digit_counts.get(digit, 0) / total
            expected_freq = 0.1
            deviation = actual_freq - expected_freq
            
            distributions[digit] = {
                "frequency": actual_freq,
                "deviation": deviation,
                "status": "HOT" if deviation > 0.05 else "COLD" if deviation < -0.05 else "NORMAL"
            }
        
        return distributions
    
    def _calculate_alternation_score(self, pattern: List[int]) -> float:
        """Calculate how much a pattern alternates (0 = no alternation, 1 = perfect alternation)"""
        if len(pattern) < 2:
            return 0
        
        alternations = sum(1 for i in range(1, len(pattern)) if pattern[i] != pattern[i-1])
        max_alternations = len(pattern) - 1
        return alternations / max_alternations if max_alternations > 0 else 0
    
    def _calculate_pattern_confidence(self, patterns: Dict) -> float:
        """Calculate confidence boost based on identified patterns"""
        boost = 0
        
        # Sequence patterns boost
        if patterns["sequences"]:
            max_sequence_count = max(patterns["sequences"].values())
            boost += min(max_sequence_count * 5, 15)  # Max 15% boost from sequences
        
        # Cycle patterns boost
        cycles = patterns["cycles"]
        if cycles.get("even_odd_alternation", 0) > 0.7:
            boost += 10  # Strong alternation pattern
        elif cycles.get("even_odd_alternation", 0) < 0.3:
            boost += 8   # Strong non-alternation pattern
        
        # Streak patterns boost
        streaks = patterns.get("streaks", {})
        if "even_odd" in streaks:
            streak_length = streaks["even_odd"]["length"]
            if streak_length >= 5:
                boost += min(streak_length * 2, 20)  # Max 20% boost from streaks
        
        return min(boost, 25)  # Maximum 25% confidence boost from patterns
    
    def _get_prediction_strength(self, patterns: Dict) -> str:
        """Get overall prediction strength"""
        total_boost = self._calculate_pattern_confidence(patterns)
        if total_boost >= 20:
            return "STRONG"
        elif total_boost >= 10:
            return "MODERATE"
        else:
            return "WEAK"

class RiskManager:
    """Advanced risk management system"""
    
    def __init__(self, initial_balance: float = 1000):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.max_daily_loss = 0.1  # 10% max daily loss
        self.max_single_trade = 0.05  # 5% max per trade
        self.daily_trades = 0
        self.daily_profit_loss = 0
        self.last_reset = datetime.now().date()
        
    def calculate_optimal_stake(self, confidence: float, ai_score: float) -> float:
        """Calculate optimal stake based on confidence and risk"""
        base_stake = self.balance * 0.02  # 2% base stake
        
        # Confidence multiplier (55% = 0.5x, 90% = 2x)
        confidence_multiplier = max(0.3, min(2.0, (confidence - 50) / 20))
        
        # AI score multiplier (0-100 AI score)
        ai_multiplier = max(0.8, min(1.5, ai_score / 50))
        
        # Risk adjustment
        risk_adjusted_stake = base_stake * confidence_multiplier * ai_multiplier
        
        # Apply maximum limits
        max_stake = self.balance * self.max_single_trade
        final_stake = min(risk_adjusted_stake, max_stake)
        
        # Check daily limits
        if self.daily_profit_loss < -self.balance * self.max_daily_loss:
            return 0  # Stop trading for the day
        
        return round(final_stake, 2)
    
    def record_trade(self, stake: float, profit_loss: float):
        """Record trade result and update balance"""
        # Reset daily counters if new day
        current_date = datetime.now().date()
        if current_date != self.last_reset:
            self.daily_trades = 0
            self.daily_profit_loss = 0
            self.last_reset = current_date
        
        self.balance += profit_loss
        self.daily_profit_loss += profit_loss
        self.daily_trades += 1
        
        logger.info(f"💰 Balance: ${self.balance:.2f} | Daily P&L: ${self.daily_profit_loss:.2f}")
    
    def should_trade(self) -> bool:
        """Determine if we should continue trading"""
        # Check daily loss limits
        if self.daily_profit_loss < -self.balance * self.max_daily_loss:
            logger.warning("🛑 Daily loss limit reached. Stopping trading.")
            return False
        
        # Check if we have sufficient balance
        if self.balance < self.initial_balance * 0.2:  # 20% of initial balance
            logger.warning("🛑 Balance too low. Stopping trading.")
            return False
        
        return True

class Wakhungu28AiWebService:
    """Enhanced web-based Wakhungu28Ai trading bot service with high-frequency capabilities"""
    
    def __init__(self, config: BotConfig, analysis_api_url: str, bot_token: str):
        self.config = config
        self.analysis_api_url = analysis_api_url
        self.bot_token = bot_token
        self.headers = {"Authorization": f"Bearer {bot_token}"}
        
        # Choose trading engine based on configuration
        if getattr(config, 'ultra_aggressive_mode', False) or config.trade_interval_seconds <= 5.0:
            # Use ultra-aggressive engine for fast trading
            self.trading_engine = UltraAggressiveTradingEngine(config, analysis_api_url, bot_token)
            logger.info(f"🚀 Using ULTRA-AGGRESSIVE Trading Engine")
        else:
            # Use standard high-frequency engine
            self.trading_engine = HighFrequencyTradingEngine(config, analysis_api_url, bot_token)
            logger.info(f"🚀 Using High-Frequency Trading Engine")
        
        # Bot State
        self.is_running = False
        self.start_time = None
        
        logger.info(f"🚀 Enhanced Wakhungu28Ai Web Service initialized")
        logger.info(f"⚡ Mode: {'ULTRA-AGGRESSIVE' if hasattr(self.trading_engine, 'start_aggressive_trading') else 'HIGH-FREQUENCY'}")
        logger.info(f"🎯 Market: {config.selected_market}")
        logger.info(f"📊 Contract: {config.trading_params.contract_type}")
        logger.info(f"💰 Stake: ${config.trading_params.stake}")
        logger.info(f"🔄 Martingale: {'Enabled' if config.trading_params.martingale_enabled else 'Disabled'}")
    
    async def start_bot(self) -> bool:
        """Start the high-frequency trading bot"""
        if self.is_running:
            logger.warning("🤖 Bot is already running")
            return False
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            
            # Start appropriate trading engine
            if hasattr(self.trading_engine, 'start_aggressive_trading'):
                # Ultra-aggressive mode
                success = await self.trading_engine.start_aggressive_trading()
                logger.info(f"🚀 ULTRA-AGGRESSIVE Wakhungu28Ai bot started")
                logger.info(f"⚡ Trade every {getattr(self.trading_engine, 'trade_interval', 3)}s")
            else:
                # High-frequency mode
                success = await self.trading_engine.start_high_frequency_trading()
                logger.info(f"🚀 High-Frequency Wakhungu28Ai bot started")
                logger.info(f"🎯 Target: {self.config.max_trades_per_hour} trades/hour")
            
            if success:
                logger.info(f"✅ Bot started successfully - Expect trades soon!")
                return True
            else:
                self.is_running = False
                return False
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            self.is_running = False
            return False
    
    async def stop_bot(self) -> bool:
        """Stop the high-frequency trading bot"""
        if not self.is_running:
            logger.warning("🤖 Bot is not running")
            return False
        
        try:
            self.is_running = False
            
            # Stop trading engine
            await self.trading_engine.stop_trading()
            
            logger.info("🛑 High-Frequency Wakhungu28Ai bot stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")
            return False
    
    async def get_bot_status(self) -> BotStatus:
        """Get current bot status from trading engine"""
        try:
            if hasattr(self.trading_engine, 'get_aggressive_status'):
                # Ultra-aggressive mode status
                status = self.trading_engine.get_aggressive_status()
            else:
                # High-frequency mode status
                status = self.trading_engine.get_status()
            return status
        except Exception as e:
            logger.error(f"❌ Error getting bot status: {e}")
            # Return default status
            uptime_seconds = 0
            if self.start_time:
                uptime_seconds = int((datetime.now() - self.start_time).total_seconds())
            
            return BotStatus(
                bot_id=self.config.id,
                status="ERROR",
                current_balance=self.config.initial_balance,
                daily_profit_loss=0.0,
                total_trades=0,
                winning_trades=0,
                win_rate=0.0,
                current_streak=0,
                best_streak=0,
                uptime_seconds=uptime_seconds,
                error_message=str(e)
            )
    
    async def get_martingale_info(self) -> Dict:
        """Get Martingale recovery information"""
        try:
            return self.trading_engine.get_martingale_info()
        except Exception as e:
            logger.error(f"❌ Error getting Martingale info: {e}")
            return {
                "is_recovering": False,
                "current_level": 0,
                "max_level": 0,
                "total_amount_to_recover": 0.0,
                "recovery_sequence": []
            }
    
    async def update_config(self, update_data: Dict) -> bool:
        """Update bot configuration"""
        try:
            # Update config object
            for key, value in update_data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                elif hasattr(self.config.trading_params, key):
                    setattr(self.config.trading_params, key, value)
            
            # Update trading engine if running
            if self.is_running:
                # Stop and restart with new config
                await self.stop_bot()
                await asyncio.sleep(1)
                await self.start_bot()
            
            logger.info(f"✅ Bot configuration updated: {list(update_data.keys())}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return False
    
    async def _trading_loop(self):
        """Main trading loop"""
        logger.info("🎯 Trading loop started")
        
        trade_count = 0
        max_trades_per_hour = 6  # Conservative approach
        
        while self.is_running:
            try:
                # Get enhanced signals
                signals = await self._get_enhanced_signals()
                
                if not signals:
                    logger.info("⏳ No qualified signals found. Waiting...")
                    await asyncio.sleep(60)  # Wait 1 minute
                    continue
                
                # Execute best signal
                best_signal = signals[0]
                logger.info(f"🎯 Best Signal: {best_signal.symbol} {best_signal.action} (Conf: {best_signal.confidence:.1f}%, AI: {best_signal.ai_score:.1f})")
                
                # Rate limiting
                if trade_count >= max_trades_per_hour:
                    logger.info("⏸️ Hourly trade limit reached. Waiting...")
                    await asyncio.sleep(600)  # Wait 10 minutes
                    trade_count = 0
                    continue
                
                trade_result = await self._execute_trade(best_signal)
                if trade_result:
                    trade_count += 1
                
                # Wait between trades
                await asyncio.sleep(120)  # 2 minutes between trades
                
            except asyncio.CancelledError:
                logger.info("🛑 Trading loop cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in trading loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _get_enhanced_signals(self) -> List[TradingSignal]:
        """Get trading signals with AI enhancements"""
        try:
            symbols = ",".join(self.config.active_markets)
            url = f"{self.analysis_api_url}/api/bot/trading-signals"
            params = {
                "symbols": symbols,
                "tick_count": 100,
                "min_confidence": self.config.min_confidence - 10  # Get more signals for AI processing
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            enhanced_signals = []
            
            for market_data in data.get("signals", []):
                symbol = market_data["symbol"]
                
                # Get recent tick data for pattern analysis
                recent_ticks = await self._get_recent_ticks(symbol, 100)
                recent_digits = [tick["last_digit"] for tick in recent_ticks[-50:]]
                
                # Analyze patterns with AI
                pattern_analysis = self.pattern_analyzer.analyze_digit_patterns(recent_digits)
                
                for signal_data in market_data["signals"]:
                    # Create base signal
                    signal = TradingSignal(
                        symbol=symbol,
                        contract_type=signal_data["contract_type"],
                        action=signal_data["action"],
                        confidence=signal_data["confidence"],
                        winning_digits=signal_data["winning_digits"],
                        reason=signal_data["reason"],
                        timestamp=datetime.now()
                    )
                    
                    # Apply AI enhancements
                    ai_score = self._calculate_ai_score(signal, pattern_analysis)
                    enhanced_confidence = min(95, signal.confidence + pattern_analysis["confidence_boost"])
                    
                    signal.ai_score = ai_score
                    signal.confidence = enhanced_confidence
                    signal.risk_level = self._assess_risk_level(signal, pattern_analysis)
                    
                    # Filter by enhanced criteria
                    if (enhanced_confidence >= self.config.min_confidence and 
                        ai_score >= self.config.min_ai_score):
                        enhanced_signals.append(signal)
            
            # Sort by AI score and confidence
            enhanced_signals.sort(key=lambda s: (s.ai_score, s.confidence), reverse=True)
            
            return enhanced_signals[:3]  # Return top 3 signals
            
        except Exception as e:
            logger.error(f"❌ Error getting enhanced signals: {e}")
            return []
    
    async def _get_recent_ticks(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Get recent tick data for analysis"""
        try:
            url = f"{self.analysis_api_url}/api/ticks/{symbol}"
            params = {"limit": limit}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return data.get("ticks", [])
            
        except Exception as e:
            logger.error(f"❌ Error getting recent ticks: {e}")
            return []
    
    def _calculate_ai_score(self, signal: TradingSignal, pattern_analysis: Dict) -> float:
        """Calculate AI enhancement score"""
        base_score = signal.confidence
        
        # Pattern strength bonus
        pattern_strength = pattern_analysis.get("prediction_strength", "WEAK")
        strength_bonus = {"STRONG": 15, "MODERATE": 8, "WEAK": 0}[pattern_strength]
        
        # Historical performance bonus (simplified)
        performance_bonus = self._get_performance_bonus()
        
        ai_score = base_score + strength_bonus + performance_bonus
        return min(100, max(0, ai_score))
    
    def _assess_risk_level(self, signal: TradingSignal, pattern_analysis: Dict) -> str:
        """Assess risk level of the signal"""
        if signal.confidence >= 80 and signal.ai_score >= 80:
            return "LOW"
        elif signal.confidence >= 70 and signal.ai_score >= 70:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _get_performance_bonus(self) -> float:
        """Get performance-based bonus"""
        if self.performance_metrics["total_trades"] < 5:
            return 0
        
        win_rate = self.performance_metrics["win_rate"]
        if win_rate >= 85:
            return 5
        elif win_rate < 50:
            return -10
        else:
            return 0
    
    async def _execute_trade(self, signal: TradingSignal) -> Optional[TradeResult]:
        """Execute trade with comprehensive validation and monitoring"""
        if not self.risk_manager.should_trade():
            logger.warning("🛑 Risk manager blocked trade execution")
            return None
        
        # Calculate optimal stake
        stake = self.risk_manager.calculate_optimal_stake(signal.confidence, signal.ai_score)
        if stake <= 0:
            logger.warning("🛑 Risk manager set stake to 0")
            return None
        
        try:
            # Simulate trade execution (replace with actual Deriv API call)
            contract_id = f"simulated_{int(time.time())}"
            
            # For simulation: calculate outcome based on confidence
            # In real implementation, this would be the actual Deriv API response
            win_probability = signal.confidence / 100
            actual_outcome = "WIN" if np.random.random() < win_probability else "LOSS"
            
            # Calculate profit/loss
            if actual_outcome == "WIN":
                profit_loss = stake * 0.95  # 95% payout
            else:
                profit_loss = -stake
            
            # Record trade
            trade_result = TradeResult(
                signal=signal,
                contract_id=contract_id,
                stake=stake,
                outcome=actual_outcome,
                profit_loss=profit_loss,
                execution_time=datetime.now()
            )
            
            # Update systems
            self.risk_manager.record_trade(stake, profit_loss)
            self.trades_history.append(trade_result)
            self._update_performance_metrics(trade_result)
            
            # Log trade
            logger.info(f"🚀 TRADE EXECUTED:")
            logger.info(f"   Symbol: {signal.symbol}")
            logger.info(f"   Action: {signal.action}")
            logger.info(f"   Confidence: {signal.confidence:.1f}%")
            logger.info(f"   AI Score: {signal.ai_score:.1f}")
            logger.info(f"   Stake: ${stake:.2f}")
            logger.info(f"   Outcome: {actual_outcome}")
            logger.info(f"   P&L: ${profit_loss:.2f}")
            
            return trade_result
            
        except Exception as e:
            logger.error(f"❌ Error executing trade: {e}")
            return None
    
    def _update_performance_metrics(self, trade_result: TradeResult):
        """Update bot performance metrics"""
        self.performance_metrics["total_trades"] += 1
        
        if trade_result.outcome == "WIN":
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
        
        self.performance_metrics["total_profit"] += trade_result.profit_loss
        
        # Auto-adjust parameters based on performance
        self._auto_adjust_parameters()
    
    def _auto_adjust_parameters(self):
        """Automatically adjust trading parameters based on performance"""
        if self.performance_metrics["total_trades"] < 10:
            return
        
        win_rate = self.performance_metrics["win_rate"]
        
        # Adjust minimum confidence based on performance
        if win_rate < 75:  # Below target
            self.config.min_confidence = min(80, self.config.min_confidence + 2)
            self.config.min_ai_score = min(80, self.config.min_ai_score + 2)
            logger.info(f"📈 Increased standards: Min Confidence={self.config.min_confidence}%, Min AI Score={self.config.min_ai_score}")
        elif win_rate > 90:  # Excellent performance
            self.config.min_confidence = max(60, self.config.min_confidence - 1)
            self.config.min_ai_score = max(55, self.config.min_ai_score - 1)
            logger.info(f"📉 Relaxed standards: Min Confidence={self.config.min_confidence}%, Min AI Score={self.config.min_ai_score}")

# Global bot instance manager - Import this into server.py
active_bots: Dict[str, Wakhungu28AiWebService] = {}

async def create_bot_instance(config: BotConfig, analysis_api_url: str, bot_token: str) -> str:
    """Create a new high-frequency bot instance"""
    bot_id = config.id
    
    if bot_id in active_bots:
        raise ValueError(f"Bot with ID {bot_id} already exists")
    
    bot_service = Wakhungu28AiWebService(config, analysis_api_url, bot_token)
    active_bots[bot_id] = bot_service
    
    logger.info(f"🤖 Created high-frequency bot instance: {bot_id}")
    logger.info(f"⚡ Max trades/hour: {config.max_trades_per_hour}")
    logger.info(f"🎯 Market: {config.selected_market}")
    return bot_id

async def start_bot_instance(bot_id: str) -> bool:
    """Start a bot instance"""
    if bot_id not in active_bots:
        raise ValueError(f"Bot with ID {bot_id} not found")
    
    return await active_bots[bot_id].start_bot()

async def stop_bot_instance(bot_id: str) -> bool:
    """Stop a bot instance"""
    if bot_id not in active_bots:
        raise ValueError(f"Bot with ID {bot_id} not found")
    
    return await active_bots[bot_id].stop_bot()

async def get_bot_status(bot_id: str) -> BotStatus:
    """Get bot status"""
    if bot_id not in active_bots:
        raise ValueError(f"Bot with ID {bot_id} not found")
    
    return await active_bots[bot_id].get_bot_status()

async def delete_bot_instance(bot_id: str) -> bool:
    """Delete a bot instance"""
    if bot_id not in active_bots:
        return False
    
    # Stop the bot first
    await stop_bot_instance(bot_id)
    
    # Remove from active bots
    del active_bots[bot_id]
    
    logger.info(f"🗑️ Deleted bot instance: {bot_id}")
    return True

def get_all_active_bots() -> List[str]:
    """Get list of all active bot IDs"""
    return list(active_bots.keys())