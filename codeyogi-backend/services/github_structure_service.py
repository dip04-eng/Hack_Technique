#!/usr/bin/env python3
"""
GitHub Repository Structure Analysis Service

This service provides API endpoints for analyzing GitHub repository structure
without requiring local cloning. It works with GitHub URLs and provides
intelligent folder organization suggestions.
"""

import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse

from agents.repo_analyzer import GitHubRepoAnalyzer
from models.schemas import (
    RepoStructureAnalysisRequest,
    RepoStructureAnalysisResult,
    QuickStructureCheckRequest,
    QuickStructureCheckResult,
    StructureRecommendation,
    StructureMetrics,
    FileDistribution,
    StructureAnalysisSummary,
)


class GitHubStructureAnalysisService:
    """Service for analyzing GitHub repository structure via API"""

    def __init__(self):
        self.analyzer = GitHubRepoAnalyzer()

    def _validate_github_url(self, url: str) -> tuple[str, str]:
        """
        Validate and parse GitHub URL

        Returns:
            tuple: (owner, repo_name)
        """
        try:
            parsed = urlparse(str(url))
            if parsed.netloc != "github.com":
                raise ValueError("URL must be a GitHub URL")

            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repository URL")

            return path_parts[0], path_parts[1]

        except Exception as e:
            raise ValueError(f"Invalid GitHub URL: {str(e)}")

    async def analyze_repository_structure(
        self, request: RepoStructureAnalysisRequest
    ) -> RepoStructureAnalysisResult:
        """
        Analyze GitHub repository structure and provide recommendations

        Args:
            request: Structure analysis request
                - You can now optionally include a 'custom_input' field in the request to provide additional user context or requirements. This will be appended to the analysis prompt for more tailored recommendations.

        Returns:
            Structure analysis results
        """
        try:
            # Validate GitHub URL
            owner, repo_name = self._validate_github_url(request.github_url)

            # Set up analyzer with token if provided
            if request.github_token:
                self.analyzer.github_token = request.github_token
                from github import Github

                self.analyzer.github_client = Github(request.github_token)

            # Download repository to temporary directory
            temp_dir = await self._download_github_repo(owner, repo_name)

            try:
                # Perform structure analysis
                if request.detailed_analysis:
                    # Full analysis with all details
                    analysis = self.analyzer.analyze_repo_structure(
                        temp_dir, request.exclude_patterns
                    )
                    summary = None
                else:
                    # Quick analysis with summary
                    analysis = await self.analyzer.quick_structure_analysis(
                        temp_dir, request.exclude_patterns
                    )
                    summary = self._convert_to_summary_model(analysis.get("summary"))

                # Convert to API response models
                structure_metrics = self._convert_to_metrics_model(
                    analysis["structure_metrics"]
                )
                file_distribution = self._convert_to_distribution_model(
                    analysis["file_distribution"]
                )
                structure_suggestions = self._convert_to_suggestions_model(
                    analysis["structure_suggestions"]
                )

                return RepoStructureAnalysisResult(
                    success=True,
                    github_url=str(request.github_url),
                    project_type=analysis["project_type"],
                    structure_metrics=structure_metrics,
                    file_distribution=file_distribution,
                    structure_suggestions=structure_suggestions,
                    recommended_folders=analysis["recommended_folders"],
                    summary=summary,
                    timestamp=datetime.now().isoformat(),
                )

            finally:
                # Cleanup temporary directory
                self._safe_cleanup(temp_dir)

        except Exception as e:
            return RepoStructureAnalysisResult(
                success=False,
                github_url=str(request.github_url),
                project_type="unknown",
                structure_metrics=StructureMetrics(
                    total_files=0,
                    total_directories=0,
                    max_depth=0,
                    average_depth=0.0,
                    files_per_directory=0.0,
                    organization_score=0,
                    large_directories_count=0,
                ),
                file_distribution=FileDistribution(
                    root_files=0,
                    max_files_in_directory=0,
                    type_distribution={},
                    directories_with_mixed_types=[],
                    scattered_types=[],
                ),
                structure_suggestions=[],
                recommended_folders={},
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    async def quick_structure_check(
        self, request: QuickStructureCheckRequest
    ) -> QuickStructureCheckResult:
        """
        Quick structure check with minimal response

        Args:
            request: Quick check request
                - You can now optionally include a 'custom_input' field in the request to provide additional user context or requirements. This will be appended to the analysis prompt for more tailored recommendations.

        Returns:
            Quick check results
        """
        try:
            # Validate GitHub URL
            owner, repo_name = self._validate_github_url(request.github_url)

            # Set up analyzer with token if provided
            if request.github_token:
                self.analyzer.github_token = request.github_token
                from github import Github

                self.analyzer.github_client = Github(request.github_token)

            # Download repository to temporary directory
            temp_dir = await self._download_github_repo(owner, repo_name)

            try:
                # Quick analysis
                analysis = await self.analyzer.quick_structure_analysis(temp_dir)

                # Extract key information
                metrics = analysis["structure_metrics"]
                summary = analysis["summary"]
                suggestions = analysis["structure_suggestions"]

                # Get top 3 suggestions
                top_suggestions = [s["reason"] for s in suggestions[:3]]

                return QuickStructureCheckResult(
                    success=True,
                    github_url=str(request.github_url),
                    organization_score=metrics["organization_score"],
                    organization_level=summary["organization_level"],
                    project_type=analysis["project_type"],
                    total_files=metrics["total_files"],
                    main_issues=summary["main_issues"],
                    top_suggestions=top_suggestions,
                )

            finally:
                # Cleanup temporary directory
                self._safe_cleanup(temp_dir)

        except Exception as e:
            return QuickStructureCheckResult(
                success=False,
                github_url=str(request.github_url),
                organization_score=0,
                organization_level="Error",
                project_type="unknown",
                total_files=0,
                main_issues=[],
                top_suggestions=[],
                error_message=str(e),
            )

    async def _download_github_repo(self, owner: str, repo_name: str) -> str:
        """Download GitHub repository to temporary directory"""
        import requests
        import zipfile
        import io

        temp_dir = tempfile.mkdtemp()

        try:
            # Try downloading as ZIP (works for public repos without auth)
            zip_url = (
                f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip"
            )
            response = requests.get(zip_url, timeout=30)

            if response.status_code == 404:
                # Try 'master' branch if 'main' doesn't exist
                zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip"
                response = requests.get(zip_url, timeout=30)

            if response.status_code == 200:
                # Extract ZIP file
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    zip_file.extractall(temp_dir)

                # Find the extracted directory
                extracted_dirs = [
                    d
                    for d in os.listdir(temp_dir)
                    if os.path.isdir(os.path.join(temp_dir, d))
                ]

                if extracted_dirs:
                    # Move contents from extracted directory to temp_dir root
                    extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                    final_temp_dir = tempfile.mkdtemp()

                    for item in os.listdir(extracted_path):
                        src = os.path.join(extracted_path, item)
                        dst = os.path.join(final_temp_dir, item)
                        if os.path.isdir(src):
                            shutil.move(src, dst)
                        else:
                            shutil.move(src, dst)

                    # Remove old temp directory
                    self._safe_cleanup(temp_dir)
                    return final_temp_dir

                return temp_dir
            else:
                raise Exception(
                    f"Failed to download repository: HTTP {response.status_code}"
                )

        except Exception as e:
            self._safe_cleanup(temp_dir)
            raise Exception(f"Failed to download repository: {str(e)}")

    def _safe_cleanup(self, dir_path: str):
        """Safely remove temporary directory"""

        def handle_remove_readonly(func, path, exc):
            import stat

            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)

        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Warning: Could not remove directory {dir_path}: {e}")

    def _convert_to_metrics_model(self, metrics: Dict) -> StructureMetrics:
        """Convert metrics dict to Pydantic model"""
        return StructureMetrics(
            total_files=metrics.get("total_files", 0),
            total_directories=metrics.get("total_directories", 0),
            max_depth=metrics.get("max_depth", 0),
            average_depth=metrics.get("average_depth", 0.0),
            files_per_directory=metrics.get("files_per_directory", 0.0),
            organization_score=metrics.get("organization_score", 0),
            large_directories_count=metrics.get("large_directories_count", 0),
        )

    def _convert_to_distribution_model(self, distribution: Dict) -> FileDistribution:
        """Convert file distribution dict to Pydantic model"""
        return FileDistribution(
            root_files=distribution.get("root_files", 0),
            max_files_in_directory=distribution.get("max_files_in_directory", 0),
            type_distribution=distribution.get("type_distribution", {}),
            directories_with_mixed_types=distribution.get(
                "directories_with_mixed_types", []
            ),
            scattered_types=distribution.get("scattered_types", []),
        )

    def _convert_to_suggestions_model(
        self, suggestions: List[Dict]
    ) -> List[StructureRecommendation]:
        """Convert suggestions list to Pydantic models"""
        return [
            StructureRecommendation(
                type=s.get("type", "unknown"),
                folder=s.get("folder", ""),
                reason=s.get("reason", ""),
                priority=s.get("priority", "medium"),
                suggested_subfolders=s.get("suggested_subfolders"),
            )
            for s in suggestions
        ]

    def _convert_to_summary_model(
        self, summary: Optional[Dict]
    ) -> Optional[StructureAnalysisSummary]:
        """Convert summary dict to Pydantic model"""
        if not summary:
            return None

        return StructureAnalysisSummary(
            organization_level=summary.get("organization_level", "Unknown"),
            main_issues=summary.get("main_issues", []),
            quick_wins=summary.get("quick_wins", []),
            estimated_improvement_time=summary.get(
                "estimated_improvement_time", "Unknown"
            ),
        )


# Global service instance
structure_service = GitHubStructureAnalysisService()
