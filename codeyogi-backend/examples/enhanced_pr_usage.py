#!/usr/bin/env python3
"""
Example usage of the enhanced GitHub PR Creator with comprehensive metrics
"""

import sys
import os

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pr_creator import GitHubPRCreator
from rich.console import Console
from rich.table import Table
import json

console = Console()


def demonstrate_enhanced_pr_creation():
    """Demonstrate the enhanced PR creation with comprehensive metrics"""

    console.print("🚀 Enhanced GitHub PR Creator Demo", style="bold blue")
    console.print("=" * 50)

    try:
        # Initialize PR Creator
        pr_creator = GitHubPRCreator()

        # Example 1: Single workflow optimization
        console.print("\n📝 Example 1: Workflow Optimization")

        repo_name = "your-username/your-repo"  # Replace with actual repo
        optimized_yaml = pr_creator.get_optimized_workflow_yaml()
        improvement_summary = pr_creator.create_improvement_summary()

        # This would create an actual PR (commented out for demo)
        # result = pr_creator.create_optimization_pr(
        #     repo_name=repo_name,
        #     optimized_yaml=optimized_yaml,
        #     improvement_summary=improvement_summary
        # )

        # Simulate the result structure with metrics
        result = {
            "success": True,
            "pr_number": 123,
            "pr_url": f"https://github.com/{repo_name}/pull/123",
            "branch_name": "codeyogi-optimization",
            "commit_sha": "abc123def456",
            "workflow_path": ".github/workflows/codeyogi-optimized.yml",
            # These would be included automatically:
            "ai_completion_metrics": {
                "total_ai_completions": 1,
                "ai_processing_time": 1643723400.0,
                "ai_model_used": "CodeYogi AI v2.0",
                "ai_confidence_score": 0.92,
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
        }

        display_pr_results(result)

        # Example 2: Multi-file optimization
        console.print("\n📝 Example 2: Multi-file Code Optimization")

        optimized_files = {
            "src/main.py": "# Optimized Python code\nprint('Hello, optimized world!')",
            "src/utils.py": "# Optimized utility functions\ndef optimized_function():\n    pass",
            "tests/test_main.py": "# Optimized test code\nimport unittest",
        }

        # This would create an actual PR (commented out for demo)
        # multi_result = pr_creator.create_multi_file_optimization_pr(
        #     repo_name=repo_name,
        #     optimized_files=optimized_files,
        #     improvement_summary="Multi-language optimizations applied"
        # )

        # Simulate multi-file result
        multi_result = {
            "success": True,
            "pr_number": 124,
            "pr_url": f"https://github.com/{repo_name}/pull/124",
            "branch_name": "codeyogi-code-optimization",
            "files_count": len(optimized_files),
            "ai_completion_metrics": {
                "total_ai_completions": 3,
                "ai_processing_time": 1643723500.0,
                "ai_model_used": "CodeYogi AI v2.0",
                "ai_confidence_score": 0.94,
                "ai_suggestions_applied": 3,
            },
            "code_optimization_metrics": {
                "files_optimized": 3,
                "lines_of_code_improved": 245,
                "lines_of_code_optimized": 185,
                "performance_improvement_percent": 28.5,
                "complexity_reduction_percent": 22.0,
                "security_issues_fixed": 2,
                "code_duplication_reduced_percent": 18.0,
                "test_coverage_improvement": 15.0,
                "build_time_reduction_percent": 32.0,
            },
            "carbon_savings_metrics": {
                "total_co2_saved_kg": 2.345,
                "co2_saved_build_process": 0.485,
                "co2_saved_runtime": 1.425,
                "co2_saved_development": 0.435,
                "trees_equivalent": 0.11,
                "car_miles_equivalent": 5.8,
                "energy_saved_kwh": 4.69,
                "monthly_savings_estimate": 28.1,
                "carbon_footprint_reduction_percent": 23.5,
            },
        }

        display_pr_results(multi_result, "Multi-file Optimization")

        return True

    except Exception as e:
        console.print(f"[red]❌ Error in demonstration: {str(e)}[/red]")
        return False


def display_pr_results(result, title="Workflow Optimization"):
    """Display PR results in a formatted table"""

    if not result.get("success"):
        console.print(
            f"[red]❌ {title} failed: {result.get('error', 'Unknown error')}[/red]"
        )
        return

    console.print(f"\n✅ {title} PR Created Successfully!")

    # Basic PR Info Table
    basic_table = Table(title="📋 PR Information")
    basic_table.add_column("Property", style="cyan")
    basic_table.add_column("Value", style="green")

    basic_table.add_row("PR Number", str(result.get("pr_number", "N/A")))
    basic_table.add_row("PR URL", result.get("pr_url", "N/A"))
    basic_table.add_row("Branch", result.get("branch_name", "N/A"))
    basic_table.add_row(
        "Files Count",
        str(
            result.get(
                "files_count",
                result.get("ai_completion_metrics", {}).get("total_ai_completions", 1),
            )
        ),
    )

    console.print(basic_table)

    # AI Metrics Table
    if "ai_completion_metrics" in result:
        ai_metrics = result["ai_completion_metrics"]
        ai_table = Table(title="🤖 AI Completion Metrics")
        ai_table.add_column("Metric", style="cyan")
        ai_table.add_column("Value", style="yellow")

        ai_table.add_row(
            "Total AI Completions", str(ai_metrics.get("total_ai_completions", 0))
        )
        ai_table.add_row("AI Model Used", ai_metrics.get("ai_model_used", "N/A"))
        ai_table.add_row(
            "Confidence Score", f"{ai_metrics.get('ai_confidence_score', 0):.2f}"
        )
        ai_table.add_row(
            "Suggestions Applied", str(ai_metrics.get("ai_suggestions_applied", 0))
        )

        console.print(ai_table)

    # Code Optimization Metrics Table
    if "code_optimization_metrics" in result:
        code_metrics = result["code_optimization_metrics"]
        code_table = Table(title="⚡ Code Optimization Metrics")
        code_table.add_column("Metric", style="cyan")
        code_table.add_column("Value", style="magenta")

        code_table.add_row(
            "Files Optimized", str(code_metrics.get("files_optimized", 0))
        )
        code_table.add_row(
            "Lines Improved", str(code_metrics.get("lines_of_code_improved", 0))
        )
        code_table.add_row(
            "Performance Improvement",
            f"{code_metrics.get('performance_improvement_percent', 0):.1f}%",
        )
        code_table.add_row(
            "Build Time Reduction",
            f"{code_metrics.get('build_time_reduction_percent', 0):.1f}%",
        )
        code_table.add_row(
            "Security Issues Fixed", str(code_metrics.get("security_issues_fixed", 0))
        )
        code_table.add_row(
            "Complexity Reduction",
            f"{code_metrics.get('complexity_reduction_percent', 0):.1f}%",
        )

        console.print(code_table)

    # Carbon Savings Table
    if "carbon_savings_metrics" in result:
        carbon_metrics = result["carbon_savings_metrics"]
        carbon_table = Table(title="🌱 Environmental Impact")
        carbon_table.add_column("Metric", style="cyan")
        carbon_table.add_column("Value", style="green")

        carbon_table.add_row(
            "CO2 Saved", f"{carbon_metrics.get('total_co2_saved_kg', 0):.3f} kg"
        )
        carbon_table.add_row(
            "Energy Saved", f"{carbon_metrics.get('energy_saved_kwh', 0):.2f} kWh"
        )
        carbon_table.add_row(
            "Trees Equivalent", f"{carbon_metrics.get('trees_equivalent', 0):.2f} trees"
        )
        carbon_table.add_row(
            "Car Miles Equivalent",
            f"{carbon_metrics.get('car_miles_equivalent', 0):.1f} miles",
        )
        carbon_table.add_row(
            "Monthly CO2 Savings",
            f"{carbon_metrics.get('monthly_savings_estimate', 0):.2f} kg",
        )
        carbon_table.add_row(
            "Carbon Reduction",
            f"{carbon_metrics.get('carbon_footprint_reduction_percent', 0):.1f}%",
        )

        console.print(carbon_table)


def save_metrics_to_json(result, filename="pr_metrics.json"):
    """Save PR metrics to JSON file for further analysis"""

    try:
        with open(filename, "w") as f:
            json.dump(result, f, indent=2)
        console.print(f"\n💾 Metrics saved to {filename}")
    except Exception as e:
        console.print(f"[red]❌ Error saving metrics: {str(e)}[/red]")


if __name__ == "__main__":
    console.print("🎯 GitHub PR Creator - Enhanced Metrics Demo")
    console.print("This demo shows the comprehensive data now included in PR responses")
    console.print("=" * 70)

    success = demonstrate_enhanced_pr_creation()

    if success:
        console.print("\n🎉 Demo completed successfully!")
        console.print("\n📝 Key Features Added:")
        console.print(
            "  • AI completion metrics (total completions, confidence scores)"
        )
        console.print(
            "  • Code optimization data (performance improvements, security fixes)"
        )
        console.print("  • CO2 carbon savings (environmental impact calculations)")
        console.print("  • Enhanced PR descriptions with metrics")
        console.print("  • Comprehensive error handling with default metrics")
    else:
        console.print("\n❌ Demo failed - check your GitHub token setup")
