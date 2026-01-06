#!/usr/bin/env python3
"""
Push Monitor - Continuously polls for new pushes and triggers CodeYogi optimization
This script replaces the need for GitHub webhooks by polling for the latest commits
"""

import time
import requests
import json
import os
from datetime import datetime
from typing import Optional


class PushMonitor:
    def __init__(
        self,
        repo_url: str,
        codeyogi_url: str = "http://localhost:8000",
        poll_interval: int = 300,  # 5 minutes
        github_token: Optional[str] = None,
    ):
        """
        Initialize push monitor

        Args:
            repo_url: GitHub repository URL to monitor
            codeyogi_url: CodeYogi server URL
            poll_interval: Polling interval in seconds (default: 5 minutes)
            github_token: GitHub token for API access
        """
        self.repo_url = repo_url
        self.codeyogi_url = codeyogi_url
        self.poll_interval = poll_interval
        self.github_token = (
            github_token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        )
        self.last_known_sha = None
        self.running = False

        print(f"🔍 Push Monitor initialized")
        print(f"   Repository: {repo_url}")
        print(f"   CodeYogi URL: {codeyogi_url}")
        print(f"   Poll interval: {poll_interval}s ({poll_interval//60}m)")

    def check_codeyogi_health(self) -> bool:
        """Check if CodeYogi server is running"""
        try:
            response = requests.get(f"{self.codeyogi_url}/", timeout=10)
            return response.status_code == 200
        except:
            return False

    def check_for_push(self) -> dict:
        """Check for new push using CodeYogi endpoint"""
        try:
            payload = {
                "repo_url": self.repo_url,
                "last_known_sha": self.last_known_sha,
                "github_token": self.github_token,
            }

            response = requests.post(
                f"{self.codeyogi_url}/repos/check-push", json=payload, timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def log_event(self, message: str, level: str = "INFO"):
        """Log events with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def start_monitoring(self):
        """Start continuous monitoring loop"""
        self.running = True
        self.log_event("🚀 Starting push monitoring...")

        # Initial health check
        if not self.check_codeyogi_health():
            self.log_event(
                "❌ CodeYogi server not accessible! Please start the server.", "ERROR"
            )
            return False

        self.log_event("✅ CodeYogi server is running")

        try:
            while self.running:
                self.log_event("🔍 Checking for new pushes...")

                result = self.check_for_push()

                if result.get("success"):
                    if result.get("has_new_push"):
                        commit = result.get("latest_commit", {})
                        self.log_event(f"🎉 NEW PUSH DETECTED!", "SUCCESS")
                        self.log_event(
                            f"   Commit: {commit.get('sha', 'unknown')[:8]}..."
                        )
                        self.log_event(f"   Author: {commit.get('author', 'unknown')}")
                        self.log_event(
                            f"   Message: {commit.get('message', 'No message')[:60]}..."
                        )
                        self.log_event(
                            f"   🤖 CodeYogi optimization triggered automatically!"
                        )

                        # Update last known SHA
                        self.last_known_sha = commit.get("sha")

                    else:
                        self.log_event("📝 No new pushes detected")

                        # Still update the SHA in case this is the first run
                        if result.get("latest_commit"):
                            self.last_known_sha = result["latest_commit"]["sha"]
                else:
                    error = result.get("error", "Unknown error")
                    self.log_event(f"❌ Push check failed: {error}", "ERROR")

                # Wait for next poll
                if self.running:
                    self.log_event(
                        f"⏰ Waiting {self.poll_interval}s until next check..."
                    )
                    time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self.log_event("🛑 Monitoring stopped by user", "INFO")
        except Exception as e:
            self.log_event(f"💥 Monitoring error: {e}", "ERROR")
        finally:
            self.running = False
            self.log_event("🏁 Push monitoring stopped", "INFO")

    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.running = False


def main():
    """Main entry point"""
    print("🔍 CodeYogi Push Monitor")
    print("=" * 50)
    print("This script continuously checks for new pushes and triggers optimization")
    print("Press Ctrl+C to stop monitoring")
    print()

    # Configuration
    REPO_URL = "https://github.com/RajBhattacharyya/pv_app_api"
    CODEYOGI_URL = "http://localhost:8000"
    POLL_INTERVAL = 300  # 5 minutes

    # You can override these with environment variables
    repo_url = os.getenv("MONITOR_REPO_URL", REPO_URL)
    codeyogi_url = os.getenv("CODEYOGI_URL", CODEYOGI_URL)
    poll_interval = int(os.getenv("POLL_INTERVAL", POLL_INTERVAL))

    print(f"Configuration:")
    print(f"  Repository: {repo_url}")
    print(f"  CodeYogi URL: {codeyogi_url}")
    print(f"  Poll Interval: {poll_interval}s ({poll_interval//60}m)")
    print()

    # Create and start monitor
    monitor = PushMonitor(
        repo_url=repo_url, codeyogi_url=codeyogi_url, poll_interval=poll_interval
    )

    monitor.start_monitoring()


if __name__ == "__main__":
    main()
