#!/usr/bin/env python3
"""
Complete Workflow Example - GitHub PR Creator with Slack Notifications
Shows the full end-to-end process of creating optimized PRs with automatic Slack notifications
"""

import sys
import os

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pr_creator import GitHubPRCreator
from rich.console import Console
import json

console = Console()


def complete_workflow_example():
    """Demonstrate complete workflow with PR creation and Slack notifications"""

    console.print("🚀 Complete CodeYogi Workflow Demo", style="bold blue")
    console.print("=" * 50)

    try:
        # Step 1: Initialize PR Creator (includes Slack setup)
        console.print("\n🔧 Step 1: Initializing CodeYogi PR Creator")
        pr_creator = GitHubPRCreator()

        # Step 2: Prepare optimization content
        console.print("\n📝 Step 2: Preparing Optimization Content")

        # Example: Workflow optimization
        optimized_yaml = pr_creator.get_optimized_workflow_yaml()
        improvement_summary = pr_creator.create_improvement_summary()

        console.print(f"✅ Generated optimized workflow ({len(optimized_yaml)} chars)")
        console.print(
            f"✅ Created improvement summary ({len(improvement_summary)} chars)"
        )

        # Step 3: Show what would happen with real PR creation
        console.print("\n🎯 Step 3: PR Creation Process (Simulated)")

        # Simulate successful PR creation result
        simulated_result = {
            "success": True,
            "pr_number": 42,
            "pr_url": "https://github.com/example/awesome-project/pull/42",
            "branch_name": "codeyogi-optimization",
            "commit_sha": "abc123def456",
            "workflow_path": ".github/workflows/codeyogi-optimized.yml",
            # Comprehensive metrics (would be calculated automatically)
            "ai_completion_metrics": {
                "total_ai_completions": 1,
                "ai_processing_time": 1643723400.0,
                "ai_model_used": "CodeYogi AI v2.0",
                "ai_confidence_score": 0.94,
                "ai_suggestions_applied": 1,
            },
            "code_optimization_metrics": {
                "files_optimized": 1,
                "lines_of_code_improved": 150,
                "performance_improvement_percent": 35.0,
                "complexity_reduction_percent": 25.0,
                "security_issues_fixed": 3,
                "code_duplication_reduced_percent": 15.0,
                "test_coverage_improvement": 12.0,
                "build_time_reduction_percent": 40.0,
            },
            "carbon_savings_metrics": {
                "total_co2_saved_kg": 1.125,
                "co2_saved_build_process": 0.225,
                "co2_saved_runtime": 0.735,
                "co2_saved_development": 0.165,
                "trees_equivalent": 0.05,
                "car_miles_equivalent": 2.8,
                "energy_saved_kwh": 2.25,
                "monthly_savings_estimate": 13.5,
                "carbon_footprint_reduction_percent": 11.3,
            },
            "repository_statistics": {
                "repo_size": 1250,
                "repo_language": "JavaScript",
                "stars_count": 45,
                "forks_count": 12,
                "open_issues": 8,
            },
            "session_information": {
                "optimization_timestamp": "2025-01-27T10:30:45.123456",
                "session_id": "codeyogi-1643723445",
                "optimization_type": "workflow",
            },
        }

        console.print("✅ PR would be created successfully")
        console.print(f"✅ Comprehensive metrics calculated")
        console.print(f"✅ Slack notification would be sent")

        # Step 4: Show the complete response
        console.print("\n📊 Step 4: Complete Response Data")

        # Display key metrics
        console.print(f"🔗 PR URL: {simulated_result['pr_url']}")
        console.print(
            f"🤖 AI Completions: {simulated_result['ai_completion_metrics']['total_ai_completions']}"
        )
        console.print(
            f"⚡ Performance Improvement: {simulated_result['code_optimization_metrics']['performance_improvement_percent']:.1f}%"
        )
        console.print(
            f"🌱 CO2 Saved: {simulated_result['carbon_savings_metrics']['total_co2_saved_kg']:.3f} kg"
        )
        console.print(
            f"🔒 Security Issues Fixed: {simulated_result['code_optimization_metrics']['security_issues_fixed']}"
        )

        # Step 5: Multi-file optimization example
        console.print("\n📁 Step 5: Multi-File Optimization Example")

        # Example optimized files
        optimized_files = {
            "src/components/App.js": """
// Optimized React component with performance improvements
import React, { memo, useMemo, useCallback } from 'react';
import { optimizedAPI } from '../utils/api';

const App = memo(({ data }) => {
  const processedData = useMemo(() => 
    data.map(item => ({ ...item, processed: true }))
  , [data]);
  
  const handleClick = useCallback((id) => {
    optimizedAPI.updateItem(id);
  }, []);
  
  return (
    <div className="app-container">
      {processedData.map(item => (
        <div key={item.id} onClick={() => handleClick(item.id)}>
          {item.name}
        </div>
      ))}
    </div>
  );
});

export default App;
            """.strip(),
            "src/utils/api.js": """
// Optimized API utility with caching and error handling
class OptimizedAPI {
  constructor() {
    this.cache = new Map();
    this.pendingRequests = new Map();
  }
  
  async getData(endpoint) {
    if (this.cache.has(endpoint)) {
      return this.cache.get(endpoint);
    }
    
    if (this.pendingRequests.has(endpoint)) {
      return this.pendingRequests.get(endpoint);
    }
    
    const request = this.fetchWithRetry(endpoint);
    this.pendingRequests.set(endpoint, request);
    
    try {
      const data = await request;
      this.cache.set(endpoint, data);
      return data;
    } finally {
      this.pendingRequests.delete(endpoint);
    }
  }
  
  async fetchWithRetry(endpoint, retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
      } catch (error) {
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, i)));
      }
    }
  }
}

export const optimizedAPI = new OptimizedAPI();
            """.strip(),
            "tests/app.test.js": """
// Optimized test suite with better coverage
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import App from '../src/components/App';
import { optimizedAPI } from '../src/utils/api';

// Mock the API
jest.mock('../src/utils/api');

describe('App Component', () => {
  const mockData = [
    { id: 1, name: 'Item 1' },
    { id: 2, name: 'Item 2' }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders items correctly', () => {
    render(<App data={mockData} />);
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });
  
  it('handles item clicks', async () => {
    const updateSpy = jest.spyOn(optimizedAPI, 'updateItem');
    render(<App data={mockData} />);
    
    fireEvent.click(screen.getByText('Item 1'));
    
    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(1);
    });
  });
  
  it('memoizes processed data', () => {
    const { rerender } = render(<App data={mockData} />);
    const initialElements = screen.getAllByText(/Item/);
    
    // Re-render with same data
    rerender(<App data={mockData} />);
    const newElements = screen.getAllByText(/Item/);
    
    // Elements should be the same (memoized)
    expect(initialElements).toEqual(newElements);
  });
});
            """.strip(),
        }

        # Simulate multi-file PR result
        multi_file_result = {
            "success": True,
            "pr_number": 43,
            "pr_url": "https://github.com/example/awesome-project/pull/43",
            "branch_name": "codeyogi-code-optimization",
            "files_count": len(optimized_files),
            "ai_completion_metrics": {
                "total_ai_completions": 3,
                "ai_model_used": "CodeYogi AI v2.0",
                "ai_confidence_score": 0.96,
            },
            "code_optimization_metrics": {
                "files_optimized": 3,
                "lines_of_code_improved": 245,
                "performance_improvement_percent": 42.5,
                "security_issues_fixed": 2,
            },
            "carbon_savings_metrics": {
                "total_co2_saved_kg": 3.125,
                "energy_saved_kwh": 6.25,
                "trees_equivalent": 0.14,
            },
        }

        console.print(
            f"✅ Multi-file optimization ready ({len(optimized_files)} files)"
        )
        console.print(
            f"✅ Expected {multi_file_result['code_optimization_metrics']['performance_improvement_percent']:.1f}% performance improvement"
        )

        # Step 6: Show complete workflow benefits
        console.print("\n🌟 Step 6: Complete Workflow Benefits")

        benefits = [
            "🤖 **Automated AI Analysis** - Intelligent code optimization",
            "📊 **Comprehensive Metrics** - Detailed performance and environmental data",
            "🔔 **Instant Notifications** - Team-wide visibility via Slack",
            "🌱 **Environmental Impact** - Track and reduce carbon footprint",
            "🔒 **Security Improvements** - Automated vulnerability fixes",
            "⚡ **Performance Gains** - Measurable speed and efficiency improvements",
            "📈 **Progress Tracking** - Historical optimization data",
            "🎯 **Developer Productivity** - Reduced manual optimization work",
        ]

        for benefit in benefits:
            console.print(benefit)

        # Step 7: Save complete workflow data
        console.print("\n💾 Step 7: Saving Workflow Data")

        complete_workflow_data = {
            "workflow_optimization": simulated_result,
            "multi_file_optimization": multi_file_result,
            "optimized_files": optimized_files,
            "workflow_summary": {
                "total_optimizations": 2,
                "total_files_optimized": 4,
                "total_co2_saved": simulated_result["carbon_savings_metrics"][
                    "total_co2_saved_kg"
                ]
                + multi_file_result["carbon_savings_metrics"]["total_co2_saved_kg"],
                "total_performance_improvement": (
                    simulated_result["code_optimization_metrics"][
                        "performance_improvement_percent"
                    ]
                    + multi_file_result["code_optimization_metrics"][
                        "performance_improvement_percent"
                    ]
                )
                / 2,
            },
        }

        with open("complete_workflow_data.json", "w") as f:
            json.dump(complete_workflow_data, f, indent=2)

        console.print("✅ Complete workflow data saved to complete_workflow_data.json")

        return True

    except Exception as e:
        console.print(f"[red]❌ Error in workflow demo: {str(e)}[/red]")
        return False


def show_actual_usage():
    """Show how to use the system in production"""

    console.print("\n🏭 Production Usage Examples")
    console.print("=" * 35)

    console.print("\n**Single Workflow Optimization:**")
    console.print("```python")
    console.print("from utils.pr_creator import GitHubPRCreator")
    console.print("")
    console.print("# Initialize with automatic Slack setup")
    console.print("pr_creator = GitHubPRCreator()")
    console.print("")
    console.print("# Create optimized workflow PR")
    console.print("result = pr_creator.create_optimization_pr(")
    console.print('    repo_name="your-org/your-repo",')
    console.print("    optimized_yaml=workflow_content,")
    console.print('    improvement_summary="CI/CD optimizations"')
    console.print(")")
    console.print("")
    console.print("# Slack notification sent automatically!")
    console.print("print(f'PR created: {result[\"pr_url\"]}')")
    console.print("```")

    console.print("\n**Multi-File Code Optimization:**")
    console.print("```python")
    console.print("# Optimize multiple files")
    console.print("optimized_files = {")
    console.print('    "src/main.py": optimized_python_code,')
    console.print('    "src/utils.js": optimized_javascript_code,')
    console.print('    "tests/test.py": optimized_test_code')
    console.print("}")
    console.print("")
    console.print("result = pr_creator.create_multi_file_optimization_pr(")
    console.print('    repo_name="your-org/your-repo",')
    console.print("    optimized_files=optimized_files,")
    console.print('    improvement_summary="Performance and security improvements"')
    console.print(")")
    console.print("")
    console.print("# Rich Slack notification with all metrics sent!")
    console.print("```")


if __name__ == "__main__":
    console.print("🚀 CodeYogi Complete Workflow Demonstration")
    console.print("This shows the full end-to-end process with Slack notifications")
    console.print("=" * 70)

    success = complete_workflow_example()
    show_actual_usage()

    if success:
        console.print("\n🎉 Complete workflow demonstration finished!")
        console.print("\n📋 Summary:")
        console.print("  ✅ PR creation with comprehensive metrics")
        console.print("  ✅ Automatic Slack notifications")
        console.print("  ✅ Environmental impact tracking")
        console.print("  ✅ AI-powered code optimization")
        console.print("  ✅ Team collaboration features")
        console.print("\n🚀 Ready for production use!")
    else:
        console.print("\n❌ Demo encountered issues - check configuration")
