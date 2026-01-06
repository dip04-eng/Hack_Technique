"""
Test Script for Post-Deploy Failure Analysis API

This script tests the /api/post-deploy-analysis endpoint with realistic scenarios.
Use this to verify the endpoint works correctly before frontend integration.

Author: CodeYogi DevOps Platform
"""

import requests
import json
from datetime import datetime


# Backend API URL
API_URL = "http://localhost:8000/api/post-deploy-analysis"


def print_separator(title=""):
    """Print a formatted separator"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def print_result(response_data):
    """Pretty print the analysis result"""
    print(f"\n✅ Success: {response_data.get('success', False)}")
    print(f"\n📝 Summary:\n   {response_data.get('summary', 'N/A')}")
    print(f"\n🔍 Root Cause:\n   {response_data.get('root_cause', 'N/A')}")
    print(f"\n📁 Affected File: {response_data.get('affected_file', 'N/A')}")
    print(f"📍 Affected Line: {response_data.get('affected_line', 'N/A')}")
    print(f"\n⚠️  User Impact:\n   {response_data.get('impact', 'N/A')}")
    print(f"\n🎯 Confidence: {response_data.get('confidence', 0):.0%}")
    print(f"\n💡 Suggested Fix:\n   {response_data.get('suggested_fix', 'N/A')}")
    
    if response_data.get('detected_patterns'):
        print(f"\n🔎 Detected Patterns:")
        for pattern, data in response_data['detected_patterns'].items():
            print(f"   - {pattern.upper()}: {data.get('severity', 'unknown')} severity")
    
    print(f"\n🕐 Timestamp: {response_data.get('timestamp', 'N/A')}")
    print(f"🌍 Environment: {response_data.get('deployment_env', 'N/A')}")


def test_scenario_1_blocking_loop():
    """Test: Blocking loop causing API timeouts"""
    print_separator("TEST 1: Blocking Loop + Database in Loop")
    
    payload = {
        "git_diff": """
diff --git a/api/users.py b/api/users.py
index 123abc..456def 100644
--- a/api/users.py
+++ b/api/users.py
@@ -1,5 +1,6 @@
 from flask import jsonify
 from cache import fetch_user_cache
+import time

 def get_users():
     try:
         users = []
         for user_id in range(1, 1000):
-            users.append(fetch_user_cache(user_id))
+            # Changed to fetch from database for accuracy
+            db_user = db.query(f"SELECT * FROM users WHERE id={user_id}")
+            users.append(db_user)
+            # Add small delay for rate limiting
+            time.sleep(0.1)
         return jsonify(users)
""",
        "runtime_logs": """
[2026-01-05 10:35:22] ERROR: Request timeout on /api/users
[2026-01-05 10:35:45] WARNING: High database connection pool usage (95%)
[2026-01-05 10:36:10] ERROR: Request timeout on /api/users
[2026-01-05 10:36:30] CRITICAL: API response time: 45s (threshold: 2s)
[2026-01-05 10:37:00] ERROR: 503 Service Unavailable - /api/users
[2026-01-05 10:37:15] INFO: Average request latency: 38000ms (was 120ms before deployment)
""",
        "pipeline_logs": """
[2026-01-05 10:30:15] Starting deployment...
[2026-01-05 10:30:45] Tests passed ✓
[2026-01-05 10:31:00] Build completed ✓
[2026-01-05 10:31:30] Deploying to production...
[2026-01-05 10:32:00] Deployment successful ✓
""",
        "deployment_env": "production"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        print_result(response.json())
        return True
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        return False


def test_scenario_2_missing_env_var():
    """Test: Missing environment variable causing startup crash"""
    print_separator("TEST 2: Missing Environment Variable")
    
    payload = {
        "git_diff": """
diff --git a/config/settings.py b/config/settings.py
index 789ghi..012jkl 100644
--- a/config/settings.py
+++ b/config/settings.py
@@ -5,6 +5,7 @@ class Config:
     DATABASE_URL = os.getenv('DATABASE_URL')
     REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
+    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')  # New payment integration
     
 def init_app():
     config = Config()
+    stripe.api_key = config.STRIPE_API_KEY
     return config
""",
        "runtime_logs": """
[2026-01-05 14:22:05] INFO: Application starting...
[2026-01-05 14:22:06] ERROR: AttributeError: 'NoneType' object has no attribute 'startswith'
[2026-01-05 14:22:06] CRITICAL: Application failed to start
[2026-01-05 14:22:06] Traceback: File "config/settings.py", line 12, in init_app
[2026-01-05 14:22:06]   stripe.api_key = config.STRIPE_API_KEY
[2026-01-05 14:22:07] ERROR: Container exited with code 1
""",
        "pipeline_logs": """
[2026-01-05 14:20:10] Starting deployment...
[2026-01-05 14:20:35] Tests passed ✓
[2026-01-05 14:20:50] Build completed ✓
[2026-01-05 14:21:15] Deploying to production...
[2026-01-05 14:21:40] Deployment successful ✓
""",
        "deployment_env": "production"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        print_result(response.json())
        return True
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        return False


def test_scenario_3_memory_leak():
    """Test: Large in-memory cache causing OOM"""
    print_separator("TEST 3: Memory Leak / OOM")
    
    payload = {
        "git_diff": """
diff --git a/services/analytics.py b/services/analytics.py
index 345mno..678pqr 100644
--- a/services/analytics.py
+++ b/services/analytics.py
@@ -1,10 +1,15 @@
 import pandas as pd
+import numpy as np

 class AnalyticsService:
     def __init__(self):
-        self.cache = {}
+        # Pre-load all historical data for faster queries
+        self.cache = self._load_all_data()
     
+    def _load_all_data(self):
+        # Load last 5 years of data into memory
+        data = pd.read_sql("SELECT * FROM events WHERE created_at > '2021-01-01'", engine)
+        return data.to_dict('records')  # ~10GB of data
""",
        "runtime_logs": """
[2026-01-05 16:48:10] INFO: Starting analytics service...
[2026-01-05 16:48:45] WARNING: Memory usage: 75%
[2026-01-05 16:49:20] WARNING: Memory usage: 92%
[2026-01-05 16:49:35] CRITICAL: Memory usage: 98%
[2026-01-05 16:49:40] ERROR: Out of Memory - Process killed
[2026-01-05 16:49:45] Container crashed - exit code 137 (OOMKilled)
[2026-01-05 16:50:00] Restart attempt 1/3...
[2026-01-05 16:50:35] ERROR: Out of Memory - Process killed
""",
        "pipeline_logs": "",
        "deployment_env": "production"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        print_result(response.json())
        return True
    except Exception as e:
        print(f"\n❌ Test Failed: {str(e)}")
        return False


def test_validation_errors():
    """Test: API validation for required fields"""
    print_separator("TEST 4: Validation - Missing Required Fields")
    
    # Test missing git_diff
    print("\n📝 Testing missing git_diff...")
    payload = {
        "runtime_logs": "Some error logs",
        "deployment_env": "production"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 400:
            print(f"✅ Correctly rejected: {response.json().get('detail')}")
        else:
            print(f"❌ Should have returned 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    
    # Test missing runtime_logs
    print("\n📝 Testing missing runtime_logs...")
    payload = {
        "git_diff": "Some git diff",
        "deployment_env": "production"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 400:
            print(f"✅ Correctly rejected: {response.json().get('detail')}")
        else:
            print(f"❌ Should have returned 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Test error: {str(e)}")


def main():
    """Run all test scenarios"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║         CodeYogi - Post-Deploy Failure Analysis API Test              ║
║                                                                        ║
║  Testing endpoint: POST /api/post-deploy-analysis                     ║
║  Make sure your backend server is running on localhost:8000           ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
""")
    
    # Check if backend is running
    try:
        health_check = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Backend is running (Status: {health_check.status_code})\n")
    except Exception as e:
        print(f"❌ Backend not reachable: {str(e)}")
        print("\nPlease start the backend server:")
        print("   cd codeyogi-backend")
        print("   python main.py")
        print("\nOr using uvicorn:")
        print("   uvicorn main:app --reload --port 8000\n")
        return
    
    # Run test scenarios
    results = []
    
    # Test 1: Blocking loop
    results.append(("Blocking Loop", test_scenario_1_blocking_loop()))
    
    # Test 2: Missing env var
    results.append(("Missing Env Var", test_scenario_2_missing_env_var()))
    
    # Test 3: Memory leak
    results.append(("Memory Leak", test_scenario_3_memory_leak()))
    
    # Test 4: Validation
    test_validation_errors()
    
    # Summary
    print_separator("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The endpoint is working correctly.\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.\n")


if __name__ == "__main__":
    main()
