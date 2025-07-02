#!/usr/bin/env python3
import requests
import json
import time
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
    exit(1)

API_URL = f"{BASE_URL}/api"
print(f"Using API URL: {API_URL}")

# Real Deriv API token for testing
REAL_API_TOKEN = "dG1ac29qbdRzjJG"

# Test data for bot creation with real Deriv API token
TEST_REAL_BOT_CONFIG = {
    "api_token": REAL_API_TOKEN,
    "stake_amount": 0.35,
    "take_profit": 100.0,
    "stop_loss": 50.0,
    "martingale_multiplier": 2.0,
    "max_martingale_steps": 3,
    "martingale_repeat_attempts": 3,
    "selected_markets": ["R_100"]
}

def test_real_balance_integration():
    """Test that new bots retrieve and use actual Deriv account balance instead of hardcoded $1000"""
    print("\n=== Testing Real Balance Integration ===")
    
    # First verify the token to get the real account balance
    print("Step 1: Verifying Deriv API token to get real account balance...")
    verify_response = requests.post(
        f"{API_URL}/verify-deriv-token",
        json={"api_token": REAL_API_TOKEN}
    )
    
    if verify_response.status_code != 200:
        print(f"❌ Token verification failed: {verify_response.text}")
        return False
    
    verify_data = verify_response.json()
    real_account_balance = verify_data["account_info"]["balance"]
    print(f"✅ Token verified. Real account balance: ${real_account_balance}")
    
    # Create a bot with the real API token
    print("\nStep 2: Creating a bot with real API token...")
    bot_response = requests.post(
        f"{API_URL}/bots/quickstart", 
        json=TEST_REAL_BOT_CONFIG
    )
    
    if bot_response.status_code != 200:
        print(f"❌ Bot creation failed: {bot_response.text}")
        return False
    
    bot_data = bot_response.json()
    bot_id = bot_data["bot_id"]
    print(f"✅ Bot created with ID: {bot_id}")
    
    # Get the bot status to check if it's using the real balance
    print("\nStep 3: Checking if bot is using real account balance...")
    time.sleep(2)  # Wait for bot to initialize
    
    bots_response = requests.get(f"{API_URL}/bots")
    if bots_response.status_code != 200:
        print(f"❌ Failed to get bots list: {bots_response.text}")
        return False
    
    bots = bots_response.json()
    bot_found = False
    for bot in bots:
        if bot["id"] == bot_id:
            bot_found = True
            bot_balance = bot["current_balance"]
            print(f"Bot balance: ${bot_balance}")
            print(f"Real account balance: ${real_account_balance}")
            
            # Check if the bot balance is close to the real account balance
            # We use approximate comparison because there might be small differences due to timing
            if abs(float(bot_balance) - float(real_account_balance)) < 10:
                print(f"✅ Bot is using real account balance (${bot_balance})")
            else:
                print(f"❌ Bot is NOT using real account balance. Bot: ${bot_balance}, Real: ${real_account_balance}")
                return False
            break
    
    if not bot_found:
        print("❌ Bot not found in bots list")
        return False
    
    # Clean up - stop and delete the bot
    print("\nCleaning up - stopping and deleting the bot...")
    requests.put(f"{API_URL}/bots/{bot_id}/stop")
    requests.delete(f"{API_URL}/bots/{bot_id}")
    
    print("\n✅ Real Balance Integration Test: PASSED - Bot uses real account balance instead of hardcoded $1000")
    return True

def test_bot_restart_balance_fix():
    """Test that restarted bots use current real account balance"""
    print("\n=== Testing Bot Restart Balance Fix ===")
    
    # First verify the token to get the real account balance
    print("Step 1: Verifying Deriv API token to get real account balance...")
    verify_response = requests.post(
        f"{API_URL}/verify-deriv-token",
        json={"api_token": REAL_API_TOKEN}
    )
    
    if verify_response.status_code != 200:
        print(f"❌ Token verification failed: {verify_response.text}")
        return False
    
    verify_data = verify_response.json()
    real_account_balance = verify_data["account_info"]["balance"]
    print(f"✅ Token verified. Real account balance: ${real_account_balance}")
    
    # Create a bot with the real API token
    print("\nStep 2: Creating a bot with real API token...")
    bot_response = requests.post(
        f"{API_URL}/bots/quickstart", 
        json=TEST_REAL_BOT_CONFIG
    )
    
    if bot_response.status_code != 200:
        print(f"❌ Bot creation failed: {bot_response.text}")
        return False
    
    bot_data = bot_response.json()
    bot_id = bot_data["bot_id"]
    print(f"✅ Bot created with ID: {bot_id}")
    
    # Stop the bot
    print("\nStep 3: Stopping the bot...")
    stop_response = requests.put(f"{API_URL}/bots/{bot_id}/stop")
    if stop_response.status_code != 200:
        print(f"❌ Failed to stop bot: {stop_response.text}")
        return False
    
    print("✅ Bot stopped successfully")
    
    # Restart the bot
    print("\nStep 4: Restarting the bot...")
    restart_response = requests.put(f"{API_URL}/bots/{bot_id}/restart")
    if restart_response.status_code != 200:
        print(f"❌ Failed to restart bot: {restart_response.text}")
        return False
    
    print("✅ Bot restarted successfully")
    
    # Get the bot status to check if it's using the real balance after restart
    print("\nStep 5: Checking if restarted bot is using current real account balance...")
    time.sleep(2)  # Wait for bot to initialize
    
    bots_response = requests.get(f"{API_URL}/bots")
    if bots_response.status_code != 200:
        print(f"❌ Failed to get bots list: {bots_response.text}")
        return False
    
    bots = bots_response.json()
    bot_found = False
    for bot in bots:
        if bot["id"] == bot_id:
            bot_found = True
            bot_balance = bot["current_balance"]
            print(f"Bot balance after restart: ${bot_balance}")
            print(f"Real account balance: ${real_account_balance}")
            
            # Check if the bot balance is close to the real account balance
            if abs(float(bot_balance) - float(real_account_balance)) < 10:
                print(f"✅ Restarted bot is using current real account balance (${bot_balance})")
            else:
                print(f"❌ Restarted bot is NOT using current real account balance. Bot: ${bot_balance}, Real: ${real_account_balance}")
                return False
            break
    
    if not bot_found:
        print("❌ Bot not found in bots list after restart")
        return False
    
    # Clean up - stop and delete the bot
    print("\nCleaning up - stopping and deleting the bot...")
    requests.put(f"{API_URL}/bots/{bot_id}/stop")
    requests.delete(f"{API_URL}/bots/{bot_id}")
    
    print("\n✅ Bot Restart Balance Fix Test: PASSED - Restarted bot uses current real account balance")
    return True

def test_balance_refresh_endpoint():
    """Test the new manual balance refresh functionality"""
    print("\n=== Testing Balance Refresh Endpoint ===")
    
    # First verify the token to get the real account balance
    print("Step 1: Verifying Deriv API token to get real account balance...")
    verify_response = requests.post(
        f"{API_URL}/verify-deriv-token",
        json={"api_token": REAL_API_TOKEN}
    )
    
    if verify_response.status_code != 200:
        print(f"❌ Token verification failed: {verify_response.text}")
        return False
    
    verify_data = verify_response.json()
    real_account_balance = verify_data["account_info"]["balance"]
    print(f"✅ Token verified. Real account balance: ${real_account_balance}")
    
    # Create a bot with the real API token
    print("\nStep 2: Creating a bot with real API token...")
    bot_response = requests.post(
        f"{API_URL}/bots/quickstart", 
        json=TEST_REAL_BOT_CONFIG
    )
    
    if bot_response.status_code != 200:
        print(f"❌ Bot creation failed: {bot_response.text}")
        return False
    
    bot_data = bot_response.json()
    bot_id = bot_data["bot_id"]
    print(f"✅ Bot created with ID: {bot_id}")
    
    # Get the initial bot balance
    print("\nStep 3: Getting initial bot balance...")
    bots_response = requests.get(f"{API_URL}/bots")
    if bots_response.status_code != 200:
        print(f"❌ Failed to get bots list: {bots_response.text}")
        return False
    
    initial_bot_balance = None
    for bot in bots_response.json():
        if bot["id"] == bot_id:
            initial_bot_balance = bot["current_balance"]
            break
    
    if initial_bot_balance is None:
        print("❌ Bot not found in bots list")
        return False
    
    print(f"✅ Initial bot balance: ${initial_bot_balance}")
    
    # Test the refresh balance endpoint
    print("\nStep 4: Testing refresh balance endpoint...")
    refresh_response = requests.post(
        f"{API_URL}/refresh-bot-balance",
        json={"bot_id": bot_id}
    )
    
    if refresh_response.status_code != 200:
        print(f"❌ Balance refresh failed: {refresh_response.text}")
        return False
    
    refresh_data = refresh_response.json()
    print(f"✅ Balance refresh response: {json.dumps(refresh_data, indent=2)}")
    
    # Verify the response contains old and new balance
    if "old_balance" not in refresh_data or "new_balance" not in refresh_data:
        print("❌ Balance refresh response missing old_balance or new_balance")
        return False
    
    old_balance = refresh_data["old_balance"]
    new_balance = refresh_data["new_balance"]
    
    # Check if old balance matches initial balance
    if abs(float(old_balance) - float(initial_bot_balance)) > 1:
        print(f"❌ Old balance in response (${old_balance}) doesn't match initial bot balance (${initial_bot_balance})")
        return False
    
    print(f"✅ Old balance in response (${old_balance}) matches initial bot balance (${initial_bot_balance})")
    
    # Check if new balance is close to real account balance
    if abs(float(new_balance) - float(real_account_balance)) > 10:
        print(f"❌ New balance in response (${new_balance}) is not close to real account balance (${real_account_balance})")
        return False
    
    print(f"✅ New balance in response (${new_balance}) is close to real account balance (${real_account_balance})")
    
    # Verify the bot's balance is updated in the database
    print("\nStep 5: Verifying bot balance is updated in the database...")
    time.sleep(1)  # Wait for database update
    
    updated_bots_response = requests.get(f"{API_URL}/bots")
    if updated_bots_response.status_code != 200:
        print(f"❌ Failed to get updated bots list: {updated_bots_response.text}")
        return False
    
    updated_bot_balance = None
    for bot in updated_bots_response.json():
        if bot["id"] == bot_id:
            updated_bot_balance = bot["current_balance"]
            break
    
    if updated_bot_balance is None:
        print("❌ Bot not found in updated bots list")
        return False
    
    print(f"✅ Updated bot balance in database: ${updated_bot_balance}")
    
    # Check if updated balance matches new balance from refresh response
    if abs(float(updated_bot_balance) - float(new_balance)) > 1:
        print(f"❌ Updated bot balance in database (${updated_bot_balance}) doesn't match new balance from refresh (${new_balance})")
        return False
    
    print(f"✅ Updated bot balance in database (${updated_bot_balance}) matches new balance from refresh (${new_balance})")
    
    # Clean up - stop and delete the bot
    print("\nCleaning up - stopping and deleting the bot...")
    requests.put(f"{API_URL}/bots/{bot_id}/stop")
    requests.delete(f"{API_URL}/bots/{bot_id}")
    
    print("\n✅ Balance Refresh Endpoint Test: PASSED - Successfully refreshes bot balance from real Deriv account")
    return True

def test_bot_status_balance_display():
    """Test that GET /api/bots shows real balance"""
    print("\n=== Testing Bot Status Balance Display ===")
    
    # First verify the token to get the real account balance
    print("Step 1: Verifying Deriv API token to get real account balance...")
    verify_response = requests.post(
        f"{API_URL}/verify-deriv-token",
        json={"api_token": REAL_API_TOKEN}
    )
    
    if verify_response.status_code != 200:
        print(f"❌ Token verification failed: {verify_response.text}")
        return False
    
    verify_data = verify_response.json()
    real_account_balance = verify_data["account_info"]["balance"]
    print(f"✅ Token verified. Real account balance: ${real_account_balance}")
    
    # Create a bot with the real API token
    print("\nStep 2: Creating a bot with real API token...")
    bot_response = requests.post(
        f"{API_URL}/bots/quickstart", 
        json=TEST_REAL_BOT_CONFIG
    )
    
    if bot_response.status_code != 200:
        print(f"❌ Bot creation failed: {bot_response.text}")
        return False
    
    bot_data = bot_response.json()
    bot_id = bot_data["bot_id"]
    print(f"✅ Bot created with ID: {bot_id}")
    
    # Get the bot status to check if it's showing the real balance
    print("\nStep 3: Checking if bot status shows real account balance...")
    time.sleep(2)  # Wait for bot to initialize
    
    bots_response = requests.get(f"{API_URL}/bots")
    if bots_response.status_code != 200:
        print(f"❌ Failed to get bots list: {bots_response.text}")
        return False
    
    bots = bots_response.json()
    bot_found = False
    for bot in bots:
        if bot["id"] == bot_id:
            bot_found = True
            bot_balance = bot["current_balance"]
            print(f"Bot balance in status: ${bot_balance}")
            print(f"Real account balance: ${real_account_balance}")
            
            # Check if the bot balance is close to the real account balance
            if abs(float(bot_balance) - float(real_account_balance)) < 10:
                print(f"✅ Bot status shows real account balance (${bot_balance})")
            else:
                print(f"❌ Bot status does NOT show real account balance. Bot: ${bot_balance}, Real: ${real_account_balance}")
                return False
            break
    
    if not bot_found:
        print("❌ Bot not found in bots list")
        return False
    
    # Clean up - stop and delete the bot
    print("\nCleaning up - stopping and deleting the bot...")
    requests.put(f"{API_URL}/bots/{bot_id}/stop")
    requests.delete(f"{API_URL}/bots/{bot_id}")
    
    print("\n✅ Bot Status Balance Display Test: PASSED - Bot status shows real account balance")
    return True

def run_all_tests():
    """Run all real balance integration tests"""
    print(f"Starting real balance integration tests at {datetime.now().isoformat()}")
    print("Testing Wakhungu28Ai Trading Bot Real Balance Integration")
    
    results = {}
    
    # Test 1: Real Balance Integration
    results["Real Balance Integration"] = test_real_balance_integration()
    
    # Test 2: Bot Restart Balance Fix
    results["Bot Restart Balance Fix"] = test_bot_restart_balance_fix()
    
    # Test 3: Balance Refresh Endpoint
    results["Balance Refresh Endpoint"] = test_balance_refresh_endpoint()
    
    # Test 4: Bot Status Balance Display
    results["Bot Status Balance Display"] = test_bot_status_balance_display()
    
    # Print summary
    print("\n=== TEST SUMMARY ===")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Print overall result
    passed_count = sum(1 for passed in results.values() if passed)
    total_count = len(results)
    print(f"\nOverall Result: {passed_count}/{total_count} tests passed ({passed_count/total_count*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    run_all_tests()