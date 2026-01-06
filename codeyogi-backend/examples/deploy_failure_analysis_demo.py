"""
Deploy Failure Analysis Demo

Demonstrates the capabilities of the Post-Deploy Failure Root Cause Analysis agent.
Shows various failure scenarios and how the agent diagnoses them.
"""

import os
import sys
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.deploy_failure_analyzer import DeployFailureAnalyzer


def scenario_1_blocking_loop():
    """Scenario: Blocking sleep added to API endpoint causing timeouts"""
    return {
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
        "pipeline_logs": """
[2026-01-05 10:30:15] Starting deployment...
[2026-01-05 10:30:45] Tests passed ✓
[2026-01-05 10:31:00] Build completed ✓
[2026-01-05 10:31:30] Deploying to production...
[2026-01-05 10:32:00] Deployment successful ✓
""",
        "runtime_logs": """
[2026-01-05 10:35:22] ERROR: Request timeout on /api/users
[2026-01-05 10:35:45] WARNING: High database connection pool usage (95%)
[2026-01-05 10:36:10] ERROR: Request timeout on /api/users
[2026-01-05 10:36:30] CRITICAL: API response time: 45s (threshold: 2s)
[2026-01-05 10:37:00] ERROR: 503 Service Unavailable - /api/users
[2026-01-05 10:37:15] INFO: Average request latency: 38000ms (was 120ms before deployment)
""",
        "deployment_env": "production"
    }


def scenario_2_missing_env_var():
    """Scenario: New feature requires environment variable that's not set"""
    return {
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
        "pipeline_logs": """
[2026-01-05 14:20:10] Starting deployment...
[2026-01-05 14:20:35] Tests passed ✓
[2026-01-05 14:20:50] Build completed ✓
[2026-01-05 14:21:15] Deploying to production...
[2026-01-05 14:21:40] Deployment successful ✓
""",
        "runtime_logs": """
[2026-01-05 14:22:05] INFO: Application starting...
[2026-01-05 14:22:06] ERROR: AttributeError: 'NoneType' object has no attribute 'startswith'
[2026-01-05 14:22:06] CRITICAL: Application failed to start
[2026-01-05 14:22:06] Traceback: File "config/settings.py", line 12, in init_app
[2026-01-05 14:22:06]   stripe.api_key = config.STRIPE_API_KEY
[2026-01-05 14:22:07] ERROR: Container exited with code 1
""",
        "deployment_env": "production"
    }


def scenario_3_memory_leak():
    """Scenario: Large in-memory cache added causing OOM"""
    return {
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
+    
     def get_metrics(self, date_range):
-        return self.db.query(date_range)
+        return [d for d in self.cache if d['date'] in date_range]
""",
        "pipeline_logs": """
[2026-01-05 16:45:00] Starting deployment...
[2026-01-05 16:45:30] Tests passed ✓
[2026-01-05 16:45:50] Build completed ✓
[2026-01-05 16:46:20] Deploying to production...
[2026-01-05 16:46:50] Deployment successful ✓
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
        "deployment_env": "production"
    }


def scenario_4_async_to_sync():
    """Scenario: Async function converted to sync causing request backlog"""
    return {
        "git_diff": """
diff --git a/api/notifications.py b/api/notifications.py
index 901stu..234vwx 100644
--- a/api/notifications.py
+++ b/api/notifications.py
@@ -8,10 +8,10 @@ from email_service import send_email
-async def send_notification(user_id, message):
+def send_notification(user_id, message):
     user = get_user(user_id)
-    await send_email(user.email, message)
-    await send_push(user.device_token, message)
-    await log_notification(user_id, message)
+    send_email(user.email, message)  # Now blocking
+    send_push(user.device_token, message)  # Now blocking
+    log_notification(user_id, message)  # Now blocking
     return {"status": "sent"}
 
 @app.route('/notify')
 def notify_endpoint():
-    await send_notification(request.user_id, request.message)
+    send_notification(request.user_id, request.message)
""",
        "pipeline_logs": """
[2026-01-05 18:10:00] Starting deployment...
[2026-01-05 18:10:25] Tests passed ✓
[2026-01-05 18:10:40] Build completed ✓
[2026-01-05 18:11:00] Deploying to production...
[2026-01-05 18:11:30] Deployment successful ✓
""",
        "runtime_logs": """
[2026-01-05 18:15:00] INFO: Request to /notify - processing
[2026-01-05 18:15:15] WARNING: Request queue growing: 45 pending
[2026-01-05 18:15:30] WARNING: Request queue growing: 120 pending
[2026-01-05 18:15:45] ERROR: Worker timeout - request took >30s
[2026-01-05 18:16:00] CRITICAL: Request queue: 350 pending
[2026-01-05 18:16:15] ERROR: 503 Service Unavailable - workers exhausted
[2026-01-05 18:16:30] WARNING: Average response time: 25s (was 200ms)
""",
        "deployment_env": "production"
    }


def run_analysis(scenario_name, scenario_data, analyzer):
    """Run analysis on a scenario and display results"""
    print(f"\n{'='*80}")
    print(f"SCENARIO: {scenario_name}")
    print(f"{'='*80}\n")
    
    result = analyzer.analyze_failure(**scenario_data)
    
    print("📊 ANALYSIS RESULT:\n")
    print(f"Summary: {result['summary']}")
    print(f"\n🔍 Root Cause:\n{result['root_cause']}")
    print(f"\n📁 Affected File: {result['affected_file']}")
    print(f"📍 Affected Line: {result['affected_line']}")
    print(f"\n⚠️  User Impact:\n{result['impact']}")
    print(f"\n🎯 Confidence: {result['confidence']:.0%}")
    print(f"\n💡 Suggested Fix:\n{result['suggested_fix']}")
    
    if "detected_patterns" in result:
        print(f"\n🔎 Detected Patterns: {', '.join(result['detected_patterns'].keys())}")
    
    print(f"\n{'='*80}\n")
    
    return result


def main():
    """Run all demo scenarios"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║           CodeYogi - Post-Deploy Failure Analysis Demo                ║
║                                                                        ║
║  This demo showcases the SRE AI agent's ability to diagnose           ║
║  production failures by correlating code changes with runtime errors  ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize analyzer
    api_key = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
    
    try:
        analyzer = DeployFailureAnalyzer(api_key=api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease set GROQ_API_KEY environment variable or update the script with your API key.")
        return
    
    # Run scenarios
    scenarios = [
        ("Blocking Loop & Database in Loop", scenario_1_blocking_loop()),
        ("Missing Environment Variable", scenario_2_missing_env_var()),
        ("Memory Leak / OOM", scenario_3_memory_leak()),
        ("Async to Sync Conversion", scenario_4_async_to_sync()),
    ]
    
    results = []
    for name, data in scenarios:
        try:
            result = run_analysis(name, data, analyzer)
            results.append({"scenario": name, "result": result})
        except Exception as e:
            print(f"❌ Error analyzing {name}: {e}\n")
    
    # Summary
    print(f"\n{'='*80}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*80}\n")
    
    for item in results:
        confidence_emoji = "🟢" if item["result"]["confidence"] > 0.7 else "🟡" if item["result"]["confidence"] > 0.5 else "🔴"
        print(f"{confidence_emoji} {item['scenario']}")
        print(f"   Confidence: {item['result']['confidence']:.0%} | File: {item['result']['affected_file']}")
        print(f"   {item['result']['summary']}\n")
    
    print("✅ Demo complete!\n")


if __name__ == "__main__":
    main()
