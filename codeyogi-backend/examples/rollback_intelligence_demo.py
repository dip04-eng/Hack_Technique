"""
Rollback Intelligence Demo

This script demonstrates how to use the Rollback Intelligence Agent
to safely rollback deployments with AI-powered recommendations.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from agents.rollback_intelligence_agent import RollbackIntelligenceAgent


def demo_rollback_intelligence():
    """
    Demonstrate the Rollback Intelligence feature
    """
    
    print("=" * 70)
    print("🔄 ROLLBACK INTELLIGENCE DEMO")
    print("=" * 70)
    print()
    
    # Initialize agent
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Error: GITHUB_TOKEN not found in environment")
        print("Please set GITHUB_TOKEN in your .env file")
        return
    
    agent = RollbackIntelligenceAgent(github_token=github_token)
    print("✅ Rollback Intelligence Agent initialized")
    print()
    
    # Example repository (change to your repo)
    repo_owner = input("Enter repository owner (e.g., 'octocat'): ").strip()
    repo_name = input("Enter repository name (e.g., 'Hello-World'): ").strip()
    branch = input("Enter branch (default: main): ").strip() or "main"
    
    print()
    print("-" * 70)
    print("📋 FETCHING ROLLBACK CANDIDATES")
    print("-" * 70)
    print()
    
    # Fetch rollback candidates
    result = agent.get_rollback_candidates(
        repo_owner=repo_owner,
        repo_name=repo_name,
        branch=branch,
        limit=10
    )
    
    if not result.get("success"):
        print(f"❌ Error: {result.get('error')}")
        return
    
    print(f"✅ Found {result['total_candidates']} rollback candidates")
    print(f"📦 Repository: {result['repository']}")
    print(f"🌿 Branch: {result['branch']}")
    print()
    
    # Display AI recommendation
    if result.get("ai_recommendation"):
        rec = result["ai_recommendation"]
        print("🤖 AI RECOMMENDATION:")
        print(f"   Recommended: #{rec['recommended_number']}")
        print(f"   Safety Level: {rec['safety_level']}")
        print(f"   Reason: {rec['reason']}")
        if rec.get('warning'):
            print(f"   ⚠️  Warning: {rec['warning']}")
        print()
    
    # Display candidates
    print("-" * 70)
    print("📝 ROLLBACK CANDIDATES")
    print("-" * 70)
    print()
    
    for candidate in result["candidates"]:
        print(f"#{candidate['number']} {'[CURRENT]' if candidate['is_current'] else ''}")
        print(f"   SHA: {candidate['short_sha']}")
        print(f"   Message: {candidate['message']}")
        print(f"   Author: {candidate['author']}")
        print(f"   Time: {candidate['timestamp_readable']}")
        print(f"   Changes: {candidate['files_changed']} files "
              f"(+{candidate['additions']}/-{candidate['deletions']})")
        print(f"   Status: {candidate['deployment_status']}")
        print()
    
    # Ask user if they want to perform a rollback
    print("-" * 70)
    print("🎯 ROLLBACK SIMULATION")
    print("-" * 70)
    print()
    
    choice = input("Enter commit number to rollback to (or 'skip'): ").strip()
    
    if choice.lower() == 'skip':
        print("⏭️  Skipping rollback simulation")
        return
    
    try:
        rollback_number = int(choice)
    except ValueError:
        print("❌ Invalid input")
        return
    
    if rollback_number == 1:
        print("❌ Cannot rollback to current deployment (commit #1)")
        return
    
    if rollback_number < 1 or rollback_number > len(result["candidates"]):
        print(f"❌ Invalid commit number. Must be between 1 and {len(result['candidates'])}")
        return
    
    print()
    print("🔍 Analyzing rollback safety...")
    print()
    
    # Analyze safety
    safety = agent.analyze_rollback_safety(
        repo_owner=repo_owner,
        repo_name=repo_name,
        rollback_number=rollback_number,
        candidates=result["candidates"]
    )
    
    if "error" in safety:
        print(f"❌ Error: {safety['error']}")
        return
    
    print(f"🛡️  SAFETY ANALYSIS:")
    print(f"   Risk Level: {safety['risk_level']}")
    print(f"   Age: {safety['age_days']} days old")
    
    if safety.get('warnings'):
        print(f"   ⚠️  Warnings:")
        for warning in safety['warnings']:
            print(f"      - {warning}")
    
    print()
    
    if safety.get('requires_confirmation'):
        confirm = input("⚠️  This rollback requires confirmation. Proceed? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Rollback cancelled by user")
            return
        force = True
    else:
        force = False
    
    print()
    print("🚀 Executing rollback (simulation)...")
    print()
    
    # Execute rollback
    exec_result = agent.execute_rollback(
        repo_owner=repo_owner,
        repo_name=repo_name,
        rollback_number=rollback_number,
        branch=branch,
        create_rollback_commit=True,
        force=force
    )
    
    if not exec_result.get("success"):
        print(f"❌ Rollback failed: {exec_result.get('error')}")
        return
    
    print("✅ Rollback prepared successfully!")
    print()
    
    if exec_result.get("target_commit"):
        target = exec_result["target_commit"]
        print(f"🎯 Target Commit:")
        print(f"   SHA: {target['short_sha']}")
        print(f"   Message: {target['message']}")
        print(f"   Author: {target['author']}")
        print()
    
    if exec_result.get("git_instructions"):
        print("📝 Git Instructions:")
        for cmd in exec_result["git_instructions"]["commands"]:
            print(f"   $ {cmd}")
        print()
    
    if exec_result.get("next_steps"):
        print("📋 Next Steps:")
        for step in exec_result["next_steps"]:
            print(f"   {step}")
        print()
    
    print("=" * 70)
    print("✨ Demo completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        demo_rollback_intelligence()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
