import difflib
from typing import List, Dict, Any, Optional
import re
import os
import tempfile
import shutil
import requests
import zipfile
import io
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Handle imports that might fail due to missing dependencies
try:
    from github import Github

    GITHUB_AVAILABLE = True
except ImportError:
    print("GitHub library not available. Please install: pip install PyGithub")
    GITHUB_AVAILABLE = False

try:
    from utils.pr_creator import GitHubPRCreator

    PR_CREATOR_AVAILABLE = True
except ImportError:
    print("PR Creator not available due to missing dependencies")
    PR_CREATOR_AVAILABLE = False

load_dotenv()

# Import Groq for AI-powered optimization
try:
    from groq import Groq

    GROQ_AVAILABLE = True
except ImportError:
    print("Groq not available. Please install: pip install groq")
    GROQ_AVAILABLE = False


class GitHubMultiLanguageOptimizer:
    """Multi-language code optimizer using Groq AI for intelligent optimization"""

    def __init__(self):
        self.optimizations = []
        self.groq_client = None
        self.setup_groq()


class GitHubMultiLanguageOptimizer:
    """Multi-language code optimizer using Groq AI for intelligent optimization with GitHub integration"""

    def __init__(self, github_token: Optional[str] = None):
        self.optimizations = []
        self.groq_client = None

        # Load GitHub token from parameter, environment variables, or .env file
        if github_token:
            self.github_token = github_token
        else:
            # Ensure .env file is loaded
            load_dotenv(override=False)  # Don't override existing env vars
            self.github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

        self.pr_creator = None
        self.setup_groq()
        self.setup_github()

    def setup_groq(self):
        """Setup Groq client"""
        if not GROQ_AVAILABLE:
            print("Groq not available. Install with: pip install groq")
            return

        # Ensure .env file is loaded and try to get Groq API key from environment
        load_dotenv(override=False)  # Don't override existing env vars
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("⚠️ GROQ_API_KEY not found in environment variables or .env file")
            print(
                "Please set your Groq API key in .env file: GROQ_API_KEY='your_key_here'"
            )
            print(
                "Or export it as environment variable: export GROQ_API_KEY='your_key_here'"
            )
            return

        try:
            self.groq_client = Groq(api_key=api_key)
            print("🎉 Groq client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Groq client: {e}")

    def setup_github(self):
        """Setup GitHub client and PR creator"""
        if not GITHUB_AVAILABLE:
            print("⚠️ GitHub library not available. Install with: pip install PyGithub")
            return

        if self.github_token:
            try:
                self.github_client = Github(self.github_token)

                if PR_CREATOR_AVAILABLE:
                    self.pr_creator = GitHubPRCreator(self.github_token)
                    print("🎉 GitHub client and PR creator initialized successfully")
                else:
                    print("🎉 GitHub client initialized (PR creator unavailable)")
            except Exception as e:
                print(f"❌ Failed to initialize GitHub client: {e}")
        else:
            print("⚠️ No GitHub token found in environment variables or .env file.")
            print(
                "Please set GITHUB_TOKEN in your .env file or as an environment variable."
            )
            print("PR creation will be disabled.")

    def parse_github_url(self, github_url: str) -> tuple:
        """Parse GitHub URL to extract owner and repo name"""
        try:
            parsed = urlparse(github_url)
            if parsed.netloc != "github.com":
                raise ValueError("URL must be a GitHub URL")

            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repository URL")

            return path_parts[0], path_parts[1]
        except Exception as e:
            raise ValueError(f"Invalid GitHub URL: {str(e)}")

    def download_repository(self, github_url: str) -> str:
        """Download GitHub repository to temporary directory"""
        owner, repo_name = self.parse_github_url(github_url)
        temp_dir = tempfile.mkdtemp()

        try:
            # Try downloading as ZIP (works for public repos)
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
                    shutil.rmtree(temp_dir)
                    return final_temp_dir

                return temp_dir
            else:
                raise Exception(
                    f"Failed to download repository: HTTP {response.status_code}"
                )

        except Exception as e:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise Exception(f"Failed to download repository: {str(e)}")

    def identify_important_files(self, repo_path: str) -> List[Dict[str, Any]]:
        """Identify important files for optimization based on patterns and file types"""
        important_files = []

        # Define patterns for important files
        important_patterns = {
            "main_files": [
                "main.py",
                "app.py",
                "index.js",
                "server.js",
                "index.ts",
                "App.java",
                "main.cpp",
            ],
            "config_files": [
                "package.json",
                "requirements.txt",
                "pom.xml",
                "CMakeLists.txt",
                "Cargo.toml",
            ],
            "api_files": ["*api*.py", "*route*.py", "*controller*.py", "*service*.py"],
            "core_logic": ["*utils*.py", "*helper*.py", "*lib*.py", "*core*.py"],
        }

        # Files to exclude
        exclude_patterns = [
            ".git",
            "__pycache__",
            "node_modules",
            ".vscode",
            ".idea",
            "dist",
            "build",
        ]

        for root, dirs, files in os.walk(repo_path):
            # Filter out excluded directories
            dirs[:] = [
                d for d in dirs if not any(pattern in d for pattern in exclude_patterns)
            ]

            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)

                # Skip excluded patterns
                if any(pattern in relative_path for pattern in exclude_patterns):
                    continue

                # Check if file is important
                importance_score = 0
                importance_reasons = []

                # Check for main files
                if file in important_patterns["main_files"]:
                    importance_score += 10
                    importance_reasons.append("Main application file")

                # Check for config files
                if file in important_patterns["config_files"]:
                    importance_score += 8
                    importance_reasons.append("Configuration file")

                # Check for API/service files
                for pattern in important_patterns["api_files"]:
                    if pattern.replace("*", "") in file.lower():
                        importance_score += 7
                        importance_reasons.append("API/Service file")
                        break

                # Check for core logic files
                for pattern in important_patterns["core_logic"]:
                    if pattern.replace("*", "") in file.lower():
                        importance_score += 6
                        importance_reasons.append("Core logic file")
                        break

                # Check file extension for source code
                language = self.detect_language(file_path)
                if language != "unknown" and importance_score == 0:
                    importance_score += 3
                    importance_reasons.append(f"Source code ({language})")

                # Check file size (prioritize larger files)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > 5000:  # Files larger than 5KB
                        importance_score += 2
                        importance_reasons.append("Large file")
                except:
                    pass

                # Only include files with some importance
                if importance_score > 0:
                    important_files.append(
                        {
                            "path": relative_path,
                            "full_path": file_path,
                            "language": language,
                            "importance_score": importance_score,
                            "reasons": importance_reasons,
                            "size": (
                                os.path.getsize(file_path)
                                if os.path.exists(file_path)
                                else 0
                            ),
                        }
                    )

        # Sort by importance score (descending)
        important_files.sort(key=lambda x: x["importance_score"], reverse=True)

        # Return top 20 most important files
        return important_files[:20]

    def analyze_github_repository(self, github_url: str) -> Dict[str, Any]:
        """Analyze GitHub repository and suggest optimizations for important files"""
        try:
            print(f"🔍 Analyzing repository: {github_url}")

            # Download repository
            repo_path = self.download_repository(github_url)

            try:
                # Identify important files
                important_files = self.identify_important_files(repo_path)

                print(f"📁 Found {len(important_files)} important files to analyze")

                # Analyze each important file
                file_optimizations = []
                total_optimizations = 0

                for file_info in important_files:
                    if file_info["language"] == "unknown":
                        continue

                    try:
                        # Read file content
                        with open(
                            file_info["full_path"],
                            "r",
                            encoding="utf-8",
                            errors="ignore",
                        ) as f:
                            content = f.read()

                        # Skip very large files (>50KB)
                        if len(content) > 50000:
                            continue

                        # Optimize the file
                        optimization_result = self.optimize_code(
                            content, file_info["language"], file_info["path"]
                        )

                        if (
                            optimization_result["status"] == "success"
                            and optimization_result["optimizations"]
                        ):
                            file_optimizations.append(
                                {
                                    "file": file_info["path"],
                                    "language": file_info["language"],
                                    "importance_score": file_info["importance_score"],
                                    "importance_reasons": file_info["reasons"],
                                    "original_content": content,
                                    "optimized_content": optimization_result[
                                        "optimized_code"
                                    ],
                                    "diff": optimization_result["diff"],
                                    "optimizations": optimization_result[
                                        "optimizations"
                                    ],
                                }
                            )
                            total_optimizations += len(
                                optimization_result["optimizations"]
                            )

                    except Exception as e:
                        print(f"❌ Error analyzing {file_info['path']}: {e}")
                        continue

                return {
                    "status": "success",
                    "repository_url": github_url,
                    "total_files_analyzed": len(important_files),
                    "files_with_optimizations": len(file_optimizations),
                    "total_optimizations": total_optimizations,
                    "file_optimizations": file_optimizations,
                    "repo_path": repo_path,  # Keep for potential PR creation
                }

            finally:
                # Don't clean up immediately if we might need to create a PR
                pass

        except Exception as e:
            return {"status": "error", "error": str(e), "repository_url": github_url}

    def create_optimization_pr(
        self, analysis_result: Dict[str, Any], auto_merge: bool = False
    ) -> Dict[str, Any]:
        """Create a PR with optimization suggestions"""
        if not PR_CREATOR_AVAILABLE:
            return {
                "status": "error",
                "error": "PR Creator not available due to missing dependencies. Please install required packages.",
            }

        if not self.pr_creator:
            return {
                "status": "error",
                "error": "GitHub token not configured. Cannot create PR.",
            }

        if (
            analysis_result["status"] != "success"
            or not analysis_result["file_optimizations"]
        ):
            return {
                "status": "error",
                "error": "No optimizations available to create PR.",
            }

        try:
            owner, repo_name = self.parse_github_url(analysis_result["repository_url"])
            repo_full_name = f"{owner}/{repo_name}"

            # Prepare the optimization summary
            summary_lines = [
                f"🤖 **CodeYogi AI Optimization Report**",
                f"",
                f"Analyzed {analysis_result['total_files_analyzed']} important files and found {analysis_result['total_optimizations']} optimization opportunities across {analysis_result['files_with_optimizations']} files.",
                f"",
                f"## 📊 Optimization Summary",
                f"",
            ]

            # Add details for each optimized file
            for file_opt in analysis_result["file_optimizations"]:
                summary_lines.extend(
                    [
                        f"### 📄 {file_opt['file']} ({file_opt['language']})",
                        f"**Importance:** {file_opt['importance_score']}/10 - {', '.join(file_opt['importance_reasons'])}",
                        f"**Optimizations Applied:**",
                    ]
                )

                for i, opt in enumerate(file_opt["optimizations"], 1):
                    summary_lines.append(f"{i}. {opt}")

                summary_lines.append("")

            improvement_summary = "\n".join(summary_lines)

            # Create optimization files content
            optimized_files = {}
            for file_opt in analysis_result["file_optimizations"]:
                optimized_files[file_opt["file"]] = file_opt["optimized_content"]

            # Also create a detailed optimization report
            report_content = f"""# CodeYogi Optimization Report

{improvement_summary}

## 🔍 Detailed Analysis

"""

            for file_opt in analysis_result["file_optimizations"]:
                report_content += f"""
### {file_opt['file']}

**Language:** {file_opt['language']}
**Importance Score:** {file_opt['importance_score']}/10

**Optimizations:**
"""
                for opt in file_opt["optimizations"]:
                    report_content += f"- {opt}\n"

                report_content += f"""
**Diff:**
```diff
{file_opt['diff']}
```

---

"""

            # Add the optimization report to the files
            optimized_files["CODEYOGI_OPTIMIZATION_REPORT.md"] = report_content

            # Generate README.md if it doesn't exist or update if it does
            try:
                from agents import readme_generator
                import asyncio
                
                # Get existing README content if it exists
                existing_readme = None
                for file_opt in analysis_result.get("file_optimizations", []):
                    if file_opt["file"].upper() == "README.MD":
                        existing_readme = file_opt.get("original_content", "")
                        break
                
                # Generate comprehensive README
                readme_gen = readme_generator.ReadmeGenerator()
                readme_result = asyncio.run(readme_gen.generate_readme_for_repository(
                    github_url=analysis_result["repository_url"],
                    github_token=self.github_token,
                    existing_content=existing_readme
                ))
                
                if readme_result.get("success") and readme_result.get("content"):
                    optimized_files["README.md"] = readme_result["content"]
                    print("✅ Generated/Updated README.md")
                else:
                    print("⚠️ Could not generate README.md")
            except Exception as e:
                print(f"⚠️ Error generating README.md: {str(e)}")
                # Continue without README if generation fails

            # Create PR with actual optimized files, README, AND the detailed report
            pr_result = self.pr_creator.create_multi_file_optimization_pr(
                repo_name=repo_full_name,
                optimized_files=optimized_files,
                improvement_summary=improvement_summary,
                branch_name="codeyogi-code-optimization",
                commit_message="🤖 CodeYogi: Multi-language code optimization with README",
            )

            if pr_result and pr_result.get("success"):
                # Auto-merge if requested and conditions are met
                if auto_merge:
                    merge_result = self.pr_creator.merge_pr(
                        repo_full_name,
                        pr_result["pr_number"],
                        "🤖 CodeYogi: Auto-merge optimization suggestions",
                    )
                    pr_result["auto_merged"] = merge_result

                return {
                    "status": "success",
                    "pr_created": True,
                    "pr_url": pr_result["pr_url"],
                    "pr_number": pr_result["pr_number"],
                    "optimizations_count": analysis_result["total_optimizations"],
                    "files_optimized": analysis_result["files_with_optimizations"],
                    "files_count": pr_result.get("files_count", len(optimized_files)),
                    "auto_merged": pr_result.get("auto_merged", False),
                }
            else:
                return {
                    "status": "error",
                    "error": pr_result.get("error", "Unknown error creating PR"),
                }

        except Exception as e:
            return {"status": "error", "error": f"Failed to create PR: {str(e)}"}
        finally:
            # Clean up repository
            if "repo_path" in analysis_result and os.path.exists(
                analysis_result["repo_path"]
            ):
                shutil.rmtree(analysis_result["repo_path"])

    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()

        ext_map = {
            ".py": "python",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".java": "java",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".cs": "csharp",
            ".kt": "kotlin",
            ".swift": "swift",
        }

        return ext_map.get(ext, "unknown")

    def optimize_code(
        self, source_code: str, language: str = None, file_path: str = None
    ) -> Dict[str, Any]:
        """Main optimization entry point using Groq AI"""
        try:
            if file_path and not language:
                language = self.detect_language(file_path)

            if language == "unknown":
                return {"error": "Unsupported language", "status": "error"}

            self.optimizations = []  # Reset optimizations

            # Use Groq AI for optimization if available
            if self.groq_client:
                optimized_code = self.optimize_with_groq(source_code, language)
            else:
                # Fallback to pattern-based optimization
                optimized_code = self.optimize_with_patterns(source_code, language)

            # Generate diff
            diff = "\n".join(
                difflib.unified_diff(
                    source_code.splitlines(),
                    optimized_code.splitlines(),
                    fromfile=f"before.{self.get_file_extension(language)}",
                    tofile=f"after.{self.get_file_extension(language)}",
                    lineterm="",
                )
            )

            return {
                "optimized_code": optimized_code,
                "diff": diff,
                "optimizations": self.optimizations,
                "language": language,
                "status": "success",
            }

        except Exception as e:
            return {"error": str(e), "status": "error"}

    def optimize_with_groq(self, source_code: str, language: str) -> str:
        """Optimize code using Groq AI"""
        try:
            prompt = f"""
You are an expert code optimizer. Analyze the following {language} code and provide an optimized version.

Focus on these optimization areas:
1. Performance improvements (algorithm efficiency, loop optimizations)
2. Memory usage optimization
3. Code readability and maintainability
4. Remove dead code and unused variables
5. Simplify complex expressions
6. Use language-specific best practices

Original {language} code:
```{language}
{source_code}
```

Provide:
1. The optimized code
2. A list of specific optimizations made

Format your response as:
OPTIMIZED_CODE:
```{language}
[optimized code here]
```

OPTIMIZATIONS:
- [list each optimization made]

Make sure the optimized code maintains the same functionality as the original.
"""

            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/llama-4-scout-17b-16e-instruct",  # Using Mixtral model for code optimization
                temperature=0.1,  # Low temperature for consistent optimization
                max_tokens=4000,
            )

            response_text = response.choices[0].message.content

            # Parse the response to extract optimized code and optimizations
            optimized_code, optimizations = self.parse_groq_response(
                response_text, source_code
            )

            # Store optimizations for reporting
            self.optimizations = optimizations

            return optimized_code

        except Exception as e:
            print(f"❌ Groq optimization failed: {e}")
            # Fallback to pattern-based optimization
            return self.optimize_with_patterns(source_code, language)

    def parse_groq_response(self, response_text: str, original_code: str) -> tuple:
        """Parse Groq response to extract optimized code and optimizations"""
        try:
            # Extract optimized code
            optimized_code = original_code  # Default fallback

            if "OPTIMIZED_CODE:" in response_text:
                # Find the code block after OPTIMIZED_CODE:
                code_start = response_text.find("OPTIMIZED_CODE:")
                code_section = response_text[code_start:]

                # Look for code between triple backticks
                import re

                code_match = re.search(
                    r"```(?:\w+)?\n(.*?)\n```", code_section, re.DOTALL
                )
                if code_match:
                    optimized_code = code_match.group(1).strip()

            # Extract optimizations list
            optimizations = []
            if "OPTIMIZATIONS:" in response_text:
                opt_start = response_text.find("OPTIMIZATIONS:")
                opt_section = response_text[opt_start:]

                # Extract bullet points
                lines = opt_section.split("\n")
                for line in lines[1:]:  # Skip the "OPTIMIZATIONS:" line
                    line = line.strip()
                    if (
                        line.startswith("-")
                        or line.startswith("•")
                        or line.startswith("*")
                    ):
                        optimizations.append(line[1:].strip())
                    elif line and not line.startswith("OPTIMIZED_CODE:"):
                        # Handle numbered lists or plain text
                        if re.match(r"^\d+\.", line):
                            optimizations.append(re.sub(r"^\d+\.\s*", "", line))
                        elif line and len(line) > 10:  # Ignore very short lines
                            optimizations.append(line)

            return optimized_code, optimizations

        except Exception as e:
            print(f"Warning: Failed to parse Groq response: {e}")
            return original_code, ["AI optimization attempted but parsing failed"]

    def optimize_with_patterns(self, source_code: str, language: str) -> str:
        """Fallback pattern-based optimization"""
        if language == "python":
            return self.optimize_python_patterns(source_code)
        elif language in ["c", "cpp"]:
            return self.optimize_c_cpp_patterns(source_code)
        elif language == "java":
            return self.optimize_java_patterns(source_code)
        elif language in ["javascript", "typescript"]:
            return self.optimize_js_ts_patterns(source_code)

        return source_code

    # ===== PATTERN-BASED OPTIMIZATIONS =====
    def optimize_python_patterns(self, source_code: str) -> str:
        """Pattern-based Python optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            # Optimize range(len()) patterns
            if re.search(r"for\s+\w+\s+in\s+range\(len\((\w+)\)\):", line):
                var_match = re.search(
                    r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):", line
                )
                if var_match:
                    loop_var, list_var = var_match.groups()
                    indent = len(line) - len(line.lstrip())
                    optimized_lines.append(
                        " " * indent
                        + f"# [OPTIMIZED] Changed from range(len({list_var})) to direct iteration"
                    )
                    optimized_lines.append(
                        line.replace(f"range(len({list_var}))", list_var)
                    )
                    self.optimizations.append(
                        f"Optimized range(len({list_var})) to direct iteration at line {i+1}"
                    )
                    continue

            # Remove dead code (if False)
            if re.search(r"if\s+False\s*:", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent
                    + "# [OPTIMIZED] Removed dead code (always-false condition)"
                )
                self.optimizations.append(f"Removed dead code (if False) at line {i+1}")
                continue

            # Simplify always true conditions
            if re.search(r"if\s+True\s*:", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "# [OPTIMIZED] Removed always-true if condition"
                )
                self.optimizations.append(
                    f"Simplified always-true condition at line {i+1}"
                )
                continue

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def optimize_c_cpp_patterns(self, source_code: str) -> str:
        """Pattern-based C/C++ optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            # Optimize strlen in loops
            if re.search(r"for\s*\(.*;\s*\w+\s*<\s*strlen\(", line):
                optimized_lines.append(
                    "    // [OPTIMIZED] Consider caching strlen() result"
                )
                optimized_lines.append(line)
                self.optimizations.append(
                    f"Suggested strlen optimization at line {i+1}"
                )
                continue

            # Remove unnecessary assignments
            if re.search(r"^\s*\w+\s*=\s*\w+\s*;\s*$", line):
                var_match = re.search(r"^\s*(\w+)\s*=\s*(\w+)\s*;\s*$", line)
                if var_match and var_match.group(1) == var_match.group(2):
                    optimized_lines.append("    // [OPTIMIZED] Removed self-assignment")
                    self.optimizations.append(f"Removed self-assignment at line {i+1}")
                    continue

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def optimize_java_patterns(self, source_code: str) -> str:
        """Pattern-based Java optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            # Optimize traditional for loops to enhanced for loops
            if re.search(
                r"for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\.length\s*;\s*\w+\+\+\s*\)",
                line,
            ):
                optimized_lines.append(
                    "        // [OPTIMIZED] Consider using enhanced for loop"
                )
                optimized_lines.append(line)
                self.optimizations.append(f"Suggested enhanced for loop at line {i+1}")
                continue

            # String concatenation in loops
            if (
                "+=" in line
                and "String" in line
                and "for" in "".join(lines[max(0, i - 3) : i])
            ):
                optimized_lines.append(
                    "        // [OPTIMIZED] Consider using StringBuilder for string concatenation in loops"
                )
                optimized_lines.append(line)
                self.optimizations.append(
                    f"Suggested StringBuilder optimization at line {i+1}"
                )
                continue

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def optimize_js_ts_patterns(self, source_code: str) -> str:
        """Pattern-based JavaScript/TypeScript optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            # Optimize traditional for loops to for...of
            if re.search(
                r"for\s*\(\s*let\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\.length\s*;\s*\w+\+\+\s*\)",
                line,
            ):
                optimized_lines.append(
                    "    // [OPTIMIZED] Consider using for...of loop"
                )
                optimized_lines.append(line)
                self.optimizations.append(f"Suggested for...of loop at line {i+1}")
                continue

            # Use const instead of let for non-reassigned variables
            if re.search(r"let\s+\w+\s*=", line) and not any(
                "=" in l and line.split("=")[0].strip().split()[-1] in l
                for l in lines[i + 1 : i + 10]
            ):
                new_line = line.replace("let ", "const ")
                optimized_lines.append(
                    "    // [OPTIMIZED] Changed let to const for non-reassigned variable"
                )
                optimized_lines.append(new_line)
                self.optimizations.append(f"Changed let to const at line {i+1}")
                continue

            optimized_lines.append(line)

        return "\n".join(optimized_lines)

    def get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        ext_map = {
            "python": "py",
            "c": "c",
            "cpp": "cpp",
            "java": "java",
            "javascript": "js",
            "typescript": "ts",
            "go": "go",
            "rust": "rs",
            "php": "php",
            "ruby": "rb",
            "csharp": "cs",
            "kotlin": "kt",
            "swift": "swift",
        }
        return ext_map.get(language, "txt")


# ===== MAIN INTERFACE FUNCTIONS =====
def optimize_multi_language_code(
    source_code: str,
    language: str = None,
    file_path: str = None,
    with_llm_review: bool = False,
) -> Dict[str, Any]:
    """
    Main function to optimize code in multiple languages

    Args:
        source_code: The source code to optimize
        language: Programming language ('python', 'c', 'cpp', 'java', 'javascript', 'typescript')
        file_path: File path to auto-detect language
        with_llm_review: Whether to include LLM review (if available)

    Returns:
        Dictionary with optimization results
    """
    optimizer = GitHubMultiLanguageOptimizer()
    result = optimizer.optimize_code(source_code, language, file_path)

    # Add LLM review if requested and available
    if with_llm_review and result["status"] == "success":
        try:
            # Note: ast_optimizer import removed as it's not available
            result["comments"] = ["⚠️ LLM review not available in this setup"]
        except Exception as e:
            result["comments"] = [f"⚠️ LLM review unavailable: {e}"]

    return result


def analyze_github_repository_for_optimization(
    github_url: str,
    github_token: str = None,
    create_pr: bool = False,
    auto_merge: bool = False,
) -> Dict[str, Any]:
    """
    Analyze GitHub repository and suggest code optimizations

    Args:
        github_url: GitHub repository URL
        github_token: GitHub token for authentication (if not provided, will try to load from .env file)
        create_pr: Whether to create a PR with optimization suggestions
        auto_merge: Whether to auto-merge the PR (if create_pr is True)

    Returns:
        Dictionary with analysis results and optimization suggestions
    """
    # If no GitHub token provided, try to load from .env file
    if not github_token:
        load_dotenv(override=False)
        github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

    optimizer = GitHubMultiLanguageOptimizer(github_token)

    # Analyze repository
    analysis_result = optimizer.analyze_github_repository(github_url)

    # Create PR if requested and analysis was successful
    if create_pr and analysis_result.get("status") == "success":
        pr_result = optimizer.create_optimization_pr(analysis_result, auto_merge)
        analysis_result["pr_result"] = pr_result

    return analysis_result


if __name__ == "__main__":
    # Test with different languages and GitHub repositories

    # Python test
    python_code = """
def process_data(data):
    for i in range(len(data)):
        print(data[i])
    
    if False:
        print("Dead code")
    
    if True:
        print("Always runs")
"""

    # JavaScript test
    js_code = """
function processArray(arr) {
    for (let i = 0; i < arr.length; i++) {
        console.log(arr[i]);
    }
    
    let count = 0;
    count = 5; // This could be const
}
"""

    print("=== GROQ-POWERED MULTI-LANGUAGE OPTIMIZER TEST ===")
    print(
        "Note: Set GROQ_API_KEY in .env file or environment variable to use AI optimization"
    )
    print("Note: Set GITHUB_TOKEN in .env file or environment variable to create PRs")

    # Test code optimization
    print(f"\n{'='*50}")
    print("Testing PYTHON optimization:")
    print(f"{'='*50}")

    result = optimize_multi_language_code(python_code, language="python")

    if result["status"] == "success":
        print("\nOptimized Python code:")
        print("-" * 30)
        print(result["optimized_code"])

        print("\nOptimizations applied:")
        print("-" * 30)
        for i, opt in enumerate(result["optimizations"], 1):
            print(f"{i}. {opt}")

    # Test GitHub repository analysis (uncomment to test with real repos)
    """
    print(f"\n{'='*50}")
    print("Testing GITHUB REPOSITORY analysis:")
    print(f"{'='*50}")
    
    # Example: analyze a small public repository
    test_repo_url = "https://github.com/octocat/Hello-World"
    
    result = analyze_github_repository_for_optimization(
        github_url=test_repo_url,
        create_pr=False  # Set to True to create actual PRs (requires GITHUB_TOKEN)
    )
    
    if result["status"] == "success":
        print(f"\nRepository Analysis Results:")
        print(f"Total files analyzed: {result['total_files_analyzed']}")
        print(f"Files with optimizations: {result['files_with_optimizations']}")
        print(f"Total optimizations: {result['total_optimizations']}")
        
        for file_opt in result['file_optimizations'][:3]:  # Show first 3
            print(f"\n📄 {file_opt['file']} ({file_opt['language']}):")
            for opt in file_opt['optimizations']:
                print(f"  - {opt}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
    """
