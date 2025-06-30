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

# Test data for bot creation
TEST_BOT_CONFIG = {
    "api_token": "test_token_123",
    "stake_amount": 25.0,
    "take_profit": 750.0,
    "stop_loss": 300.0,
    "martingale_multiplier": 2.5,
    "max_martingale_steps": 4,
    "selected_markets": ["R_100", "R_25"]
}

# WebSocket connection for real-time data verification
ws_connected = False
ws_received_data = False
ws_messages = []

def on_ws_message(ws, message):
    global ws_received_data
    ws_received_data = True
    ws_messages.append(json.loads(message))
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
        required_symbols = ["R_10", "R_25", "R_50", "R_75", "R_100"]
        for symbol in required_symbols:
            assert symbol in symbols, f"Required symbol {symbol} not found in markets response"
        
        print("✅ Markets Endpoint: PASSED")
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

def test_bot_creation():
    """Test the bot creation endpoint"""
    print("\n=== Testing Bot Creation Endpoint ===")
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
            
            # Store bot_id for later tests
            bot_id = data["bot_id"]
            
            print("✅ Bot Creation Endpoint: PASSED")
            return True, bot_id
        else:
            print(f"Response: {response.text}")
            print("❌ Bot Creation Endpoint: FAILED - Non-200 status code")
            return False, None
    except Exception as e:
        print(f"❌ Bot Creation Endpoint: FAILED - {str(e)}")
        return False, None

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
            
            print("✅ Bots List Endpoint: PASSED")
            return True
        else:
            print(f"Response: {response.text}")
            print("❌ Bots List Endpoint: FAILED - Non-200 status code")
            return False
    except Exception as e:
        print(f"❌ Bots List Endpoint: FAILED - {str(e)}")
        return False

def test_websocket_connection():
    """Test WebSocket connection for real-time data"""
    print("\n=== Testing WebSocket Connection ===")
    try:
        ws, ws_thread = start_websocket()
        
        # Wait for data to be received
        timeout = 15
        start_time = time.time()
        while not ws_received_data and time.time() - start_time < timeout:
            time.sleep(1)
            print("Waiting for WebSocket data...")
        
        if ws_received_data:
            print(f"Received {len(ws_messages)} WebSocket messages")
            if len(ws_messages) > 0:
                print(f"Sample message type: {ws_messages[0].get('type', 'unknown')}")
            
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
    
    # Test 1: API Health Check
    results["API Health Check"] = test_api_health()
    
    # Test 2: Markets Endpoint
    results["Market Data Endpoints"] = test_markets_endpoint() and test_ticks_endpoint()
    
    # Test 3: Bot Management Endpoints
    bot_creation_result, bot_id = test_bot_creation()
    bot_list_result = test_bots_list()
    results["Bot Management Endpoints"] = bot_creation_result and bot_list_result
    
    # Test 4: Real-time Data Verification
    results["Real-time Data Verification"] = test_websocket_connection()
    
    # Test 5: Error Handling
    results["Error Handling"] = test_error_handling()
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    return results

if __name__ == "__main__":
    print(f"Starting backend API tests at {datetime.now().isoformat()}")
    run_all_tests()