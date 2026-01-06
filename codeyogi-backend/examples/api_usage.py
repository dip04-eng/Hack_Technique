"""
Example usage of the CodeYogi Repository Analyzer API
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"


def analyze_repository(github_url: str, analysis_type: str = "full") -> Dict[Any, Any]:
    """
    Analyze a GitHub repository using the CodeYogi API

    Args:
        github_url: GitHub repository URL
        analysis_type: Type of analysis ("structure", "cleanup", "optimization", "full")

    Returns:
        Analysis results
    """

    payload = {
        "github_url": github_url,
        "analysis_type": analysis_type,
        "include_dependencies": True,
        "exclude_patterns": [".git", "node_modules", "__pycache__", ".vscode"],
    }

    try:
        response = requests.post(f"{API_BASE_URL}/analyze/", json=payload)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Failed to parse response: {e}")
        return {}


def print_analysis_summary(result: Dict[Any, Any]):
    """Print a summary of the analysis results"""

    if not result:
        print("❌ No analysis results to display")
        return

    repo_info = result.get("repo_info", {})
    metrics = result.get("metrics", {})
    structure_suggestions = result.get("structure_suggestions", [])
    cleanup_suggestions = result.get("cleanup_suggestions", [])
    recommendations = result.get("recommendations", [])

    print(f"\n🔍 Repository Analysis Results")
    print("=" * 50)

    # Repository Info
    print(f"\n📊 Repository: {repo_info.get('name', 'Unknown')}")
    print(f"   Language: {repo_info.get('language', 'Unknown')}")
    print(f"   Size: {repo_info.get('size', 0)} KB")
    print(f"   Stars: {repo_info.get('stars', 0)}")
    print(f"   Last Updated: {repo_info.get('updated_at', 'Unknown')}")

    # Metrics
    print(f"\n📈 Project Metrics:")
    print(f"   Total Files: {metrics.get('total_files', 0)}")
    print(f"   Total Size: {metrics.get('total_size_mb', 0)} MB")
    print(f"   Directories: {metrics.get('directory_count', 0)}")

    file_types = metrics.get("file_types", {})
    if file_types:
        print(f"   File Types:")
        for file_type, count in file_types.items():
            print(f"     - {file_type.replace('_', ' ').title()}: {count}")

    languages = metrics.get("languages", {})
    if languages:
        print(f"   Languages:")
        for language, count in languages.items():
            print(f"     - {language}: {count} files")

    # Structure Suggestions
    print(f"\n🏗️ Structure Suggestions ({len(structure_suggestions)}):")
    if structure_suggestions:
        for i, suggestion in enumerate(structure_suggestions[:5], 1):
            print(f"   {i}. {suggestion['reason']}")
            print(
                f"      {suggestion['current_path']} → {suggestion['suggested_path']}"
            )
            print(f"      Priority: {suggestion['priority']}/5")
    else:
        print("   ✅ No structure improvements needed!")

    # Cleanup Suggestions
    print(f"\n🧹 Cleanup Suggestions ({len(cleanup_suggestions)}):")
    if cleanup_suggestions:
        total_savings = sum(s.get("size_savings", 0) for s in cleanup_suggestions)
        print(f"   💾 Potential Space Savings: {total_savings / 1024:.1f} KB")

        for i, suggestion in enumerate(cleanup_suggestions[:5], 1):
            action = suggestion.get("action", "unknown").title()
            file_path = suggestion.get("file_path", "unknown")
            reason = suggestion.get("reason", "No reason provided")
            risk = suggestion.get("risk_level", "unknown")
            savings = suggestion.get("size_savings", 0)

            print(f"   {i}. {action}: {file_path}")
            print(f"      Reason: {reason}")
            print(f"      Risk: {risk.title()}, Savings: {savings} bytes")
    else:
        print("   ✅ No cleanup needed!")

    # Recommendations
    print(f"\n💡 Recommendations:")
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    else:
        print("   ✅ Your repository is well organized!")


def main():
    """Main example function"""

    print("🚀 CodeYogi Repository Analyzer - Example Usage")
    print("=" * 60)

    # Example repositories to analyze
    examples = [
        {
            "name": "Small Python Project",
            "url": "https://github.com/pallets/flask",
            "type": "structure",
        },
        {
            "name": "JavaScript Project",
            "url": "https://github.com/expressjs/express",
            "type": "cleanup",
        },
    ]

    for example in examples:
        print(f"\n🔍 Analyzing: {example['name']}")
        print(f"URL: {example['url']}")
        print(f"Analysis Type: {example['type']}")

        result = analyze_repository(example["url"], example["type"])
        print_analysis_summary(result)

        print("\n" + "-" * 60)


if __name__ == "__main__":
    print("⚠️  Make sure the CodeYogi server is running:")
    print("   uvicorn main:app --reload")
    print("\nPress Enter to continue or Ctrl+C to exit...")

    try:
        input()
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
