"""
Quick Start Guide - Post-Deploy Failure Analysis

This script helps you get started with the Post-Deploy Failure Analysis feature.
Run this after setting up your environment.

Author: CodeYogi Platform
"""

import os
import sys


def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...\n")
    
    issues = []
    
    # Check for .env file
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_file):
        issues.append("❌ .env file not found")
        print("❌ .env file not found")
        print("   Create a .env file with: GROQ_API_KEY=your_api_key_here\n")
    else:
        print("✅ .env file exists\n")
    
    # Check for GROQ_API_KEY
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        issues.append("❌ GROQ_API_KEY not set")
        print("❌ GROQ_API_KEY environment variable not set")
        print("   Add to .env: GROQ_API_KEY=gsk_your_key_here\n")
    else:
        print(f"✅ GROQ_API_KEY is set (length: {len(groq_key)} chars)\n")
    
    # Check for required packages
    try:
        import fastapi
        print("✅ FastAPI installed\n")
    except ImportError:
        issues.append("❌ FastAPI not installed")
        print("❌ FastAPI not installed")
        print("   Run: pip install -r requirements.txt\n")
    
    try:
        import groq
        print("✅ Groq SDK installed\n")
    except ImportError:
        issues.append("❌ Groq SDK not installed")
        print("❌ Groq SDK not installed")
        print("   Run: pip install groq\n")
    
    # Check if agent exists
    agent_file = os.path.join(os.path.dirname(__file__), 'agents', 'deploy_failure_analyzer.py')
    if os.path.exists(agent_file):
        print("✅ Deploy Failure Analyzer agent exists\n")
    else:
        issues.append("❌ Agent file missing")
        print("❌ Deploy Failure Analyzer agent not found\n")
    
    return len(issues) == 0


def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 80)
    print("  POST-DEPLOY FAILURE ANALYSIS - QUICK START GUIDE")
    print("=" * 80 + "\n")
    
    print("📚 STEP 1: Start the Backend Server")
    print("-" * 80)
    print("Option A - Using Python directly:")
    print("   cd codeyogi-backend")
    print("   python main.py")
    print("\nOption B - Using uvicorn:")
    print("   cd codeyogi-backend")
    print("   uvicorn main:app --reload --port 8000")
    print()
    
    print("📚 STEP 2: Test the API Endpoint")
    print("-" * 80)
    print("Run the test script:")
    print("   python test_deploy_failure_api.py")
    print()
    
    print("📚 STEP 3: Use the Feature")
    print("-" * 80)
    print("Option A - Frontend UI:")
    print("   1. Start the frontend: cd CodeYogi_Frontend && npm run dev")
    print("   2. Navigate to the CodeYogi UI")
    print("   3. Click 'Deploy Failure Analysis' in the Quick Actions sidebar")
    print("   4. Paste your git diff and runtime logs")
    print("   5. Click 'Analyze Root Cause'")
    print("\nOption B - Direct API Call:")
    print("   curl -X POST http://localhost:8000/api/post-deploy-analysis \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "git_diff": "diff --git a/file.py...",')
    print('       "runtime_logs": "[ERROR] Production error...",')
    print('       "deployment_env": "production"')
    print("     }'")
    print()
    
    print("📚 STEP 4: Run Demo Examples")
    print("-" * 80)
    print("See examples with realistic failure scenarios:")
    print("   python examples/deploy_failure_analysis_demo.py")
    print()
    
    print("📖 DOCUMENTATION")
    print("-" * 80)
    print("Read the full documentation:")
    print("   README_DEPLOY_FAILURE_ANALYSIS.md")
    print()
    
    print("🎯 API ENDPOINT")
    print("-" * 80)
    print("Endpoint: POST /api/post-deploy-analysis")
    print("Request:")
    print("   {")
    print('     "git_diff": "required - git diff content",')
    print('     "runtime_logs": "required - production error logs",')
    print('     "pipeline_logs": "optional - CI/CD logs",')
    print('     "deployment_env": "optional - default: production"')
    print("   }")
    print("\nResponse:")
    print("   {")
    print('     "success": true,')
    print('     "summary": "One-line failure explanation",')
    print('     "root_cause": "Detailed root cause",')
    print('     "affected_file": "file.py",')
    print('     "affected_line": "function_name()",')
    print('     "impact": "User-facing impact",')
    print('     "confidence": 0.95,')
    print('     "suggested_fix": "Concrete fix recommendation",')
    print('     "detected_patterns": {...}')
    print("   }")
    print()


def main():
    """Main execution"""
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║       CodeYogi - Post-Deploy Failure Analysis Setup Checker           ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    if check_environment():
        print("=" * 80)
        print("✅ Environment is properly configured!")
        print("=" * 80)
        print_instructions()
        print("\n🚀 You're ready to use Post-Deploy Failure Analysis!\n")
    else:
        print("=" * 80)
        print("⚠️  Environment configuration incomplete")
        print("=" * 80)
        print("\nPlease fix the issues above before proceeding.\n")
        print("💡 Quick fixes:")
        print("   1. Create .env file: cp .env.example .env")
        print("   2. Add your Groq API key to .env")
        print("   3. Install dependencies: pip install -r requirements.txt\n")


if __name__ == "__main__":
    main()
