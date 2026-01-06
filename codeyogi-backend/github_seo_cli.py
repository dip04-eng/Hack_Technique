#!/usr/bin/env python3
"""
GitHub SEO Optimizer CLI

A command-line tool to automatically optimize GitHub repositories for SEO.

Usage:
    python github_seo_cli.py <github_url>

Example:
    python github_seo_cli.py https://github.com/username/repository

Features:
- Analyzes repository content
- Generates AI-powered SEO metadata
- Optimizes HTML files with meta tags
- Creates SEO-friendly README.md
- Automatically creates pull request with improvements
"""

import sys
import asyncio
import os
from pathlib import Path

# Add the parent directory to path to import agents
sys.path.append(str(Path(__file__).parent))

from agents.seo_injector import optimize_github_repository_seo


def print_usage():
    """Print usage instructions"""
    print("GitHub SEO Optimizer CLI")
    print("=" * 30)
    print()
    print("Usage:")
    print("  python github_seo_cli.py <github_url>")
    print()
    print("Example:")
    print("  python github_seo_cli.py https://github.com/username/repository")
    print()
    print("Prerequisites:")
    print("  1. Create a .env file with:")
    print("     GITHUB_TOKEN=your_github_token")
    print("     GEMINI_API_KEY=your_gemini_api_key")
    print("  2. Install dependencies: pip install -r requirements.txt")


def check_environment():
    """Check if required environment variables are set"""
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment variables")
        print("   Get one at: https://github.com/settings/tokens")
        return False

    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("   Get one at: https://ai.google.dev/")
        return False

    return True


async def main():
    """Main CLI function"""
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    github_url = sys.argv[1]

    # Validate URL format
    if not github_url.startswith("http"):
        print("❌ Please provide a valid GitHub URL starting with http or https")
        sys.exit(1)

    if "github.com" not in github_url:
        print("❌ Please provide a valid GitHub repository URL")
        sys.exit(1)

    # Check environment
    if not check_environment():
        sys.exit(1)

    print("🚀 GitHub SEO Optimizer")
    print("=" * 40)
    print(f"🎯 Target Repository: {github_url}")
    print()

    try:
        # Run optimization
        result = await optimize_github_repository_seo(github_url)

        if result.get("success"):
            print()
            print("✅ SEO Optimization Complete!")
            print("=" * 40)
            print(f"📁 Repository: {result['repository']}")
            print(f"📝 Files Modified: {result['modified_files']}")
            print(f"🌐 HTML Files: {result['html_files_processed']}")
            print(f"🌿 Branch: {result['branch_name']}")

            if result.get("pull_request_url"):
                print(f"🔗 Pull Request: {result['pull_request_url']}")
                print()
                print("🎉 Success! A pull request has been created.")
                print("   Review and merge the changes when ready.")

            print()
            print("📊 SEO Metadata Generated:")
            metadata = result["seo_metadata"]
            print(f"   Title: {metadata.get('title', 'N/A')}")
            print(f"   Description: {metadata.get('description', 'N/A')}")
            print(f"   Keywords: {', '.join(metadata.get('keywords', []))}")

        else:
            print()
            print("❌ Optimization Failed")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
