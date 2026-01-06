#!/usr/bin/env python3
"""
Example usage of the new Workflow Optimization with Deployment endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


def optimize_repository_workflow():
    """
    Example: Optimize a repository's workflow and automatically create a PR
    """

    # Configuration
    api_base_url = "http://localhost:8000"  # Adjust if running on different host/port
    github_token = os.getenv("GITHUB_TOKEN")  # Make sure this is set in your .env file

    if not github_token:
        print("❌ Please set GITHUB_TOKEN in your .env file")
        return

    # Repository to optimize (replace with your repository)
    repo_url = "https://github.com/your-username/your-repo"

    # Request payload
    payload = {
        "repo_url": repo_url,
        "github_token": github_token,
        "branch_name": "codeyogi-workflow-optimization",  # Optional: custom branch name
        "workflow_path": ".github/workflows/codeyogi-optimized.yml",  # Optional: custom path
        "commit_message": "🚀 CodeYogi: Optimize CI/CD workflow for better performance",  # Optional
        "auto_merge": False,  # Optional: set to True if you want to attempt auto-merge (requires permissions)
    }

    print("🤖 CodeYogi Workflow Optimization with Deployment")
    print("=" * 50)
    print(f"📁 Repository: {repo_url}")
    print(f"🌿 Branch: {payload['branch_name']}")
    print(f"📝 Workflow Path: {payload['workflow_path']}")
    print("\n🚀 Starting optimization and deployment...")

    try:
        # Make the API call
        response = requests.post(
            f"{api_base_url}/workflow-optimization/",
            json=payload,
            timeout=300,  # 5 minute timeout for analysis
        )

        if response.status_code == 200:
            result = response.json()

            if result["success"]:
                print("\n✅ Workflow optimization and PR creation successful!")

                # PR Information
                pr_info = result.get("pr_info", {})
                if pr_info:
                    print(f"\n🎉 Pull Request Created:")
                    print(f"   🔗 URL: {pr_info.get('pr_url')}")
                    print(f"   📊 PR Number: #{pr_info.get('pr_number')}")
                    print(f"   🌿 Branch: {pr_info.get('branch_name')}")
                    print(f"   📝 Commit: {pr_info.get('commit_sha', '')[:8]}...")

                # Optimization Analysis Summary
                analysis = result.get("optimization_analysis", {})
                if analysis:
                    repo_info = analysis.get("repository", {})
                    analysis_data = analysis.get("analysis", {})
                    optimized_workflow = analysis.get("optimized_workflow", {})

                    print(f"\n📊 Optimization Analysis:")
                    print(f"   🏷️  Language: {repo_info.get('language', 'Unknown')}")
                    print(
                        f"   🔧 Framework: {analysis_data.get('framework_type', 'Generic')}"
                    )
                    print(
                        f"   📈 Optimization Score: {analysis_data.get('optimization_score', 'N/A')}/100"
                    )
                    print(
                        f"   ⚡ Estimated Time Savings: {optimized_workflow.get('estimated_time_savings', 'Optimized')}"
                    )
                    print(
                        f"   🎯 AI Confidence: {optimized_workflow.get('confidence_score', 'N/A')}/100"
                    )

                    # Show key improvements
                    improvements = optimized_workflow.get("improvements", [])
                    if improvements:
                        print(f"\n🚀 Key Improvements:")
                        for improvement in improvements[:5]:  # Show first 5
                            print(f"   • {improvement}")

                print(f"\n💡 Next Steps:")
                print(
                    f"   1. Review the pull request at: {pr_info.get('pr_url', 'GitHub')}"
                )
                print(
                    f"   2. Test the optimized workflow in your development environment"
                )
                print(f"   3. Merge the PR when ready to apply the optimizations")
                print(f"   4. Monitor the improved CI/CD performance")

            else:
                print(
                    f"\n❌ Optimization failed: {result.get('error_message', 'Unknown error')}"
                )

        else:
            print(f"\n❌ API request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {error_detail.get('detail', response.text)}")
            except:
                print(f"Error: {response.text}")

    except requests.RequestException as e:
        print(f"\n❌ Network error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


def show_api_documentation():
    """Show API endpoint documentation"""

    print("\n📚 API Documentation")
    print("=" * 30)
    print("Endpoint: POST /workflow-optimization/")
    print("\nRequest Body:")
    print(
        json.dumps(
            {
                "repo_url": "https://github.com/owner/repo",
                "github_token": "your_github_token",
                "branch_name": "codeyogi-workflow-optimization",  # Optional
                "workflow_path": ".github/workflows/codeyogi-optimized.yml",  # Optional
                "commit_message": "🚀 CodeYogi: Optimize CI/CD workflow",  # Optional
                "auto_merge": False,  # Optional
            },
            indent=2,
        )
    )

    print("\nResponse:")
    print(
        json.dumps(
            {
                "success": True,
                "optimization_analysis": "{ ... comprehensive analysis ... }",
                "pr_info": {
                    "pr_url": "https://github.com/owner/repo/pull/123",
                    "pr_number": 123,
                    "branch_name": "codeyogi-workflow-optimization",
                    "commit_sha": "abc123...",
                },
                "timestamp": "2024-01-01T12:00:00Z",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--docs":
        show_api_documentation()
    else:
        optimize_repository_workflow()
