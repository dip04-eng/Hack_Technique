#!/usr/bin/env python3
"""
GitHub Token Setup Helper
Helps users configure their GitHub token for CodeYogi workflow optimization
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
from github import Github
import getpass


def check_token_validity(token: str) -> tuple[bool, str]:
    """
    Check if a GitHub token is valid

    Args:
        token: GitHub personal access token

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        g = Github(token)
        user = g.get_user()
        return True, f"✅ Token is valid! Authenticated as: {user.login}"
    except Exception as e:
        return False, f"❌ Token validation failed: {str(e)}"


def check_token_permissions(token: str) -> tuple[bool, str]:
    """
    Check if token has required permissions

    Args:
        token: GitHub personal access token

    Returns:
        Tuple of (has_permissions, message)
    """
    try:
        g = Github(token)
        # Try to access a repository to check permissions
        # This is a basic check - for full validation we'd need to test specific scopes
        user = g.get_user()
        repos = list(user.get_repos(type="owner")[:1])  # Get just one repo to test

        if repos:
            repo = repos[0]
            # Try to get workflows to check workflow permissions
            try:
                workflows = list(repo.get_workflows())
                return True, "✅ Token has required repository and workflow permissions"
            except Exception:
                return (
                    False,
                    "❌ Token lacks workflow permissions. Please ensure 'workflow' scope is enabled.",
                )
        else:
            return True, "✅ Token is valid (no repositories found to test permissions)"

    except Exception as e:
        return False, f"❌ Permission check failed: {str(e)}"


def setup_github_token():
    """
    Interactive setup for GitHub token
    """
    print("🔧 GitHub Token Setup for CodeYogi")
    print("=" * 40)
    print()

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("📄 Creating .env file from template...")
        env_example = Path(".env.example")
        if env_example.exists():
            with open(env_example, "r") as f:
                content = f.read()
            with open(env_file, "w") as f:
                f.write(content)
            print("✅ Created .env file")
        else:
            print("⚠️  No .env.example found, creating basic .env file")
            with open(env_file, "w") as f:
                f.write(
                    "# CodeYogi Configuration\nGITHUB_TOKEN=your_github_token_here\n"
                )

    # Load current environment
    load_dotenv()
    current_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    if current_token and current_token != "your_github_token_here":
        print(f"🔍 Found existing token: {current_token[:8]}...{current_token[-4:]}")

        # Validate existing token
        is_valid, message = check_token_validity(current_token)
        print(message)

        if is_valid:
            has_perms, perm_message = check_token_permissions(current_token)
            print(perm_message)

            if has_perms:
                print("\n✅ Your GitHub token is properly configured!")
                return True

        print("\n❓ Would you like to update your token? (y/N): ", end="")
        if input().lower() != "y":
            return False

    print("\n📋 GitHub Token Setup Instructions:")
    print("1. Go to: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name like 'CodeYogi Workflow Optimizer'")
    print("4. Select these scopes:")
    print("   ✓ repo (Full control of repositories)")
    print("   ✓ workflow (Update GitHub Action workflows)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (it starts with 'ghp_')")
    print()

    # Get token from user
    token = getpass.getpass("🔑 Paste your GitHub token here: ").strip()

    if not token:
        print("❌ No token provided")
        return False

    # Validate token
    is_valid, message = check_token_validity(token)
    print(message)

    if not is_valid:
        return False

    # Check permissions
    has_perms, perm_message = check_token_permissions(token)
    print(perm_message)

    if not has_perms:
        print("\n⚠️  Token is valid but may lack required permissions.")
        print("❓ Do you want to save it anyway? (y/N): ", end="")
        if input().lower() != "y":
            return False

    # Save token to .env file
    try:
        set_key(env_file, "GITHUB_TOKEN", token)
        print("✅ Token saved to .env file")

        # Also set in current environment
        os.environ["GITHUB_TOKEN"] = token

        print("\n🎉 GitHub token setup complete!")
        print("You can now use the workflow optimization with deployment feature.")
        return True

    except Exception as e:
        print(f"❌ Failed to save token: {str(e)}")
        return False


def test_token():
    """
    Test the current GitHub token configuration
    """
    print("🧪 Testing GitHub Token Configuration")
    print("=" * 35)

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    if not token:
        print("❌ No GitHub token found in environment")
        print("Run: python setup_github_token.py --setup")
        return False

    print(f"🔍 Found token: {token[:8]}...{token[-4:]}")

    # Test validity
    is_valid, message = check_token_validity(token)
    print(message)

    if not is_valid:
        return False

    # Test permissions
    has_perms, perm_message = check_token_permissions(token)
    print(perm_message)

    if has_perms:
        print("\n✅ All tests passed! Your token is ready for use.")
        return True
    else:
        print("\n⚠️  Token validation completed with warnings.")
        return False


def show_help():
    """
    Show help information
    """
    print("🔧 GitHub Token Setup Helper")
    print("=" * 30)
    print()
    print("Usage:")
    print("  python setup_github_token.py --setup    Interactive token setup")
    print("  python setup_github_token.py --test     Test current token")
    print("  python setup_github_token.py --help     Show this help")
    print()
    print("The token needs these GitHub permissions:")
    print("  • repo (Full control of repositories)")
    print("  • workflow (Update GitHub Action workflows)")
    print()
    print("Create a token at: https://github.com/settings/tokens")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--setup":
            setup_github_token()
        elif sys.argv[1] == "--test":
            test_token()
        elif sys.argv[1] == "--help":
            show_help()
        else:
            print("❌ Unknown option. Use --help for usage information.")
    else:
        # Default to setup if no arguments
        setup_github_token()
