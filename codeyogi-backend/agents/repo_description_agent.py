import os
import re
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Any
from datetime import datetime
import requests
from github import Github
from git import Repo
from collections import defaultdict, Counter
import ast

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    RepoDescriptionRequest,
    RepoDescriptionResult,
    FlowchartNode,
    FlowchartEdge,
    ProjectFlowchart,
    DirectoryStructure,
    FileInfo,
    FileType,
)
from agents.ai_analyzer import ai_analyzer


class RepoDescriptionAgent:
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the Repository Description Agent

        Args:
            github_token: GitHub personal access token for API access
        """
        self.github_token = github_token
        self.github_client = Github(github_token) if github_token else Github()

        # Framework and library patterns
        self.framework_patterns = {
            "python": {
                "web": ["flask", "django", "fastapi", "tornado", "bottle", "pyramid"],
                "data": ["pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly"],
                "ml": ["tensorflow", "keras", "pytorch", "scikit-learn", "xgboost"],
                "testing": ["pytest", "unittest", "nose", "tox"],
                "async": ["asyncio", "aiohttp", "celery"],
                "database": ["sqlalchemy", "pymongo", "psycopg2", "mysql"],
            },
            "javascript": {
                "frontend": ["react", "vue", "angular", "svelte", "next", "nuxt"],
                "backend": ["express", "koa", "fastify", "nest"],
                "testing": ["jest", "mocha", "cypress", "puppeteer"],
                "build": ["webpack", "vite", "rollup", "parcel"],
                "state": ["redux", "mobx", "vuex", "pinia"],
            },
            "java": {
                "framework": ["spring", "hibernate", "struts", "jsf"],
                "testing": ["junit", "testng", "mockito"],
                "build": ["maven", "gradle", "ant"],
                "web": ["servlet", "jsp", "spring-boot"],
            },
        }

        # Project type patterns
        self.project_patterns = {
            "web_app": ["app.py", "main.py", "server.js", "index.html", "package.json"],
            "api": ["api", "routes", "endpoints", "controllers", "handlers"],
            "library": ["setup.py", "__init__.py", "lib", "src"],
            "cli": ["cli", "command", "cmd", "console"],
            "desktop": ["gui", "ui", "window", "qt", "tkinter"],
            "mobile": ["android", "ios", "react-native", "flutter"],
            "data_science": ["notebook", "analysis", "model", "dataset"],
            "ml_project": ["model", "training", "inference", "pipeline"],
            "game": ["game", "player", "scene", "sprite", "engine"],
            "microservice": ["service", "microservice", "docker", "kubernetes"],
        }

    async def analyze_repository_description(
        self, request: RepoDescriptionRequest
    ) -> RepoDescriptionResult:
        """
        Analyze a GitHub repository and provide comprehensive description with flowchart

        Args:
            request: Repository description request

        Returns:
            Detailed repository description with flowchart
        """
        try:
            # Get repository information
            repo_info = await self._get_repo_info(request)

            # Clone or download repository
            local_path = await self._download_repository(request)

            try:
                # Analyze repository structure
                directory_structure = self._analyze_directory_structure(local_path)

                # Detect tech stack
                tech_stack = self._analyze_tech_stack(directory_structure, repo_info)

                # Determine project type
                project_type = self._determine_project_type(
                    directory_structure, tech_stack
                )

                # Analyze architecture
                architecture_summary = await self._analyze_architecture(
                    directory_structure, tech_stack, repo_info
                )

                # Extract key features
                key_features = await self._extract_key_features(
                    directory_structure, repo_info, local_path
                )

                # Calculate complexity
                complexity_analysis = self._analyze_complexity(directory_structure)

                # Generate flowchart
                flowchart = await self._generate_project_flowchart(
                    directory_structure, tech_stack, project_type, local_path
                )

                # Generate AI-powered description
                ai_insights = {}
                description = await self._generate_description(
                    repo_info,
                    tech_stack,
                    architecture_summary,
                    key_features,
                    project_type,
                )

                if ai_analyzer.is_available():
                    ai_insights = await self._get_ai_insights(
                        repo_info, tech_stack, architecture_summary, complexity_analysis
                    )

                return RepoDescriptionResult(
                    repo_info=repo_info,
                    description=description,
                    tech_stack=tech_stack,
                    architecture_summary=architecture_summary,
                    key_features=key_features,
                    project_type=project_type,
                    complexity_analysis=complexity_analysis,
                    flowchart=flowchart,
                    ai_insights=ai_insights if ai_insights else None,
                )

            finally:
                # Cleanup temporary directory
                if local_path and os.path.exists(local_path):
                    self._safe_remove_directory(local_path)

        except Exception as e:
            raise Exception(f"Repository description analysis failed: {str(e)}")

    async def _get_repo_info(self, request: RepoDescriptionRequest) -> Dict:
        """Get repository information from GitHub API"""
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
                "open_issues": repo.open_issues_count,
                "subscribers_count": repo.subscribers_count,
                "watchers_count": repo.watchers_count,
            }
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")

    async def _download_repository(self, request: RepoDescriptionRequest) -> str:
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
            env_vars["GIT_TERMINAL_PROMPT"] = "0"

            try:
                # Try shallow clone first
                Repo.clone_from(
                    clone_url,
                    temp_dir,
                    depth=1,
                    env=env_vars,
                    config="core.longpaths=true",
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
                    zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/master.zip"
                    response = requests.get(zip_url, timeout=30)

                if response.status_code == 200:
                    import zipfile
                    import io

                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        zip_file.extractall(temp_dir)

                    # Find the extracted directory
                    extracted_dirs = [
                        d
                        for d in os.listdir(temp_dir)
                        if os.path.isdir(os.path.join(temp_dir, d))
                    ]

                    if extracted_dirs:
                        extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                        for item in os.listdir(extracted_path):
                            src = os.path.join(extracted_path, item)
                            dst = os.path.join(temp_dir, item)
                            if os.path.isdir(src):
                                shutil.move(src, dst)
                            else:
                                shutil.move(src, dst)
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
            import stat

            if os.path.exists(path):
                os.chmod(path, stat.S_IWRITE)
                func(path)

        try:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Warning: Could not remove directory {dir_path}: {e}")

    def _analyze_directory_structure(self, root_path: str) -> DirectoryStructure:
        """Analyze directory structure for description purposes"""

        def analyze_directory(dir_path: str) -> DirectoryStructure:
            files = []
            subdirectories = []
            total_files = 0
            total_size = 0

            try:
                for item in os.listdir(dir_path):
                    if item.startswith("."):
                        continue

                    item_path = os.path.join(dir_path, item)
                    relative_path = os.path.relpath(item_path, root_path)

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
        """Analyze individual file for description purposes"""
        try:
            stat = os.stat(file_path)
            size = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

            # Determine file type
            file_type = self._determine_file_type(relative_path)

            # Detect language
            language = self._detect_language(relative_path)

            return FileInfo(
                path=relative_path,
                size=size,
                type=file_type,
                language=language,
                last_modified=last_modified,
                is_necessary=True,
            )

        except Exception:
            return FileInfo(
                path=relative_path, size=0, type=FileType.UNKNOWN, is_necessary=True
            )

    def _determine_file_type(self, file_path: str) -> FileType:
        """Determine the type of file based on extension and path"""
        extension = Path(file_path).suffix.lower()

        source_exts = {
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
        }
        config_exts = {".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env"}
        doc_exts = {".md", ".rst", ".txt", ".doc", ".html"}

        if extension in source_exts:
            return FileType.SOURCE_CODE
        elif extension in config_exts:
            return FileType.CONFIG
        elif extension in doc_exts:
            return FileType.DOCUMENTATION
        elif "test" in file_path.lower():
            return FileType.TEST
        else:
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
        }

        return language_map.get(extension)

    def _analyze_tech_stack(
        self, structure: DirectoryStructure, repo_info: Dict
    ) -> Dict[str, Any]:
        """Analyze and detect technology stack"""
        tech_stack = {
            "primary_language": repo_info.get("language"),
            "languages": repo_info.get("languages", {}),
            "frameworks": [],
            "libraries": [],
            "tools": [],
            "databases": [],
            "deployment": [],
        }

        # Collect all files
        all_files = []

        def collect_files(dir_struct: DirectoryStructure):
            all_files.extend([f.path for f in dir_struct.files])
            for subdir in dir_struct.subdirectories:
                collect_files(subdir)

        collect_files(structure)

        # Analyze configuration files
        config_files = [
            f
            for f in all_files
            if any(
                f.endswith(ext)
                for ext in [
                    "package.json",
                    "requirements.txt",
                    "pom.xml",
                    "Cargo.toml",
                    "go.mod",
                ]
            )
        ]

        # Check for frameworks and libraries
        primary_lang = tech_stack["primary_language"]
        if primary_lang and primary_lang.lower() in self.framework_patterns:
            patterns = self.framework_patterns[primary_lang.lower()]

            for category, frameworks in patterns.items():
                for framework in frameworks:
                    if any(framework in f.lower() for f in all_files):
                        tech_stack["frameworks"].append(framework)

        # Check for common tools
        if any("docker" in f.lower() for f in all_files):
            tech_stack["tools"].append("Docker")
        if any(".github" in f for f in all_files):
            tech_stack["tools"].append("GitHub Actions")
        if any("makefile" in f.lower() for f in all_files):
            tech_stack["tools"].append("Make")

        return tech_stack

    def _determine_project_type(
        self, structure: DirectoryStructure, tech_stack: Dict
    ) -> str:
        """Determine the type of project"""
        all_files = []

        def collect_files(dir_struct: DirectoryStructure):
            all_files.extend([f.path.lower() for f in dir_struct.files])
            for subdir in dir_struct.subdirectories:
                collect_files(subdir)

        collect_files(structure)

        # Check patterns
        for project_type, patterns in self.project_patterns.items():
            if any(any(pattern in f for f in all_files) for pattern in patterns):
                return project_type.replace("_", " ").title()

        # Fallback based on primary language
        primary_lang_value = tech_stack.get("primary_language")
        primary_lang = primary_lang_value.lower() if primary_lang_value else ""
        if primary_lang == "python":
            return "Python Application"
        elif primary_lang in ["javascript", "typescript"]:
            return "JavaScript Application"
        elif primary_lang == "java":
            return "Java Application"
        else:
            return "Software Project"

    async def _analyze_architecture(
        self, structure: DirectoryStructure, tech_stack: Dict, repo_info: Dict
    ) -> str:
        """Analyze project architecture"""
        architecture_patterns = []

        all_dirs = []

        def collect_dirs(dir_struct: DirectoryStructure):
            all_dirs.append(dir_struct.path)
            for subdir in dir_struct.subdirectories:
                collect_dirs(subdir)

        collect_dirs(structure)

        # Detect common architectural patterns
        if any(
            "mvc" in d.lower()
            or all(
                x in [d.lower() for d in all_dirs]
                for x in ["models", "views", "controllers"]
            )
            for d in all_dirs
        ):
            architecture_patterns.append("MVC (Model-View-Controller)")

        if any("api" in d.lower() for d in all_dirs):
            architecture_patterns.append("API-based")

        if any("microservice" in d.lower() for d in all_dirs):
            architecture_patterns.append("Microservices")

        if any("components" in d.lower() for d in all_dirs):
            architecture_patterns.append("Component-based")

        # Generate architecture summary
        if architecture_patterns:
            return f"The project follows {', '.join(architecture_patterns)} architecture pattern(s)."
        else:
            return f"Standard {tech_stack.get('primary_language', 'software')} project structure."

    async def _extract_key_features(
        self, structure: DirectoryStructure, repo_info: Dict, local_path: str
    ) -> List[str]:
        """Extract key features from the repository"""
        features = []

        # Check README for features
        readme_files = ["README.md", "README.rst", "README.txt"]
        for readme_file in readme_files:
            readme_path = os.path.join(local_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()

                    # Look for feature indicators
                    feature_keywords = [
                        "authentication",
                        "database",
                        "api",
                        "rest",
                        "graphql",
                        "dashboard",
                        "analytics",
                        "monitoring",
                        "testing",
                        "deployment",
                        "docker",
                        "kubernetes",
                        "machine learning",
                        "ai",
                        "real-time",
                        "chat",
                        "notification",
                        "payment",
                    ]

                    for keyword in feature_keywords:
                        if keyword in content:
                            features.append(keyword.title())

                except Exception:
                    pass
                break

        # Add features based on file analysis
        all_files = []

        def collect_files(dir_struct: DirectoryStructure):
            all_files.extend([f.path.lower() for f in dir_struct.files])
            for subdir in dir_struct.subdirectories:
                collect_files(subdir)

        collect_files(structure)

        # Feature detection from file patterns
        if any("test" in f for f in all_files):
            features.append("Unit Testing")
        if any("docker" in f for f in all_files):
            features.append("Containerization")
        if any("api" in f for f in all_files):
            features.append("RESTful API")
        if any("database" in f or "db" in f for f in all_files):
            features.append("Database Integration")

        return list(set(features))  # Remove duplicates

    def _analyze_complexity(self, structure: DirectoryStructure) -> Dict[str, Any]:
        """Analyze project complexity"""
        total_files = structure.total_files
        total_size = structure.total_size

        # Count directories
        dir_count = 0

        def count_dirs(dir_struct: DirectoryStructure):
            nonlocal dir_count
            dir_count += 1
            for subdir in dir_struct.subdirectories:
                count_dirs(subdir)

        count_dirs(structure)

        # Calculate complexity score (0-10)
        complexity_factors = {
            "file_count": min(total_files / 100, 3),  # Max 3 points
            "directory_depth": min(dir_count / 20, 2),  # Max 2 points
            "size_factor": min(
                total_size / (1024 * 1024 * 10), 2
            ),  # Max 2 points for 10MB
        }

        complexity_score = sum(complexity_factors.values())

        if complexity_score < 2:
            complexity_level = "Low"
        elif complexity_score < 5:
            complexity_level = "Medium"
        else:
            complexity_level = "High"

        return {
            "score": round(complexity_score, 2),
            "level": complexity_level,
            "factors": complexity_factors,
            "total_files": total_files,
            "total_directories": dir_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }

    async def _generate_project_flowchart(
        self,
        structure: DirectoryStructure,
        tech_stack: Dict,
        project_type: str,
        local_path: str,
    ) -> ProjectFlowchart:
        """Generate project flowchart based on structure and code analysis"""
        nodes = []
        edges = []

        # Start node
        nodes.append(
            FlowchartNode(
                id="start",
                label="Start",
                type="start",
                description="Application entry point",
            )
        )

        # Analyze main files to understand flow
        main_files = self._find_main_files(structure)

        # Create nodes for main components
        node_id = 1

        for main_file in main_files:
            nodes.append(
                FlowchartNode(
                    id=f"main_{node_id}",
                    label=f"Main Module\n({main_file})",
                    type="process",
                    description=f"Primary application logic in {main_file}",
                )
            )

            # Connect start to main
            edges.append(
                FlowchartEdge(
                    from_node="start", to_node=f"main_{node_id}", label="Initialize"
                )
            )
            node_id += 1

        # Add common components based on project type
        if "api" in project_type.lower() or "web" in project_type.lower():
            nodes.extend(
                [
                    FlowchartNode(
                        id="routing",
                        label="Request Routing",
                        type="decision",
                        description="Route incoming requests",
                    ),
                    FlowchartNode(
                        id="processing",
                        label="Business Logic",
                        type="process",
                        description="Process requests and apply business rules",
                    ),
                    FlowchartNode(
                        id="response",
                        label="Send Response",
                        type="process",
                        description="Format and send response",
                    ),
                ]
            )

            # Connect the flow
            if main_files:
                edges.extend(
                    [
                        FlowchartEdge(
                            from_node="main_1",
                            to_node="routing",
                            label="Handle Request",
                        ),
                        FlowchartEdge(
                            from_node="routing",
                            to_node="processing",
                            label="Valid Route",
                        ),
                        FlowchartEdge(
                            from_node="processing",
                            to_node="response",
                            label="Process Complete",
                        ),
                    ]
                )

        # Add database node if database-related files found
        if self._has_database_components(structure):
            nodes.append(
                FlowchartNode(
                    id="database",
                    label="Database",
                    type="data",
                    description="Data storage and retrieval",
                )
            )

            edges.append(
                FlowchartEdge(
                    from_node="processing", to_node="database", label="Query/Update"
                )
            )

        # End node
        nodes.append(
            FlowchartNode(
                id="finish", label="End", type="end", description="Process complete"
            )
        )

        # Connect to end
        if "response" in [node.id for node in nodes]:
            edges.append(FlowchartEdge(from_node="response", to_node="finish"))
        elif main_files:
            edges.append(FlowchartEdge(from_node="main_1", to_node="finish"))

        # Generate Mermaid diagram
        mermaid_diagram = self._generate_mermaid_diagram(nodes, edges)

        return ProjectFlowchart(
            title=f"{project_type} Flow",
            description=f"High-level flow diagram for the {project_type.lower()}",
            nodes=nodes,
            edges=edges,
            mermaid_diagram=mermaid_diagram,
            complexity_score=len(nodes) / 10,  # Simple complexity based on node count
        )

    def _find_main_files(self, structure: DirectoryStructure) -> List[str]:
        """Find main entry point files"""
        main_patterns = [
            "main.py",
            "app.py",
            "server.py",
            "index.js",
            "app.js",
            "server.js",
            "Main.java",
            "Application.java",
            "main.go",
        ]

        main_files = []

        def search_main_files(dir_struct: DirectoryStructure):
            for file in dir_struct.files:
                if any(pattern in file.path for pattern in main_patterns):
                    main_files.append(file.path)

            for subdir in dir_struct.subdirectories:
                search_main_files(subdir)

        search_main_files(structure)
        return main_files[:3]  # Return max 3 main files

    def _has_database_components(self, structure: DirectoryStructure) -> bool:
        """Check if project has database-related components"""
        db_indicators = ["model", "db", "database", "sql", "mongo", "redis"]

        def check_db_files(dir_struct: DirectoryStructure) -> bool:
            for file in dir_struct.files:
                if any(indicator in file.path.lower() for indicator in db_indicators):
                    return True

            for subdir in dir_struct.subdirectories:
                if any(indicator in subdir.path.lower() for indicator in db_indicators):
                    return True
                if check_db_files(subdir):
                    return True
            return False

        return check_db_files(structure)

    def _generate_mermaid_diagram(
        self, nodes: List[FlowchartNode], edges: List[FlowchartEdge]
    ) -> str:
        """Generate Mermaid flowchart diagram"""
        mermaid = ["graph TD"]

        # Reserved keywords in Mermaid that should be avoided
        reserved_keywords = {"end", "start", "subgraph", "class", "click", "style"}

        # Add nodes with proper Mermaid syntax
        for node in nodes:
            # Clean label for multi-line support
            clean_label = node.label.replace("\n", "<br>")

            # Ensure node ID doesn't conflict with reserved keywords
            node_id = node.id
            if node_id.lower() in reserved_keywords:
                node_id = f"node_{node_id}"

            if node.type == "start":
                mermaid.append(f"    {node_id}([{clean_label}])")
            elif node.type == "end":
                mermaid.append(f"    {node_id}([{clean_label}])")
            elif node.type == "decision":
                mermaid.append(f"    {node_id}{{{clean_label}}}")
            elif node.type == "data":
                mermaid.append(f"    {node_id}[({clean_label})]")
            else:
                mermaid.append(f'    {node_id}["{clean_label}"]')

        # Add edges with proper syntax
        for edge in edges:
            # Handle reserved keywords in edge references
            from_node = edge.from_node
            to_node = edge.to_node

            if from_node.lower() in reserved_keywords:
                from_node = f"node_{from_node}"
            if to_node.lower() in reserved_keywords:
                to_node = f"node_{to_node}"

            if edge.label:
                mermaid.append(f"    {from_node} -->|{edge.label}| {to_node}")
            else:
                mermaid.append(f"    {from_node} --> {to_node}")

        return "\n".join(mermaid)

    async def _generate_description(
        self,
        repo_info: Dict,
        tech_stack: Dict,
        architecture: str,
        features: List[str],
        project_type: str,
    ) -> str:
        """Generate comprehensive repository description"""
        name = repo_info.get("name", "Unknown Project")
        description = repo_info.get("description", "")
        primary_lang = tech_stack.get("primary_language", "Unknown")

        # Build description
        desc_parts = []

        # Project introduction
        if description:
            desc_parts.append(f"{name} is {description}")
        else:
            desc_parts.append(
                f"{name} is a {project_type.lower()} built with {primary_lang}"
            )

        # Technical details
        if tech_stack.get("frameworks"):
            frameworks = ", ".join(tech_stack["frameworks"][:3])
            desc_parts.append(f"The project uses {frameworks} as its main framework(s)")

        # Architecture
        desc_parts.append(architecture)

        # Features
        if features:
            feature_list = ", ".join(features[:5])
            desc_parts.append(f"Key features include: {feature_list}")

        # Repository stats
        stars = repo_info.get("stars", 0)
        forks = repo_info.get("forks", 0)
        if stars > 0 or forks > 0:
            desc_parts.append(f"The repository has {stars} stars and {forks} forks")

        return ". ".join(desc_parts) + "."

    async def _get_ai_insights(
        self, repo_info: Dict, tech_stack: Dict, architecture: str, complexity: Dict
    ) -> Dict[str, Any]:
        """Get AI-powered insights about the repository"""
        if not ai_analyzer.is_available():
            return {"ai_insights": "AI analysis not available"}

        try:
            context = {
                "repository": repo_info,
                "tech_stack": tech_stack,
                "architecture": architecture,
                "complexity": complexity,
            }

            prompt = f"""
Analyze this repository and provide strategic insights:

Repository Context:
{json.dumps(context, indent=2)}

Provide insights on:
1. **Strategic Value**: What makes this project valuable?
2. **Technical Strengths**: Key technical advantages
3. **Potential Improvements**: Areas for enhancement
4. **Market Position**: How it compares to similar projects
5. **Innovation Aspects**: Novel or interesting approaches
6. **Scalability Assessment**: Growth potential
7. **Developer Experience**: Ease of contribution

Provide specific, actionable insights with clear reasoning.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software architect and technology consultant with expertise in evaluating software projects.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )

            return {
                "strategic_analysis": response.choices[0].message.content,
                "model_used": "llama-3.1-8b-instant",
                "analysis_type": "strategic_repository_analysis",
            }

        except Exception as e:
            return {"ai_insights": f"AI analysis failed: {str(e)}"}


# Global agent instance
description_agent = RepoDescriptionAgent()


async def analyze_repository_description(
    request: RepoDescriptionRequest,
) -> RepoDescriptionResult:
    """
    Main function to analyze repository for description and flowchart

    Args:
        request: Repository description request

    Returns:
        Comprehensive repository description with flowchart
    """
    return await description_agent.analyze_repository_description(request)
