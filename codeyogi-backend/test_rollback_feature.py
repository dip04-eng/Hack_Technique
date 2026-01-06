import asyncio
import httpx
from datetime import datetime

async def test_rollback_flow():
    """Complete test of rollback feature"""
    
    base_url = "http://localhost:8000"
    repo_owner = "Asif556"
    repo_name = "Vista-Js"
    branch = "main"
    
    print("🧪 Starting Rollback Intelligence Test\n")
    
    # Step 1: Get rollback candidates
    print("📋 Step 1: Fetching rollback candidates...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{base_url}/api/rollback/candidates",
            json={
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "branch": branch,
                "limit": 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('candidates', []))} commits")
            
            if data.get('candidates'):
                # Get second commit (not current)
                target_commit = data['candidates'][1] if len(data['candidates']) > 1 else data['candidates'][0]
                print(f"\n🎯 Target commit: {target_commit['sha'][:7]}")
                print(f"   Message: {target_commit['message']}")
                print(f"   Author: {target_commit['author']}")
                
                # Step 2: Safety check
                print("\n🛡️ Step 2: Running safety check...")
                safety_response = await client.post(
                    f"{base_url}/api/rollback/safety-check",
                    json={
                        "repo_owner": repo_owner,
                        "repo_name": repo_name,
                        "rollback_number": 2,  # Using commit #2
                        "branch": branch
                    }
                )
                
                if safety_response.status_code == 200:
                    safety_data = safety_response.json()
                    print(f"✅ Safety check complete")
                    print(f"   Risk Level: {safety_data.get('risk_level', 'UNKNOWN')}")
                    print(f"   Recommendation: {safety_data.get('recommendation', 'N/A')}")
                    
                    if safety_data.get('warnings'):
                        print(f"   ⚠️ Warnings: {', '.join(safety_data['warnings'])}")
                    
                    # Step 3: Execute rollback
                    print("\n🔄 Step 3: Executing rollback...")
                    print("⏳ This may take 10-15 seconds...")
                    
                    rollback_response = await client.post(
                        f"{base_url}/api/rollback/execute",
                        json={
                            "repo_owner": repo_owner,
                            "repo_name": repo_name,
                            "rollback_number": 2,  # Rollback to commit #2
                            "branch": branch,
                            "force": False
                        },
                        timeout=30.0
                    )
                    
                    if rollback_response.status_code == 200:
                        rollback_data = rollback_response.json()
                        
                        if r
                            # Check for pull_request details
                            pr_info = rollback_data.get('pull_request', {})
                            if pr_info:
                                print(f"✅ PR Created: {pr_info.get('url')}")
                                print(f"✅ PR Number: #{pr_info.get('number')}")
                                print(f"✅ Branch: {pr_info.get('branch')}")
                                print(f"\n📝 Next steps:")
                                print(f"   1. Open: {pr_info.get('url')}")
                                print(f"   2. Review the changes")
                                print(f"   3. Merge the PR to complete rollback")
                            elif rollback_data.get('manual_pr_link'):
                                print(f"⚠️ Manual PR creation required")
                                print(f"🔗 Link: {rollback_data.get('manual_pr_link')}")
                                print(f"\n📝 Click the link to create PR manually")
                            ")
                            print(f"   2. Review the changes")
                            print(f"   3. Merge the PR to complete rollback")
                            return True
                        else:
                            print(f"\n❌ Rollback failed: {rollback_data.get('message')}")
                            return False
                    else:
                        print(f"\n❌ Rollback request failed: {rollback_response.status_code}")
                        print(f"   Error: {rollback_response.text}")
                        return False
                else:
                    print(f"\n❌ Safety check failed: {safety_response.status_code}")
                    return False
            else:
                print("❌ No commits found for rollback")
                return False
        else:
            print(f"❌ Failed to fetch candidates: {response.status_code}")
            print(f"   Error: {response.text}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔄 ROLLBACK INTELLIGENCE FEATURE TEST")
    print("=" * 60)
    print()
    
    try:
        result = asyncio.run(test_rollback_flow())
        print("\n" + "=" * 60)
        if result:
            print("✅ TEST PASSED - Rollback feature is working!")
        else:
            print("❌ TEST FAILED - Check errors above")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test crashed: {str(e)}")
        import traceback
        traceback.print_exc()