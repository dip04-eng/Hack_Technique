#!/usr/bin/env python3
"""
Example Usage of the Enhanced GitHub SEO Optimizer

This script demonstrates how to use the GitHub SEO Optimizer to:
1. Take a GitHub repository URL
2. Clone and analyze the repository
3. Generate SEO metadata using AI
4. Inject SEO improvements into HTML files
5. Create an optimized README.md
6. Automatically create a pull request with the changes

Prerequisites:
- Set up your .env file with GITHUB_TOKEN and GEMINI_API_KEY
- Install dependencies: pip install -r requirements.txt
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the agents directory to the path so we can import the seo_injector
sys.path.append(str(Path(__file__).parent / "agents"))

from seo_injector import optimize_github_repository_seo


async def demo_seo_optimization():
    """
    Demonstrate the GitHub SEO optimization process
    """
    print("🚀 GitHub SEO Optimizer Demo")
    print("=" * 50)

    # Example GitHub URLs (you can replace with any public repository)
    example_repos = [
        "https://github.com/microsoft/vscode",
        "https://github.com/facebook/react",
        "https://github.com/openai/openai-python",
        # Add your own repository URL here
    ]

    print("Available example repositories:")
    for i, repo in enumerate(example_repos, 1):
        print(f"{i}. {repo}")

    print("\nOptions:")
    print("1. Enter a number to use one of the example repositories")
    print("2. Enter a custom GitHub URL")
    print("3. Type 'quit' to exit")

    user_input = input("\nYour choice: ").strip()

    if user_input.lower() == "quit":
        print("Goodbye!")
        return

    # Determine the repository URL
    github_url = None
    if user_input.isdigit():
        choice = int(user_input)
        if 1 <= choice <= len(example_repos):
            github_url = example_repos[choice - 1]
        else:
            print("Invalid choice number!")
            return
    elif user_input.startswith("http"):
        github_url = user_input
    else:
        print("Invalid input! Please enter a number or a GitHub URL.")
        return

    print(f"\n🎯 Starting SEO optimization for: {github_url}")
    print("-" * 50)

    # Run the SEO optimization
    try:
        result = await optimize_github_repository_seo(github_url)

        if result.get("success"):
            print("\n✅ SEO Optimization Completed Successfully!")
            print("=" * 50)
            print(f"📁 Repository: {result['repository']}")
            print(f"📝 Files Modified: {result['modified_files']}")
            print(f"🌐 HTML Files Processed: {result['html_files_processed']}")
            print(f"🌿 Branch Created: {result['branch_name']}")

            if result.get("pull_request_url"):
                print(f"🔗 Pull Request: {result['pull_request_url']}")
                print("\n🎉 A pull request has been created with the SEO improvements!")
                print("Review the changes and merge when ready.")

            print("\n📊 Generated SEO Metadata:")
            metadata = result["seo_metadata"]
            print(f"  📝 Title: {metadata.get('title', 'N/A')}")
            print(f"  📖 Description: {metadata.get('description', 'N/A')}")
            print(f"  🏷️  Keywords: {', '.join(metadata.get('keywords', []))}")

            if metadata.get("og_title"):
                print(f"  📱 Social Title: {metadata.get('og_title')}")
            if metadata.get("og_description"):
                print(f"  📱 Social Description: {metadata.get('og_description')}")

        else:
            print(f"\n❌ SEO Optimization Failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")

    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


def check_environment():
    """
    Check if the required environment variables are set up
    """
    required_env_vars = ["GITHUB_TOKEN", "GEMINI_API_KEY"]
    missing_vars = []

    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the following format:")
        print("GITHUB_TOKEN=your_github_token_here")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("\nTo get these tokens:")
        print("- GitHub Token: https://github.com/settings/tokens")
        print("- Gemini API Key: https://ai.google.dev/")
        return False

    return True


if __name__ == "__main__":
    print("🔧 GitHub SEO Optimizer - Example Usage")
    print("=" * 50)

    # Check environment setup
    if not check_environment():
        sys.exit(1)

    print("✅ Environment variables configured")
    print("🚀 Starting demo...")
    print()

    # Run the demo
    asyncio.run(demo_seo_optimization())
