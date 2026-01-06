#!/usr/bin/env python3
"""
Example usage of the Repository Structure Analyzer

This example shows how to use the new structure analysis features
to analyze and improve repository organization.
"""

import asyncio
import os
from pathlib import Path
from agents.repo_analyzer import analyze_local_structure, quick_structure_check


class StructureAnalyzer:
    """Wrapper class for easy structure analysis"""

    def __init__(self):
        self.results = None

    async def analyze_project(self, project_path: str, detailed: bool = False):
        """
        Analyze project structure and provide recommendations

        Args:
            project_path: Path to the project directory
            detailed: Whether to include detailed analysis
        """
        print(f"🔍 Analyzing: {os.path.basename(project_path)}")
        print("-" * 50)

        try:
            if detailed:
                # Full analysis with all details
                self.results = analyze_local_structure(project_path)
                await self._display_detailed_results()
            else:
                # Quick analysis with actionable recommendations
                self.results = await quick_structure_check(project_path)
                await self._display_quick_results()

        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")

    async def _display_quick_results(self):
        """Display quick analysis results"""
        summary = self.results["summary"]
        metrics = self.results["structure_metrics"]

        print(
            f"📊 Organization Score: {metrics['organization_score']}/100 ({summary['organization_level']})"
        )
        print(
            f"📁 Files: {metrics['total_files']} | Directories: {metrics['total_directories']}"
        )
        print(f"🎯 Project Type: {self.results['project_type']}")

        # Main issues
        if summary["main_issues"]:
            print(f"\n⚠️  Issues Found:")
            for issue in summary["main_issues"]:
                print(f"   • {issue}")

        # Quick wins
        if summary["quick_wins"]:
            print(f"\n🚀 Quick Improvements ({summary['estimated_improvement_time']}):")
            for win in summary["quick_wins"]:
                print(f"   • {win['description']}")

        # Top suggestions
        suggestions = self.results.get("structure_suggestions", [])
        if suggestions:
            print(f"\n💡 Recommendations:")
            for i, suggestion in enumerate(suggestions[:3], 1):
                priority = "🔴" if suggestion.get("priority") == "high" else "🟡"
                print(f"   {i}. {priority} {suggestion['reason']}")

        print()

    async def _display_detailed_results(self):
        """Display detailed analysis results"""
        metrics = self.results["structure_metrics"]
        distribution = self.results["file_distribution"]

        print(f"📊 Detailed Metrics:")
        print(f"   • Organization Score: {metrics['organization_score']}/100")
        print(f"   • Total Files: {metrics['total_files']}")
        print(f"   • Total Directories: {metrics['total_directories']}")
        print(f"   • Maximum Depth: {metrics['max_depth']}")
        print(f"   • Average Depth: {metrics['average_depth']}")
        print(f"   • Files per Directory: {metrics['files_per_directory']}")

        print(f"\n📄 File Type Distribution:")
        for file_type, count in distribution["type_distribution"].items():
            print(f"   • {file_type}: {count}")

        print(f"\n📁 Structure Analysis:")
        print(f"   • Root Files: {distribution['root_files']}")
        print(
            f"   • Mixed Type Directories: {len(distribution['directories_with_mixed_types'])}"
        )
        print(f"   • Scattered Types: {len(distribution['scattered_types'])}")

        # All suggestions
        suggestions = self.results.get("structure_suggestions", [])
        if suggestions:
            print(f"\n💡 All Recommendations ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                priority = "🔴" if suggestion.get("priority") == "high" else "🟡"
                print(f"   {i}. {priority} {suggestion['reason']}")
                if "folder" in suggestion:
                    print(
                        f"      → Action: {suggestion['type']} - {suggestion['folder']}"
                    )

        print()

    def save_report(self, output_path: str):
        """Save analysis report to file"""
        if not self.results:
            print("❌ No analysis results to save")
            return

        import json

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"💾 Report saved to: {output_path}")


async def main():
    """Main example function"""
    analyzer = StructureAnalyzer()

    # Example 1: Quick analysis of current project
    current_dir = Path(__file__).parent
    print("🏗️  Repository Structure Analyzer")
    print("=" * 60)
    print("Example 1: Quick Analysis")
    await analyzer.analyze_project(str(current_dir), detailed=False)

    # Example 2: Detailed analysis
    print("=" * 60)
    print("Example 2: Detailed Analysis")
    await analyzer.analyze_project(str(current_dir), detailed=True)

    # Save report
    analyzer.save_report("structure_report.json")


def analyze_multiple_projects():
    """Example of analyzing multiple projects"""

    async def batch_analysis():
        analyzer = StructureAnalyzer()

        # List of project paths to analyze
        projects = [
            ".",  # Current directory
            # Add more project paths here
            # "/path/to/project1",
            # "/path/to/project2",
        ]

        results = []

        for project_path in projects:
            if os.path.exists(project_path):
                print(f"\n{'='*60}")
                await analyzer.analyze_project(project_path, detailed=False)

                if analyzer.results:
                    results.append(
                        {
                            "path": project_path,
                            "score": analyzer.results["structure_metrics"][
                                "organization_score"
                            ],
                            "type": analyzer.results["project_type"],
                            "issues": len(analyzer.results["summary"]["main_issues"]),
                        }
                    )

        # Summary of all projects
        if results:
            print(f"\n{'='*60}")
            print("📋 Batch Analysis Summary:")
            for result in sorted(results, key=lambda x: x["score"], reverse=True):
                print(
                    f"   {result['path']:30} | Score: {result['score']:3}/100 | Type: {result['type']:15} | Issues: {result['issues']}"
                )

    asyncio.run(batch_analysis())


if __name__ == "__main__":
    print("Choose analysis type:")
    print("1. Single project analysis")
    print("2. Batch analysis of multiple projects")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        analyze_multiple_projects()
    else:
        print("Invalid choice. Running default single project analysis...")
        asyncio.run(main())
