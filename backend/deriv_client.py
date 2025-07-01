import asyncio
import json
import websockets
import logging
from typing import Dict, List, Callable, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class DerivWebSocketClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.app_id = "1089"  # Generic app_id for basic functionality
        self.websocket = None
        self.is_connected = False
        self.is_authorized = False
        self.subscriptions = {}
        self.tick_handlers = []
        self.base_url = "wss://ws.derivws.com/websockets/v3"
        
    async def connect(self):
        """Connect to Deriv WebSocket API"""
        try:
            url = f"{self.base_url}?app_id={self.app_id}"
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            logger.info(f"Connected to Deriv WebSocket API with app_id: {self.app_id}")
            
            # Start listening for messages
            asyncio.create_task(self._listen())
            
            # Authorize the connection
            await self._authorize()
            
        except Exception as e:
            logger.error(f"Failed to connect to Deriv API: {e}")
            self.is_connected = False
            raise
    
    async def _authorize(self):
        """Authorize the WebSocket connection with API token"""
        try:
            authorize_message = json.dumps({
                "authorize": self.api_token
            })
            await self.websocket.send(authorize_message)
            logger.info("Sent authorization request")
        except Exception as e:
            logger.error(f"Failed to authorize: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            self.is_authorized = False
            logger.info("Disconnected from Deriv WebSocket API")
    
    async def _send_ping(self):
        """Send ping to keep connection alive"""
        if self.is_connected:
            ping_message = json.dumps({"ping": 1})
            await self.websocket.send(ping_message)
    
    async def _listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
            self.is_connected = False
            self.is_authorized = False
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {e}")
    
    async def _handle_message(self, data: dict):
        """Handle incoming WebSocket messages"""
        try:
            # Handle authorization response
            if 'authorize' in data:
                if data.get('authorize'):
                    self.is_authorized = True
                    logger.info("Successfully authorized with Deriv API")
                    # Start subscribing to tick data after authorization
                    await self._start_subscriptions()
                else:
                    logger.error("Authorization failed")
                    if 'error' in data:
                        logger.error(f"Authorization error: {data['error']}")
            
            # Handle balance response
            elif 'balance' in data:
                balance_data = data['balance']
                logger.info(f"💰 Account Balance: ${balance_data.get('balance', 0):.2f} {balance_data.get('currency', 'USD')}")
            
            # Handle buy response (real trade execution)
            elif 'buy' in data:
                buy_data = data['buy']
                contract_id = buy_data.get('contract_id')
                buy_price = buy_data.get('buy_price')
                logger.info(f"✅ REAL TRADE EXECUTED: Contract ID {contract_id}, Price: ${buy_price}")
            
            # Handle tick data
            elif 'tick' in data:
                tick_data = data['tick']
                await self._process_tick(tick_data)
            
            # Handle ping responses
            elif 'pong' in data:
                logger.debug("Received pong from server")
            
            # Handle errors
            elif 'error' in data:
                logger.error(f"Deriv API Error: {data['error']}")
            
            else:
                logger.debug(f"Received message: {data}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def _start_subscriptions(self):
        """Start subscriptions after successful authorization"""
        try:
            # Subscribe to all volatility indices (including 1-second indices)
            volatility_symbols = ['R_10', 'R_25', 'R_50', 'R_75', 'R_100', '1HZ10V', '1HZ25V', '1HZ50V', '1HZ75V', '1HZ100V']
            for symbol in volatility_symbols:
                if symbol not in self.subscriptions:
                    await self.subscribe_to_ticks(symbol)
                    await asyncio.sleep(0.5)  # Small delay between subscriptions
        except Exception as e:
            logger.error(f"Error starting subscriptions: {e}")
    
    async def _process_tick(self, tick_data: dict):
        """Process incoming tick data"""
        try:
            # Extract tick information
            symbol = tick_data.get('symbol', '')
            price = float(tick_data.get('quote', 0))
            epoch = int(tick_data.get('epoch', 0))
            timestamp = datetime.fromtimestamp(epoch)
            
            # Calculate last digit of the price (the rightmost digit)
            # Examples: 7678.08 -> last digit is 8, 6558.77 -> last digit is 7
            # Convert to string and get the last character, ignoring decimal points
            price_str = str(price).replace('.', '')  # Remove decimal point
            last_digit = int(price_str[-1])  # Get the last digit
            
            tick = {
                'symbol': symbol,
                'price': price,
                'timestamp': timestamp.isoformat(),
                'epoch': epoch,
                'last_digit': last_digit
            }
            
            logger.info(f"Processed tick for {symbol}: {price} -> digit {last_digit}")
            
            # Notify all tick handlers
            for handler in self.tick_handlers:
                try:
                    await handler(tick)
                except Exception as e:
                    logger.error(f"Error in tick handler: {e}")
                    
        except Exception as e:
            logger.error(f"Error processing tick: {e}")
    
    async def subscribe_to_ticks(self, symbol: str):
        """Subscribe to tick stream for a symbol"""
        try:
            if not self.is_authorized:
                logger.warning(f"Cannot subscribe to {symbol} - not authorized yet")
                return
                
            subscribe_message = json.dumps({
                "ticks": symbol,
                "subscribe": 1
            })
            
            await self.websocket.send(subscribe_message)
            self.subscriptions[symbol] = True
            logger.info(f"Subscribed to ticks for {symbol}")
            
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol}: {e}")
            raise
    
    async def unsubscribe_from_ticks(self, symbol: str):
        """Unsubscribe from tick stream"""
        try:
            if symbol in self.subscriptions:
                unsubscribe_message = json.dumps({
                    "forget_all": "ticks"
                })
                await self.websocket.send(unsubscribe_message)
                del self.subscriptions[symbol]
                logger.info(f"Unsubscribed from ticks for {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {symbol}: {e}")
    
    def add_tick_handler(self, handler: Callable):
        """Add a tick data handler"""
        self.tick_handlers.append(handler)
    
    def remove_tick_handler(self, handler: Callable):
        """Remove a tick data handler"""
        if handler in self.tick_handlers:
            self.tick_handlers.remove(handler)
    
    async def get_account_balance(self):
        """Get real account balance from Deriv API"""
        try:
            balance_message = json.dumps({
                "balance": 1,
                "subscribe": 1
            })
            await self.websocket.send(balance_message)
            logger.info("Requested account balance")
        except Exception as e:
            logger.error(f"Failed to get account balance: {e}")
    
    async def buy_contract(self, contract_type: str, symbol: str, stake: float, barrier: str = None):
        """Execute real trade on Deriv"""
        try:
            # Determine contract parameters based on signal
            if contract_type == "EVEN_ODD":
                if "EVEN" in barrier:
                    contract_params = {
                        "buy": 1,
                        "price": stake,
                        "parameters": {
                            "contract_type": "DIGITEVEN",
                            "symbol": symbol,
                            "duration": 1,
                            "duration_unit": "t",  # 1 tick
                            "currency": "USD"
                        }
                    }
                else:  # ODD
                    contract_params = {
                        "buy": 1,
                        "price": stake,
                        "parameters": {
                            "contract_type": "DIGITODD",
                            "symbol": symbol,
                            "duration": 1,
                            "duration_unit": "t",
                            "currency": "USD"
                        }
                    }
            elif contract_type == "OVER_UNDER":
                if "OVER" in barrier:
                    contract_params = {
                        "buy": 1,
                        "price": stake,
                        "parameters": {
                            "contract_type": "DIGITOVER",
                            "symbol": symbol,
                            "duration": 1,
                            "duration_unit": "t",
                            "barrier": "5",
                            "currency": "USD"
                        }
                    }
                else:  # UNDER
                    contract_params = {
                        "buy": 1,
                        "price": stake,
                        "parameters": {
                            "contract_type": "DIGITUNDER",
                            "symbol": symbol,
                            "duration": 1,
                            "duration_unit": "t",
                            "barrier": "5",
                            "currency": "USD"
                        }
                    }
            
            # Send real trade request
            await self.websocket.send(json.dumps(contract_params))
            logger.info(f"🚀 REAL TRADE EXECUTED: {contract_type} on {symbol} with ${stake}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute real trade: {e}")
            return False

# Global WebSocket client instance
deriv_client = None

async def get_deriv_client():
    """Get or create Deriv WebSocket client"""
    global deriv_client
    if deriv_client is None or not deriv_client.is_connected:
        api_token = os.environ.get('DERIV_API_KEY')
        if not api_token:
            raise ValueError("DERIV_API_KEY not found in environment")
        
        deriv_client = DerivWebSocketClient(api_token)
        await deriv_client.connect()
    
    return deriv_client