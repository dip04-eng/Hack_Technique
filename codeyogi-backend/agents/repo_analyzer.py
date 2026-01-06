import os
import re
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import requests
from github import Github
from git import Repo
import chardet
from collections import defaultdict, Counter

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    RepoAnalysisRequest,
    RepoAnalysisResult,
    DirectoryStructure,
    FileInfo,
    FileType,
    StructureSuggestion,
    CleanupSuggestion,
)

from agents.ai_analyzer import ai_analyzer


class GitHubRepoAnalyzer:
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the GitHub Repository Analyzer

        Args:
            github_token: GitHub personal access token for API access
        """
        self.github_token = github_token
        self.github_client = Github(github_token) if github_token else Github()

        # File type mappings
        self.file_extensions = {
            "source_code": {
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c",
                ".cs",
                ".rb",
                ".php",
                ".go",
                ".rs",
                ".kt",
                ".swift",
                ".scala",
                ".r",
                ".m",
                ".mm",
                ".h",
                ".hpp",
                ".cc",
                ".cxx",
                ".jsx",
                ".tsx",
                ".vue",
                ".svelte",
            },
            "config": {
                ".json",
                ".yaml",
                ".yml",
                ".toml",
                ".ini",
                ".cfg",
                ".conf",
                ".config",
                ".env",
                ".properties",
                ".xml",
                ".plist",
            },
            "documentation": {
                ".md",
                ".rst",
                ".txt",
                ".doc",
                ".docx",
                ".pdf",
                ".html",
                ".htm",
            },
            "build": {
                ".dockerfile",
                ".makefile",
                ".cmake",
                ".gradle",
                ".maven",
                ".sbt",
                ".bazel",
                ".buck",
            },
            "test": {".test.", ".spec.", "_test.", "_spec."},
            "asset": {
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".svg",
                ".ico",
                ".css",
                ".scss",
                ".sass",
                ".less",
                ".woff",
                ".woff2",
                ".ttf",
                ".eot",
            },
        }

        # Common unnecessary files/directories
        self.unnecessary_patterns = {
            "build_artifacts": [
                "*.pyc",
                "*.pyo",
                "*.class",
                "*.o",
                "*.so",
                "*.dll",
                "*.exe",
                "__pycache__/",
                "node_modules/",
                "dist/",
                "build/",
                "target/",
                ".pytest_cache/",
                ".coverage",
                "*.egg-info/",
                ".tox/",
            ],
            "editor_files": [
                ".vscode/",
                ".idea/",
                "*.swp",
                "*.swo",
                "*~",
                ".DS_Store",
                "Thumbs.db",
                "*.tmp",
                "*.temp",
            ],
            "log_files": ["*.log", "logs/", "log/", "*.out", "*.err"],
            "backup_files": ["*.bak", "*.backup", "*.old", "*.orig"],
        }

        # Best practice directory structures by language/framework
        self.structure_templates = {
            "python": {
                "files": ["requirements.txt", "setup.py", "README.md", ".gitignore"],
                "dirs": ["src/", "tests/", "docs/"],
                "patterns": {
                    "src/": "Main source code",
                    "tests/": "Test files",
                    "docs/": "Documentation",
                    "scripts/": "Utility scripts",
                    "config/": "Configuration files",
                },
            },
            "javascript": {
                "files": ["package.json", "README.md", ".gitignore"],
                "dirs": ["src/", "test/", "docs/", "public/"],
                "patterns": {
                    "src/": "Source code",
                    "test/": "Test files",
                    "public/": "Static assets",
                    "docs/": "Documentation",
                },
            },
            "java": {
                "files": ["pom.xml", "README.md", ".gitignore"],
                "dirs": ["src/main/java/", "src/test/java/", "src/main/resources/"],
                "patterns": {
                    "src/main/java/": "Main Java source",
                    "src/test/java/": "Test source",
                    "src/main/resources/": "Resources",
                },
            },
        }

        # Advanced structure patterns for different project types
        self.advanced_structure_patterns = {
            "web_application": {
                "indicators": ["package.json", "index.html", "webpack", "vite", "next"],
                "suggested_structure": {
                    "src/": "Source code",
                    "src/components/": "Reusable components",
                    "src/pages/": "Page components",
                    "src/utils/": "Utility functions",
                    "src/assets/": "Static assets",
                    "src/styles/": "CSS/SCSS files",
                    "public/": "Public static files",
                    "tests/": "Test files",
                    "docs/": "Documentation",
                },
            },
            "api_backend": {
                "indicators": ["app.py", "main.py", "server.js", "api", "routes"],
                "suggested_structure": {
                    "src/": "Source code",
                    "src/routes/": "API route handlers",
                    "src/models/": "Data models",
                    "src/services/": "Business logic",
                    "src/utils/": "Utility functions",
                    "src/middleware/": "Middleware functions",
                    "tests/": "Test files",
                    "config/": "Configuration files",
                    "docs/": "API documentation",
                },
            },
            "data_science": {
                "indicators": ["jupyter", ".ipynb", "pandas", "numpy", "sklearn"],
                "suggested_structure": {
                    "data/": "Data files",
                    "data/raw/": "Raw data",
                    "data/processed/": "Processed data",
                    "notebooks/": "Jupyter notebooks",
                    "src/": "Source code",
                    "src/data/": "Data processing scripts",
                    "src/models/": "Model definitions",
                    "src/visualization/": "Visualization scripts",
                    "tests/": "Test files",
                    "reports/": "Generated reports",
                },
            },
            "mobile_app": {
                "indicators": ["android", "ios", "flutter", "react-native", "xamarin"],
                "suggested_structure": {
                    "src/": "Source code",
                    "src/screens/": "Screen components",
                    "src/components/": "Reusable components",
                    "src/navigation/": "Navigation logic",
                    "src/services/": "API services",
                    "src/utils/": "Utility functions",
                    "assets/": "Images and assets",
                    "tests/": "Test files",
                },
            },
            "library_package": {
                "indicators": [
                    "setup.py",
                    "pyproject.toml",
                    "package.json",
                    "lib",
                    "library",
                ],
                "suggested_structure": {
                    "src/": "Library source code",
                    "tests/": "Test files",
                    "docs/": "Documentation",
                    "examples/": "Usage examples",
                    "benchmarks/": "Performance benchmarks",
                },
            },
        }

    def analyze_repo_structure(
        self, repo_path: str, exclude_patterns: List[str] = None
    ) -> Dict:
        """
        Analyze repository file structure and suggest better folder organization

        Args:
            repo_path: Path to the repository
            exclude_patterns: Patterns to exclude from analysis

        Returns:
            Dictionary containing structure analysis and suggestions
        """
        if exclude_patterns is None:
            exclude_patterns = [".git", "__pycache__", "node_modules", ".pytest_cache"]

        # Analyze current structure
        current_structure = self._scan_repository_structure(repo_path, exclude_patterns)

        # Detect project type
        project_type = self._detect_project_type(current_structure)

        # Analyze file distribution
        file_distribution = self._analyze_file_distribution(current_structure)

        # Generate structure suggestions
        structure_suggestions = self._generate_structure_recommendations(
            current_structure, project_type, file_distribution
        )

        # Calculate structure metrics
        structure_metrics = self._calculate_structure_metrics(current_structure)

        return {
            "current_structure": current_structure,
            "project_type": project_type,
            "file_distribution": file_distribution,
            "structure_suggestions": structure_suggestions,
            "structure_metrics": structure_metrics,
            "recommended_folders": self._get_recommended_folders(project_type),
        }

    def _scan_repository_structure(
        self, repo_path: str, exclude_patterns: List[str]
    ) -> Dict:
        """Scan and map the current repository structure"""
        structure = {
            "directories": [],
            "files_by_type": defaultdict(list),
            "files_by_directory": defaultdict(list),
            "depth_analysis": defaultdict(int),
            "large_directories": [],
        }

        def should_exclude(path: str) -> bool:
            return any(pattern in path.lower() for pattern in exclude_patterns)

        for root, dirs, files in os.walk(repo_path):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d))]

            relative_root = os.path.relpath(root, repo_path)
            if relative_root == ".":
                relative_root = "/"

            structure["directories"].append(relative_root)

            # Calculate directory depth
            depth = relative_root.count(os.sep) if relative_root != "/" else 0
            structure["depth_analysis"][depth] += 1

            # Analyze files in this directory
            for file in files:
                if should_exclude(file):
                    continue

                file_path = os.path.join(relative_root, file)
                file_ext = Path(file).suffix.lower()

                # Categorize by type
                file_type = self._categorize_file_type(file_path, file_ext)
                structure["files_by_type"][file_type].append(file_path)
                structure["files_by_directory"][relative_root].append(
                    {"name": file, "type": file_type, "extension": file_ext}
                )

            # Track large directories
            if len(files) > 20:
                structure["large_directories"].append(
                    {"path": relative_root, "file_count": len(files)}
                )

        return structure

    def _detect_project_type(self, structure: Dict) -> str:
        """Detect the type of project based on files and structure"""
        all_files = []
        for files_list in structure["files_by_type"].values():
            all_files.extend(files_list)

        file_content = " ".join(all_files).lower()

        # Check against patterns
        for project_type, config in self.advanced_structure_patterns.items():
            indicators = config["indicators"]
            matches = sum(1 for indicator in indicators if indicator in file_content)

            if matches >= 2:  # At least 2 indicators must match
                return project_type

        # Fallback detection based on file extensions
        file_types = structure["files_by_type"]

        if file_types.get("javascript", []) or file_types.get("typescript", []):
            if any("component" in f.lower() or "page" in f.lower() for f in all_files):
                return "web_application"
            return "javascript_project"

        if file_types.get("python", []):
            if any("model" in f.lower() or "notebook" in f.lower() for f in all_files):
                return "data_science"
            if any("api" in f.lower() or "route" in f.lower() for f in all_files):
                return "api_backend"
            return "python_project"

        return "general"

    def _categorize_file_type(self, file_path: str, extension: str) -> str:
        """Categorize file based on extension and path"""
        path_lower = file_path.lower()

        # Test files
        if any(pattern in path_lower for pattern in ["test", "spec", "__test__"]):
            return "test"

        # Documentation
        if extension in [".md", ".rst", ".txt"] or "doc" in path_lower:
            return "documentation"

        # Configuration
        if extension in [".json", ".yaml", ".yml", ".toml", ".ini", ".env"]:
            return "configuration"

        # Source code by extension
        source_extensions = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".jsx": "javascript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".css": "stylesheet",
            ".scss": "stylesheet",
            ".html": "markup",
        }

        if extension in source_extensions:
            return source_extensions[extension]

        # Assets
        if extension in [".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"]:
            return "asset"

        return "other"

    def _analyze_file_distribution(self, structure: Dict) -> Dict:
        """Analyze how files are distributed across directories"""
        distribution = {
            "root_files": len(structure["files_by_directory"].get("/", [])),
            "max_files_in_directory": 0,
            "directories_with_mixed_types": [],
            "type_distribution": {},
            "scattered_types": [],
        }

        # Calculate type distribution
        for file_type, files in structure["files_by_type"].items():
            distribution["type_distribution"][file_type] = len(files)

        # Find max files in any directory
        for directory, files in structure["files_by_directory"].items():
            file_count = len(files)
            if file_count > distribution["max_files_in_directory"]:
                distribution["max_files_in_directory"] = file_count

        # Find directories with mixed file types
        for directory, files in structure["files_by_directory"].items():
            types_in_dir = set(file["type"] for file in files)
            if len(types_in_dir) > 3:  # More than 3 different types
                distribution["directories_with_mixed_types"].append(
                    {
                        "directory": directory,
                        "types": list(types_in_dir),
                        "file_count": len(files),
                    }
                )

        # Find scattered file types (types spread across many directories)
        type_locations = defaultdict(set)
        for directory, files in structure["files_by_directory"].items():
            for file in files:
                type_locations[file["type"]].add(directory)

        for file_type, locations in type_locations.items():
            if len(locations) > 3:  # Type found in more than 3 directories
                distribution["scattered_types"].append(
                    {
                        "type": file_type,
                        "locations": list(locations),
                        "location_count": len(locations),
                    }
                )

        return distribution

    def _generate_structure_recommendations(
        self, structure: Dict, project_type: str, file_distribution: Dict
    ) -> List[Dict]:
        """Generate specific recommendations for better folder structure"""
        recommendations = []

        # Get recommended structure for project type
        if project_type in self.advanced_structure_patterns:
            recommended = self.advanced_structure_patterns[project_type][
                "suggested_structure"
            ]

            for folder, description in recommended.items():
                if folder not in [d + "/" for d in structure["directories"]]:
                    recommendations.append(
                        {
                            "type": "create_directory",
                            "folder": folder,
                            "reason": description,
                            "priority": "high",
                        }
                    )

        # Root file organization
        if file_distribution["root_files"] > 10:
            recommendations.append(
                {
                    "type": "organize_root",
                    "folder": "src/",
                    "reason": f"Move {file_distribution['root_files']} files from root to organized folders",
                    "priority": "high",
                }
            )

        # Mixed type directories
        for mixed_dir in file_distribution["directories_with_mixed_types"]:
            if mixed_dir["file_count"] > 5:
                recommendations.append(
                    {
                        "type": "separate_types",
                        "folder": mixed_dir["directory"],
                        "reason": f"Separate {len(mixed_dir['types'])} different file types in {mixed_dir['directory']}",
                        "priority": "medium",
                        "suggested_subfolders": self._suggest_subfolders_for_types(
                            mixed_dir["types"]
                        ),
                    }
                )

        # Scattered types
        for scattered in file_distribution["scattered_types"]:
            if scattered["location_count"] > 4:
                recommendations.append(
                    {
                        "type": "consolidate_type",
                        "folder": f"{scattered['type']}/",
                        "reason": f"Consolidate {scattered['type']} files scattered across {scattered['location_count']} directories",
                        "priority": "medium",
                    }
                )

        # Large directories
        for large_dir in structure["large_directories"]:
            if large_dir["file_count"] > 30:
                recommendations.append(
                    {
                        "type": "split_directory",
                        "folder": large_dir["path"],
                        "reason": f"Split large directory with {large_dir['file_count']} files into smaller modules",
                        "priority": "medium",
                    }
                )

        return recommendations

    def _suggest_subfolders_for_types(self, types: List[str]) -> List[str]:
        """Suggest appropriate subfolders for different file types"""
        subfolder_map = {
            "javascript": "components/",
            "typescript": "components/",
            "python": "modules/",
            "stylesheet": "styles/",
            "asset": "assets/",
            "test": "tests/",
            "documentation": "docs/",
            "configuration": "config/",
        }

        return [subfolder_map.get(file_type, f"{file_type}/") for file_type in types]

    def _calculate_structure_metrics(self, structure: Dict) -> Dict:
        """Calculate metrics about the repository structure"""
        total_files = sum(len(files) for files in structure["files_by_type"].values())
        total_directories = len(structure["directories"])

        # Calculate depth metrics
        max_depth = (
            max(structure["depth_analysis"].keys())
            if structure["depth_analysis"]
            else 0
        )
        avg_depth = (
            (
                sum(
                    depth * count
                    for depth, count in structure["depth_analysis"].items()
                )
                / sum(structure["depth_analysis"].values())
            )
            if structure["depth_analysis"]
            else 0
        )

        # Calculate organization score (0-100)
        organization_score = self._calculate_organization_score(structure)

        return {
            "total_files": total_files,
            "total_directories": total_directories,
            "max_depth": max_depth,
            "average_depth": round(avg_depth, 2),
            "files_per_directory": (
                round(total_files / total_directories, 2)
                if total_directories > 0
                else 0
            ),
            "organization_score": organization_score,
            "large_directories_count": len(structure["large_directories"]),
        }

    def _calculate_organization_score(self, structure: Dict) -> int:
        """Calculate a score (0-100) representing how well organized the repository is"""
        score = 100

        # Deduct points for too many root files
        root_files = len(structure["files_by_directory"].get("/", []))
        if root_files > 15:
            score -= min(30, (root_files - 15) * 2)

        # Deduct points for large directories
        for large_dir in structure["large_directories"]:
            if large_dir["file_count"] > 50:
                score -= 10

        # Deduct points for very deep nesting
        max_depth = (
            max(structure["depth_analysis"].keys())
            if structure["depth_analysis"]
            else 0
        )
        if max_depth > 6:
            score -= (max_depth - 6) * 5

        # Deduct points for scattered file types
        scattered_count = sum(
            1
            for locations in [
                files
                for files in structure["files_by_type"].values()
                if len(set(os.path.dirname(f) for f in files)) > 3
            ]
        )
        score -= scattered_count * 5

        return max(0, score)

    def _get_recommended_folders(self, project_type: str) -> Dict:
        """Get recommended folder structure for the detected project type"""
        if project_type in self.advanced_structure_patterns:
            return self.advanced_structure_patterns[project_type]["suggested_structure"]

        # Default structure for unknown types
        return {
            "src/": "Source code",
            "tests/": "Test files",
            "docs/": "Documentation",
            "config/": "Configuration files",
        }

    async def analyze_repository(
        self, request: RepoAnalysisRequest
    ) -> RepoAnalysisResult:
        """
        Analyze a GitHub repository and provide structure and cleanup suggestions

        Args:
            request: Repository analysis request

        Returns:
            Analysis results with suggestions
        """
        try:
            # Get repository information
            repo_info = await self._get_repo_info(request)

            # Clone or download repository
            local_path = await self._download_repository(request)

            try:
                # Analyze directory structure
                directory_structure = self._analyze_directory_structure(
                    local_path, request.exclude_patterns
                )

                # Generate structure suggestions
                structure_suggestions = self._generate_structure_suggestions(
                    directory_structure, repo_info
                )

                # Generate cleanup suggestions
                cleanup_suggestions = self._generate_cleanup_suggestions(
                    directory_structure
                )

                # Calculate metrics
                metrics = self._calculate_metrics(directory_structure)

                # Generate AI-powered insights if available
                ai_insights = {}
                if ai_analyzer.is_available():
                    print("🤖 Generating AI-powered analysis...")

                    # Get comprehensive AI analysis
                    ai_structure_analysis = (
                        await ai_analyzer.analyze_repository_structure(
                            repo_info, metrics
                        )
                    )
                    ai_insights.update(ai_structure_analysis)

                    # Get smart recommendations
                    ai_recommendations = (
                        await ai_analyzer.generate_smart_recommendations(
                            cleanup_suggestions, structure_suggestions, repo_info
                        )
                    )
                    ai_insights.update(ai_recommendations)

                    # Get code pattern analysis
                    pattern_analysis = await ai_analyzer.analyze_code_patterns(
                        metrics, repo_info
                    )
                    ai_insights.update(pattern_analysis)

                    # Get project health score
                    health_assessment = await ai_analyzer.generate_project_health_score(
                        {
                            **metrics,
                            "repo_info": repo_info,
                            "structure_suggestions_count": len(structure_suggestions),
                            "cleanup_suggestions_count": len(cleanup_suggestions),
                        }
                    )
                    ai_insights.update(health_assessment)

                # Generate enhanced recommendations with AI insights
                recommendations = self._generate_recommendations(
                    directory_structure,
                    structure_suggestions,
                    cleanup_suggestions,
                    ai_insights,
                )

                return RepoAnalysisResult(
                    repo_info=repo_info,
                    directory_structure=directory_structure,
                    structure_suggestions=structure_suggestions,
                    cleanup_suggestions=cleanup_suggestions,
                    metrics=metrics,
                    recommendations=recommendations,
                    ai_insights=ai_insights if ai_insights else None,
                )

            finally:
                # Cleanup temporary directory
                if local_path and os.path.exists(local_path):
                    self._safe_remove_directory(local_path)

        except Exception as e:
            raise Exception(f"Analysis failed: {str(e)}")

    async def _get_repo_info(self, request: RepoAnalysisRequest) -> Dict:
        """Get repository information from GitHub API"""
        try:
            if request.github_url:
                # Parse GitHub URL
                url_parts = (
                    str(request.github_url)
                    .replace("https://github.com/", "")
                    .split("/")
                )
                owner, repo_name = url_parts[0], url_parts[1]
            else:
                owner, repo_name = request.repo_owner, request.repo_name

            repo = self.github_client.get_repo(f"{owner}/{repo_name}")

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "languages": repo.get_languages(),
                "size": repo.size,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "default_branch": repo.default_branch,
                "license": repo.license.name if repo.license else None,
                "topics": repo.get_topics(),
                "has_issues": repo.has_issues,
                "has_projects": repo.has_projects,
                "has_wiki": repo.has_wiki,
            }
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")

    async def _download_repository(self, request: RepoAnalysisRequest) -> str:
        """Download repository to temporary directory"""
        temp_dir = tempfile.mkdtemp()

        try:
            if request.github_url:
                url_parts = (
                    str(request.github_url)
                    .replace("https://github.com/", "")
                    .split("/")
                )
                owner, repo_name = url_parts[0], url_parts[1]
            else:
                owner, repo_name = request.repo_owner, request.repo_name

            clone_url = f"https://github.com/{owner}/{repo_name}.git"

            # Clone repository with specific options for Windows
            env_vars = os.environ.copy()
            env_vars["GIT_TERMINAL_PROMPT"] = "0"  # Disable git prompts

            try:
                # Try shallow clone first
                Repo.clone_from(
                    clone_url,
                    temp_dir,
                    depth=1,
                    env=env_vars,
                    config="core.longpaths=true",  # Handle long paths on Windows
                )
            except Exception as clone_error:
                # If clone fails, try downloading as zip
                print(f"Clone failed, trying ZIP download: {clone_error}")

                # Remove failed clone directory
                if os.path.exists(temp_dir):
                    self._safe_remove_directory(temp_dir)
                    temp_dir = tempfile.mkdtemp()

                # Download as ZIP
                zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/main.zip"
                response = requests.get(zip_url, timeout=30)

                if response.status_code == 404:
                    # Try 'master' branch if 'main' doesn't exist
                    zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip"
                    response = requests.get(zip_url, timeout=30)

                if response.status_code == 200:
                    import zipfile
                    import io

                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        zip_file.extractall(temp_dir)

                    # Find the extracted directory (usually repo-name-branch)
                    extracted_dirs = [
                        d
                        for d in os.listdir(temp_dir)
                        if os.path.isdir(os.path.join(temp_dir, d))
                    ]

                    if extracted_dirs:
                        # Move contents from extracted directory to temp_dir
                        extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                        for item in os.listdir(extracted_path):
                            src = os.path.join(extracted_path, item)
                            dst = os.path.join(temp_dir, item)
                            if os.path.isdir(src):
                                shutil.move(src, dst)
                            else:
                                shutil.move(src, dst)

                        # Remove empty extracted directory
                        os.rmdir(extracted_path)
                else:
                    raise Exception(
                        f"Failed to download repository: HTTP {response.status_code}"
                    )

            return temp_dir

        except Exception as e:
            if os.path.exists(temp_dir):
                self._safe_remove_directory(temp_dir)
            raise Exception(f"Failed to download repository: {str(e)}")

    def _safe_remove_directory(self, dir_path: str):
        """Safely remove directory on Windows"""

        def handle_remove_readonly(func, path, exc):
            """Handle read-only files on Windows"""
            import stat

            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)

        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Warning: Could not remove directory {dir_path}: {e}")
            # Try alternative cleanup
            try:
                import subprocess

                subprocess.run(["rmdir", "/s", "/q", dir_path], shell=True, check=False)
            except Exception:
                pass  # Ignore cleanup errors

    def _analyze_directory_structure(
        self, root_path: str, exclude_patterns: List[str]
    ) -> DirectoryStructure:
        """Analyze directory structure and file information"""

        def should_exclude(path: str) -> bool:
            for pattern in exclude_patterns:
                if pattern in path:
                    return True
            return False

        def analyze_directory(dir_path: str) -> DirectoryStructure:
            files = []
            subdirectories = []
            total_files = 0
            total_size = 0

            try:
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    relative_path = os.path.relpath(item_path, root_path)

                    if should_exclude(relative_path):
                        continue

                    if os.path.isfile(item_path):
                        file_info = self._analyze_file(item_path, relative_path)
                        files.append(file_info)
                        total_files += 1
                        total_size += file_info.size

                    elif os.path.isdir(item_path):
                        subdir = analyze_directory(item_path)
                        subdirectories.append(subdir)
                        total_files += subdir.total_files
                        total_size += subdir.total_size

            except PermissionError:
                pass

            relative_dir_path = os.path.relpath(dir_path, root_path)
            if relative_dir_path == ".":
                relative_dir_path = "/"

            return DirectoryStructure(
                path=relative_dir_path,
                files=files,
                subdirectories=subdirectories,
                total_files=total_files,
                total_size=total_size,
            )

        return analyze_directory(root_path)

    def _analyze_file(self, file_path: str, relative_path: str) -> FileInfo:
        """Analyze individual file"""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

            # Determine file type
            file_type = self._determine_file_type(relative_path)

            # Detect language
            language = self._detect_language(relative_path)

            # Calculate complexity (simplified)
            complexity_score = self._calculate_file_complexity(file_path, file_type)

            # Determine if file is necessary
            is_necessary, reason = self._is_file_necessary(relative_path, file_type)

            return FileInfo(
                path=relative_path,
                size=size,
                type=file_type,
                language=language,
                complexity_score=complexity_score,
                last_modified=last_modified,
                is_necessary=is_necessary,
                reason=reason,
            )

        except Exception:
            return FileInfo(
                path=relative_path, size=0, type=FileType.UNKNOWN, is_necessary=True
            )

    def _determine_file_type(self, file_path: str) -> FileType:
        """Determine the type of file based on extension and path"""
        file_path_lower = file_path.lower()
        extension = Path(file_path).suffix.lower()

        # Check for test files first
        if any(
            test_pattern in file_path_lower
            for test_pattern in self.file_extensions["test"]
        ):
            return FileType.TEST

        # Check other types
        for file_type, extensions in self.file_extensions.items():
            if file_type == "test":
                continue
            if extension in extensions:
                return FileType(file_type.upper())

        return FileType.UNKNOWN

    def _detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        extension = Path(file_path).suffix.lower()

        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".go": "Go",
            ".rs": "Rust",
            ".kt": "Kotlin",
            ".swift": "Swift",
            ".scala": "Scala",
            ".r": "R",
        }

        return language_map.get(extension)

    def _calculate_file_complexity(
        self, file_path: str, file_type: FileType
    ) -> Optional[float]:
        """Calculate a simple complexity score for the file"""
        if file_type != FileType.SOURCE_CODE:
            return None

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Simple complexity metrics
            lines = len(content.splitlines())
            if lines == 0:
                return 0.0

            # Count complexity indicators
            complexity_indicators = [
                "if ",
                "for ",
                "while ",
                "switch ",
                "case ",
                "catch ",
                "function ",
                "def ",
                "class ",
                "interface ",
                "try ",
            ]

            complexity_count = sum(
                content.count(indicator) for indicator in complexity_indicators
            )

            # Normalize by lines of code
            return min(complexity_count / lines * 10, 10.0)

        except Exception:
            return None

    def _is_file_necessary(
        self, file_path: str, file_type: FileType
    ) -> Tuple[bool, Optional[str]]:
        """Determine if a file is necessary or can be removed"""
        file_path_lower = file_path.lower()

        # Check against unnecessary patterns
        for category, patterns in self.unnecessary_patterns.items():
            for pattern in patterns:
                if pattern.endswith("/"):
                    if pattern[:-1] in file_path_lower:
                        return False, f"Unnecessary {category.replace('_', ' ')}"
                else:
                    if pattern.replace("*", "") in file_path_lower:
                        return False, f"Unnecessary {category.replace('_', ' ')}"

        return True, None

    def _generate_structure_suggestions(
        self, structure: DirectoryStructure, repo_info: Dict
    ) -> List[StructureSuggestion]:
        """Generate suggestions for better directory structure"""
        suggestions = []

        # Detect primary language
        primary_language = repo_info.get("language", "")
        if primary_language:
            primary_language = primary_language.lower()

        languages = repo_info.get("languages", {})

        if not primary_language and languages:
            primary_language = max(languages.keys(), key=languages.get).lower()

        # Get appropriate template
        template = None
        if primary_language:
            for lang in ["python", "javascript", "java"]:
                if lang in primary_language:
                    template = self.structure_templates[lang]
                    break

        if template:
            suggestions.extend(self._compare_with_template(structure, template))

        # Additional structure suggestions
        suggestions.extend(self._analyze_file_organization(structure))

        return sorted(suggestions, key=lambda x: x.priority, reverse=True)

    def _compare_with_template(
        self, structure: DirectoryStructure, template: Dict
    ) -> List[StructureSuggestion]:
        """Compare current structure with best practice template"""
        suggestions = []

        # Check for recommended directories
        current_dirs = {subdir.path for subdir in structure.subdirectories}

        for recommended_dir, description in template["patterns"].items():
            if (
                recommended_dir not in current_dirs
                and f"./{recommended_dir}" not in current_dirs
            ):
                suggestions.append(
                    StructureSuggestion(
                        current_path="",
                        suggested_path=recommended_dir,
                        reason=f"Create {recommended_dir} directory for {description}",
                        priority=4,
                    )
                )

        return suggestions

    def _analyze_file_organization(
        self, structure: DirectoryStructure
    ) -> List[StructureSuggestion]:
        """Analyze file organization and suggest improvements"""
        suggestions = []

        # Check for files in root that should be organized
        root_source_files = [
            f for f in structure.files if f.type == FileType.SOURCE_CODE
        ]

        if len(root_source_files) > 5:
            suggestions.append(
                StructureSuggestion(
                    current_path="/",
                    suggested_path="/src/",
                    reason="Move source files to src/ directory for better organization",
                    priority=3,
                )
            )

        # Check for test files mixed with source
        for subdir in structure.subdirectories:
            source_files = [f for f in subdir.files if f.type == FileType.SOURCE_CODE]
            test_files = [f for f in subdir.files if f.type == FileType.TEST]

            if source_files and test_files:
                suggestions.append(
                    StructureSuggestion(
                        current_path=subdir.path,
                        suggested_path=f"{subdir.path}/tests/",
                        reason="Separate test files from source code",
                        priority=2,
                    )
                )

        return suggestions

    def _generate_cleanup_suggestions(
        self, structure: DirectoryStructure
    ) -> List[CleanupSuggestion]:
        """Generate suggestions for file cleanup"""
        suggestions = []

        def analyze_directory(directory: DirectoryStructure):
            for file_info in directory.files:
                if not file_info.is_necessary:
                    suggestions.append(
                        CleanupSuggestion(
                            file_path=file_info.path,
                            action="delete",
                            reason=file_info.reason or "Unnecessary file",
                            size_savings=file_info.size,
                            risk_level="low",
                        )
                    )

            for subdir in directory.subdirectories:
                analyze_directory(subdir)

        analyze_directory(structure)

        # Find duplicate files
        suggestions.extend(self._find_duplicate_files(structure))

        # Find large unused files
        suggestions.extend(self._find_large_unused_files(structure))

        return sorted(suggestions, key=lambda x: x.size_savings, reverse=True)

    def _find_duplicate_files(
        self, structure: DirectoryStructure
    ) -> List[CleanupSuggestion]:
        """Find potential duplicate files"""
        suggestions = []
        file_sizes = defaultdict(list)

        def collect_files(directory: DirectoryStructure):
            for file_info in directory.files:
                if file_info.size > 0:
                    file_sizes[file_info.size].append(file_info)

            for subdir in directory.subdirectories:
                collect_files(subdir)

        collect_files(structure)

        for size, files in file_sizes.items():
            if len(files) > 1 and size > 1024:  # Only check files larger than 1KB
                for file_info in files[1:]:  # Keep first, suggest removing others
                    suggestions.append(
                        CleanupSuggestion(
                            file_path=file_info.path,
                            action="delete",
                            reason=f"Potential duplicate (same size as {files[0].path})",
                            size_savings=file_info.size,
                            risk_level="medium",
                        )
                    )

        return suggestions

    def _find_large_unused_files(
        self, structure: DirectoryStructure
    ) -> List[CleanupSuggestion]:
        """Find large files that might be unused"""
        suggestions = []
        large_files = []

        def collect_large_files(directory: DirectoryStructure):
            for file_info in directory.files:
                if file_info.size > 1024 * 1024:  # Files larger than 1MB
                    large_files.append(file_info)

            for subdir in directory.subdirectories:
                collect_large_files(subdir)

        collect_large_files(structure)

        for file_info in large_files:
            if file_info.type in [FileType.ASSET, FileType.UNKNOWN]:
                suggestions.append(
                    CleanupSuggestion(
                        file_path=file_info.path,
                        action="move",
                        reason=f"Large file ({file_info.size // 1024}KB) - consider moving to assets or external storage",
                        size_savings=0,
                        risk_level="low",
                    )
                )

        return suggestions

    def _calculate_metrics(self, structure: DirectoryStructure) -> Dict:
        """Calculate repository metrics"""
        total_files = structure.total_files
        total_size = structure.total_size

        file_types = Counter()
        languages = Counter()

        def count_files(directory: DirectoryStructure):
            for file_info in directory.files:
                file_types[file_info.type.value] += 1
                if file_info.language:
                    languages[file_info.language] += 1

            for subdir in directory.subdirectories:
                count_files(subdir)

        count_files(structure)

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": dict(file_types),
            "languages": dict(languages),
            "directory_count": len(structure.subdirectories),
            "avg_file_size": (
                round(total_size / total_files, 2) if total_files > 0 else 0
            ),
        }

    def _generate_recommendations(
        self,
        structure: DirectoryStructure,
        structure_suggestions: List[StructureSuggestion],
        cleanup_suggestions: List[CleanupSuggestion],
        ai_insights: Dict = None,
    ) -> List[str]:
        """Generate high-level recommendations with AI enhancement"""
        recommendations = []

        # Traditional recommendations
        if len(structure_suggestions) > 0:
            recommendations.append(
                f"Consider reorganizing your project structure. "
                f"Found {len(structure_suggestions)} improvement opportunities."
            )

        # Cleanup recommendations
        total_cleanup_savings = sum(s.size_savings for s in cleanup_suggestions)
        if total_cleanup_savings > 1024 * 1024:  # More than 1MB savings
            recommendations.append(
                f"Remove unnecessary files to save {total_cleanup_savings // (1024 * 1024)}MB of space."
            )

        # File organization
        if structure.total_files > 100:
            recommendations.append(
                "Consider breaking down large directories into smaller, more focused modules."
            )

        # Documentation
        has_readme = any(
            f.path.lower() in ["readme.md", "readme.txt", "readme.rst"]
            for f in structure.files
        )
        if not has_readme:
            recommendations.append("Add a README.md file to document your project.")

        # Add AI-powered recommendations if available
        if ai_insights and ai_insights.get("smart_recommendations"):
            recommendations.append(
                "🤖 AI-Powered Insights Available - Check the detailed AI analysis for comprehensive recommendations."
            )

        return recommendations

    async def quick_structure_analysis(
        self, repo_path: str, exclude_patterns: List[str] = None
    ) -> Dict:
        """
        Quick structure analysis for local repositories

        Args:
            repo_path: Path to the local repository
            exclude_patterns: Patterns to exclude from analysis

        Returns:
            Structure analysis results with recommendations
        """
        analysis_result = self.analyze_repo_structure(repo_path, exclude_patterns)

        # Add summary statistics
        analysis_result["summary"] = {
            "organization_level": self._get_organization_level(
                analysis_result["structure_metrics"]["organization_score"]
            ),
            "main_issues": self._identify_main_issues(analysis_result),
            "quick_wins": self._identify_quick_wins(
                analysis_result["structure_suggestions"]
            ),
            "estimated_improvement_time": self._estimate_improvement_time(
                analysis_result["structure_suggestions"]
            ),
        }

        return analysis_result

    def _get_organization_level(self, score: int) -> str:
        """Convert organization score to descriptive level"""
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 30:
            return "Poor"
        else:
            return "Needs Major Restructuring"

    def _identify_main_issues(self, analysis: Dict) -> List[str]:
        """Identify the main structural issues"""
        issues = []

        structure_metrics = analysis["structure_metrics"]
        file_distribution = analysis["file_distribution"]

        if file_distribution["root_files"] > 15:
            issues.append("Too many files in root directory")

        if structure_metrics["max_depth"] > 6:
            issues.append("Directory structure too deep")

        if len(file_distribution["directories_with_mixed_types"]) > 3:
            issues.append("Multiple directories mixing different file types")

        if len(file_distribution["scattered_types"]) > 2:
            issues.append("Similar file types scattered across directories")

        if structure_metrics["large_directories_count"] > 2:
            issues.append("Several directories with too many files")

        return issues

    def _identify_quick_wins(self, suggestions: List[Dict]) -> List[Dict]:
        """Identify suggestions that are quick to implement"""
        quick_wins = []

        for suggestion in suggestions:
            if suggestion.get("priority") == "high" and suggestion["type"] in [
                "create_directory",
                "organize_root",
            ]:
                quick_wins.append(
                    {
                        "action": suggestion["type"],
                        "description": suggestion["reason"],
                        "estimated_time": "15-30 minutes",
                    }
                )

        return quick_wins[:3]  # Top 3 quick wins

    def _estimate_improvement_time(self, suggestions: List[Dict]) -> str:
        """Estimate time needed to implement all suggestions"""
        total_suggestions = len(suggestions)

        if total_suggestions == 0:
            return "No improvements needed"
        elif total_suggestions <= 3:
            return "1-2 hours"
        elif total_suggestions <= 6:
            return "3-5 hours"
        elif total_suggestions <= 10:
            return "1-2 days"
        else:
            return "Several days to 1 week"


# Global analyzer instance
analyzer = GitHubRepoAnalyzer()


def analyze_local_structure(repo_path: str, exclude_patterns: List[str] = None) -> Dict:
    """
    Analyze local repository structure without GitHub API calls

    Args:
        repo_path: Path to the local repository
        exclude_patterns: Patterns to exclude from analysis

    Returns:
        Structure analysis results
    """
    local_analyzer = GitHubRepoAnalyzer()
    return local_analyzer.analyze_repo_structure(repo_path, exclude_patterns)


async def quick_structure_check(repo_path: str) -> Dict:
    """
    Quick structure check with recommendations for local repo

    Args:
        repo_path: Path to the local repository

    Returns:
        Quick analysis with actionable recommendations
    """
    local_analyzer = GitHubRepoAnalyzer()
    return await local_analyzer.quick_structure_analysis(repo_path)


# Global analyzer instance
analyzer = GitHubRepoAnalyzer()


async def analyze(request: RepoAnalysisRequest) -> RepoAnalysisResult:
    """
    Main function to analyze a repository

    Args:
        request: Repository analysis request

    Returns:
        Analysis results
    """
    return await analyzer.analyze_repository(request)
