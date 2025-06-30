import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import asyncio
import json
import secrets
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from models import (
    VolatilityIndex, TickData, TickAnalysis, PredictionRequest,
    BotConfig, BotStatus, BotTrade, BotCreateRequest, BotUpdateRequest,
    AdvancedBotCreateRequest, TradingParameters
)
from deriv_client import get_deriv_client
from analysis import analyze_ticks
from wakhungu28ai_service import (
    create_bot_instance, start_bot_instance, stop_bot_instance,
    get_bot_status, delete_bot_instance, get_all_active_bots
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Wakhungu28Ai Trading Platform", version="2.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Volatility indices available for trading
VOLATILITY_INDICES = [
    {"id": "R_10", "name": "Volatility 10 Index", "symbol": "R_10", "description": "Simulates market volatility of 10%"},
    {"id": "R_25", "name": "Volatility 25 Index", "symbol": "R_25", "description": "Simulates market volatility of 25%"},
    {"id": "R_50", "name": "Volatility 50 Index", "symbol": "R_50", "description": "Simulates market volatility of 50%"},
    {"id": "R_75", "name": "Volatility 75 Index", "symbol": "R_75", "description": "Simulates market volatility of 75%"},
    {"id": "R_100", "name": "Volatility 100 Index", "symbol": "R_100", "description": "Simulates market volatility of 100%"},
    {"id": "1HZ10V", "name": "Volatility 10 (1s) Index", "symbol": "1HZ10V", "description": "1-second volatility 10% index"},
    {"id": "1HZ25V", "name": "Volatility 25 (1s) Index", "symbol": "1HZ25V", "description": "1-second volatility 25% index"},
    {"id": "1HZ50V", "name": "Volatility 50 (1s) Index", "symbol": "1HZ50V", "description": "1-second volatility 50% index"},
    {"id": "1HZ75V", "name": "Volatility 75 (1s) Index", "symbol": "1HZ75V", "description": "1-second volatility 75% index"},
    {"id": "1HZ100V", "name": "Volatility 100 (1s) Index", "symbol": "1HZ100V", "description": "1-second volatility 100% index"}
]

# In-memory storage for tick data and bot instances (in production, use Redis or similar)
tick_storage: Dict[str, List[Dict]] = {}
active_websockets: List[WebSocket] = []
active_bots: Dict[str, Any] = {}

# API Token management (in production, store in database with expiration)
API_TOKENS = {
    "bot_token_demo_123": {
        "name": "Demo Trading Bot",
        "permissions": ["read", "analysis"],
        "created": datetime.utcnow(),
        "expires": datetime.utcnow() + timedelta(days=365)
    }
}

# Initialize tick storage for each symbol
for index in VOLATILITY_INDICES:
    tick_storage[index["symbol"]] = []

# Security dependency for API token authentication
security = HTTPBearer()

async def verify_api_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token for bot access"""
    token = credentials.credentials
    if token not in API_TOKENS:
        raise HTTPException(status_code=401, detail="Invalid API token")
    
    token_info = API_TOKENS[token]
    if datetime.utcnow() > token_info["expires"]:
        raise HTTPException(status_code=401, detail="API token expired")
    
    return token_info

async def store_tick_data(tick_data: Dict):
    """Store tick data in memory and database"""
    try:
        symbol = tick_data['symbol']
        
        # Store in memory (keep last 2000 ticks per symbol)
        if symbol in tick_storage:
            tick_storage[symbol].append(tick_data)
            # Keep only last 2000 ticks
            if len(tick_storage[symbol]) > 2000:
                tick_storage[symbol] = tick_storage[symbol][-2000:]
        
        # Store in database
        tick_doc = TickData(
            symbol=symbol,
            price=tick_data['price'],
            timestamp=datetime.fromisoformat(tick_data['timestamp']),
            epoch=tick_data['epoch'],
            last_digit=tick_data['last_digit']
        )
        
        await db.ticks.insert_one(tick_doc.dict())
        
        # Broadcast to all connected WebSocket clients
        await broadcast_tick_update(tick_data)
        
    except Exception as e:
        logger.error(f"Error storing tick data: {e}")

async def broadcast_tick_update(tick_data: Dict):
    """Broadcast tick update to all connected WebSocket clients"""
    if active_websockets:
        message = json.dumps({
            "type": "tick_update",
            "data": tick_data
        })
        
        # Remove disconnected clients
        disconnected = []
        for websocket in active_websockets:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        for ws in disconnected:
            active_websockets.remove(ws)

@api_router.get("/")
async def root():
    return {"message": "Wakhungu28Ai Trading Platform API", "status": "active", "version": "2.0.0"}

@api_router.get("/markets", response_model=List[VolatilityIndex])
async def get_markets():
    """Get available volatility indices"""
    return [VolatilityIndex(**market) for market in VOLATILITY_INDICES]

@api_router.get("/ticks/{symbol}")
async def get_ticks(symbol: str, limit: int = 1000):
    """Get historical tick data for a symbol"""
    try:
        if symbol not in tick_storage:
            raise HTTPException(status_code=404, detail="Symbol not found")
        
        # Get from memory first (faster)
        ticks = tick_storage[symbol][-limit:] if len(tick_storage[symbol]) >= limit else tick_storage[symbol]
        
        # If not enough data in memory, get from database
        if len(ticks) < limit:
            db_ticks = await db.ticks.find(
                {"symbol": symbol}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
            
            # Convert to the format expected by frontend
            db_ticks_formatted = []
            for tick in db_ticks:
                db_ticks_formatted.append({
                    "symbol": tick["symbol"],
                    "price": tick["price"],
                    "timestamp": tick["timestamp"].isoformat(),
                    "epoch": tick["epoch"],
                    "last_digit": tick["last_digit"]
                })
            
            # Combine and deduplicate
            all_ticks = db_ticks_formatted + ticks
            # Remove duplicates based on epoch
            seen_epochs = set()
            unique_ticks = []
            for tick in reversed(all_ticks):  # Reverse to prioritize newer data
                if tick["epoch"] not in seen_epochs:
                    unique_ticks.append(tick)
                    seen_epochs.add(tick["epoch"])
            
            ticks = list(reversed(unique_ticks))[-limit:]  # Get latest N ticks
        
        return {
            "symbol": symbol,
            "ticks": ticks,
            "count": len(ticks)
        }
        
    except Exception as e:
        logger.error(f"Error getting ticks for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analysis")
async def get_analysis(request: PredictionRequest):
    """Get analysis and predictions for a symbol"""
    try:
        # Get tick data
        ticks = tick_storage.get(request.symbol, [])
        
        # Use only the requested number of ticks
        analysis_ticks = ticks[-request.tick_count:] if len(ticks) >= request.tick_count else ticks
        
        if not analysis_ticks:
            raise HTTPException(status_code=404, detail="No tick data available for analysis")
        
        # Perform analysis
        analysis_result = analyze_ticks(analysis_ticks)
        
        # Store analysis in database
        analysis_doc = TickAnalysis(
            symbol=request.symbol,
            tick_count=len(analysis_ticks),
            digit_frequency=analysis_result["digit_frequency"],
            even_odd_analysis=analysis_result["even_odd_analysis"],
            over_under_analysis=analysis_result["over_under_analysis"],
            predictions=analysis_result["predictions"]
        )
        
        await db.analyses.insert_one(analysis_doc.dict())
        
        return {
            "symbol": request.symbol,
            "contract_type": request.contract_type,
            "analysis": analysis_result
        }
        
    except Exception as e:
        logger.error(f"Error performing analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# BOT API ENDPOINTS - Secured with API Token Authentication
# =============================================================================

@api_router.get("/bot/trading-signals", dependencies=[Depends(verify_api_token)])
async def get_trading_signals(
    symbols: str = "R_100,R_25,R_50", 
    tick_count: int = 100,
    min_confidence: float = 55.0
):
    """
    Get trading signals for AI bots with confidence filtering
    
    Args:
        symbols: Comma-separated list of symbols (e.g., "R_100,R_25,R_50")
        tick_count: Number of recent ticks to analyze
        min_confidence: Minimum confidence level to include in results
    
    Returns:
        Trading signals in bot-friendly format
    """
    try:
        symbols_list = [s.strip() for s in symbols.split(",")]
        signals = []
        
        for symbol in symbols_list:
            # Get tick data
            ticks = tick_storage.get(symbol, [])
            analysis_ticks = ticks[-tick_count:] if len(ticks) >= tick_count else ticks
            
            if len(analysis_ticks) < 10:  # Minimum data requirement
                continue
                
            # Perform analysis
            analysis_result = analyze_ticks(analysis_ticks)
            predictions = analysis_result["predictions"]
            
            # Extract high-confidence signals
            signal_data = {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "data_points": len(analysis_ticks),
                "signals": []
            }
            
            # Even/Odd Signal
            even_odd = predictions["even_odd_recommendation"]
            if even_odd["confidence"] >= min_confidence:
                signal_data["signals"].append({
                    "contract_type": "EVEN_ODD",
                    "recommendation": even_odd["trade_type"],
                    "confidence": round(even_odd["confidence"], 2),
                    "action": f"BUY_{even_odd['trade_type']}",
                    "winning_digits": even_odd["winning_digits"],
                    "reason": even_odd["reason"]
                })
            
            # Over/Under Signal
            over_under = predictions["over_under_recommendation"]
            if over_under["confidence"] >= min_confidence:
                signal_data["signals"].append({
                    "contract_type": "OVER_UNDER",
                    "recommendation": over_under["trade_type"],
                    "confidence": round(over_under["confidence"], 2),
                    "action": f"BUY_{over_under['trade_type'].replace(' ', '_')}",
                    "winning_digits": over_under["winning_digits"],
                    "reason": over_under["reason"]
                })
            
            # Match/Differ Signal
            match_differ = predictions["match_differ_recommendation"]
            if match_differ["match_confidence"] >= min_confidence:
                signal_data["signals"].append({
                    "contract_type": "MATCH_DIFFER",
                    "recommendation": f"MATCH_{match_differ['match_digit']}",
                    "confidence": round(match_differ["match_confidence"], 2),
                    "action": f"BUY_MATCH_{match_differ['match_digit']}",
                    "target_digit": match_differ["match_digit"],
                    "reason": match_differ["match_reason"]
                })
            
            if signal_data["signals"]:
                signals.append(signal_data)
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "parameters": {
                "symbols": symbols_list,
                "tick_count": tick_count,
                "min_confidence": min_confidence
            },
            "signals": signals,
            "total_signals": sum(len(s["signals"]) for s in signals)
        }
        
    except Exception as e:
        logger.error(f"Error getting trading signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/market-status", dependencies=[Depends(verify_api_token)])
async def get_market_status():
    """Get real-time market status and data availability for bots"""
    try:
        market_status = []
        
        for market in VOLATILITY_INDICES:
            symbol = market["symbol"]
            ticks = tick_storage.get(symbol, [])
            
            if ticks:
                latest_tick = ticks[-1]
                status = {
                    "symbol": symbol,
                    "name": market["name"],
                    "status": "ACTIVE",
                    "latest_price": latest_tick["price"],
                    "latest_digit": latest_tick["last_digit"],
                    "last_update": latest_tick["timestamp"],
                    "available_ticks": len(ticks),
                    "data_quality": "GOOD" if len(ticks) >= 50 else "LIMITED"
                }
            else:
                status = {
                    "symbol": symbol,
                    "name": market["name"],
                    "status": "NO_DATA",
                    "latest_price": None,
                    "latest_digit": None,
                    "last_update": None,
                    "available_ticks": 0,
                    "data_quality": "NONE"
                }
            
            market_status.append(status)
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "markets": market_status,
            "total_markets": len(market_status),
            "active_markets": len([m for m in market_status if m["status"] == "ACTIVE"])
        }
        
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/generate-token")
async def generate_api_token(bot_name: str, duration_days: int = 365):
    """Generate a new API token for bot access (protected endpoint)"""
    try:
        # In production, this should be protected by admin authentication
        token = f"bot_token_{secrets.token_urlsafe(16)}"
        
        API_TOKENS[token] = {
            "name": bot_name,
            "permissions": ["read", "analysis"],
            "created": datetime.utcnow(),
            "expires": datetime.utcnow() + timedelta(days=duration_days)
        }
        
        return {
            "status": "success",
            "token": token,
            "bot_name": bot_name,
            "expires": API_TOKENS[token]["expires"].isoformat(),
            "permissions": API_TOKENS[token]["permissions"]
        }
        
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# WAKHUNGU28AI BOT MANAGEMENT ENDPOINTS - Web Service Integration
# =============================================================================

@api_router.post("/bot/create")
async def create_bot(request: BotCreateRequest):
    """Create a new Wakhungu28Ai bot instance"""
    try:
        # Create bot configuration
        config = BotConfig(
            bot_name=request.bot_name,
            initial_balance=request.initial_balance,
            deriv_api_token=request.deriv_api_token,
            min_confidence=request.min_confidence,
            active_markets=request.active_markets
        )
        
        # Store bot config in database
        await db.bot_configs.insert_one(config.dict())
        
        # Create bot service instance
        analysis_api_url = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').replace('//', '//').rstrip('/')
        bot_token = "bot_token_demo_123"  # Use existing demo token
        
        bot_id = await create_bot_instance(config, analysis_api_url, bot_token)
        
        return {
            "status": "success",
            "message": "Wakhungu28Ai bot created successfully",
            "bot_id": bot_id,
            "config": config.dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/{bot_id}/start")
async def start_bot(bot_id: str):
    """Start a Wakhungu28Ai bot instance"""
    try:
        success = await start_bot_instance(bot_id)
        
        if success:
            # Update bot status in database
            await db.bot_configs.update_one(
                {"id": bot_id},
                {"$set": {"is_active": True, "updated_at": datetime.utcnow()}}
            )
            
            return {
                "status": "success",
                "message": f"Bot {bot_id} started successfully",
                "bot_id": bot_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to start bot")
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bot/{bot_id}/stop")
async def stop_bot(bot_id: str):
    """Stop a Wakhungu28Ai bot instance"""
    try:
        success = await stop_bot_instance(bot_id)
        
        if success:
            # Update bot status in database
            await db.bot_configs.update_one(
                {"id": bot_id},
                {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
            )
            
            return {
                "status": "success",
                "message": f"Bot {bot_id} stopped successfully",
                "bot_id": bot_id
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to stop bot")
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bot/{bot_id}/status")
async def get_bot_status_endpoint(bot_id: str):
    """Get status of a Wakhungu28Ai bot instance"""
    try:
        status = await get_bot_status(bot_id)
        return {
            "status": "success",
            "bot_status": status.dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting bot status for {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/bot/{bot_id}/config")
async def update_bot_config(bot_id: str, request: BotUpdateRequest):
    """Update bot configuration"""
    try:
        # Update configuration in database
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.bot_configs.update_one(
            {"id": bot_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Bot not found")
        
        return {
            "status": "success",
            "message": f"Bot {bot_id} configuration updated",
            "updated_fields": list(update_data.keys())
        }
        
    except Exception as e:
        logger.error(f"Error updating bot config for {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/bot/{bot_id}")
async def delete_bot(bot_id: str):
    """Delete a Wakhungu28Ai bot instance"""
    try:
        # Delete from service
        success = await delete_bot_instance(bot_id)
        
        # Delete from database
        await db.bot_configs.delete_one({"id": bot_id})
        await db.bot_trades.delete_many({"bot_id": bot_id})
        
        return {
            "status": "success",
            "message": f"Bot {bot_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting bot {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bots")
async def list_bots():
    """List all bot instances"""
    try:
        # Get from database
        bot_configs = await db.bot_configs.find().to_list(100)
        
        # Get active bot IDs from service
        active_bot_ids = get_all_active_bots()
        
        bots = []
        for config in bot_configs:
            bot_info = {
                "id": config["id"],
                "bot_name": config["bot_name"],
                "is_active": config["id"] in active_bot_ids,
                "initial_balance": config["initial_balance"],
                "created_at": config["created_at"],
                "updated_at": config.get("updated_at", config["created_at"])
            }
            bots.append(bot_info)
        
        return {
            "status": "success",
            "bots": bots,
            "total_bots": len(bots),
            "active_bots": len(active_bot_ids)
        }
        
    except Exception as e:
        logger.error(f"Error listing bots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time tick updates"""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task to manage Deriv WebSocket connection
async def start_deriv_connection():
    """Start Deriv WebSocket connection and subscribe to symbols"""
    try:
        deriv_client = await get_deriv_client()
        
        # Add tick handler to store data
        deriv_client.add_tick_handler(store_tick_data)
        
        # Subscribe to all volatility indices
        for market in VOLATILITY_INDICES:
            try:
                await deriv_client.subscribe_to_ticks(market["symbol"])
                logger.info(f"Subscribed to {market['symbol']}")
                await asyncio.sleep(1)  # Avoid rate limiting
            except Exception as e:
                logger.error(f"Failed to subscribe to {market['symbol']}: {e}")
        
        # Keep connection alive
        while deriv_client.is_connected:
            await asyncio.sleep(30)  # Send ping every 30 seconds
            try:
                await deriv_client._send_ping()
            except Exception as e:
                logger.error(f"Failed to send ping: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in Deriv connection: {e}")
        # Retry connection after 10 seconds
        await asyncio.sleep(10)
        asyncio.create_task(start_deriv_connection())

@app.on_event("startup")
async def startup_event():
    """Initialize Deriv connection on startup"""
    logger.info("🚀 Starting Wakhungu28Ai Trading Platform...")
    logger.info("📡 Initializing Deriv WebSocket connection...")
    
    # Start Deriv connection in background
    asyncio.create_task(start_deriv_connection())
    
    logger.info("✅ Wakhungu28Ai Trading Platform started successfully!")
    logger.info("🌐 Web interface: Access your bot through the web dashboard")
    logger.info("🤖 API: Bot management endpoints available at /api/bot/*")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Wakhungu28Ai Trading Platform...")
    
    try:
        # Stop all active bots
        active_bot_ids = get_all_active_bots()
        for bot_id in active_bot_ids:
            try:
                await stop_bot_instance(bot_id)
                logger.info(f"Stopped bot: {bot_id}")
            except:
                pass
        
        # Close Deriv connection
        from deriv_client import deriv_client
        if deriv_client:
            await deriv_client.disconnect()
    except:
        pass
    
    # Close MongoDB connection
    client.close()
    
    logger.info("✅ Wakhungu28Ai Trading Platform shutdown complete")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
