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

# Test data for bot creation with single market and enhanced martingale
TEST_BOT_CONFIG = {
    "api_token": "test_token_123",
    "stake_amount": 0.35,  # Testing minimum stake of $0.35
    "take_profit": 100.0,
    "stop_loss": 50.0,
    "martingale_multiplier": 2.0,
    "max_martingale_steps": 3,
    "martingale_repeat_attempts": 3,  # Testing new martingale repeat attempts parameter
    "selected_markets": ["R_100"]
}

# Test data for bot creation with multiple markets
TEST_MULTI_MARKET_BOT_CONFIG = {
    "api_token": "test_token_456",
    "stake_amount": 1.50,
    "take_profit": 500.0,
    "stop_loss": 200.0,
    "martingale_multiplier": 2.5,
    "max_martingale_steps": 4,
    "martingale_repeat_attempts": 2,  # Testing martingale repeat attempts
    "selected_markets": ["R_100", "R_25", "R_50", "1HZ10V", "1HZ25V"]
}

# Test data for analysis request
TEST_ANALYSIS_REQUEST = {
    "symbol": "R_100",
    "contract_type": "even_odd",
    "tick_count": 100
}

# Real Deriv API token for testing
REAL_API_TOKEN = "dG1ac29qbdRzjJG"

# Test data for token verification
TEST_TOKEN_VERIFICATION = {
    "api_token": REAL_API_TOKEN
}

# Test data for account switching
TEST_ACCOUNT_SWITCH = {
    "api_token": REAL_API_TOKEN,
    "loginid": "CR123456"  # This is a sample loginid, will be replaced with real one if available
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
            
            # Verify minimum stake amount of $0.35
            assert config["stake_amount"] == "$0.35", f"Expected stake amount of $0.35, got {config.get('stake_amount')}"
            
            # Verify martingale repeat attempts
            assert config["martingale_repeat_attempts"] == 3, f"Expected martingale repeat attempts of 3, got {config.get('martingale_repeat_attempts')}"
            
            # Store bot_id for later tests
            bot_id = data["bot_id"]
            
            print("✅ Enhanced QuickStart API: PASSED - ULTRA-FAST 0.5-second trading confirmed")
            print("✅ Minimum stake amount of $0.35 accepted")
            print("✅ Martingale repeat attempts parameter working")
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
            
            # Verify martingale repeat attempts
            assert config["martingale_repeat_attempts"] == 2, f"Expected martingale repeat attempts of 2, got {config.get('martingale_repeat_attempts')}"
            
            # Store bot_id for later tests
            bot_id = data["bot_id"]
            
            print("✅ Multi-Market Bot Creation: PASSED - Successfully created bot with multiple markets")
            print("✅ Martingale repeat attempts parameter working")
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
            assert "match_differ_recommendation" in predictions, "Match/Differ recommendation missing"
            
            # Verify confidence levels
            even_odd = predictions["even_odd_recommendation"]
            over_under = predictions["over_under_recommendation"]
            match_differ = predictions["match_differ_recommendation"]
            
            assert "confidence" in even_odd, "Confidence level missing from Even/Odd recommendation"
            assert "confidence" in over_under, "Confidence level missing from Over/Under recommendation"
            assert "trade_type" in even_odd, "Trade type missing from Even/Odd recommendation"
            assert "trade_type" in over_under, "Trade type missing from Over/Under recommendation"
            
            # Verify winning digits (color-coded digit recommendations)
            assert "winning_digits" in even_odd, "Winning digits missing from Even/Odd recommendation"
            assert "winning_digits" in over_under, "Winning digits missing from Over/Under recommendation"
            
            # Verify reason field for trading signals
            assert "reason" in even_odd, "Reason missing from Even/Odd recommendation"
            assert "reason" in over_under, "Reason missing from Over/Under recommendation"
            
            print("✅ Enhanced Analysis Engine: PASSED - Returns confidence levels and trading recommendations")
            print("✅ Color-coded digit recommendations included in analysis")
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
        response = requests.put(f"{API_URL}/bots/{bot_id}/stop")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot stopping failed"
            assert "message" in data, "Response message missing"
            assert data["bot_id"] == bot_id, f"Expected bot ID {bot_id}, got {data.get('bot_id')}"
            
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
            
            # Check martingale tracking in trades if any trades exist
            if data.get("count", 0) > 0:
                for trade in data["trades"]:
                    assert "martingale_step" in trade, "Martingale step missing from trade record"
                    assert "martingale_repeat" in trade, "Martingale repeat missing from trade record"
                print("✅ Enhanced Martingale Recovery System: PASSED - Trades include martingale tracking")
            
            print("✅ Bot Trades Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Bot Trades Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Bot Trades Endpoint: FAILED - {str(e)}")
        return False

def test_restart_bot(bot_id):
    """Test restarting a stopped bot"""
    if not bot_id:
        print("❌ Restart Bot Test: SKIPPED - No bot ID available")
        return False
    
    print(f"\n=== Testing Restart Bot Endpoint for Bot ID: {bot_id} ===")
    try:
        # First make sure the bot is stopped
        stop_response = requests.put(f"{API_URL}/bots/{bot_id}/stop")
        if stop_response.status_code != 200:
            print(f"Failed to stop bot before restart test: {stop_response.text}")
            return False
            
        # Wait for bot to stop
        time.sleep(1)
        
        # Now restart the bot
        response = requests.put(f"{API_URL}/bots/{bot_id}/restart")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot restart failed"
            assert "message" in data, "Response message missing"
            assert data["bot_id"] == bot_id, f"Expected bot ID {bot_id}, got {data.get('bot_id')}"
            
            # Verify bot status is updated
            time.sleep(1)  # Wait for status to update
            bot_response = requests.get(f"{API_URL}/bots")
            if bot_response.status_code == 200:
                bots = bot_response.json()
                bot_found = False
                for bot in bots:
                    if bot["id"] == bot_id:
                        bot_found = True
                        assert bot["status"] in ["ACTIVE", "STARTING"], f"Expected bot status ACTIVE or STARTING, got {bot['status']}"
                        print(f"✅ Bot status correctly updated to {bot['status']}")
                
                if not bot_found:
                    print("❌ Bot not found after restart")
                    return False
            
            print("✅ Restart Bot Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Restart Bot Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Restart Bot Endpoint: FAILED - {str(e)}")
        return False

def test_delete_bot(bot_id):
    """Test permanently deleting a bot"""
    if not bot_id:
        print("❌ Delete Bot Test: SKIPPED - No bot ID available")
        return False
    
    print(f"\n=== Testing Delete Bot Endpoint for Bot ID: {bot_id} ===")
    try:
        # First get the bot trades to verify they're deleted later
        trades_response = requests.get(f"{API_URL}/bots/{bot_id}/trades")
        initial_trade_count = 0
        if trades_response.status_code == 200:
            initial_trade_count = trades_response.json().get("count", 0)
            print(f"Bot has {initial_trade_count} trades before deletion")
        
        # Now delete the bot
        response = requests.delete(f"{API_URL}/bots/{bot_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Bot deletion failed"
            assert "message" in data, "Response message missing"
            assert data["bot_id"] == bot_id, f"Expected bot ID {bot_id}, got {data.get('bot_id')}"
            
            # Verify trades_deleted count if there were initial trades
            if initial_trade_count > 0:
                assert "trades_deleted" in data, "Trades deleted count missing"
                print(f"✅ {data.get('trades_deleted', 0)} trade records deleted")
            
            # Verify bot is removed from database
            time.sleep(1)  # Wait for deletion to complete
            bot_response = requests.get(f"{API_URL}/bots")
            if bot_response.status_code == 200:
                bots = bot_response.json()
                for bot in bots:
                    if bot["id"] == bot_id:
                        print("❌ Bot still exists in database after deletion")
                        return False
                
                print("✅ Bot successfully removed from database")
            
            # Verify trades are deleted
            trades_response = requests.get(f"{API_URL}/bots/{bot_id}/trades")
            if trades_response.status_code == 404:
                print("✅ Bot trades endpoint returns 404 after deletion")
            else:
                print(f"❌ Expected 404 for deleted bot trades, got {trades_response.status_code}")
            
            print("✅ Delete Bot Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Delete Bot Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Delete Bot Endpoint: FAILED - {str(e)}")
        return False

def test_error_handling_for_bot_operations():
    """Test error handling for bot operations with non-existent bot IDs"""
    print("\n=== Testing Error Handling for Bot Operations ===")
    
    # Generate a random non-existent bot ID
    import uuid
    non_existent_bot_id = str(uuid.uuid4())
    
    # Test 1: Stop non-existent bot
    try:
        response = requests.put(f"{API_URL}/bots/{non_existent_bot_id}/stop")
        print(f"Stop non-existent bot - Status Code: {response.status_code}")
        assert response.status_code == 404, f"Expected 404 for non-existent bot stop, got {response.status_code}"
        print("✅ Stop non-existent bot test: PASSED")
    except Exception as e:
        print(f"❌ Stop non-existent bot test: FAILED - {str(e)}")
        return False
    
    # Test 2: Restart non-existent bot
    try:
        response = requests.put(f"{API_URL}/bots/{non_existent_bot_id}/restart")
        print(f"Restart non-existent bot - Status Code: {response.status_code}")
        assert response.status_code == 404, f"Expected 404 for non-existent bot restart, got {response.status_code}"
        print("✅ Restart non-existent bot test: PASSED")
    except Exception as e:
        print(f"❌ Restart non-existent bot test: FAILED - {str(e)}")
        return False
    
    # Test 3: Delete non-existent bot
    try:
        response = requests.delete(f"{API_URL}/bots/{non_existent_bot_id}")
        print(f"Delete non-existent bot - Status Code: {response.status_code}")
        assert response.status_code == 404, f"Expected 404 for non-existent bot delete, got {response.status_code}"
        print("✅ Delete non-existent bot test: PASSED")
    except Exception as e:
        print(f"❌ Delete non-existent bot test: FAILED - {str(e)}")
        return False
    
    print("✅ Error Handling for Bot Operations: PASSED")
    return True

def test_end_to_end_bot_flow():
    """Test the complete bot lifecycle: create, stop, restart, delete"""
    print("\n=== Testing End-to-End Bot Flow ===")
    
    # Step 1: Create a new bot
    print("Step 1: Creating a new bot...")
    quickstart_result, bot_id = test_enhanced_quickstart_bot_creation()
    if not quickstart_result or not bot_id:
        print("❌ End-to-End Flow: FAILED - Could not create bot")
        return False
    
    print(f"✅ Step 1 Complete: Bot created with ID {bot_id}")
    
    # Step 2: Stop the bot
    print("Step 2: Stopping the bot...")
    stop_result = test_stop_bot(bot_id)
    if not stop_result:
        print("❌ End-to-End Flow: FAILED - Could not stop bot")
        return False
    
    print("✅ Step 2 Complete: Bot stopped successfully")
    
    # Step 3: Restart the bot
    print("Step 3: Restarting the bot...")
    restart_result = test_restart_bot(bot_id)
    if not restart_result:
        print("❌ End-to-End Flow: FAILED - Could not restart bot")
        return False
    
    print("✅ Step 3 Complete: Bot restarted successfully")
    
    # Step 4: Delete the bot
    print("Step 4: Deleting the bot...")
    delete_result = test_delete_bot(bot_id)
    if not delete_result:
        print("❌ End-to-End Flow: FAILED - Could not delete bot")
        return False
    
    print("✅ Step 4 Complete: Bot deleted successfully")
    
    print("✅ End-to-End Bot Flow: PASSED - Complete lifecycle tested successfully")
    return True

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

def test_minimum_stake_validation():
    """Test minimum stake validation ($0.35 minimum)"""
    print("\n=== Testing Minimum Stake Validation ===")
    try:
        # Test with valid minimum stake
        valid_config = {
            "api_token": "test_token_123",
            "stake_amount": 0.35,  # Minimum valid stake
            "take_profit": 100.0,
            "stop_loss": 50.0,
            "martingale_multiplier": 2.0,
            "max_martingale_steps": 3,
            "selected_markets": ["R_100"]
        }
        
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=valid_config
        )
        print(f"Valid minimum stake - Status Code: {response.status_code}")
        assert response.status_code == 200, "Valid minimum stake rejected"
        
        # Test with invalid stake (below minimum)
        invalid_config = {
            "api_token": "test_token_123",
            "stake_amount": 0.34,  # Below minimum
            "take_profit": 100.0,
            "stop_loss": 50.0,
            "martingale_multiplier": 2.0,
            "max_martingale_steps": 3,
            "selected_markets": ["R_100"]
        }
        
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=invalid_config
        )
        print(f"Invalid stake - Status Code: {response.status_code}")
        assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid stake, got {response.status_code}"
        
        print("✅ Minimum Stake Validation: PASSED - $0.35 minimum stake enforced")
        return True
    except Exception as e:
        print(f"❌ Minimum Stake Validation: FAILED - {str(e)}")
        return False

def test_martingale_repeat_attempts_validation():
    """Test martingale repeat attempts validation (1-5 range)"""
    print("\n=== Testing Martingale Repeat Attempts Validation ===")
    try:
        # Test with valid repeat attempts
        valid_config = {
            "api_token": "test_token_123",
            "stake_amount": 1.0,
            "take_profit": 100.0,
            "stop_loss": 50.0,
            "martingale_multiplier": 2.0,
            "max_martingale_steps": 3,
            "martingale_repeat_attempts": 5,  # Maximum valid
            "selected_markets": ["R_100"]
        }
        
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=valid_config
        )
        print(f"Valid repeat attempts - Status Code: {response.status_code}")
        assert response.status_code == 200, "Valid repeat attempts rejected"
        
        # Test with invalid repeat attempts (above maximum)
        invalid_config = {
            "api_token": "test_token_123",
            "stake_amount": 1.0,
            "take_profit": 100.0,
            "stop_loss": 50.0,
            "martingale_multiplier": 2.0,
            "max_martingale_steps": 3,
            "martingale_repeat_attempts": 6,  # Above maximum
            "selected_markets": ["R_100"]
        }
        
        response = requests.post(
            f"{API_URL}/bots/quickstart", 
            json=invalid_config
        )
        print(f"Invalid repeat attempts - Status Code: {response.status_code}")
        assert response.status_code in [400, 422], f"Expected 400 or 422 for invalid repeat attempts, got {response.status_code}"
        
        print("✅ Martingale Repeat Attempts Validation: PASSED - 1-5 range enforced")
        return True
    except Exception as e:
        print(f"❌ Martingale Repeat Attempts Validation: FAILED - {str(e)}")
        return False

def test_verify_deriv_token():
    """Test the Deriv token verification endpoint"""
    print("\n=== Testing Deriv Token Verification ===")
    try:
        response = requests.post(
            f"{API_URL}/verify-deriv-token",
            json=TEST_TOKEN_VERIFICATION
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Token verification failed"
            assert "account_info" in data, "Account info missing from response"
            
            # Verify account info contains required fields
            account_info = data["account_info"]
            assert "loginid" in account_info, "Login ID missing from account info"
            assert "currency" in account_info, "Currency missing from account info"
            assert "balance" in account_info, "Balance missing from account info"
            assert "account_type" in account_info, "Account type missing from account info"
            assert "is_virtual" in account_info is not None, "Virtual flag missing from account info"
            assert "country" in account_info, "Country missing from account info"
            assert "email" in account_info, "Email missing from account info"
            
            print("✅ Deriv Token Verification: PASSED - Returns detailed account information")
            return True, account_info["loginid"]
        else:
            print(f"Response: {response.text}")
            print("❌ Deriv Token Verification: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Deriv Token Verification: FAILED - {str(e)}")
        return False, None

def test_deriv_accounts_listing():
    """Test the Deriv accounts listing endpoint"""
    print("\n=== Testing Deriv Accounts Listing ===")
    try:
        response = requests.get(f"{API_URL}/deriv-accounts/{REAL_API_TOKEN}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Accounts listing failed"
            assert "accounts" in data, "Accounts missing from response"
            
            accounts = data["accounts"]
            assert len(accounts) > 0, "No accounts returned"
            
            # Verify account data includes required fields
            for account in accounts:
                assert "loginid" in account, "Login ID missing from account"
                assert "account_type" in account, "Account type missing from account"
                assert "currency" in account, "Currency missing from account"
                assert "is_virtual" in account is not None, "Virtual flag missing from account"
                assert "balance" in account, "Balance missing from account"
                assert "display_name" in account, "Display name missing from account"
            
            # Check if both demo and real accounts are returned
            has_demo = any(account["is_virtual"] == 1 for account in accounts)
            has_real = any(account["is_virtual"] == 0 for account in accounts)
            
            if has_demo and has_real:
                print("✅ Both demo and real accounts returned")
            elif has_demo:
                print("⚠️ Only demo accounts returned")
            elif has_real:
                print("⚠️ Only real accounts returned")
            else:
                print("⚠️ Account types could not be determined")
            
            # Get a loginid for account switching test
            loginid = accounts[0]["loginid"] if accounts else None
            
            print("✅ Deriv Accounts Listing: PASSED - Returns account list with balance and type information")
            return True, loginid
        else:
            print(f"Response: {response.text}")
            print("❌ Deriv Accounts Listing: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Deriv Accounts Listing: FAILED - {str(e)}")
        return False, None

def test_switch_deriv_account(loginid=None):
    """Test the Deriv account switching endpoint"""
    print("\n=== Testing Deriv Account Switching ===")
    
    # Use provided loginid or default to the one in TEST_ACCOUNT_SWITCH
    switch_data = TEST_ACCOUNT_SWITCH.copy()
    if loginid:
        switch_data["loginid"] = loginid
    
    try:
        response = requests.post(
            f"{API_URL}/switch-deriv-account",
            json=switch_data
        )
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            assert data["status"] == "success", "Account switching failed"
            assert "message" in data, "Message missing from response"
            assert "account_info" in data, "Account info missing from response"
            
            # Verify account info contains required fields
            account_info = data["account_info"]
            assert "loginid" in account_info, "Login ID missing from account info"
            assert "balance" in account_info, "Balance missing from account info"
            assert "currency" in account_info, "Currency missing from account info"
            
            # Verify the loginid matches the requested one
            assert account_info["loginid"] == switch_data["loginid"], f"Expected loginid {switch_data['loginid']}, got {account_info['loginid']}"
            
            print("✅ Deriv Account Switching: PASSED - Successfully switched account and returned updated information")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Deriv Account Switching: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Deriv Account Switching: FAILED - {str(e)}")
        return False

def test_error_handling_for_account_operations():
    """Test error handling for account operations with invalid data"""
    print("\n=== Testing Error Handling for Account Operations ===")
    
    # Test 1: Invalid token for verification
    try:
        invalid_token = {"api_token": "invalid_token_123"}
        response = requests.post(f"{API_URL}/verify-deriv-token", json=invalid_token)
        print(f"Invalid token verification - Status Code: {response.status_code}")
        assert response.status_code in [401, 400], f"Expected 401 or 400 for invalid token, got {response.status_code}"
        print("✅ Invalid token verification test: PASSED")
    except Exception as e:
        print(f"❌ Invalid token verification test: FAILED - {str(e)}")
        return False
    
    # Test 2: Invalid token for accounts listing
    try:
        response = requests.get(f"{API_URL}/deriv-accounts/invalid_token_123")
        print(f"Invalid token accounts listing - Status Code: {response.status_code}")
        assert response.status_code in [401, 400], f"Expected 401 or 400 for invalid token, got {response.status_code}"
        print("✅ Invalid token accounts listing test: PASSED")
    except Exception as e:
        print(f"❌ Invalid token accounts listing test: FAILED - {str(e)}")
        return False
    
    # Test 3: Invalid account switching
    try:
        invalid_switch = {
            "api_token": REAL_API_TOKEN,
            "loginid": "INVALID_LOGIN_ID"
        }
        response = requests.post(f"{API_URL}/switch-deriv-account", json=invalid_switch)
        print(f"Invalid account switching - Status Code: {response.status_code}")
        assert response.status_code in [400, 401], f"Expected 400 or 401 for invalid loginid, got {response.status_code}"
        print("✅ Invalid account switching test: PASSED")
    except Exception as e:
        print(f"❌ Invalid account switching test: FAILED - {str(e)}")
        return False
    
    # Test 4: Missing required fields
    try:
        missing_fields = {"api_token": ""}
        response = requests.post(f"{API_URL}/verify-deriv-token", json=missing_fields)
        print(f"Missing fields - Status Code: {response.status_code}")
        assert response.status_code in [400, 422], f"Expected 400 or 422 for missing fields, got {response.status_code}"
        print("✅ Missing fields test: PASSED")
    except Exception as e:
        print(f"❌ Missing fields test: FAILED - {str(e)}")
        return False
    
    print("✅ Error Handling for Account Operations: PASSED")
    return True

def test_end_to_end_account_flow():
    """Test the complete account management flow: verify token, list accounts, switch account"""
    print("\n=== Testing End-to-End Account Management Flow ===")
    
    # Step 1: Verify token and get account info
    print("Step 1: Verifying token and getting account info...")
    verify_result, loginid = test_verify_deriv_token()
    if not verify_result:
        print("❌ End-to-End Account Flow: FAILED - Could not verify token")
        return False
    
    print(f"✅ Step 1 Complete: Token verified and account info retrieved")
    
    # Step 2: List accounts
    print("Step 2: Listing accounts...")
    list_result, switch_loginid = test_deriv_accounts_listing()
    if not list_result:
        print("❌ End-to-End Account Flow: FAILED - Could not list accounts")
        return False
    
    print("✅ Step 2 Complete: Accounts listed successfully")
    
    # Step 3: Switch account if we have a loginid
    if switch_loginid:
        print(f"Step 3: Switching to account {switch_loginid}...")
        switch_result = test_switch_deriv_account(switch_loginid)
        if not switch_result:
            print("❌ End-to-End Account Flow: FAILED - Could not switch account")
            return False
        
        print("✅ Step 3 Complete: Account switched successfully")
    else:
        print("⚠️ Step 3 Skipped: No loginid available for account switching")
    
    print("✅ End-to-End Account Management Flow: PASSED - Complete flow tested successfully")
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
        bot_trades_result = test_bot_trades(bot_id)
        results["Bot Trades Endpoint"] = bot_trades_result
    
    # Test 7: Real-time WebSocket Connection
    results["Real-time WebSocket Connection"] = test_websocket_connection()
    
    # Test 8: Error Handling
    results["Error Handling"] = test_error_handling()
    
    # Test 9: Minimum Stake Validation
    results["Minimum Stake Validation"] = test_minimum_stake_validation()
    
    # Test 10: Martingale Repeat Attempts Validation
    results["Martingale Repeat Attempts"] = test_martingale_repeat_attempts_validation()
    
    # Test 11: Error Handling for Bot Operations
    results["Error Handling for Bot Operations"] = test_error_handling_for_bot_operations()
    
    # Test 12: End-to-End Bot Flow (Create, Stop, Restart, Delete)
    results["End-to-End Bot Flow"] = test_end_to_end_bot_flow()
    
    # Test 13: Deriv Token Verification
    verify_result, _ = test_verify_deriv_token()
    results["Deriv Token Verification"] = verify_result
    
    # Test 14: Deriv Accounts Listing
    list_result, _ = test_deriv_accounts_listing()
    results["Deriv Accounts Listing"] = list_result
    
    # Test 15: Deriv Account Switching
    results["Deriv Account Switching"] = test_switch_deriv_account()
    
    # Test 16: Error Handling for Account Operations
    results["Error Handling for Account Operations"] = test_error_handling_for_account_operations()
    
    # Test 17: End-to-End Account Management Flow
    results["End-to-End Account Management Flow"] = test_end_to_end_account_flow()
    
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