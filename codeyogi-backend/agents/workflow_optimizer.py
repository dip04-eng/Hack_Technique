import os
import yaml
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from github import Github
from git import Repo
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class WorkflowAnalysis:
    """Data class for workflow analysis results"""

    repo_language: str
    framework_type: str
    dependencies: List[str]
    existing_workflows: List[Dict]
    project_structure: Dict
    recommended_actions: List[str]
    optimization_score: int


@dataclass
class OptimizedWorkflow:
    """Data class for optimized workflow configuration"""

    workflow_name: str
    workflow_content: str
    optimization_type: str  # "new" or "improved"
    improvements: List[str]
    estimated_time_savings: str
    confidence_score: int


class WorkflowOptimizer:
    def __init__(
        self, github_token: Optional[str] = None, groq_api_key: Optional[str] = None
    ):
        """
        Initialize the Workflow Optimizer

        Args:
            github_token: GitHub personal access token
            groq_api_key: Groq AI API key
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

        # Initialize clients
        self.github_client = (
            Github(self.github_token) if self.github_token else Github()
        )
        self.groq_client = (
            Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        )

        # Framework detection patterns
        self.framework_patterns = {
            "python": {
                "django": ["manage.py", "settings.py", "django"],
                "flask": ["app.py", "flask", "from flask"],
                "fastapi": ["main.py", "fastapi", "from fastapi"],
                "poetry": ["pyproject.toml"],
                "pipenv": ["Pipfile"],
                "pytest": ["pytest", "test_", "_test.py"],
                "unittest": ["unittest", "TestCase"],
            },
            "javascript": {
                "react": ["package.json", "react", "jsx"],
                "vue": ["vue.config.js", "vue", ".vue"],
                "angular": ["angular.json", "@angular"],
                "express": ["express", "app.js"],
                "nextjs": ["next.config.js", "next"],
                "nuxt": ["nuxt.config.js"],
                "jest": ["jest.config.js", "jest"],
                "cypress": ["cypress.json", "cypress"],
                "npm": ["package.json"],
                "yarn": ["yarn.lock"],
                "pnpm": ["pnpm-lock.yaml"],
            },
            "java": {
                "maven": ["pom.xml"],
                "gradle": ["build.gradle", "gradle.build"],
                "spring": ["spring", "@SpringBootApplication"],
                "junit": ["junit", "@Test"],
            },
            "go": {"modules": ["go.mod"], "testing": ["_test.go"]},
            "rust": {"cargo": ["Cargo.toml"], "testing": ["#[test]"]},
        }

        # Common workflow templates
        self.workflow_templates = {
            "python-basic": self._get_python_basic_workflow(),
            "python-django": self._get_python_django_workflow(),
            "python-fastapi": self._get_python_fastapi_workflow(),
            "javascript-react": self._get_javascript_react_workflow(),
            "javascript-node": self._get_javascript_node_workflow(),
            "java-maven": self._get_java_maven_workflow(),
            "go-basic": self._get_go_basic_workflow(),
            "rust-basic": self._get_rust_basic_workflow(),
            "docker-multi": self._get_docker_workflow(),
        }

    async def analyze_and_optimize_workflow(
        self, repo_url: str, custom_input: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main function to analyze repository and generate optimized workflow

        Args:
            repo_url: GitHub repository URL

        Returns:
            Comprehensive analysis and optimization results
        """
        try:
            # Parse repository information
            repo_info = await self._get_repo_info(repo_url)

            # Download repository for analysis
            local_path = await self._download_repository(repo_url)

            try:
                # Analyze repository structure and dependencies
                analysis = await self._analyze_repository_structure(
                    local_path, repo_info
                )

                # Detect existing workflows
                existing_workflows = self._detect_existing_workflows(local_path)
                analysis.existing_workflows = existing_workflows


                # Always use Groq AI for workflow generation if available
                if self.groq_client:
                    ai_analysis = await self._ai_analyze_workflow_needs(
                        analysis, repo_info, custom_input=custom_input
                    )
                    optimized_workflow = await self._ai_generate_optimized_workflow(
                        analysis, ai_analysis, custom_input=custom_input
                    )
                else:
                    # Fallback to template-based optimization
                    optimized_workflow = self._template_based_optimization(analysis)
                    ai_analysis = {
                        "message": "AI analysis not available - using template-based optimization"
                    }

                return {
                    "repository": repo_info,
                    "analysis": analysis.__dict__,
                    "ai_insights": ai_analysis,
                    "optimized_workflow": (
                        optimized_workflow.__dict__ if optimized_workflow else None
                    ),
                    "recommendations": self._generate_implementation_guide(
                        analysis, optimized_workflow
                    ),
                    "timestamp": datetime.now().isoformat(),
                }

            finally:
                # Cleanup
                if local_path and os.path.exists(local_path):
                    shutil.rmtree(local_path, ignore_errors=True)

        except Exception as e:
            raise Exception(f"Workflow optimization failed: {str(e)}")

    async def _get_repo_info(self, repo_url: str) -> Dict[str, Any]:
        """Extract repository information from GitHub"""
        # Parse GitHub URL
        if "github.com" in repo_url:
            parts = (
                repo_url.replace("https://github.com/", "")
                .replace(".git", "")
                .split("/")
            )
            owner, repo_name = parts[0], parts[1]
        else:
            raise ValueError("Invalid GitHub URL")

        try:
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
                "default_branch": repo.default_branch,
                "topics": repo.get_topics(),
                "has_issues": repo.has_issues,
                "has_projects": repo.has_projects,
                "visibility": "private" if repo.private else "public",
            }
        except Exception as e:
            raise Exception(f"Failed to get repository info: {str(e)}")

    async def _download_repository(self, repo_url: str) -> str:
        """Download repository to temporary directory"""
        temp_dir = tempfile.mkdtemp()

        try:
            # Try Git clone first
            try:
                Repo.clone_from(repo_url, temp_dir, depth=1)
            except Exception:
                # Fallback to ZIP download
                parts = (
                    repo_url.replace("https://github.com/", "")
                    .replace(".git", "")
                    .split("/")
                )
                owner, repo_name = parts[0], parts[1]

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

                    # Move extracted content to root
                    extracted_dirs = [
                        d
                        for d in os.listdir(temp_dir)
                        if os.path.isdir(os.path.join(temp_dir, d))
                    ]
                    if extracted_dirs:
                        extracted_path = os.path.join(temp_dir, extracted_dirs[0])
                        for item in os.listdir(extracted_path):
                            shutil.move(
                                os.path.join(extracted_path, item),
                                os.path.join(temp_dir, item),
                            )
                        os.rmdir(extracted_path)
                else:
                    raise Exception(
                        f"Failed to download repository: HTTP {response.status_code}"
                    )

            return temp_dir

        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    async def _analyze_repository_structure(
        self, repo_path: str, repo_info: Dict
    ) -> WorkflowAnalysis:
        """Analyze repository structure to understand project type and needs"""

        # Detect programming language and framework
        language = repo_info.get("language", "").lower()
        if not language:
            language = self._detect_language_from_files(repo_path)

        framework_type = self._detect_framework(repo_path, language)
        dependencies = self._extract_dependencies(repo_path, language)
        project_structure = self._analyze_project_structure(repo_path)

        # Generate basic recommendations
        recommended_actions = []
        optimization_score = 50  # Base score

        # Analyze testing setup
        if self._has_tests(repo_path, language):
            optimization_score += 15
        else:
            recommended_actions.append("Add automated testing")

        # Check for Docker
        if os.path.exists(os.path.join(repo_path, "Dockerfile")):
            optimization_score += 10
        elif framework_type in ["django", "fastapi", "express", "spring"]:
            recommended_actions.append("Consider containerization with Docker")

        # Check for security scanning
        if not self._has_security_workflow(repo_path):
            recommended_actions.append("Add security vulnerability scanning")

        return WorkflowAnalysis(
            repo_language=language,
            framework_type=framework_type,
            dependencies=dependencies,
            existing_workflows=[],  # Will be filled later
            project_structure=project_structure,
            recommended_actions=recommended_actions,
            optimization_score=optimization_score,
        )

    def _detect_existing_workflows(self, repo_path: str) -> List[Dict]:
        """Detect existing CI/CD workflows in the repository"""
        workflows = []

        # Check GitHub Actions
        github_workflows_path = os.path.join(repo_path, ".github", "workflows")
        if os.path.exists(github_workflows_path):
            for file in os.listdir(github_workflows_path):
                if file.endswith((".yml", ".yaml")):
                    file_path = os.path.join(github_workflows_path, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            workflow_data = yaml.safe_load(content)
                            workflows.append(
                                {
                                    "name": file,
                                    "type": "github-actions",
                                    "content": content,
                                    "parsed": workflow_data,
                                    "path": file_path,
                                }
                            )
                    except Exception as e:
                        workflows.append(
                            {
                                "name": file,
                                "type": "github-actions",
                                "error": f"Failed to parse: {str(e)}",
                                "path": file_path,
                            }
                        )

        # Check other CI systems
        ci_files = {
            "travis": [".travis.yml"],
            "circleci": [".circleci/config.yml"],
            "appveyor": [".appveyor.yml", "appveyor.yml"],
            "jenkins": ["Jenkinsfile"],
            "gitlab": [".gitlab-ci.yml"],
        }

        for ci_type, files in ci_files.items():
            for file_name in files:
                file_path = os.path.join(repo_path, file_name)
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            workflows.append(
                                {
                                    "name": file_name,
                                    "type": ci_type,
                                    "content": content,
                                    "path": file_path,
                                }
                            )
                    except Exception as e:
                        workflows.append(
                            {
                                "name": file_name,
                                "type": ci_type,
                                "error": f"Failed to read: {str(e)}",
                                "path": file_path,
                            }
                        )

        return workflows

    def _detect_language_from_files(self, repo_path: str) -> str:
        """Detect primary language from file extensions"""
        language_extensions = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".ts", ".tsx"],
            "java": [".java"],
            "go": [".go"],
            "rust": [".rs"],
            "php": [".php"],
            "ruby": [".rb"],
            "csharp": [".cs"],
            "cpp": [".cpp", ".cc", ".cxx"],
            "c": [".c"],
        }

        file_counts = {}

        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common build directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["node_modules", "__pycache__", "target", "build"]
            ]

            for file in files:
                ext = Path(file).suffix.lower()
                for lang, extensions in language_extensions.items():
                    if ext in extensions:
                        file_counts[lang] = file_counts.get(lang, 0) + 1

        if file_counts:
            return max(file_counts.keys(), key=file_counts.get)
        return "unknown"

    def _detect_framework(self, repo_path: str, language: str) -> str:
        """Detect framework or project type"""
        if language not in self.framework_patterns:
            return "generic"

        patterns = self.framework_patterns[language]
        detected_frameworks = []

        for framework, indicators in patterns.items():
            for indicator in indicators:
                # Check for files
                if "." in indicator:
                    if self._file_exists_in_repo(repo_path, indicator):
                        detected_frameworks.append(framework)
                        break
                # Check for content in files
                else:
                    if self._content_exists_in_repo(repo_path, indicator):
                        detected_frameworks.append(framework)
                        break

        # Return the most specific framework detected
        priority_order = {
            "python": ["django", "fastapi", "flask", "poetry", "pipenv"],
            "javascript": ["nextjs", "nuxt", "react", "vue", "angular", "express"],
        }

        if language in priority_order:
            for framework in priority_order[language]:
                if framework in detected_frameworks:
                    return framework

        return detected_frameworks[0] if detected_frameworks else "generic"

    def _extract_dependencies(self, repo_path: str, language: str) -> List[str]:
        """Extract project dependencies"""
        dependencies = []

        dependency_files = {
            "python": ["requirements.txt", "pyproject.toml", "Pipfile", "setup.py"],
            "javascript": ["package.json"],
            "java": ["pom.xml", "build.gradle"],
            "go": ["go.mod"],
            "rust": ["Cargo.toml"],
        }

        if language in dependency_files:
            for dep_file in dependency_files[language]:
                file_path = os.path.join(repo_path, dep_file)
                if os.path.exists(file_path):
                    deps = self._parse_dependency_file(file_path, dep_file)
                    dependencies.extend(deps)

        return list(set(dependencies))  # Remove duplicates

    def _parse_dependency_file(self, file_path: str, file_name: str) -> List[str]:
        """Parse specific dependency file types"""
        dependencies = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if file_name == "package.json":
                data = json.loads(content)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                dependencies.extend(list(deps.keys()) + list(dev_deps.keys()))

            elif file_name == "requirements.txt":
                for line in content.split("\n"):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        # Extract package name (before version specifiers)
                        pkg_name = (
                            line.split("==")[0]
                            .split(">=")[0]
                            .split("<=")[0]
                            .split(">")[0]
                            .split("<")[0]
                            .split("[")[0]
                        )
                        dependencies.append(pkg_name.strip())

            elif file_name == "pyproject.toml":
                # Simple TOML parsing for dependencies
                lines = content.split("\n")
                in_dependencies = False
                for line in lines:
                    if (
                        "[tool.poetry.dependencies]" in line
                        or "[project.dependencies]" in line
                    ):
                        in_dependencies = True
                    elif line.startswith("[") and in_dependencies:
                        in_dependencies = False
                    elif in_dependencies and "=" in line:
                        dep_name = line.split("=")[0].strip().strip('"').strip("'")
                        if dep_name != "python":
                            dependencies.append(dep_name)

            elif file_name in ["pom.xml", "build.gradle"]:
                # Basic XML/Gradle parsing would go here
                # For now, just note that Java dependencies exist
                dependencies.append("java-dependencies-detected")

        except Exception as e:
            print(f"Error parsing {file_name}: {e}")

        return dependencies

    def _analyze_project_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze overall project structure"""
        structure = {
            "has_tests": False,
            "has_docs": False,
            "has_docker": False,
            "has_ci": False,
            "has_security": False,
            "directory_count": 0,
            "file_count": 0,
            "main_directories": [],
        }

        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            structure["directory_count"] += len(dirs)
            structure["file_count"] += len(files)

            # Check for specific patterns
            for directory in dirs:
                if directory.lower() in [
                    "test",
                    "tests",
                    "testing",
                    "__tests__",
                    "spec",
                ]:
                    structure["has_tests"] = True
                if directory.lower() in ["docs", "documentation", "doc"]:
                    structure["has_docs"] = True

                # Track main directories (at root level)
                if root == repo_path:
                    structure["main_directories"].append(directory)

            for file in files:
                if file.lower() in [
                    "dockerfile",
                    "docker-compose.yml",
                    "docker-compose.yaml",
                ]:
                    structure["has_docker"] = True
                if (
                    "test" in file.lower()
                    or file.endswith("_test.py")
                    or file.endswith(".test.js")
                ):
                    structure["has_tests"] = True

        # Check for CI/CD
        ci_indicators = [
            ".github",
            ".travis.yml",
            ".circleci",
            "Jenkinsfile",
            ".gitlab-ci.yml",
        ]
        for indicator in ci_indicators:
            if os.path.exists(os.path.join(repo_path, indicator)):
                structure["has_ci"] = True
                break

        return structure

    def _file_exists_in_repo(self, repo_path: str, filename: str) -> bool:
        """Check if a file exists anywhere in the repository"""
        for root, dirs, files in os.walk(repo_path):
            if filename in files:
                return True
        return False

    def _content_exists_in_repo(self, repo_path: str, content: str) -> bool:
        """Check if content exists in any file in the repository"""
        for root, dirs, files in os.walk(repo_path):
            # Skip binary and large files
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["node_modules", "__pycache__", "target"]
            ]

            for file in files:
                if file.endswith(
                    (
                        ".py",
                        ".js",
                        ".java",
                        ".go",
                        ".rs",
                        ".json",
                        ".yml",
                        ".yaml",
                        ".toml",
                    )
                ):
                    try:
                        file_path = os.path.join(root, file)
                        with open(
                            file_path, "r", encoding="utf-8", errors="ignore"
                        ) as f:
                            file_content = f.read()
                            if content.lower() in file_content.lower():
                                return True
                    except Exception:
                        continue
        return False

    def _has_tests(self, repo_path: str, language: str) -> bool:
        """Check if the repository has tests"""
        test_patterns = {
            "python": ["test_*.py", "*_test.py", "tests/", "pytest", "unittest"],
            "javascript": [
                "*.test.js",
                "*.spec.js",
                "__tests__/",
                "jest",
                "mocha",
                "cypress",
            ],
            "java": ["*Test.java", "src/test/", "junit"],
            "go": ["*_test.go"],
            "rust": ["#[test]", "tests/"],
        }

        if language in test_patterns:
            patterns = test_patterns[language]
            for pattern in patterns:
                if "/" in pattern:
                    if os.path.exists(os.path.join(repo_path, pattern)):
                        return True
                elif self._content_exists_in_repo(repo_path, pattern):
                    return True
                elif "*" in pattern:
                    # Simple glob-like matching
                    pattern_parts = pattern.split("*")
                    if self._pattern_exists_in_files(repo_path, pattern_parts):
                        return True

        return False

    def _pattern_exists_in_files(
        self, repo_path: str, pattern_parts: List[str]
    ) -> bool:
        """Check if a pattern exists in filenames"""
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if all(part in file for part in pattern_parts if part):
                    return True
        return False

    def _has_security_workflow(self, repo_path: str) -> bool:
        """Check if repository has security scanning configured"""
        security_indicators = [
            "dependabot.yml",
            "codeql",
            "security.yml",
            "snyk",
            "semgrep",
        ]

        for indicator in security_indicators:
            if self._content_exists_in_repo(repo_path, indicator):
                return True

        return False

    async def _ai_analyze_workflow_needs(
        self,
        analysis: WorkflowAnalysis,
        repo_info: Dict,
        custom_input: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Use Groq AI to analyze workflow optimization needs"""
        if not self.groq_client:
            return {"error": "Groq AI not available"}

        try:
            context = {
                "repository": {
                    "name": repo_info.get("name"),
                    "language": analysis.repo_language,
                    "framework": analysis.framework_type,
                    "size": repo_info.get("size"),
                    "visibility": repo_info.get("visibility"),
                },
                "current_state": {
                    "dependencies": analysis.dependencies[
                        :10
                    ],  # Limit for token efficiency
                    "existing_workflows": len(analysis.existing_workflows),
                    "has_tests": analysis.project_structure.get("has_tests"),
                    "has_docker": analysis.project_structure.get("has_docker"),
                    "optimization_score": analysis.optimization_score,
                },
                "existing_workflows": [
                    {"name": w.get("name"), "type": w.get("type")}
                    for w in analysis.existing_workflows
                ],
            }

            prompt = f"""
You are a DevOps expert specializing in CI/CD optimization. Analyze this repository and provide comprehensive workflow recommendations.

Repository Context:
{json.dumps(context, indent=2)}
"""
            if custom_input:
                prompt += f"\n\n# Additional User Input:\n{custom_input}\n"
            prompt += """

Please provide:

1. **Workflow Assessment**: Evaluate current CI/CD setup and identify gaps
2. **Optimization Opportunities**: Specific areas for improvement
3. **Security Recommendations**: Security best practices for CI/CD
4. **Performance Optimization**: Ways to reduce build times and costs
5. **Modern Practices**: Latest CI/CD trends applicable to this project
6. **Tool Recommendations**: Specific tools and actions to implement
7. **Risk Analysis**: Potential risks and mitigation strategies
8. **Implementation Priority**: Order of recommended changes

Consider the project's language ({analysis.repo_language}), framework ({analysis.framework_type}), and current setup.
Focus on actionable, specific recommendations that improve reliability, security, and efficiency.
"""

            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior DevOps engineer with expertise in CI/CD pipeline optimization, security, and modern development practices.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            return {
                "ai_analysis": response.choices[0].message.content,
                "model_used": "meta-llama/llama-4-scout-17b-16e-instruct",
                "analysis_type": "workflow_optimization",
            }

        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

    async def _ai_generate_optimized_workflow(
        self,
        analysis: WorkflowAnalysis,
        ai_analysis: Dict,
        custom_input: Optional[str] = None,
    ) -> Optional[OptimizedWorkflow]:
        """Use Groq AI to generate an optimized workflow"""
        if not self.groq_client or "error" in ai_analysis:
            return self._template_based_optimization(analysis)

        try:
            # Determine if we're improving existing or creating new
            optimization_type = "improved" if analysis.existing_workflows else "new"

            # Prepare context for workflow generation
            workflow_context = {
                "language": analysis.repo_language,
                "framework": analysis.framework_type,
                "dependencies": analysis.dependencies[:15],
                "optimization_type": optimization_type,
                "existing_workflows": [
                    {
                        "name": w.get("name"),
                        "type": w.get("type"),
                        "has_error": "error" in w,
                    }
                    for w in analysis.existing_workflows
                ],
                "project_features": {
                    "has_tests": analysis.project_structure.get("has_tests"),
                    "has_docker": analysis.project_structure.get("has_docker"),
                    "has_docs": analysis.project_structure.get("has_docs"),
                },
            }

            prompt = f"""
Generate an optimized GitHub Actions workflow for this repository based on the analysis.

Context:
{json.dumps(workflow_context, indent=2)}
"""
            if custom_input:
                prompt += f"\n\n# Additional User Input:\n{custom_input}\n"
            prompt += """

Requirements:
1. Create a complete, production-ready GitHub Actions workflow
2. Include appropriate triggers (push, pull_request, etc.)
3. Add comprehensive testing, building, and deployment steps
4. Include security scanning and dependency checks
5. Optimize for performance (caching, parallel jobs, etc.)
6. Follow current best practices and use latest action versions
7. Add proper error handling and notifications
8. Include environment-specific configurations

For {analysis.repo_language} {analysis.framework_type} projects, ensure:
- Proper dependency management and caching
- Framework-specific build and test commands
- Appropriate deployment strategies
- Security best practices

Generate a complete workflow YAML that can be saved as .github/workflows/ci-cd.yml

Return ONLY the YAML content, no additional text or explanations.
"""

            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert DevOps engineer specializing in GitHub Actions and CI/CD optimization. Generate clean, production-ready YAML workflows.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=2500,
            )

            workflow_content = response.choices[0].message.content.strip()

            # Clean up the response (remove any markdown formatting)
            if workflow_content.startswith("```yaml"):
                workflow_content = workflow_content[7:]
            if workflow_content.startswith("```"):
                workflow_content = workflow_content[3:]
            if workflow_content.endswith("```"):
                workflow_content = workflow_content[:-3]

            workflow_content = workflow_content.strip()

            # Generate improvements list
            improvements = [
                "Optimized dependency caching for faster builds",
                "Added comprehensive testing pipeline",
                "Included security vulnerability scanning",
                "Implemented parallel job execution",
                "Added proper error handling and notifications",
                "Configured environment-specific deployments",
            ]

            return OptimizedWorkflow(
                workflow_name="ci-cd.yml",
                workflow_content=workflow_content,
                optimization_type=optimization_type,
                improvements=improvements,
                estimated_time_savings="30-50% reduction in build time",
                confidence_score=90,
            )

        except Exception as e:
            print(f"AI workflow generation failed: {e}")
            return self._template_based_optimization(analysis)

    def _template_based_optimization(
        self, analysis: WorkflowAnalysis
    ) -> OptimizedWorkflow:
        """Fallback template-based workflow optimization"""
        template_key = f"{analysis.repo_language}-{analysis.framework_type}"

        if template_key not in self.workflow_templates:
            template_key = f"{analysis.repo_language}-basic"

        if template_key not in self.workflow_templates:
            template_key = "generic"

        # Use generic template if specific one not found
        if template_key == "generic":
            workflow_content = self._get_generic_workflow(analysis.repo_language)
        else:
            workflow_content = self.workflow_templates.get(
                template_key, self._get_generic_workflow(analysis.repo_language)
            )

        optimization_type = "improved" if analysis.existing_workflows else "new"

        improvements = [
            "Template-based workflow optimization",
            "Basic CI/CD pipeline structure",
            "Standard testing and building steps",
        ]

        if not analysis.project_structure.get("has_tests"):
            improvements.append("Added placeholder for testing setup")

        return OptimizedWorkflow(
            workflow_name="ci-cd.yml",
            workflow_content=workflow_content,
            optimization_type=optimization_type,
            improvements=improvements,
            estimated_time_savings="Basic optimization applied",
            confidence_score=70,
        )

    def _generate_implementation_guide(
        self, analysis: WorkflowAnalysis, optimized_workflow: OptimizedWorkflow
    ) -> Dict[str, Any]:
        """Generate step-by-step implementation guide"""

        steps = []

        if not analysis.existing_workflows:
            steps.extend(
                [
                    "1. Create .github/workflows/ directory in your repository",
                    "2. Save the optimized workflow as .github/workflows/ci-cd.yml",
                    "3. Commit and push the workflow to trigger the first run",
                ]
            )
        else:
            steps.extend(
                [
                    "1. Backup your existing workflow files",
                    "2. Replace or update existing workflows with the optimized version",
                    "3. Test the new workflow in a feature branch first",
                ]
            )

        steps.extend(
            [
                "4. Configure repository secrets for deployment credentials",
                "5. Set up branch protection rules to require CI checks",
                "6. Monitor the first few workflow runs for any issues",
            ]
        )

        if not analysis.project_structure.get("has_tests"):
            steps.append("7. Add comprehensive tests to your project")

        if not analysis.project_structure.get("has_docker"):
            steps.append("8. Consider containerizing your application")

        return {
            "implementation_steps": steps,
            "required_secrets": self._get_required_secrets(analysis),
            "estimated_setup_time": "30-60 minutes",
            "difficulty_level": (
                "Intermediate" if analysis.existing_workflows else "Beginner"
            ),
            "prerequisites": self._get_prerequisites(analysis),
            "testing_checklist": [
                "Verify workflow triggers on push/PR",
                "Check that all jobs complete successfully",
                "Validate test execution and results",
                "Confirm security scans are working",
                "Test deployment process (if applicable)",
            ],
        }

    def _get_required_secrets(self, analysis: WorkflowAnalysis) -> List[str]:
        """Get list of required repository secrets"""
        secrets = []

        if analysis.framework_type in ["django", "fastapi", "express", "spring"]:
            secrets.extend(["DEPLOY_TOKEN", "DATABASE_URL (for testing)"])

        if "docker" in analysis.dependencies or analysis.project_structure.get(
            "has_docker"
        ):
            secrets.extend(["DOCKER_USERNAME", "DOCKER_PASSWORD"])

        if analysis.repo_language == "python":
            secrets.append("PYPI_TOKEN (for package publishing)")
        elif analysis.repo_language == "javascript":
            secrets.append("NPM_TOKEN (for package publishing)")

        return list(set(secrets))

    def _get_prerequisites(self, analysis: WorkflowAnalysis) -> List[str]:
        """Get prerequisites for implementing the workflow"""
        prerequisites = [
            "GitHub repository with appropriate permissions",
            "Understanding of your deployment target",
        ]

        if not analysis.project_structure.get("has_tests"):
            prerequisites.append("Test suite setup (recommended before CI/CD)")

        if analysis.framework_type in ["django", "fastapi", "express"]:
            prerequisites.append("Environment configuration files")

        return prerequisites

    # Workflow template methods (basic implementations)
    def _get_python_basic_workflow(self) -> str:
        return """name: Python CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.11]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8
    
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: pypa/gh-action-pip-audit@v1.0.8
      with:
        inputs: requirements.txt
"""

    def _get_python_django_workflow(self) -> str:
        return """name: Django CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run Django tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        SECRET_KEY: test-secret-key
      run: |
        python manage.py migrate
        coverage run --source='.' manage.py test
        coverage xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Django security check
      run: |
        pip install django-security
        python manage.py check --deploy
"""

    def _get_python_fastapi_workflow(self) -> str:
        return """name: FastAPI CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio httpx
    
    - name: Test with pytest
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  docker:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: |
        docker build -t fastapi-app .
        docker run --rm fastapi-app python -c "import main"
"""

    def _get_javascript_react_workflow(self) -> str:
        return """name: React CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm test -- --coverage --watchAll=false
    
    - name: Build application
      run: npm run build
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security audit
      run: |
        npm audit --audit-level high
        npx audit-ci --high
"""

    def _get_javascript_node_workflow(self) -> str:
        return """name: Node.js CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [16, 18, 20]

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run linter
      run: npm run lint
    
    - name: Run tests
      run: npm test
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: matrix.node-version == 18

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security audit
      run: npm audit --audit-level high
"""

    def _get_java_maven_workflow(self) -> str:
        return """name: Java Maven CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up JDK 11
      uses: actions/setup-java@v3
      with:
        java-version: '11'
        distribution: 'temurin'
    
    - name: Cache Maven dependencies
      uses: actions/cache@v3
      with:
        path: ~/.m2
        key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
        restore-keys: ${{ runner.os }}-m2
    
    - name: Run tests
      run: mvn clean test
    
    - name: Generate test report
      run: mvn jacoco:report
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./target/site/jacoco/jacoco.xml

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      run: |
        mvn org.owasp:dependency-check-maven:check
"""

    def _get_go_basic_workflow(self) -> str:
        return """name: Go CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Go
      uses: actions/setup-go@v4
      with:
        go-version: '1.21'
    
    - name: Cache Go modules
      uses: actions/cache@v3
      with:
        path: ~/go/pkg/mod
        key: ${{ runner.os }}-go-${{ hashFiles('**/go.sum') }}
        restore-keys: |
          ${{ runner.os }}-go-
    
    - name: Install dependencies
      run: go mod download
    
    - name: Run tests
      run: go test -v -race -coverprofile=coverage.out ./...
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.out

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: securecodewarrior/github-action-gosec@master
      with:
        args: './...'
"""

    def _get_rust_basic_workflow(self) -> str:
        return """name: Rust CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Rust
      uses: actions-rs/toolchain@v1
      with:
        toolchain: stable
        components: rustfmt, clippy
    
    - name: Cache cargo registry
      uses: actions/cache@v3
      with:
        path: ~/.cargo/registry
        key: ${{ runner.os }}-cargo-registry-${{ hashFiles('**/Cargo.lock') }}
    
    - name: Cache cargo index
      uses: actions/cache@v3
      with:
        path: ~/.cargo/git
        key: ${{ runner.os }}-cargo-index-${{ hashFiles('**/Cargo.lock') }}
    
    - name: Check formatting
      run: cargo fmt -- --check
    
    - name: Run clippy
      run: cargo clippy -- -D warnings
    
    - name: Run tests
      run: cargo test --verbose

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Security audit
      uses: actions-rs/audit@v1
"""

    def _get_docker_workflow(self) -> str:
        return """name: Docker Build and Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  docker:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to Docker Hub
      if: github.event_name != 'pull_request'
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: my-app
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
"""

    def _get_generic_workflow(self, language: str) -> str:
        return f"""name: {language.title()} CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
    
    - name: Setup environment
      run: |
        echo "Setting up {language} environment"
        # Add language-specific setup commands here
    
    - name: Install dependencies
      run: |
        echo "Installing dependencies"
        # Add dependency installation commands here
    
    - name: Run tests
      run: |
        echo "Running tests"
        # Add test commands here
    
    - name: Build application
      run: |
        echo "Building application"
        # Add build commands here

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      run: |
        echo "Running security scan"
        # Add security scanning commands here
"""


# Global optimizer instance
workflow_optimizer = WorkflowOptimizer()


async def optimize(repo_url: str, custom_input: Optional[str] = None) -> Dict[str, Any]:
    """
    Main function to optimize workflow for a repository

    Args:
        repo_url: GitHub repository URL

    Returns:
        Optimization results
    """
    return await workflow_optimizer.analyze_and_optimize_workflow(
        repo_url, custom_input=custom_input
    )


async def optimize_and_deploy(
    repo_url: str,
    github_token: str,
    branch_name: str = "codeyogi-workflow-optimization",
    workflow_path: str = ".github/workflows/codeyogi-optimized.yml",
    commit_message: str = "🚀 CodeYogi: Optimize CI/CD workflow for better performance",
    auto_merge: bool = False,
    custom_input: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Optimize workflow and automatically create a PR with the changes

    Args:
        repo_url: GitHub repository URL
        github_token: GitHub personal access token
        branch_name: Name for the optimization branch
        workflow_path: Path to the workflow file
        commit_message: Commit message for the changes
        auto_merge: Whether to auto-merge the PR (if permissions allow)

    Returns:
        Optimization results with PR information
    """
    try:
        from utils.pr_creator import GitHubPRCreator
        from datetime import datetime

        # First, perform the workflow optimization analysis
        optimization_result = await workflow_optimizer.analyze_and_optimize_workflow(
            repo_url, custom_input=custom_input
        )

        # Extract the optimized workflow content
        optimized_workflow = optimization_result.get("optimized_workflow")
        if not optimized_workflow or not optimized_workflow.get("workflow_content"):
            return {
                "success": False,
                "optimization_analysis": optimization_result,
                "error_message": "Failed to generate optimized workflow content",
                "timestamp": datetime.now().isoformat(),
            }

        workflow_content = optimized_workflow["workflow_content"]
        improvements = optimized_workflow.get("improvements", [])

        # Create improvement summary for PR description
        improvement_summary = f"""
### 🔧 Workflow Optimization Summary

**Optimization Type**: {optimized_workflow.get('optimization_type', 'enhanced').title()}
**Confidence Score**: {optimized_workflow.get('confidence_score', 'N/A')}/100
**Estimated Time Savings**: {optimized_workflow.get('estimated_time_savings', 'Optimized for better performance')}

### 🚀 Key Improvements:
{chr(10).join([f"- {improvement}" for improvement in improvements])}

### 📊 Repository Analysis:
- **Language**: {optimization_result.get('analysis', {}).get('repo_language', 'Unknown')}
- **Framework**: {optimization_result.get('analysis', {}).get('framework_type', 'Generic')}
- **Optimization Score**: {optimization_result.get('analysis', {}).get('optimization_score', 'N/A')}/100

### 🔍 AI Insights:
{optimization_result.get('ai_insights', {}).get('ai_analysis', 'Template-based optimization applied')}
        """

        # Parse repository name from URL
        if "github.com" in repo_url:
            repo_parts = (
                repo_url.replace("https://github.com/", "")
                .replace(".git", "")
                .split("/")
            )
            repo_name = f"{repo_parts[0]}/{repo_parts[1]}"
        else:
            raise ValueError("Invalid GitHub URL format")

        # Initialize PR Creator
        try:
            pr_creator = GitHubPRCreator(github_token)
        except ValueError as e:
            return {
                "success": False,
                "optimization_analysis": optimization_result,
                "error_message": f"GitHub authentication failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

        # Create PR with optimized workflow
        pr_result = pr_creator.create_optimization_pr(
            repo_name=repo_name,
            optimized_yaml=workflow_content,
            improvement_summary=improvement_summary,
            branch_name=branch_name,
            workflow_path=workflow_path,
            commit_message=commit_message,
        )

        if pr_result and pr_result.get("success"):
            result = {
                "success": True,
                "optimization_analysis": optimization_result,
                "pr_info": pr_result,
                "timestamp": datetime.now().isoformat(),
            }

            # If auto-merge is requested and we have permissions
            if auto_merge and pr_result.get("pr_number"):
                try:
                    # Note: Auto-merge would require additional permissions and checks
                    # For now, we'll just add it to the result as a note
                    result["auto_merge_note"] = (
                        "Auto-merge requested but requires manual approval for safety"
                    )
                except Exception as e:
                    result["auto_merge_error"] = f"Auto-merge failed: {str(e)}"

            return result
        else:
            return {
                "success": False,
                "optimization_analysis": optimization_result,
                "error_message": f"Failed to create PR: {pr_result.get('error', 'Unknown error') if pr_result else 'PR creation failed'}",
                "timestamp": datetime.now().isoformat(),
            }

    except Exception as e:
        from datetime import datetime

        return {
            "success": False,
            "optimization_analysis": {},
            "error_message": f"Workflow optimization and deployment failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
