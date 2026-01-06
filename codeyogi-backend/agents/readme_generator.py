#!/usr/bin/env python3
"""
README Generator Agent

An AI-powered tool that analyzes GitHub repositories and automatically generates
comprehensive, professional README.md files based on the codebase analysis.

Features:
- Analyzes repository structure and code
- Generates contextual README content using AI
- Creates professional documentation with proper sections
- Automatically creates pull requests with the new README
- Supports multiple README styles and customization options
"""

import os
import json
import tempfile
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime
from github import Github, GithubException
from urllib.parse import urlparse
from dotenv import load_dotenv

# Import AI analyzer for intelligent content generation
from .ai_analyzer import ai_analyzer

# Load environment variables
load_dotenv()


class ReadmeGenerator:
    def __init__(self, github_token: Optional[str] = None):
        """Initialize README generator with GitHub token"""
        self.github_token = (
            github_token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        )

        if self.github_token:
            self.github_client = Github(self.github_token)
        else:
            self.github_client = None
            print("[WARNING] GitHub token not found. Some features may be limited.")

    def parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract owner and repository name"""
        if url.endswith(".git"):
            url = url[:-4]

        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) >= 2:
            return {"owner": path_parts[0], "repo_name": path_parts[1]}
        else:
            raise ValueError(
                "Invalid GitHub URL format. Expected: https://github.com/owner/repo"
            )

    def clone_repository(self, repo_url: str, temp_dir: str) -> str:
        """Clone repository to temporary directory"""
        try:
            print(f"[INFO] Cloning repository: {repo_url}")
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, temp_dir],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"[SUCCESS] Repository cloned to: {temp_dir}")
            return temp_dir
        except subprocess.CalledProcessError as e:
            raise Exception(f"Git clone failed: {e.stderr}")

    def analyze_repository_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze repository structure and code to understand the project"""
        repo_pathlib = Path(repo_path)

        analysis = {
            "files": [],
            "directories": [],
            "languages": {},
            "frameworks": [],
            "dependencies": {},
            "has_tests": False,
            "has_docs": False,
            "has_ci": False,
            "project_type": "unknown",
            "main_files": [],
            "config_files": [],
            "total_files": 0,
            "total_size": 0,
        }

        # Language and framework detection patterns
        language_patterns = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".go": "Go",
            ".rs": "Rust",
            ".swift": "Swift",
            ".kt": "Kotlin",
            ".dart": "Dart",
            ".html": "HTML",
            ".css": "CSS",
            ".scss": "SCSS",
            ".vue": "Vue.js",
            ".jsx": "React",
        }

        framework_indicators = {
            "package.json": ["Node.js", "npm"],
            "requirements.txt": ["Python"],
            "Pipfile": ["Python", "pipenv"],
            "poetry.lock": ["Python", "Poetry"],
            "Cargo.toml": ["Rust"],
            "composer.json": ["PHP", "Composer"],
            "pom.xml": ["Java", "Maven"],
            "build.gradle": ["Java", "Gradle"],
            "Dockerfile": ["Docker"],
            "docker-compose.yml": ["Docker Compose"],
            ".github/workflows": ["GitHub Actions"],
            ".travis.yml": ["Travis CI"],
            ".circleci": ["CircleCI"],
            "next.config.js": ["Next.js"],
            "nuxt.config.js": ["Nuxt.js"],
            "angular.json": ["Angular"],
            "vue.config.js": ["Vue.js"],
            "webpack.config.js": ["Webpack"],
            "vite.config.js": ["Vite"],
        }

        # Scan repository
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["node_modules", "__pycache__", "dist", "build"]
            ]

            rel_root = os.path.relpath(root, repo_path)
            if rel_root != ".":
                analysis["directories"].append(rel_root)

            for file in files:
                if file.startswith("."):
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)

                # Get file info
                try:
                    file_size = os.path.getsize(file_path)
                    analysis["total_size"] += file_size
                    analysis["total_files"] += 1

                    file_ext = Path(file).suffix.lower()

                    # Language detection
                    if file_ext in language_patterns:
                        lang = language_patterns[file_ext]
                        analysis["languages"][lang] = (
                            analysis["languages"].get(lang, 0) + 1
                        )

                    # Framework detection
                    for indicator, frameworks in framework_indicators.items():
                        if indicator in rel_path or file == indicator:
                            analysis["frameworks"].extend(frameworks)

                    # Special file detection
                    if file.lower() in ["readme.md", "readme.txt", "readme.rst"]:
                        analysis["main_files"].append(rel_path)
                    elif file.lower() in ["license", "license.txt", "license.md"]:
                        analysis["main_files"].append(rel_path)
                    elif "test" in file.lower() or "test" in rel_path.lower():
                        analysis["has_tests"] = True
                    elif "doc" in rel_path.lower() or file.endswith(
                        (".md", ".rst", ".txt")
                    ):
                        analysis["has_docs"] = True
                    elif file in [
                        "package.json",
                        "requirements.txt",
                        "Pipfile",
                        "Cargo.toml",
                    ]:
                        analysis["config_files"].append(rel_path)

                        # Parse dependencies
                        try:
                            if file == "package.json":
                                with open(file_path, "r", encoding="utf-8") as f:
                                    package_data = json.load(f)
                                    deps = package_data.get("dependencies", {})
                                    dev_deps = package_data.get("devDependencies", {})
                                    analysis["dependencies"]["npm"] = {
                                        **deps,
                                        **dev_deps,
                                    }
                        except:
                            pass

                    analysis["files"].append(
                        {"path": rel_path, "size": file_size, "extension": file_ext}
                    )

                except OSError:
                    continue

        # Determine project type
        if "Python" in analysis["languages"]:
            if "Django" in analysis["frameworks"] or any(
                "django" in f for f in analysis["frameworks"]
            ):
                analysis["project_type"] = "Django Web Application"
            elif "Flask" in analysis["frameworks"] or any(
                "flask" in f for f in analysis["frameworks"]
            ):
                analysis["project_type"] = "Flask Web Application"
            elif "FastAPI" in analysis["frameworks"] or any(
                "fastapi" in f for f in analysis["frameworks"]
            ):
                analysis["project_type"] = "FastAPI Application"
            else:
                analysis["project_type"] = "Python Application"
        elif (
            "JavaScript" in analysis["languages"]
            or "TypeScript" in analysis["languages"]
        ):
            if "React" in analysis["frameworks"] or "Next.js" in analysis["frameworks"]:
                analysis["project_type"] = "React Application"
            elif (
                "Vue.js" in analysis["frameworks"]
                or "Nuxt.js" in analysis["frameworks"]
            ):
                analysis["project_type"] = "Vue.js Application"
            elif "Angular" in analysis["frameworks"]:
                analysis["project_type"] = "Angular Application"
            elif "Node.js" in analysis["frameworks"]:
                analysis["project_type"] = "Node.js Application"
            else:
                analysis["project_type"] = "JavaScript Application"

        # Remove duplicates
        analysis["frameworks"] = list(set(analysis["frameworks"]))

        return analysis

    async def generate_readme_content(
        self,
        repo_info: Dict[str, str],
        analysis: Dict[str, Any],
        style: str = "comprehensive",
    ) -> Dict[str, Any]:
        """Generate README content using AI analysis"""

        # Prepare context for AI
        context = {
            "repository": repo_info,
            "analysis": analysis,
            "style_preference": style,
        }

        # Create prompt for AI README generation
        prompt = f"""
You are an expert technical writer specializing in creating professional README.md files for software projects.

Analyze this repository and create a comprehensive, professional README.md content:

Repository Context:
{json.dumps(context, indent=2)}

Create a README with the following sections (adapt based on project type):

1. **Project Title & Description**: Clear, engaging project description
2. **Badges**: Relevant GitHub badges (stars, license, version, build status)
3. **Features**: Key features and capabilities
4. **Installation**: Step-by-step installation instructions
5. **Usage**: Code examples and usage instructions
6. **API Documentation**: If applicable, brief API overview
7. **Configuration**: Environment setup and configuration
8. **Contributing**: Guidelines for contributors
9. **Testing**: How to run tests
10. **Deployment**: Deployment instructions if applicable
11. **License**: License information
12. **Contact & Support**: Contact information and support resources

Style: {style} (professional, comprehensive, engaging)

Requirements:
- Use proper Markdown formatting
- Include relevant code examples in the project's main language
- Add appropriate emojis for visual appeal
- Make it beginner-friendly but technically accurate
- Include realistic, project-specific examples
- Ensure all sections are relevant to the project type

Return the response as a JSON object with the following structure:
{{
  "title": "Project Title",
  "description": "Brief description",
  "badges": ["badge_markdown_1", "badge_markdown_2"],
  "installation": "## Installation\\n\\nInstallation content...",
  "usage": "## Usage\\n\\nUsage content...",
  "features": "## Features\\n\\nFeatures content...",
  "api_docs": "## API Documentation\\n\\nAPI content...",
  "contributing": "## Contributing\\n\\nContributing content...",
  "license": "## License\\n\\nLicense content...",
  "contact": "## Contact\\n\\nContact content..."
}}

Make it specific to this project, not generic!
"""

        try:
            if ai_analyzer.is_available():
                # Use AI to generate content
                ai_result = await ai_analyzer.client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert technical writer who creates professional, engaging README files that help developers understand and use projects effectively.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.4,
                    max_tokens=3000,
                )

                content_text = ai_result.choices[0].message.content

                # Try to parse JSON response
                try:
                    content_json = json.loads(content_text)
                    return {
                        "success": True,
                        "content": content_json,
                        "method": "ai_generated",
                    }
                except json.JSONDecodeError:
                    # Fallback to template-based generation
                    return self.generate_template_readme(repo_info, analysis, style)

            else:
                # Fallback to template-based generation
                return self.generate_template_readme(repo_info, analysis, style)

        except Exception as e:
            print(f"[WARNING] AI generation failed: {e}")
            return self.generate_template_readme(repo_info, analysis, style)

    def generate_template_readme(
        self, repo_info: Dict[str, str], analysis: Dict[str, Any], style: str
    ) -> Dict[str, Any]:
        """Generate README content using templates (fallback method)"""

        owner = repo_info["owner"]
        repo_name = repo_info["repo_name"]
        project_type = analysis.get("project_type", "Software Project")
        main_language = (
            max(analysis["languages"].items(), key=lambda x: x[1])[0]
            if analysis["languages"]
            else "Unknown"
        )

        # Generate badges
        badges = [
            f"![GitHub stars](https://img.shields.io/github/stars/{owner}/{repo_name})",
            f"![GitHub forks](https://img.shields.io/github/forks/{owner}/{repo_name})",
            f"![GitHub issues](https://img.shields.io/github/issues/{owner}/{repo_name})",
            f"![GitHub license](https://img.shields.io/github/license/{owner}/{repo_name})",
        ]

        if "CI" in str(analysis.get("frameworks", [])):
            badges.append(
                f"![Build Status](https://img.shields.io/github/workflow/status/{owner}/{repo_name}/CI)"
            )

        # Generate installation instructions based on project type
        installation = self.generate_installation_section(analysis, main_language)
        usage = self.generate_usage_section(analysis, main_language)
        features = self.generate_features_section(analysis)

        content = {
            "title": repo_name.replace("-", " ").replace("_", " ").title(),
            "description": f"A {project_type.lower()} built with {main_language}",
            "badges": badges,
            "installation": installation,
            "usage": usage,
            "features": features,
            "api_docs": (
                self.generate_api_docs_section(analysis)
                if "API" in project_type
                else None
            ),
            "contributing": self.generate_contributing_section(owner, repo_name),
            "license": "## License\n\nThis project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.",
            "contact": f"## Contact\n\n- Repository: [https://github.com/{owner}/{repo_name}](https://github.com/{owner}/{repo_name})\n- Issues: [Report bugs or request features](https://github.com/{owner}/{repo_name}/issues)",
        }

        return {"success": True, "content": content, "method": "template_generated"}

    def generate_installation_section(
        self, analysis: Dict[str, Any], language: str
    ) -> str:
        """Generate installation instructions based on project analysis"""

        if "Python" in language:
            if "requirements.txt" in str(analysis.get("config_files", [])):
                return """## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/username/repository.git
cd repository

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```"""
            else:
                return """## Installation

### Prerequisites
- Python 3.7 or higher

### Setup
```bash
# Clone the repository
git clone https://github.com/username/repository.git
cd repository

# Install dependencies (if any)
pip install -e .
```"""

        elif "JavaScript" in language or "TypeScript" in language:
            return """## Installation

### Prerequisites
- Node.js 14 or higher
- npm or yarn package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/username/repository.git
cd repository

# Install dependencies
npm install
# or
yarn install
```"""

        else:
            return """## Installation

```bash
# Clone the repository
git clone https://github.com/username/repository.git
cd repository

# Follow the setup instructions specific to your development environment
```"""

    def generate_usage_section(self, analysis: Dict[str, Any], language: str) -> str:
        """Generate usage examples based on project analysis"""

        if "Python" in language:
            return """## Usage

### Basic Usage
```python
# Import the main module
from your_project import main_function

# Use the functionality
result = main_function()
print(result)
```

### Advanced Usage
```python
# More detailed examples here
```"""

        elif "JavaScript" in language:
            return """## Usage

### Basic Usage
```javascript
// Import the module
const { mainFunction } = require('./your-project');

// Use the functionality
const result = mainFunction();
console.log(result);
```

### Running the Application
```bash
# Start the application
npm start

# Run in development mode
npm run dev
```"""

        else:
            return """## Usage

### Basic Usage
```
// Basic usage examples will be added here
```

### Getting Started
1. Follow the installation instructions
2. Run the main application
3. Check the documentation for advanced features
"""

    def generate_features_section(self, analysis: Dict[str, Any]) -> str:
        """Generate features section based on project analysis"""

        features = ["## Features\n"]

        # Add features based on detected frameworks and structure
        if analysis.get("has_tests"):
            features.append("- ✅ Comprehensive test suite")

        if analysis.get("has_docs"):
            features.append("- 📚 Well-documented codebase")

        if "Docker" in analysis.get("frameworks", []):
            features.append("- 🐳 Docker support for easy deployment")

        if "CI" in str(analysis.get("frameworks", [])):
            features.append("- 🔄 Continuous Integration/Deployment")

        # Add language-specific features
        languages = analysis.get("languages", {})
        if "Python" in languages:
            features.append("- 🐍 Built with Python for reliability and performance")
        if "TypeScript" in languages:
            features.append("- 🔷 TypeScript support for type safety")
        if "JavaScript" in languages:
            features.append("- ⚡ Modern JavaScript features")

        # Add framework-specific features
        frameworks = analysis.get("frameworks", [])
        if "React" in frameworks:
            features.append("- ⚛️ React-based user interface")
        if "FastAPI" in frameworks:
            features.append("- 🚀 High-performance API with FastAPI")
        if "Next.js" in frameworks:
            features.append("- 🔥 Server-side rendering with Next.js")

        return "\n".join(features)

    def generate_api_docs_section(self, analysis: Dict[str, Any]) -> str:
        """Generate API documentation section"""

        return """## API Documentation

### Endpoints

#### GET /api/health
Returns the health status of the application.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T14:30:45Z"
}
```

#### Additional Endpoints
For complete API documentation, visit `/docs` when the application is running.
"""

    def generate_contributing_section(self, owner: str, repo_name: str) -> str:
        """Generate contributing guidelines"""

        return f"""## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

### Issues

Found a bug or have a feature request? Please [open an issue](https://github.com/{owner}/{repo_name}/issues).
"""

    def create_readme_markdown(self, content: Dict[str, Any]) -> str:
        """Combine all sections into final README markdown"""

        readme_parts = []

        # Title and description
        readme_parts.append(f"# {content['title']}\n")
        readme_parts.append(f"{content['description']}\n")

        # Badges
        if content.get("badges"):
            readme_parts.append(" ".join(content["badges"]) + "\n")

        # Features
        if content.get("features"):
            readme_parts.append(content["features"] + "\n")

        # Installation
        if content.get("installation"):
            readme_parts.append(content["installation"] + "\n")

        # Usage
        if content.get("usage"):
            readme_parts.append(content["usage"] + "\n")

        # API Documentation
        if content.get("api_docs"):
            readme_parts.append(content["api_docs"] + "\n")

        # Contributing
        if content.get("contributing"):
            readme_parts.append(content["contributing"] + "\n")

        # License
        if content.get("license"):
            readme_parts.append(content["license"] + "\n")

        # Contact
        if content.get("contact"):
            readme_parts.append(content["contact"] + "\n")

        # Footer
        readme_parts.append("---\n")
        readme_parts.append(
            "*This README was generated automatically by CodeYogi README Generator*"
        )

        return "\n".join(readme_parts)

    def commit_and_push_changes(
        self, repo_path: str, branch_name: str, commit_message: str
    ) -> bool:
        """Commit and push README changes"""

        try:
            original_cwd = os.getcwd()
            os.chdir(repo_path)

            # Create and checkout new branch
            subprocess.run(
                ["git", "checkout", "-b", branch_name], check=True, capture_output=True
            )

            # Add README file
            subprocess.run(["git", "add", "README.md"], check=True, capture_output=True)

            # Commit changes
            subprocess.run(
                ["git", "commit", "-m", commit_message], check=True, capture_output=True
            )

            # Push to origin
            subprocess.run(
                ["git", "push", "origin", branch_name], check=True, capture_output=True
            )

            print(f"[SUCCESS] Changes committed and pushed to branch: {branch_name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git operation failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)

    def create_pull_request(
        self,
        repo_info: Dict[str, str],
        branch_name: str,
        readme_summary: Dict[str, Any],
    ) -> Optional[str]:
        """Create pull request with the new README"""

        if not self.github_client:
            print("[ERROR] GitHub client not available for PR creation")
            return None

        try:
            repo = self.github_client.get_repo(
                f"{repo_info['owner']}/{repo_info['repo_name']}"
            )

            pr_title = "📚 Auto-generated README.md Enhancement"
            pr_body = f"""## 📖 README Enhancement Summary

This pull request adds a comprehensive, professionally generated README.md file based on automated analysis of your repository.

### ✨ What's Included

- **Professional Structure**: Well-organized sections with clear navigation
- **Installation Instructions**: Step-by-step setup guide
- **Usage Examples**: Practical code examples and usage patterns
- **Project Features**: Highlighted key features and capabilities
- **Contributing Guidelines**: Clear contribution workflow
- **Badges & Metadata**: GitHub badges for professional appearance

### 🔍 Analysis Results

- **Project Type**: {readme_summary.get('project_type', 'N/A')}
- **Primary Language**: {readme_summary.get('main_language', 'N/A')}
- **Frameworks Detected**: {', '.join(readme_summary.get('frameworks', [])) or 'None detected'}
- **Total Files Analyzed**: {readme_summary.get('total_files', 'N/A')}

### 🎯 Benefits

- Improved project discoverability
- Better first impressions for new users
- Clear guidance for contributors
- Professional project presentation
- Enhanced developer experience

### 🛠️ Customization

Feel free to modify any sections to better reflect your project's specific needs. This README serves as a solid foundation that you can customize further.

---

*Generated by CodeYogi README Generator - Automated documentation for better projects*
"""

            pr = repo.create_pull(
                title=pr_title, body=pr_body, head=branch_name, base=repo.default_branch
            )

            print(f"[SUCCESS] Pull request created: {pr.html_url}")
            return pr.html_url

        except Exception as e:
            print(f"[ERROR] Failed to create pull request: {e}")
            return None

    async def generate_readme_for_repository(
        self,
        github_url: str,
        github_token: Optional[str] = None,
        branch_name: Optional[str] = None,
        create_pr: bool = True,
        style: str = "comprehensive",
    ) -> Dict[str, Any]:
        """Main function to generate README for a GitHub repository"""

        temp_dir = None

        try:
            # Parse repository URL
            print(f"[INFO] Starting README generation for: {github_url}")
            repo_info = self.parse_github_url(github_url)
            print(f"[INFO] Repository: {repo_info['owner']}/{repo_info['repo_name']}")

            # Create temporary directory
            temp_dir = tempfile.mkdtemp(prefix="readme_generator_")
            print(f"[INFO] Created temporary directory: {temp_dir}")

            # Clone repository
            repo_path = self.clone_repository(github_url, temp_dir)

            # Analyze repository
            print("[INFO] Analyzing repository structure...")
            analysis = self.analyze_repository_structure(repo_path)

            # Generate README content
            print("[INFO] Generating README content...")
            content_result = await self.generate_readme_content(
                repo_info, analysis, style
            )

            if not content_result.get("success"):
                return {"success": False, "error": "Failed to generate README content"}

            readme_content = content_result["content"]
            readme_markdown = self.create_readme_markdown(readme_content)

            # Write README file
            readme_path = os.path.join(repo_path, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_markdown)

            print("[SUCCESS] README.md generated successfully")

            # Create branch name if not provided
            if not branch_name:
                branch_name = (
                    f"readme-enhancement-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                )

            # Commit and push changes
            commit_message = f"docs: Add comprehensive README.md\n\n- Generated professional README with project analysis\n- Added installation and usage instructions\n- Included contributing guidelines and project structure\n- Enhanced with badges and proper documentation sections"

            if self.commit_and_push_changes(repo_path, branch_name, commit_message):
                pr_url = None
                pr_number = None

                # Create pull request if requested
                if create_pr:
                    analysis_summary = {
                        "project_type": analysis.get("project_type"),
                        "main_language": (
                            max(analysis["languages"].items(), key=lambda x: x[1])[0]
                            if analysis["languages"]
                            else "Unknown"
                        ),
                        "frameworks": analysis.get("frameworks", []),
                        "total_files": analysis.get("total_files", 0),
                    }

                    pr_url = self.create_pull_request(
                        repo_info, branch_name, analysis_summary
                    )

                    # Extract PR number from URL
                    if pr_url:
                        try:
                            pr_number = int(pr_url.split("/")[-1])
                        except:
                            pr_number = None

                return {
                    "success": True,
                    "repository": f"{repo_info['owner']}/{repo_info['repo_name']}",
                    "readme_content": readme_content,
                    "readme_markdown": readme_markdown,
                    "branch_name": branch_name,
                    "pull_request_url": pr_url,
                    "pull_request_number": pr_number,
                    "analysis_summary": analysis,
                    "generation_method": content_result.get("method"),
                }
            else:
                return {"success": False, "error": "Failed to commit and push changes"}

        except Exception as e:
            print(f"[ERROR] README generation failed: {e}")
            return {"success": False, "error": str(e)}

        finally:
            # Cleanup temporary directory
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    print(f"[INFO] Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    print(f"[WARNING] Failed to cleanup temp directory: {e}")

    async def analyze_existing_readme(
        self, github_url: str, github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze existing README and suggest improvements"""

        try:
            repo_info = self.parse_github_url(github_url)

            # Use GitHub API to get current README
            if github_token:
                g = Github(github_token)
            else:
                g = Github()

            repo = g.get_repo(f"{repo_info['owner']}/{repo_info['repo_name']}")

            current_readme = None
            readme_analysis = {}

            try:
                readme_file = repo.get_readme()
                readme_content = readme_file.decoded_content.decode("utf-8")

                # Analyze current README
                readme_analysis = {
                    "length": len(readme_content),
                    "sections": self.analyze_readme_sections(readme_content),
                    "has_badges": "![" in readme_content
                    or "https://img.shields.io" in readme_content,
                    "has_installation": any(
                        word in readme_content.lower()
                        for word in ["install", "setup", "getting started"]
                    ),
                    "has_usage": any(
                        word in readme_content.lower()
                        for word in ["usage", "example", "how to"]
                    ),
                    "has_contributing": "contribut" in readme_content.lower(),
                    "has_license": "license" in readme_content.lower(),
                    "code_blocks": readme_content.count("```"),
                    "links": readme_content.count("]("),
                }

                current_readme = {
                    "content": readme_content,
                    "analysis": readme_analysis,
                }

            except:
                readme_analysis = {"exists": False}

            # Generate improvement suggestions
            improvements = []
            if not readme_analysis.get("has_badges"):
                improvements.append(
                    "Add GitHub badges for stars, forks, and build status"
                )
            if not readme_analysis.get("has_installation"):
                improvements.append("Add clear installation instructions")
            if not readme_analysis.get("has_usage"):
                improvements.append("Include usage examples and code snippets")
            if not readme_analysis.get("has_contributing"):
                improvements.append("Add contributing guidelines")
            if readme_analysis.get("code_blocks", 0) < 2:
                improvements.append("Add more code examples and snippets")
            if readme_analysis.get("length", 0) < 500:
                improvements.append("Expand documentation with more detailed sections")

            # Calculate completeness score
            score_factors = [
                readme_analysis.get("has_badges", False),
                readme_analysis.get("has_installation", False),
                readme_analysis.get("has_usage", False),
                readme_analysis.get("has_contributing", False),
                readme_analysis.get("has_license", False),
                readme_analysis.get("code_blocks", 0) >= 2,
                readme_analysis.get("length", 0) >= 500,
            ]
            completeness_score = int((sum(score_factors) / len(score_factors)) * 100)

            return {
                "success": True,
                "repository": f"{repo_info['owner']}/{repo_info['repo_name']}",
                "current_readme": current_readme,
                "improvement_suggestions": improvements,
                "completeness_score": completeness_score,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_readme_sections(self, content: str) -> List[str]:
        """Analyze which sections are present in the README"""

        sections = []
        lines = content.lower().split("\n")

        section_patterns = {
            "title": lambda line: line.startswith("# "),
            "description": lambda line: any(
                word in line for word in ["description", "about"]
            ),
            "installation": lambda line: any(
                word in line for word in ["install", "setup", "getting started"]
            ),
            "usage": lambda line: any(
                word in line for word in ["usage", "example", "how to", "quickstart"]
            ),
            "features": lambda line: "feature" in line,
            "api": lambda line: "api" in line,
            "contributing": lambda line: "contribut" in line,
            "license": lambda line: "license" in line,
            "contact": lambda line: any(
                word in line for word in ["contact", "support", "author"]
            ),
        }

        for line in lines:
            if line.startswith("#"):
                for section_name, pattern in section_patterns.items():
                    if pattern(line) and section_name not in sections:
                        sections.append(section_name)

        return sections

    async def get_current_readme_content(
        self, github_url: str, github_token: Optional[str] = None
    ) -> Optional[str]:
        """Get current README content from GitHub repository"""
        try:
            repo_info = self.parse_github_url(github_url)

            # Use GitHub API to get current README
            if github_token:
                g = Github(github_token)
            else:
                g = Github()

            repo = g.get_repo(f"{repo_info['owner']}/{repo_info['repo_name']}")

            try:
                readme_file = repo.get_readme()
                return readme_file.decoded_content.decode("utf-8")
            except GithubException:
                # No README found
                return None

        except Exception as e:
            print(f"[ERROR] Failed to get README content: {e}")
            return None


# Global README generator instance
readme_generator = ReadmeGenerator()


# Module-level wrapper functions for easier import
async def generate_readme_for_repository(
    github_url: str,
    github_token: Optional[str] = None,
    branch_name: Optional[str] = None,
    create_pr: bool = True,
    style: str = "comprehensive",
) -> Dict[str, Any]:
    """Generate README for a GitHub repository"""
    return await readme_generator.generate_readme_for_repository(
        github_url=github_url,
        github_token=github_token,
        branch_name=branch_name,
        create_pr=create_pr,
        style=style,
    )


async def analyze_existing_readme(
    github_url: str, github_token: Optional[str] = None
) -> Dict[str, Any]:
    """Analyze existing README and suggest improvements"""
    return await readme_generator.analyze_existing_readme(
        github_url=github_url, github_token=github_token
    )


async def get_current_readme_content(
    github_url: str, github_token: Optional[str] = None
) -> Optional[str]:
    """Get current README content from GitHub repository"""
    return await readme_generator.get_current_readme_content(
        github_url=github_url, github_token=github_token
    )


def analyze_repository_structure(repo_path: str) -> Dict[str, Any]:
    """Analyze repository structure and code to understand the project"""
    return readme_generator.analyze_repository_structure(repo_path)
