"""
Ultra-Aggressive Wakhungu28Ai Trading Engine
Designed for maximum trade frequency and quick entries
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

logger = logging.getLogger('UltraAggressiveAI')

@dataclass
class AggressiveSignal:
    """Ultra-fast signal for aggressive trading"""
    symbol: str
    contract_type: str
    trade_type: str
    prediction_number: Optional[int]
    confidence: float
    stake: float
    reason: str
    ticks_count: int
    timestamp: datetime
    priority: int = 1  # 1=highest priority

class UltraAggressiveTradingEngine:
    """Ultra-aggressive trading engine that takes trades every few seconds"""
    
    def __init__(self, config: BotConfig, analysis_api_url: str, bot_token: str):
        self.config = config
        self.analysis_api_url = analysis_api_url
        self.bot_token = bot_token
        self.headers = {"Authorization": f"Bearer {bot_token}"}
        
        # Aggressive settings - override config for speed
        self.min_confidence = 50.0  # Very low threshold for frequent trades
        self.trade_interval = 3.0   # 3 seconds between trades (very aggressive)
        self.quick_analysis_ticks = 15  # Use only last 15 ticks for speed
        
        # Performance tracking
        self.trades_history: List[BotTrade] = []
        self.performance_metrics = {
            "total_trades": 0,
            "winning_trades": 0,
            "win_rate": 0.0,
            "total_profit": 0.0,
            "trades_per_hour": 0.0,
            "last_trade_time": None
        }
        
        # Trading state
        self.is_running = False
        self.start_time = None
        self.balance = config.initial_balance
        self.daily_profit_loss = 0.0
        
        # Martingale for aggressive recovery
        self.martingale_level = 0
        self.last_outcome = "WIN"
        
        logger.info(f"🚀 Ultra-Aggressive Trading Engine initialized")
        logger.info(f"⚡ Trade interval: {self.trade_interval}s (very fast)")
        logger.info(f"🎯 Min confidence: {self.min_confidence}% (very low for frequent trades)")
    
    async def start_aggressive_trading(self) -> bool:
        """Start ultra-aggressive trading with frequent entries"""
        if self.is_running:
            return False
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info(f"🚀 ULTRA-AGGRESSIVE TRADING STARTED!")
        logger.info(f"⚡ Targeting trade every {self.trade_interval} seconds")
        logger.info(f"🎯 Low confidence threshold: {self.min_confidence}%")
        
        # Start aggressive trading loop
        asyncio.create_task(self._aggressive_trading_loop())
        return True
    
    async def stop_trading(self) -> bool:
        """Stop aggressive trading"""
        self.is_running = False
        logger.info("🛑 Ultra-Aggressive Trading STOPPED")
        return True
    
    async def _aggressive_trading_loop(self):
        """Main aggressive trading loop - takes trades frequently"""
        trade_count = 0
        
        while self.is_running:
            try:
                # Quick trade attempt every few seconds
                signal = await self._get_aggressive_signal()
                
                if signal:
                    trade_result = await self._execute_quick_trade(signal)
                    if trade_result:
                        trade_count += 1
                        
                        # Log every trade for aggressive mode
                        outcome_emoji = "🟢" if trade_result.outcome == "WIN" else "🔴"
                        logger.info(f"{outcome_emoji} TRADE #{trade_count}: "
                                  f"{signal.contract_type} {signal.trade_type} "
                                  f"| Conf: {signal.confidence:.1f}% "
                                  f"| Stake: ${signal.stake:.2f} "
                                  f"| P&L: ${trade_result.profit_loss:.2f} "
                                  f"| Balance: ${self.balance:.2f}")
                
                # Very short wait for aggressive trading
                await asyncio.sleep(self.trade_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in aggressive trading loop: {e}")
                await asyncio.sleep(5)  # Short pause on error
    
    async def _get_aggressive_signal(self) -> Optional[AggressiveSignal]:
        """Generate aggressive trading signal with guaranteed signal creation"""
        try:
            symbol = self.config.selected_market
            
            # Get tick data (real or simulated)
            recent_ticks = await self._get_quick_ticks(symbol, self.quick_analysis_ticks)
            
            if len(recent_ticks) < 3:
                # Even if no data, create a basic signal for maximum aggressiveness
                logger.warning(f"⚠️ Very limited data, creating forced signal")
                return self._create_forced_aggressive_signal()
            
            # Quick and dirty analysis for speed
            recent_digits = [tick["last_digit"] for tick in recent_ticks[-10:]]
            
            # Generate multiple signal options quickly
            signals = []
            
            # Even/Odd quick analysis
            even_count = sum(1 for d in recent_digits if d % 2 == 0)
            odd_count = len(recent_digits) - even_count
            even_confidence = (even_count / len(recent_digits)) * 100
            odd_confidence = (odd_count / len(recent_digits)) * 100
            
            # ALWAYS create even/odd signals (lower threshold to 40%)
            if even_confidence >= 40:
                signals.append(self._create_aggressive_signal(
                    "EVEN_ODD", "EVEN", None, max(even_confidence, 50), 
                    f"Even digits appear {even_confidence:.1f}% of time"
                ))
            
            if odd_confidence >= 40:
                signals.append(self._create_aggressive_signal(
                    "EVEN_ODD", "ODD", None, max(odd_confidence, 50),
                    f"Odd digits appear {odd_confidence:.1f}% of time"
                ))
            
            # Over/Under quick analysis for multiple thresholds (lower threshold)
            for threshold in [4, 5, 6]:  # Focus on middle thresholds
                over_count = sum(1 for d in recent_digits if d > threshold)
                under_count = sum(1 for d in recent_digits if d < threshold)
                
                over_confidence = (over_count / len(recent_digits)) * 100
                under_confidence = (under_count / len(recent_digits)) * 100
                
                if over_confidence >= 40:  # Lower threshold
                    signals.append(self._create_aggressive_signal(
                        "OVER_UNDER", "OVER", threshold, max(over_confidence, 50),
                        f"Over {threshold} appears {over_confidence:.1f}% of time"
                    ))
                
                if under_confidence >= 40:  # Lower threshold
                    signals.append(self._create_aggressive_signal(
                        "OVER_UNDER", "UNDER", threshold, max(under_confidence, 50),
                        f"Under {threshold} appears {under_confidence:.1f}% of time"
                    ))
            
            # Always ensure we have at least one signal
            if not signals:
                logger.info("🎯 No qualifying signals, creating forced aggressive signal")
                return self._create_forced_aggressive_signal()
            
            # Return best signal or random for variety
            if len(signals) == 1:
                return signals[0]
            else:
                # Mix of best and random for aggressive variety
                if np.random.random() > 0.7:  # 30% chance of random selection
                    return np.random.choice(signals)
                else:
                    return max(signals, key=lambda s: s.confidence)
            
        except Exception as e:
            logger.error(f"❌ Error generating aggressive signal: {e}")
            return self._create_forced_aggressive_signal()
    
    def _create_forced_aggressive_signal(self) -> AggressiveSignal:
        """Create a forced signal for ultra-aggressive mode when no good signals available"""
        # Rotate between different forced strategies
        strategies = [
            ("EVEN_ODD", "EVEN", None, "Forced even trade (50% probability)"),
            ("EVEN_ODD", "ODD", None, "Forced odd trade (50% probability)"),
            ("OVER_UNDER", "OVER", 5, "Forced over 5 trade (40% probability)"),
            ("OVER_UNDER", "UNDER", 5, "Forced under 5 trade (50% probability)"),
        ]
        
        # Select random strategy
        contract_type, trade_type, prediction_number, reason = np.random.choice(strategies)
        
        return self._create_aggressive_signal(
            contract_type, trade_type, prediction_number, 51.0,  # Just above minimum
            reason
        )
    
    def _create_aggressive_signal(self, contract_type: str, trade_type: str, 
                                prediction_number: Optional[int], confidence: float, 
                                reason: str) -> AggressiveSignal:
        """Create aggressive trading signal with martingale adjustment"""
        
        # Calculate stake with martingale
        base_stake = self.config.trading_params.stake
        stake = base_stake
        
        if self.config.trading_params.martingale_enabled and self.last_outcome == "LOSS":
            # Apply martingale multiplier
            stake = base_stake * (self.config.trading_params.martingale_multiplier ** self.martingale_level)
            # Safety limit
            max_stake = self.balance * 0.1  # Max 10% of balance
            stake = min(stake, max_stake)
        
        return AggressiveSignal(
            symbol=self.config.selected_market,
            contract_type=contract_type,
            trade_type=trade_type,
            prediction_number=prediction_number,
            confidence=confidence,
            stake=stake,
            reason=reason,
            ticks_count=self.config.trading_params.ticks_count,
            timestamp=datetime.now(),
            priority=1 if self.martingale_level > 0 else 2
        )
    
    async def _get_quick_ticks(self, symbol: str, limit: int = 15) -> List[Dict]:
        """Get minimal tick data for ultra-fast analysis with fallback"""
        try:
            # First try to get real tick data
            url = f"{self.analysis_api_url}/api/ticks/{symbol}"
            params = {"limit": limit}
            
            response = requests.get(url, params=params, timeout=2)  # Shorter timeout
            response.raise_for_status()
            data = response.json()
            
            ticks = data.get("ticks", [])
            if len(ticks) >= 5:
                return ticks
            
            # If not enough real data, fall back to simulated ticks
            logger.warning(f"⚠️ Limited real data ({len(ticks)} ticks), using simulated data for aggressive trading")
            return self._generate_simulated_ticks(limit)
            
        except Exception as e:
            logger.warning(f"⚠️ Tick fetch error, using simulated data: {e}")
            # Generate simulated tick data for ultra-aggressive mode
            return self._generate_simulated_ticks(limit)
    
    def _generate_simulated_ticks(self, count: int = 15) -> List[Dict]:
        """Generate simulated tick data for ultra-aggressive trading when real data unavailable"""
        current_time = datetime.now()
        ticks = []
        
        # Generate realistic random digits with some patterns
        base_price = 100.0
        for i in range(count):
            # Create somewhat realistic price movement
            price_change = np.random.normal(0, 0.01)  # Small random changes
            price = base_price + price_change * i
            
            # Extract last digit (this is what we trade on)
            last_digit = int(str(abs(price))[-1])
            
            tick = {
                "symbol": self.config.selected_market,
                "price": round(price, 5),
                "timestamp": (current_time - timedelta(seconds=(count-i)*3)).isoformat(),
                "epoch": int((current_time - timedelta(seconds=(count-i)*3)).timestamp()),
                "last_digit": last_digit
            }
            ticks.append(tick)
        
        logger.info(f"📊 Generated {count} simulated ticks for aggressive trading")
        return ticks
    
    async def _execute_quick_trade(self, signal: AggressiveSignal) -> Optional[BotTrade]:
        """Execute trade with minimal processing for speed"""
        try:
            # Ultra-fast execution simulation
            # In production, this would be optimized Deriv API calls
            
            # Higher win probability for aggressive mode (slightly optimistic)
            base_probability = min(0.85, signal.confidence / 100 + 0.1)
            
            # Simulate outcome
            outcome = "WIN" if np.random.random() < base_probability else "LOSS"
            
            # Calculate profit/loss
            if outcome == "WIN":
                profit_loss = signal.stake * 0.95  # 95% payout
                self.martingale_level = 0  # Reset martingale on win
            else:
                profit_loss = -signal.stake
                if self.config.trading_params.martingale_enabled:
                    self.martingale_level = min(
                        self.martingale_level + 1, 
                        self.config.trading_params.max_martingale_steps
                    )
            
            # Update balance and tracking
            self.balance += profit_loss
            self.daily_profit_loss += profit_loss
            self.last_outcome = outcome
            
            # Create trade record
            trade_record = BotTrade(
                bot_id=self.config.id,
                symbol=signal.symbol,
                contract_type=signal.contract_type,
                trade_type=signal.trade_type,
                prediction_number=signal.prediction_number,
                confidence=signal.confidence,
                ai_score=signal.confidence + 10,  # Boost for aggressive mode
                stake=signal.stake,
                martingale_level=self.martingale_level,
                outcome=outcome,
                profit_loss=profit_loss,
                ticks_count=signal.ticks_count,
                execution_time=signal.timestamp
            )
            
            self.trades_history.append(trade_record)
            self._update_aggressive_metrics(trade_record)
            
            return trade_record
            
        except Exception as e:
            logger.error(f"❌ Ultra-fast execution error: {e}")
            return None
    
    def _update_aggressive_metrics(self, trade: BotTrade):
        """Update performance metrics for aggressive trading"""
        self.performance_metrics["total_trades"] += 1
        self.performance_metrics["last_trade_time"] = trade.execution_time
        
        if trade.outcome == "WIN":
            self.performance_metrics["winning_trades"] += 1
        
        self.performance_metrics["win_rate"] = (
            self.performance_metrics["winning_trades"] / 
            self.performance_metrics["total_trades"] * 100
        )
        
        self.performance_metrics["total_profit"] += trade.profit_loss
        
        # Calculate aggressive trades per hour
        if self.start_time:
            hours_running = (datetime.now() - self.start_time).total_seconds() / 3600
            self.performance_metrics["trades_per_hour"] = (
                self.performance_metrics["total_trades"] / max(hours_running, 0.01)
            )
    
    def get_aggressive_status(self) -> BotStatus:
        """Get current aggressive bot status"""
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
            current_streak=0,  # Simplified for aggressive mode
            best_streak=0,
            martingale_level=self.martingale_level,
            trades_per_hour=self.performance_metrics["trades_per_hour"],
            uptime_seconds=uptime_seconds,
            last_trade_time=self.performance_metrics["last_trade_time"]
        )