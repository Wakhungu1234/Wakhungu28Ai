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
    BotConfig, BotStatus, BotTrade, BotCreateRequest, BotUpdateRequest
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

# In-memory storage for tick data (in production, use Redis or similar)
tick_storage: Dict[str, List[Dict]] = {}
active_websockets: List[WebSocket] = []

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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
