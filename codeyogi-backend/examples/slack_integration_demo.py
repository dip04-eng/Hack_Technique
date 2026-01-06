#!/usr/bin/env python3
"""
Slack Integration Example for GitHub PR Creator
Demonstrates how to set up and use Slack notifications for PR creation
"""

import sys
import os

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pr_creator import GitHubPRCreator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def demonstrate_slack_integration():
    """Demonstrate the Slack integration setup and usage"""

    console.print("🔔 Slack Integration Demo for GitHub PR Creator", style="bold blue")
    console.print("=" * 60)

    # Step 1: Show environment setup
    console.print("\n📋 Step 1: Environment Variables Setup")

    env_table = Table(title="Required Environment Variables")
    env_table.add_column("Variable", style="cyan")
    env_table.add_column("Description", style="green")
    env_table.add_column("Example", style="yellow")

    env_table.add_row(
        "SLACK_BOT_TOKEN", "Slack Bot User OAuth Token", "xoxb-your-token-here"
    )
    env_table.add_row(
        "SLACK_CHANNEL",
        "Channel to send notifications to",
        "#general or #dev-notifications",
    )
    env_table.add_row(
        "GITHUB_TOKEN", "GitHub Personal Access Token", "ghp_your-token-here"
    )

    console.print(env_table)

    # Step 2: Show setup instructions
    console.print("\n🛠️  Step 2: Slack App Setup Instructions")

    setup_steps = [
        "1. Go to https://api.slack.com/apps and create a new app",
        "2. Under 'OAuth & Permissions', add these Bot Token Scopes:",
        "   • chat:write - Send messages to channels",
        "   • chat:write.public - Send messages to channels the app isn't in",
        "3. Install the app to your workspace",
        "4. Copy the 'Bot User OAuth Token' to SLACK_BOT_TOKEN env var",
        "5. Invite the bot to your desired channel: /invite @your-bot-name",
    ]

    for step in setup_steps:
        if step.startswith("   •"):
            console.print(f"    {step}", style="dim")
        else:
            console.print(step)

    # Step 3: Check current configuration
    console.print("\n🔍 Step 3: Current Configuration Check")

    slack_token = os.getenv("SLACK_BOT_TOKEN")
    slack_channel = os.getenv("SLACK_CHANNEL")
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    config_table = Table()
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Status", style="green")
    config_table.add_column("Value", style="yellow")

    config_table.add_row(
        "Slack Token",
        "✅ Configured" if slack_token else "❌ Missing",
        f"***{slack_token[-8:]}" if slack_token else "Not set",
    )
    config_table.add_row(
        "Slack Channel",
        "✅ Configured" if slack_channel else "⚠️  Using default",
        slack_channel or "#general (default)",
    )
    config_table.add_row(
        "GitHub Token",
        "✅ Configured" if github_token else "❌ Missing",
        f"***{github_token[-8:]}" if github_token else "Not set",
    )

    console.print(config_table)

    # Step 4: Test the integration
    console.print("\n🧪 Step 4: Testing Slack Integration")

    try:
        pr_creator = GitHubPRCreator()

        # Show what a Slack notification would look like
        demo_metrics = {
            "ai_completion_metrics": {
                "total_ai_completions": 3,
                "ai_model_used": "CodeYogi AI v2.0",
            },
            "code_optimization_metrics": {
                "performance_improvement_percent": 35.5,
                "build_time_reduction_percent": 42.0,
                "security_issues_fixed": 3,
                "files_optimized": 5,
            },
            "carbon_savings_metrics": {
                "total_co2_saved_kg": 2.456,
                "energy_saved_kwh": 4.91,
                "trees_equivalent": 0.11,
                "carbon_footprint_reduction_percent": 24.6,
            },
            "session_information": {"session_id": "codeyogi-demo-12345"},
        }

        console.print("📱 Sample Slack Notification Preview:")

        # Create a preview of what the Slack message would look like
        slack_preview = f"""
🤖 CodeYogi AI - New PR Created! 🚀

Repository: example/awesome-project
PR Number: #42
Optimization Type: Multi-File Optimization
AI Completions: 3

🎯 Performance Improvements:
• Performance: 35.5% improvement
• Build Time: 42.0% faster  
• Security: 3 issues fixed
• Files Optimized: 5

🌱 Environmental Impact:
• CO2 Saved: 2.456 kg
• Energy Saved: 4.91 kWh
• Trees Equivalent: 0.11 trees
• Carbon Reduction: 24.6%

Session ID: codeyogi-demo-12345 | AI Model: CodeYogi AI v2.0
        """

        console.print(
            Panel(
                slack_preview.strip(),
                title="Slack Message Preview",
                border_style="blue",
            )
        )

        # Test actual notification if configured
        if slack_token and slack_channel:
            console.print("\n🔔 Testing actual Slack notification...")
            success = pr_creator.send_slack_notification(
                pr_url="https://github.com/example/test-repo/pull/42",
                pr_number=42,
                repo_name="example/test-repo",
                metrics=demo_metrics,
                pr_type="demo",
            )

            if success:
                console.print("✅ Test notification sent successfully!")
            else:
                console.print("❌ Test notification failed")
        else:
            console.print(
                "[yellow]⚠️  Slack not configured. Cannot send test notification.[/yellow]"
            )

        return True

    except Exception as e:
        console.print(f"[red]❌ Error testing Slack integration: {str(e)}[/red]")
        return False


def show_environment_setup():
    """Show how to set up environment variables"""

    console.print("\n💡 Environment Setup Instructions")
    console.print("=" * 40)

    # Windows PowerShell
    console.print("\n🪟 Windows PowerShell:")
    console.print("```powershell")
    console.print('$env:SLACK_BOT_TOKEN="xoxb-your-slack-token-here"')
    console.print('$env:SLACK_CHANNEL="#dev-notifications"')
    console.print('$env:GITHUB_TOKEN="ghp_your-github-token-here"')
    console.print("```")

    # Linux/Mac Bash
    console.print("\n🐧 Linux/Mac Bash:")
    console.print("```bash")
    console.print('export SLACK_BOT_TOKEN="xoxb-your-slack-token-here"')
    console.print('export SLACK_CHANNEL="#dev-notifications"')
    console.print('export GITHUB_TOKEN="ghp_your-github-token-here"')
    console.print("```")

    # .env file
    console.print("\n📄 Or create a .env file:")
    console.print("```env")
    console.print("SLACK_BOT_TOKEN=xoxb-your-slack-token-here")
    console.print("SLACK_CHANNEL=#dev-notifications")
    console.print("GITHUB_TOKEN=ghp_your-github-token-here")
    console.print("```")


def show_slack_features():
    """Show the features of the Slack integration"""

    console.print("\n🌟 Slack Integration Features")
    console.print("=" * 35)

    features = [
        "🎯 **Rich Message Formatting** - Interactive blocks with buttons and formatting",
        "📊 **Comprehensive Metrics** - AI completion, performance, and environmental data",
        "🔗 **Direct PR Links** - Click to view PR button in Slack",
        "🌱 **Environmental Impact** - CO2 savings and sustainability metrics",
        "🤖 **AI Insights** - Model used, confidence scores, and processing details",
        "⚡ **Performance Data** - Build time reduction, security fixes, optimization stats",
        "🔔 **Automatic Notifications** - Sent immediately when PR is created",
        "🛡️ **Error Handling** - Graceful fallback when Slack is unavailable",
    ]

    for feature in features:
        console.print(feature)


if __name__ == "__main__":
    console.print("🔔 GitHub PR Creator - Slack Integration Setup")
    console.print("This guide shows how to set up Slack notifications for PR creation")
    console.print("=" * 70)

    # Run the demonstration
    success = demonstrate_slack_integration()

    # Show additional information
    show_environment_setup()
    show_slack_features()

    if success:
        console.print("\n🎉 Slack integration demo completed!")
        console.print("\n📝 Next Steps:")
        console.print("  1. Set up your Slack app with the required permissions")
        console.print("  2. Configure environment variables")
        console.print("  3. Test with a real PR creation")
        console.print("  4. Enjoy automated notifications! 🚀")
    else:
        console.print("\n❌ Setup incomplete - follow the instructions above")
