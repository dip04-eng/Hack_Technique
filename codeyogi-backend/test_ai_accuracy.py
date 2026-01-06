"""
AI Accuracy Testing Script for CodeYogi
Tests all AI features and measures their accuracy, response time, and performance
"""

import os
import sys
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
from groq import Groq
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Import agents
from agents.ai_analyzer import GroqAIAnalyzer
# from agents.repo_analyzer import RepoAnalyzer
# from agents.workflow_optimizer import WorkflowOptimizer
# from agents.deploy_failure_analyzer import DeployFailureAnalyzer
# from agents.repo_description_agent import RepoDescriptionAgent


class AIAccuracyTester:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # Initialize metrics storage
        self.metrics = {
            "groq": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_response_time": 0,
                "response_times": [],
                "model_used": "llama-3.3-70b-versatile",
                "features_tested": []
            },
            "gemini": {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_response_time": 0,
                "response_times": [],
                "model_used": "gemini-1.5-flash",
                "features_tested": []
            }
        }
        
        # Initialize clients
        if self.groq_api_key:
            self.groq_client = Groq(api_key=self.groq_api_key)
        else:
            self.groq_client = None
            
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.gemini_model = None

    def print_header(self, text: str):
        """Print a formatted header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")

    def print_section(self, text: str):
        """Print a formatted section"""
        print("\n" + "-"*80)
        print(f"  {text}")
        print("-"*80)

    async def test_groq_basic_connection(self) -> Dict:
        """Test basic Groq API connection"""
        self.print_section("Testing Groq API Basic Connection")
        
        if not self.groq_client:
            print("❌ Groq API key not found")
            return {"success": False, "error": "No API key"}
        
        try:
            start_time = time.time()
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello, CodeYogi!' in exactly those words."}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            response_time = time.time() - start_time
            response_text = response.choices[0].message.content.strip()
            
            # Track metrics
            self.metrics["groq"]["total_requests"] += 1
            self.metrics["groq"]["response_times"].append(response_time)
            self.metrics["groq"]["total_response_time"] += response_time
            
            # Check if response is correct
            success = "hello" in response_text.lower() and "codeyogi" in response_text.lower()
            
            if success:
                self.metrics["groq"]["successful_requests"] += 1
                print(f"✅ Groq API Connection: SUCCESS")
                print(f"   Response: {response_text}")
                print(f"   Response Time: {response_time:.2f}s")
                print(f"   Model: {response.model}")
            else:
                self.metrics["groq"]["failed_requests"] += 1
                print(f"❌ Unexpected response: {response_text}")
            
            return {
                "success": success,
                "response_time": response_time,
                "response": response_text,
                "model": response.model
            }
            
        except Exception as e:
            self.metrics["groq"]["failed_requests"] += 1
            self.metrics["groq"]["total_requests"] += 1
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def test_gemini_basic_connection(self) -> Dict:
        """Test basic Gemini API connection"""
        self.print_section("Testing Gemini API Basic Connection")
        
        if not self.gemini_model:
            print("❌ Gemini API key not found")
            return {"success": False, "error": "No API key"}
        
        try:
            start_time = time.time()
            
            response = self.gemini_model.generate_content("Say 'Hello, CodeYogi!' in exactly those words.")
            
            response_time = time.time() - start_time
            response_text = response.text.strip()
            
            # Track metrics
            self.metrics["gemini"]["total_requests"] += 1
            self.metrics["gemini"]["response_times"].append(response_time)
            self.metrics["gemini"]["total_response_time"] += response_time
            
            # Check if response is correct
            success = "hello" in response_text.lower() and "codeyogi" in response_text.lower()
            
            if success:
                self.metrics["gemini"]["successful_requests"] += 1
                print(f"✅ Gemini API Connection: SUCCESS")
                print(f"   Response: {response_text}")
                print(f"   Response Time: {response_time:.2f}s")
            else:
                self.metrics["gemini"]["failed_requests"] += 1
                print(f"❌ Unexpected response: {response_text}")
            
            return {
                "success": success,
                "response_time": response_time,
                "response": response_text
            }
            
        except Exception as e:
            self.metrics["gemini"]["failed_requests"] += 1
            self.metrics["gemini"]["total_requests"] += 1
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def test_code_analysis_accuracy(self) -> Dict:
        """Test code analysis feature accuracy"""
        self.print_section("Testing Code Analysis Accuracy")
        
        test_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# This is inefficient recursive implementation
result = calculate_fibonacci(10)
print(result)
"""
        
        try:
            start_time = time.time()
            
            prompt = f"""Analyze this Python code and identify issues:
{test_code}

Expected issues: 
1. Inefficient recursive algorithm (no memoization)
2. No input validation
3. Will cause stack overflow for large n

List the issues you find."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            response_time = time.time() - start_time
            analysis = response.choices[0].message.content
            
            # Check if it identified key issues
            checks = {
                "identified_recursion_issue": "recursi" in analysis.lower() and ("inefficient" in analysis.lower() or "memoization" in analysis.lower()),
                "identified_performance": "performance" in analysis.lower() or "slow" in analysis.lower() or "time complexity" in analysis.lower(),
                "identified_stack_overflow": "stack" in analysis.lower() and "overflow" in analysis.lower()
            }
            
            accuracy = sum(checks.values()) / len(checks) * 100
            
            self.metrics["groq"]["total_requests"] += 1
            self.metrics["groq"]["response_times"].append(response_time)
            self.metrics["groq"]["total_response_time"] += response_time
            self.metrics["groq"]["features_tested"].append("code_analysis")
            
            if accuracy >= 66:
                self.metrics["groq"]["successful_requests"] += 1
                print(f"✅ Code Analysis Accuracy: {accuracy:.1f}%")
            else:
                self.metrics["groq"]["failed_requests"] += 1
                print(f"⚠️  Code Analysis Accuracy: {accuracy:.1f}% (Below threshold)")
            
            print(f"   Response Time: {response_time:.2f}s")
            print(f"   Checks Passed: {sum(checks.values())}/{len(checks)}")
            print(f"   - Recursion Issue: {'✅' if checks['identified_recursion_issue'] else '❌'}")
            print(f"   - Performance Issue: {'✅' if checks['identified_performance'] else '❌'}")
            print(f"   - Stack Overflow Risk: {'✅' if checks['identified_stack_overflow'] else '❌'}")
            
            return {
                "success": accuracy >= 66,
                "accuracy": accuracy,
                "response_time": response_time,
                "checks": checks
            }
            
        except Exception as e:
            self.metrics["groq"]["failed_requests"] += 1
            self.metrics["groq"]["total_requests"] += 1
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def test_workflow_optimization_accuracy(self) -> Dict:
        """Test workflow optimization accuracy"""
        self.print_section("Testing Workflow Optimization Accuracy")
        
        test_workflow = """
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test
"""
        
        try:
            start_time = time.time()
            
            prompt = f"""Analyze this GitHub Actions workflow and suggest optimizations:
{test_workflow}

Expected optimizations:
1. Add caching for node_modules
2. Use latest action versions
3. Add parallel jobs if possible
4. Optimize checkout (shallow clone)

Provide optimization suggestions."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a CI/CD optimization expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            response_time = time.time() - start_time
            suggestions = response.choices[0].message.content
            
            # Check if it suggested key optimizations
            checks = {
                "suggested_caching": "cach" in suggestions.lower(),
                "suggested_version_update": "v3" in suggestions or "latest" in suggestions.lower() or "update" in suggestions.lower(),
                "mentioned_performance": "performance" in suggestions.lower() or "faster" in suggestions.lower() or "speed" in suggestions.lower()
            }
            
            accuracy = sum(checks.values()) / len(checks) * 100
            
            self.metrics["groq"]["total_requests"] += 1
            self.metrics["groq"]["response_times"].append(response_time)
            self.metrics["groq"]["total_response_time"] += response_time
            self.metrics["groq"]["features_tested"].append("workflow_optimization")
            
            if accuracy >= 66:
                self.metrics["groq"]["successful_requests"] += 1
                print(f"✅ Workflow Optimization Accuracy: {accuracy:.1f}%")
            else:
                self.metrics["groq"]["failed_requests"] += 1
                print(f"⚠️  Workflow Optimization Accuracy: {accuracy:.1f}% (Below threshold)")
            
            print(f"   Response Time: {response_time:.2f}s")
            print(f"   Checks Passed: {sum(checks.values())}/{len(checks)}")
            print(f"   - Caching Suggested: {'✅' if checks['suggested_caching'] else '❌'}")
            print(f"   - Version Updates: {'✅' if checks['suggested_version_update'] else '❌'}")
            print(f"   - Performance Focus: {'✅' if checks['mentioned_performance'] else '❌'}")
            
            return {
                "success": accuracy >= 66,
                "accuracy": accuracy,
                "response_time": response_time,
                "checks": checks
            }
            
        except Exception as e:
            self.metrics["groq"]["failed_requests"] += 1
            self.metrics["groq"]["total_requests"] += 1
            print(f"❌ Error: {str(e)}")
            return {"success": False, "error": str(e)}

    def calculate_final_metrics(self):
        """Calculate final accuracy metrics"""
        self.print_header("Final AI Accuracy Metrics")
        
        for model_name, data in self.metrics.items():
            print(f"\n{'='*80}")
            print(f"  {model_name.upper()} MODEL PERFORMANCE")
            print(f"{'='*80}")
            
            if data["total_requests"] > 0:
                accuracy = (data["successful_requests"] / data["total_requests"]) * 100
                avg_response_time = data["total_response_time"] / data["total_requests"]
                
                print(f"\n📊 Overall Statistics:")
                print(f"   Model: {data['model_used']}")
                print(f"   Total Requests: {data['total_requests']}")
                print(f"   Successful: {data['successful_requests']} ✅")
                print(f"   Failed: {data['failed_requests']} ❌")
                print(f"   Accuracy Rate: {accuracy:.2f}%")
                print(f"   Average Response Time: {avg_response_time:.2f}s")
                
                if data["response_times"]:
                    print(f"\n⏱️  Response Time Analysis:")
                    print(f"   Fastest: {min(data['response_times']):.2f}s")
                    print(f"   Slowest: {max(data['response_times']):.2f}s")
                    print(f"   Average: {avg_response_time:.2f}s")
                
                if data["features_tested"]:
                    print(f"\n🔧 Features Tested: {', '.join(set(data['features_tested']))}")
                
                # Accuracy rating
                print(f"\n⭐ Accuracy Rating:")
                if accuracy >= 90:
                    print(f"   ⭐⭐⭐⭐⭐ Excellent (90-100%)")
                elif accuracy >= 80:
                    print(f"   ⭐⭐⭐⭐ Very Good (80-89%)")
                elif accuracy >= 70:
                    print(f"   ⭐⭐⭐ Good (70-79%)")
                elif accuracy >= 60:
                    print(f"   ⭐⭐ Fair (60-69%)")
                else:
                    print(f"   ⭐ Needs Improvement (<60%)")
            else:
                print(f"\n❌ No requests made - API key may be missing")

    def save_results_to_file(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_accuracy_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "summary": {}
        }
        
        for model_name, data in self.metrics.items():
            if data["total_requests"] > 0:
                accuracy = (data["successful_requests"] / data["total_requests"]) * 100
                avg_time = data["total_response_time"] / data["total_requests"]
                
                report["summary"][model_name] = {
                    "accuracy": f"{accuracy:.2f}%",
                    "avg_response_time": f"{avg_time:.2f}s",
                    "total_requests": data["total_requests"]
                }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

    async def run_all_tests(self):
        """Run all accuracy tests"""
        self.print_header("CodeYogi AI Accuracy Testing Suite")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Test Groq
        await self.test_groq_basic_connection()
        await self.test_code_analysis_accuracy()
        await self.test_workflow_optimization_accuracy()
        
        # Test Gemini
        await self.test_gemini_basic_connection()
        
        # Calculate and display final metrics
        self.calculate_final_metrics()
        
        # Save to file
        self.save_results_to_file()
        
        print(f"\n{'='*80}")
        print(f"  Test Suite Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")


async def main():
    """Main entry point"""
    tester = AIAccuracyTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
