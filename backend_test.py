#!/usr/bin/env python3
import requests
import json
import time
import websocket
import threading
import sys
import os
from datetime import datetime

# Get the backend URL from the frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.strip().split('=')[1].strip('"\'')
    except Exception as e:
        print(f"Error reading frontend .env file: {e}")
        return None

# Base URL for API requests
BASE_URL = get_backend_url()
if not BASE_URL:
    print("Error: Could not determine backend URL from frontend/.env")
    sys.exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Using API URL: {API_URL}")

# Test data for bot creation with single market
TEST_BOT_CONFIG = {
    "api_token": "test_token_123",
    "stake_amount": 25.0,
    "take_profit": 750.0,
    "stop_loss": 300.0,
    "martingale_multiplier": 2.5,
    "max_martingale_steps": 4,
    "selected_markets": ["R_100"]
}

# Test data for bot creation with multiple markets
TEST_MULTI_MARKET_BOT_CONFIG = {
    "api_token": "test_token_456",
    "stake_amount": 15.0,
    "take_profit": 500.0,
    "stop_loss": 200.0,
    "martingale_multiplier": 2.0,
    "max_martingale_steps": 3,
    "selected_markets": ["R_100", "R_25", "R_50", "1HZ10V", "1HZ25V"]
}

# Test data for analysis request
TEST_ANALYSIS_REQUEST = {
    "symbol": "R_100",
    "contract_type": "even_odd",
    "tick_count": 100
}

# WebSocket connection for real-time data verification
ws_connected = False
ws_received_data = False
ws_messages = []
ws_tick_symbols = set()  # Track which symbols we've received tick data for

def on_ws_message(ws, message):
    global ws_received_data, ws_tick_symbols
    ws_received_data = True
    message_data = json.loads(message)
    ws_messages.append(message_data)
    
    # Track which symbols we're receiving tick data for
    if message_data.get('type') == 'tick_update':
        tick_data = message_data.get('data', {})
        if 'symbol' in tick_data:
            ws_tick_symbols.add(tick_data['symbol'])
    
    print(f"WebSocket received: {message[:100]}...")

def on_ws_error(ws, error):
    print(f"WebSocket error: {error}")

def on_ws_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_ws_open(ws):
    global ws_connected
    ws_connected = True
    print("WebSocket connection established")

def start_websocket():
    ws_url = f"{BASE_URL.replace('https://', 'wss://').replace('http://', 'ws://')}/api/ws"
    print(f"Connecting to WebSocket: {ws_url}")
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_ws_message,
        on_error=on_ws_error,
        on_close=on_ws_close,
        on_open=on_ws_open
    )
    
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    # Wait for connection to establish
    timeout = 10
    start_time = time.time()
    while not ws_connected and time.time() - start_time < timeout:
        time.sleep(0.5)
    
    return ws, ws_thread

def test_api_health():
    """Test the API health check endpoint"""
    print("\n=== Testing API Health Check ===")
    try:
        response = requests.get(f"{API_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, "API health check failed with non-200 status code"
        assert "message" in response.json(), "API response missing 'message' field"
        assert "Wakhungu28Ai Trading Bot API" in response.json()["message"], "API response message incorrect"
        
        print("✅ API Health Check: PASSED")
        return True
    except Exception as e:
        print(f"❌ API Health Check: FAILED - {str(e)}")
        return False

def test_markets_endpoint():
    """Test the markets endpoint"""
    print("\n=== Testing Markets Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/markets")
        print(f"Status Code: {response.status_code}")
        print(f"Response contains {len(response.json())} markets")
        
        assert response.status_code == 200, "Markets endpoint failed with non-200 status code"
        markets = response.json()
        assert len(markets) == 10, f"Expected 10 volatility indices, got {len(markets)}"
        
        # Check if all required volatility indices are present
        symbols = [market["symbol"] for market in markets]
        required_symbols = ["R_10", "R_25", "R_50", "R_75", "R_100", 
                           "1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V"]
        for symbol in required_symbols:
            assert symbol in symbols, f"Required symbol {symbol} not found in markets response"
        
        print("✅ Markets Endpoint: PASSED - All 10 volatility indices returned")
        return True
    except Exception as e:
        print(f"❌ Markets Endpoint: FAILED - {str(e)}")
        return False

def test_ticks_endpoint():
    """Test the ticks endpoint for R_100"""
    print("\n=== Testing Ticks Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/ticks/R_100")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response contains {data.get('count', 0)} ticks for {data.get('symbol', 'unknown')}")
            
            assert data["symbol"] == "R_100", f"Expected symbol R_100, got {data.get('symbol')}"
            
            # Note: In a real test, we would wait for ticks to accumulate
            # For this test, we'll just check the structure
            assert "ticks" in data, "Ticks data missing from response"
            assert "count" in data, "Count missing from response"
            
            print("✅ Ticks Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Ticks Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Ticks Endpoint: FAILED - {str(e)}")
        return False

def test_enhanced_quickstart_bot_creation():
    """Test the enhanced QuickStart API with ULTRA-FAST trading"""
    print("\n=== Testing Enhanced QuickStart API with ULTRA-FAST Trading ===")
    try:
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=TEST_BOT_CONFIG
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot creation failed"
            assert "bot_id" in data, "Bot ID missing from response"
            assert "bot_name" in data, "Bot name missing from response"
            assert "configuration" in data, "Bot configuration missing from response"
            
            # Verify ULTRA-FAST trading configuration
            config = data["configuration"]
            assert config["trade_interval"] == "0.5 seconds", f"Expected trade interval of 0.5 seconds, got {config.get('trade_interval')}"
            assert config["expected_trades_per_hour"] == 7200, f"Expected 7200 trades per hour, got {config.get('expected_trades_per_hour')}"
            
            # Store bot_id for later tests
            bot_id = data["bot_id"]
            
            print("✅ Enhanced QuickStart API: PASSED - ULTRA-FAST 0.5-second trading confirmed")
            return True, bot_id
        else:
            print(f"Response: {response.text}")
            print("❌ Enhanced QuickStart API: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Enhanced QuickStart API: FAILED - {str(e)}")
        return False, None

def test_multi_market_bot_creation():
    """Test creating a bot with multiple markets"""
    print("\n=== Testing Multi-Market Bot Creation ===")
    try:
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=TEST_MULTI_MARKET_BOT_CONFIG
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot creation failed"
            
            # Verify multiple markets configuration
            config = data["configuration"]
            selected_markets = config.get("selected_markets", [])
            assert len(selected_markets) == len(TEST_MULTI_MARKET_BOT_CONFIG["selected_markets"]), \
                f"Expected {len(TEST_MULTI_MARKET_BOT_CONFIG['selected_markets'])} markets, got {len(selected_markets)}"
            
            for market in TEST_MULTI_MARKET_BOT_CONFIG["selected_markets"]:
                assert market in selected_markets, f"Market {market} not found in response"
            
            # Store bot_id for later tests
            bot_id = data["bot_id"]
            
            print("✅ Multi-Market Bot Creation: PASSED - Successfully created bot with multiple markets")
            return True, bot_id
        else:
            print(f"Response: {response.text}")
            print("❌ Multi-Market Bot Creation: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Multi-Market Bot Creation: FAILED - {str(e)}")
        return False, None

def test_enhanced_analysis_engine():
    """Test the enhanced analysis engine"""
    print("\n=== Testing Enhanced Analysis Engine ===")
    try:
        response = requests.post(
            f"{API_URL}/analysis",
            json=TEST_ANALYSIS_REQUEST
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Analysis response for {data.get('symbol')}: {json.dumps(data, indent=2)}")
            
            assert "analysis" in data, "Analysis data missing from response"
            analysis = data["analysis"]
            
            # Verify analysis contains required components
            assert "predictions" in analysis, "Predictions missing from analysis"
            predictions = analysis["predictions"]
            
            # Check for confidence levels and recommendations
            assert "even_odd_recommendation" in predictions, "Even/Odd recommendation missing"
            assert "over_under_recommendation" in predictions, "Over/Under recommendation missing"
            
            # Verify confidence levels
            even_odd = predictions["even_odd_recommendation"]
            over_under = predictions["over_under_recommendation"]
            
            assert "confidence" in even_odd, "Confidence level missing from Even/Odd recommendation"
            assert "confidence" in over_under, "Confidence level missing from Over/Under recommendation"
            assert "trade_type" in even_odd, "Trade type missing from Even/Odd recommendation"
            assert "trade_type" in over_under, "Trade type missing from Over/Under recommendation"
            
            print("✅ Enhanced Analysis Engine: PASSED - Returns confidence levels and trading recommendations")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Enhanced Analysis Engine: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Enhanced Analysis Engine: FAILED - {str(e)}")
        return False

def test_bots_list():
    """Test the bots list endpoint"""
    print("\n=== Testing Bots List Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/bots")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            bots = response.json()
            print(f"Response contains {len(bots)} bots")
            
            if len(bots) > 0:
                print(f"First bot: {json.dumps(bots[0], indent=2)}")
            
            # Check if bots have the required fields
            for bot in bots:
                assert "id" in bot, "Bot ID missing"
                assert "name" in bot, "Bot name missing"
                assert "status" in bot, "Bot status missing"
                assert "total_trades" in bot, "Total trades missing"
                assert "win_rate" in bot, "Win rate missing"
                assert "total_profit" in bot, "Total profit missing"
            
            print("✅ Bots List Endpoint: PASSED")
            return True, bots[0]["id"] if bots else None
        else:
            print(f"Response: {response.text}")
            print("❌ Bots List Endpoint: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Bots List Endpoint: FAILED - {str(e)}")
        return False, None

def test_stop_bot(bot_id):
    """Test stopping a bot"""
    if not bot_id:
        print("❌ Stop Bot Test: SKIPPED - No bot ID available")
        return False
    
    print(f"\n=== Testing Stop Bot Endpoint for Bot ID: {bot_id} ===")
    try:
        response = requests.delete(f"{API_URL}/bots/{bot_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot stopping failed"
            assert "message" in data, "Response message missing"
            
            # Verify bot status is updated
            time.sleep(1)  # Wait for status to update
            bot_response = requests.get(f"{API_URL}/bots")
            if bot_response.status_code == 200:
                bots = bot_response.json()
                for bot in bots:
                    if bot["id"] == bot_id:
                        assert bot["status"] == "STOPPED", f"Expected bot status STOPPED, got {bot['status']}"
                        print("✅ Bot status correctly updated to STOPPED")
            
            print("✅ Stop Bot Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Stop Bot Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Stop Bot Endpoint: FAILED - {str(e)}")
        return False

def test_bot_trades(bot_id):
    """Test getting bot trade history"""
    if not bot_id:
        print("❌ Bot Trades Test: SKIPPED - No bot ID available")
        return False
    
    print(f"\n=== Testing Bot Trades Endpoint for Bot ID: {bot_id} ===")
    try:
        response = requests.get(f"{API_URL}/bots/{bot_id}/trades")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response contains {data.get('count', 0)} trades for bot {data.get('bot_id')}")
            
            assert data["bot_id"] == bot_id, f"Expected bot ID {bot_id}, got {data.get('bot_id')}"
            assert "trades" in data, "Trades missing from response"
            assert "count" in data, "Count missing from response"
            
            print("✅ Bot Trades Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Bot Trades Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Bot Trades Endpoint: FAILED - {str(e)}")
        return False

def test_websocket_connection():
    """Test WebSocket connection for real-time data"""
    print("\n=== Testing WebSocket Connection ===")
    try:
        ws, ws_thread = start_websocket()
        
        # Wait for data to be received
        timeout = 20
        start_time = time.time()
        while not ws_received_data and time.time() - start_time < timeout:
            time.sleep(1)
            print("Waiting for WebSocket data...")
        
        if ws_received_data:
            print(f"Received {len(ws_messages)} WebSocket messages")
            if len(ws_messages) > 0:
                print(f"Sample message type: {ws_messages[0].get('type', 'unknown')}")
                
            # Check if we're receiving tick data from multiple markets
            print(f"Received tick data from {len(ws_tick_symbols)} different markets: {ws_tick_symbols}")
            
            print("✅ WebSocket Connection: PASSED")
            return True
        else:
            print("❌ WebSocket Connection: FAILED - No data received within timeout")
            return False
    except Exception as e:
        print(f"❌ WebSocket Connection: FAILED - {str(e)}")
        return False

def test_error_handling():
    """Test error handling for invalid endpoints and data"""
    print("\n=== Testing Error Handling ===")
    
    # Test 1: Invalid endpoint
    try:
        response = requests.get(f"{API_URL}/invalid_endpoint")
        print(f"Invalid endpoint - Status Code: {response.status_code}")
        assert response.status_code == 404, f"Expected 404 for invalid endpoint, got {response.status_code}"
        print("✅ Invalid endpoint test: PASSED")
    except Exception as e:
        print(f"❌ Invalid endpoint test: FAILED - {str(e)}")
        return False
    
    # Test 2: Invalid symbol for ticks
    try:
        response = requests.get(f"{API_URL}/ticks/INVALID_SYMBOL")
        print(f"Invalid symbol - Status Code: {response.status_code}")
        assert response.status_code == 404, f"Expected 404 for invalid symbol, got {response.status_code}"
        print("✅ Invalid symbol test: PASSED")
    except Exception as e:
        print(f"❌ Invalid symbol test: FAILED - {str(e)}")
        return False
    
    # Test 3: Invalid bot configuration
    try:
        invalid_config = {
            "api_token": "test_token",
            "stake_amount": -10.0,  # Invalid negative stake
            "take_profit": 100.0,
            "stop_loss": 50.0
        }
        response = requests.post(f"{API_URL}/bots/quickstart", json=invalid_config)
        print(f"Invalid bot config - Status Code: {response.status_code}")
        assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid config, got {response.status_code}"
        print("✅ Invalid bot config test: PASSED")
    except Exception as e:
        print(f"❌ Invalid bot config test: FAILED - {str(e)}")
        return False
    
    print("✅ Error Handling: PASSED")
    return True

def run_all_tests():
    """Run all API tests and return results"""
    results = {}
    bot_id = None
    
    # Test 1: API Health Check
    results["API Health Check"] = test_api_health()
    
    # Test 2: Markets Endpoint - Verify all 10 volatility indices
    results["Market Data Endpoints"] = test_markets_endpoint() and test_ticks_endpoint()
    
    # Test 3: Enhanced QuickStart API with ULTRA-FAST Trading
    quickstart_result, quickstart_bot_id = test_enhanced_quickstart_bot_creation()
    results["Enhanced QuickStart API"] = quickstart_result
    if quickstart_bot_id:
        bot_id = quickstart_bot_id
    
    # Test 4: Multi-Market Bot Creation
    multi_market_result, multi_market_bot_id = test_multi_market_bot_creation()
    results["Multi-Market Bot Creation"] = multi_market_result
    if multi_market_bot_id and not bot_id:
        bot_id = multi_market_bot_id
    
    # Test 5: Enhanced Analysis Engine
    results["Enhanced Analysis Engine"] = test_enhanced_analysis_engine()
    
    # Test 6: Bot Management
    bots_list_result, list_bot_id = test_bots_list()
    if list_bot_id and not bot_id:
        bot_id = list_bot_id
    
    # Test bot management functions if we have a bot ID
    if bot_id:
        stop_bot_result = test_stop_bot(bot_id)
        bot_trades_result = test_bot_trades(bot_id)
        results["Bot Management"] = bots_list_result and stop_bot_result and bot_trades_result
    else:
        results["Bot Management"] = bots_list_result
    
    # Test 7: Real-time WebSocket Connection
    results["Real-time WebSocket Connection"] = test_websocket_connection()
    
    # Test 8: Error Handling
    results["Error Handling"] = test_error_handling()
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    return results

if __name__ == "__main__":
    print(f"Starting backend API tests at {datetime.now().isoformat()}")
    print("Testing ULTRA-FAST Wakhungu28Ai Trading Bot Backend")
    run_all_tests()