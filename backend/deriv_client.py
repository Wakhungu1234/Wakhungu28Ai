import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class DerivWebSocketClient:
    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.environ.get('DERIV_API_TOKEN')
        self.websocket = None
        self.is_connected = False
        self.is_authorized = False
        self.subscriptions = {}
        self.tick_handlers = []
        self.ping_task = None
        
    async def connect(self):
        """Connect to Deriv WebSocket API"""
        try:
            uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"
            self.websocket = await websockets.connect(uri)
            self.is_connected = True
            logger.info("✅ Connected to Deriv WebSocket")
            
            # Start message handling
            asyncio.create_task(self._handle_messages())
            
            # Authorize if token is provided
            if self.api_token:
                await self._authorize()
            
            # Start ping task
            self.ping_task = asyncio.create_task(self._ping_loop())
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Deriv: {e}")
            self.is_connected = False
            raise
    
    async def _authorize(self):
        """Authorize with Deriv API"""
        try:
            auth_request = {
                "authorize": self.api_token
            }
            await self._send_request(auth_request)
        except Exception as e:
            logger.error(f"❌ Authorization failed: {e}")
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ Deriv WebSocket connection closed")
            self.is_connected = False
            self.is_authorized = False
        except Exception as e:
            logger.error(f"❌ Error in message handler: {e}")
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming message from Deriv"""
        try:
            # Handle authorization response
            if 'authorize' in data:
                if data.get('authorize'):
                    self.is_authorized = True
                    logger.info("✅ Successfully authorized with Deriv API")
                else:
                    logger.error("❌ Authorization failed")
                    if 'error' in data:
                        logger.error(f"Error: {data['error']}")
            
            # Handle tick data
            elif 'tick' in data:
                await self._handle_tick_data(data['tick'])
            
            # Handle subscription responses
            elif 'msg_type' in data:
                if data['msg_type'] == 'tick':
                    await self._handle_tick_data(data['tick'])
                elif data['msg_type'] == 'subscription':
                    symbol = data.get('echo_req', {}).get('ticks')
                    if symbol:
                        self.subscriptions[symbol] = data.get('subscription', {}).get('id')
                        logger.info(f"✅ Subscribed to {symbol}")
            
            # Handle errors
            elif 'error' in data:
                error = data['error']
                logger.error(f"❌ Deriv API Error: {error.get('message', 'Unknown error')}")
                
                # Handle "Already subscribed" error gracefully
                if error.get('code') == 'AlreadySubscribed':
                    logger.info("ℹ️ Already subscribed to this symbol")
                
        except Exception as e:
            logger.error(f"❌ Error processing Deriv message: {e}")
    
    async def _handle_tick_data(self, tick_data: Dict[str, Any]):
        """Process tick data and call handlers"""
        try:
            # Extract tick information
            symbol = tick_data.get('symbol', '')
            quote = tick_data.get('quote', 0)
            epoch = tick_data.get('epoch', 0)
            
            # Calculate last digit
            price_str = str(quote)
            last_digit = int(price_str[-1]) if price_str[-1].isdigit() else 0
            
            # Create standardized tick object
            tick_obj = {
                'symbol': symbol,
                'price': quote,
                'timestamp': datetime.fromtimestamp(epoch).isoformat(),
                'epoch': epoch,
                'last_digit': last_digit
            }
            
            # Call all registered tick handlers
            for handler in self.tick_handlers:
                try:
                    await handler(tick_obj)
                except Exception as e:
                    logger.error(f"❌ Error in tick handler: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Error handling tick data: {e}")
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send request to Deriv WebSocket"""
        if not self.is_connected or not self.websocket:
            raise Exception("Not connected to Deriv WebSocket")
        
        try:
            message = json.dumps(request)
            await self.websocket.send(message)
        except Exception as e:
            logger.error(f"❌ Failed to send request: {e}")
            raise
    
    async def subscribe_to_ticks(self, symbol: str):
        """Subscribe to tick stream for a symbol"""
        try:
            # Check if already subscribed
            if symbol in self.subscriptions:
                logger.info(f"ℹ️ Already subscribed to {symbol}")
                return
            
            request = {
                "ticks": symbol,
                "subscribe": 1
            }
            
            await self._send_request(request)
            logger.info(f"📡 Subscribing to {symbol} ticks...")
            
        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {symbol}: {e}")
    
    async def unsubscribe_from_ticks(self, symbol: str):
        """Unsubscribe from tick stream"""
        if symbol not in self.subscriptions:
            return
        
        try:
            subscription_id = self.subscriptions[symbol]
            request = {
                "forget": subscription_id
            }
            
            await self._send_request(request)
            del self.subscriptions[symbol]
            logger.info(f"🔇 Unsubscribed from {symbol}")
            
        except Exception as e:
            logger.error(f"❌ Failed to unsubscribe from {symbol}: {e}")
    
    def add_tick_handler(self, handler: Callable):
        """Add a tick data handler function"""
        self.tick_handlers.append(handler)
    
    def remove_tick_handler(self, handler: Callable):
        """Remove a tick data handler function"""
        if handler in self.tick_handlers:
            self.tick_handlers.remove(handler)
    
    async def _ping_loop(self):
        """Send periodic ping to keep connection alive"""
        while self.is_connected:
            try:
                await asyncio.sleep(30)  # Ping every 30 seconds
                if self.is_connected:
                    await self._send_ping()
            except Exception as e:
                logger.error(f"❌ Ping error: {e}")
                break
    
    async def _send_ping(self):
        """Send ping to server"""
        try:
            ping_request = {"ping": 1}
            await self._send_request(ping_request)
        except Exception as e:
            logger.error(f"❌ Failed to send ping: {e}")
    
    async def disconnect(self):
        """Disconnect from Deriv WebSocket"""
        try:
            self.is_connected = False
            self.is_authorized = False
            
            # Cancel ping task
            if self.ping_task:
                self.ping_task.cancel()
            
            # Close all subscriptions
            for symbol in list(self.subscriptions.keys()):
                await self.unsubscribe_from_ticks(symbol)
            
            # Close WebSocket connection
            if self.websocket:
                await self.websocket.close()
                
            logger.info("🔌 Disconnected from Deriv WebSocket")
            
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {e}")

# Global client instance
deriv_client: Optional[DerivWebSocketClient] = None

async def get_deriv_client() -> DerivWebSocketClient:
    """Get or create Deriv WebSocket client"""
    global deriv_client
    
    if deriv_client is None or not deriv_client.is_connected:
        api_token = os.environ.get('DERIV_API_TOKEN')
        deriv_client = DerivWebSocketClient(api_token)
        await deriv_client.connect()
    
    return deriv_client

async def close_deriv_client():
    """Close the global Deriv client"""
    global deriv_client
    if deriv_client:
        await deriv_client.disconnect()
        deriv_client = None