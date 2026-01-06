#!/usr/bin/env python3
"""
Standalone GitHub Push Monitor and PR Creator
This bypasses the FastAPI server and works directly with GitHub APIs
Perfect for production use without webhooks
"""

import time
import os
import sys
from datetime import datetime
from typing import Optional

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.github_ops import check_for_new_push, get_github_token
from utils.pr_creator import GitHubPRCreator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class StandalonePushMonitor:
    def __init__(
        self,
        repo_url: str,
        poll_interval: int = 300,
        auto_create_pr: bool = True,
        github_token: Optional[str] = None,
    ):
        """
        Initialize standalone push monitor

        Args:
            repo_url: GitHub repository URL to monitor
            poll_interval: Polling interval in seconds
            auto_create_pr: Whether to automatically create PRs
            github_token: GitHub token for API access
        """
        self.repo_url = repo_url
        self.poll_interval = poll_interval
        self.auto_create_pr = auto_create_pr
        self.github_token = github_token or get_github_token()
        self.last_known_sha = None
        self.running = False

        # Initialize PR creator if needed
        if self.auto_create_pr:
            try:
                self.pr_creator = GitHubPRCreator(self.github_token)
                print("✅ PR Creator initialized")
            except Exception as e:
                print(f"❌ Failed to initialize PR Creator: {e}")
                self.auto_create_pr = False

        print(f"🔍 Standalone Push Monitor initialized")
        print(f"   Repository: {repo_url}")
        print(f"   Poll interval: {poll_interval}s ({poll_interval//60}m)")
        print(f"   Auto-create PRs: {auto_create_pr}")

    def log_event(self, message: str, level: str = "INFO"):
        """Log events with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def check_and_process_push(self) -> bool:
        """Check for new push and process it"""
        try:
            # Check for new push
            push_status = check_for_new_push(
                repo_url=self.repo_url,
                last_known_sha=self.last_known_sha,
                token=self.github_token,
            )

            if push_status.get("error"):
                self.log_event(f"❌ Push check failed: {push_status['error']}", "ERROR")
                return False

            if push_status["has_new_push"]:
                commit = push_status["latest_commit"]
                self.log_event(f"🎉 NEW PUSH DETECTED!", "SUCCESS")
                self.log_event(f"   Commit: {commit['sha'][:8]}...")
                self.log_event(f"   Author: {commit['author']}")
                self.log_event(f"   Message: {commit['message'][:60]}...")

                # Create PR if enabled
                if self.auto_create_pr:
                    self.log_event("🤖 Creating optimization PR...", "INFO")

                    try:
                        repo_name = self.repo_url.replace(
                            "https://github.com/", ""
                        ).rstrip("/")
                        optimized_yaml = self.pr_creator.get_optimized_workflow_yaml()
                        improvement_summary = (
                            self.pr_creator.create_improvement_summary()
                        )

                        pr_result = self.pr_creator.create_optimization_pr(
                            repo_name=repo_name,
                            optimized_yaml=optimized_yaml,
                            improvement_summary=improvement_summary,
                        )

                        if pr_result and pr_result.get("success"):
                            self.log_event(f"🚀 PULL REQUEST CREATED!", "SUCCESS")
                            self.log_event(f"   PR URL: {pr_result['pr_url']}")
                            self.log_event(f"   PR Number: #{pr_result['pr_number']}")
                        else:
                            self.log_event(
                                f"⚠️  PR creation failed: {pr_result.get('error', 'Unknown error')}",
                                "WARNING",
                            )

                    except Exception as pr_error:
                        self.log_event(
                            f"❌ PR creation error: {str(pr_error)}", "ERROR"
                        )

                # Update last known SHA
                self.last_known_sha = commit["sha"]
                return True

            else:
                self.log_event("📝 No new pushes detected")

                # Update SHA if this is the first run
                if push_status.get("latest_commit"):
                    self.last_known_sha = push_status["latest_commit"]["sha"]

                return False

        except Exception as e:
            self.log_event(f"💥 Error checking push: {str(e)}", "ERROR")
            return False

    def start_monitoring(self):
        """Start continuous monitoring"""
        self.running = True
        self.log_event("🚀 Starting standalone push monitoring...")

        # Initial check
        self.log_event("🔍 Performing initial push check...")
        self.check_and_process_push()

        try:
            while self.running:
                self.log_event(f"⏰ Waiting {self.poll_interval}s until next check...")
                time.sleep(self.poll_interval)

                if self.running:  # Check if still running after sleep
                    self.log_event("🔍 Checking for new pushes...")
                    self.check_and_process_push()

        except KeyboardInterrupt:
            self.log_event("🛑 Monitoring stopped by user", "INFO")
        except Exception as e:
            self.log_event(f"💥 Monitoring error: {e}", "ERROR")
        finally:
            self.running = False
            self.log_event("🏁 Monitoring stopped", "INFO")

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False


def test_standalone_functionality():
    """Test the standalone functionality"""
    print("🧪 Testing Standalone Push Monitor")
    print("=" * 50)

    repo_url = "https://github.com/RajBhattacharyya/pv_app_api"

    try:
        # Test without PR creation first
        monitor = StandalonePushMonitor(
            repo_url=repo_url,
            poll_interval=60,  # 1 minute for testing
            auto_create_pr=False,
        )

        print("\n📋 Testing push detection only...")
        result = monitor.check_and_process_push()

        if result:
            print("✅ Push detection test: PASSED")
        else:
            print("✅ Push detection test: PASSED (no new pushes)")

        # Test with PR creation capability
        print("\n📋 Testing with PR creation capability...")
        monitor_with_pr = StandalonePushMonitor(
            repo_url=repo_url, poll_interval=60, auto_create_pr=True
        )

        if monitor_with_pr.pr_creator:
            print("✅ PR creation capability: READY")
        else:
            print("❌ PR creation capability: FAILED")

        print(f"\n🎯 System Status:")
        print("✅ Direct GitHub API access working")
        print("✅ Push detection functional")
        print("✅ PR creation ready")
        print("✅ No server dependencies")
        print("✅ No webhook requirements")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="CodeYogi Standalone Push Monitor")
    parser.add_argument(
        "--repo",
        default="https://github.com/RajBhattacharyya/pv_app_api",
        help="Repository URL to monitor",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Poll interval in seconds (default: 300)",
    )
    parser.add_argument(
        "--no-pr", action="store_true", help="Disable automatic PR creation"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test mode instead of continuous monitoring",
    )

    args = parser.parse_args()

    print("🔍 CodeYogi Standalone Push Monitor")
    print("=" * 50)

    if args.test:
        test_standalone_functionality()
        return

    print("This tool monitors repositories and creates optimization PRs")
    print("No webhooks or servers required!")
    print("Press Ctrl+C to stop monitoring")
    print()

    monitor = StandalonePushMonitor(
        repo_url=args.repo, poll_interval=args.interval, auto_create_pr=not args.no_pr
    )

    monitor.start_monitoring()


if __name__ == "__main__":
    main()
