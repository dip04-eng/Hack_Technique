import os
import re
import requests
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


def parse_github_url(url: str) -> Dict[str, str]:
    """
    Parse GitHub URL to extract owner and repository name

    Args:
        url: GitHub repository URL

    Returns:
        Dictionary with owner and repo_name
    """
    # Remove .git suffix if present (only at the end)
    if url.endswith(".git"):
        url = url[:-4]

    # Parse URL
    parsed = urlparse(url)

    # Extract path components
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) >= 2:
        return {"owner": path_parts[0], "repo_name": path_parts[1]}
    else:
        raise ValueError("Invalid GitHub URL format")


def validate_github_token(token: Optional[str]) -> bool:
    """
    Validate GitHub token format

    Args:
        token: GitHub personal access token

    Returns:
        True if token format is valid
    """
    if not token:
        return False

    # GitHub tokens are typically 40 characters long
    # Personal access tokens start with 'ghp_'
    # Classic tokens are 40 hex characters
    if token.startswith("ghp_") or (
        len(token) == 40 and re.match(r"^[a-f0-9]+$", token)
    ):
        return True

    return False


def get_github_token() -> Optional[str]:
    """
    Get GitHub token from environment variables

    Returns:
        GitHub token if found, None otherwise
    """
    return os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")


def format_repo_size(size_bytes: int) -> str:
    """
    Format repository size in human-readable format

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_github_url(url: str) -> bool:
    """
    Check if URL is a valid GitHub repository URL

    Args:
        url: URL to check

    Returns:
        True if it's a GitHub URL
    """
    github_patterns = [
        r"https://github\.com/[\w\-\.]+/[\w\-\.]+/?",
        r"git@github\.com:[\w\-\.]+/[\w\-\.]+\.git",
        r"https://github\.com/[\w\-\.]+/[\w\-\.]+\.git",
    ]

    return any(re.match(pattern, url) for pattern in github_patterns)


def get_latest_commit(
    repo_url: str, token: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get the latest commit from a GitHub repository

    Args:
        repo_url: GitHub repository URL
        token: GitHub token for authentication

    Returns:
        Dictionary with latest commit information or None if failed
    """
    try:
        repo_info = parse_github_url(repo_url)
        owner = repo_info["owner"]
        repo_name = repo_info["repo_name"]

        # GitHub API endpoint for latest commit
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodeYogi-Backend",
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        print(f"Fetching commits from: {api_url}")
        print(f"Using token: {'Yes' if token else 'No'}")

        # Get the latest commit (first in the list)
        response = requests.get(f"{api_url}?per_page=1", headers=headers, timeout=10)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            commits = response.json()
            if commits:
                latest_commit = commits[0]
                return {
                    "sha": latest_commit["sha"],
                    "author": latest_commit["commit"]["author"]["name"],
                    "email": latest_commit["commit"]["author"]["email"],
                    "message": latest_commit["commit"]["message"],
                    "date": latest_commit["commit"]["author"]["date"],
                    "url": latest_commit["html_url"],
                    "tree_sha": latest_commit["commit"]["tree"]["sha"],
                }
        else:
            print(f"GitHub API error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error fetching latest commit: {str(e)}")

    return None


def check_for_new_push(
    repo_url: str, last_known_sha: Optional[str] = None, token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Check if there's a new push to the repository since the last known commit

    Args:
        repo_url: GitHub repository URL
        last_known_sha: SHA of the last known commit
        token: GitHub token for authentication

    Returns:
        Dictionary with push status and commit information
    """
    latest_commit = get_latest_commit(repo_url, token)

    if not latest_commit:
        return {"has_new_push": False, "error": "Could not fetch latest commit"}

    has_new_push = last_known_sha is None or latest_commit["sha"] != last_known_sha

    return {
        "has_new_push": has_new_push,
        "latest_commit": latest_commit,
        "previous_sha": last_known_sha,
    }
