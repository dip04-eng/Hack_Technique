import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import hashlib
import mimetypes

import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import (
    FileAnalysisRequest,
    FileAnalysisResult,
    AnalysisCommand,
    OptimizationSuggestion,
    CodeExplanation,
    FileStructureAnalysisRequest,
    FileStructureAnalysisResult,
    FileStructureIssue,
    FileStructureMetrics,
)
from agents.ai_analyzer import ai_analyzer


class FileAnalyzer:
    def __init__(self):
        """Initialize the File Analyzer"""
        self.supported_languages = {
            "python": [".py"],
            "javascript": [".js", ".jsx"],
            "typescript": [".ts", ".tsx"],
            "java": [".java"],
            "cpp": [".cpp", ".cc", ".cxx"],
            "c": [".c"],
            "csharp": [".cs"],
            "go": [".go"],
            "rust": [".rs"],
            "php": [".php"],
            "ruby": [".rb"],
            "swift": [".swift"],
            "kotlin": [".kt"],
            "scala": [".scala"],
            "html": [".html", ".htm"],
            "css": [".css"],
            "sql": [".sql"],
            "json": [".json"],
            "yaml": [".yaml", ".yml"],
            "xml": [".xml"],
            "markdown": [".md", ".markdown"],
        }

        # Optimization patterns for different languages
        self.optimization_patterns = {
            "python": {
                "performance": [
                    "Use list comprehensions instead of loops",
                    "Replace string concatenation with join()",
                    "Use generators for memory efficiency",
                    "Cache expensive function calls",
                    "Use built-in functions over manual loops",
                ],
                "readability": [
                    "Use descriptive variable names",
                    "Add type hints",
                    "Break down complex functions",
                    "Add docstrings",
                    "Follow PEP 8 style guide",
                ],
                "security": [
                    "Validate user inputs",
                    "Use parameterized queries",
                    "Avoid eval() and exec()",
                    "Handle exceptions properly",
                    "Use secure random for sensitive data",
                ],
            },
            "javascript": {
                "performance": [
                    "Use const/let instead of var",
                    "Implement debouncing for frequent events",
                    "Use array methods efficiently",
                    "Minimize DOM manipulations",
                    "Use async/await properly",
                ],
                "readability": [
                    "Use meaningful function names",
                    "Implement proper error handling",
                    "Use ES6+ features appropriately",
                    "Add JSDoc comments",
                    "Structure code with modules",
                ],
                "security": [
                    "Sanitize user inputs",
                    "Use HTTPS for API calls",
                    "Implement proper authentication",
                    "Avoid eval() and innerHTML",
                    "Validate data on both client and server",
                ],
            },
        }

    async def analyze_file(self, request: FileAnalysisRequest) -> FileAnalysisResult:
        """
        Analyze a file based on the selected command and selected code portion

        Args:
            request: File analysis request containing file content, selected part, and command

        Returns:
            Analysis result with optimized code or explanation
        """
        try:
            # Detect file language
            language = self._detect_language(request.file_name or "unknown.txt")

            # Get the code to analyze (either selected part or full file)
            code_to_analyze = (
                request.selected_code if request.selected_code else request.file_content
            )

            # Validate inputs
            if not code_to_analyze.strip():
                raise ValueError("No code provided for analysis")

            # Process based on command
            if request.command == AnalysisCommand.OPTIMIZE:
                result = await self._optimize_code(
                    code_to_analyze,
                    request.file_content,
                    language,
                    request.optimization_type,
                )
            elif request.command == AnalysisCommand.EXPLAIN:
                result = await self._explain_code(
                    code_to_analyze, language, request.explanation_level
                )
            elif request.command == AnalysisCommand.REFACTOR:
                result = await self._refactor_code(
                    code_to_analyze, request.file_content, language
                )
            elif request.command == AnalysisCommand.REVIEW:
                result = await self._review_code(code_to_analyze, language)
            elif request.command == AnalysisCommand.ANALYZE_STRUCTURE:
                # For structure analysis, we need the project context
                if not request.file_name:
                    raise ValueError("File name is required for structure analysis")
                result = await self._analyze_file_structure(
                    request.file_name, code_to_analyze, language
                )
            else:
                raise ValueError(f"Unsupported command: {request.command}")

            return FileAnalysisResult(
                original_code=code_to_analyze,
                language=language,
                command=request.command,
                result=result,
                success=True,
                file_name=request.file_name,
            )

        except Exception as e:
            return FileAnalysisResult(
                original_code=request.selected_code or request.file_content,
                language="unknown",
                command=request.command,
                result={"error": str(e)},
                success=False,
                error_message=str(e),
                file_name=request.file_name,
            )

    def _detect_language(self, file_name: str) -> str:
        """Detect programming language from file extension"""
        extension = Path(file_name).suffix.lower()

        for language, extensions in self.supported_languages.items():
            if extension in extensions:
                return language

        return "unknown"

    async def _optimize_code(
        self,
        code: str,
        full_file_content: str,
        language: str,
        optimization_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Optimize code based on best practices and performance patterns"""

        if not ai_analyzer.is_available():
            return await self._static_optimize_code(code, language, optimization_type)

        try:
            # Determine optimization focus
            focus = optimization_type or "general"

            prompt = f"""
You are an expert {language} developer. Optimize the following code for {focus} improvements.

Original Code:
```{language}
{code}
```

Full File Context (for reference):
```{language}
{full_file_content[:2000]}{'...' if len(full_file_content) > 2000 else ''}
```

Provide:
1. **Optimized Code**: The improved version
2. **Changes Made**: List of specific improvements
3. **Performance Impact**: Expected performance benefits
4. **Best Practices Applied**: Which coding standards were followed
5. **Potential Issues**: Any trade-offs or considerations

Focus on:
- Performance optimization
- Code readability
- Memory efficiency
- Security improvements
- Maintainability

Return the response in JSON format with keys: optimized_code, changes_made, performance_impact, best_practices, potential_issues.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a senior {language} developer and code optimization expert. Always return valid JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            # Try to parse JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                result["analysis_type"] = "ai_optimization"
                result["optimization_focus"] = focus
                return result
            except json.JSONDecodeError:
                # Fallback to text response
                return {
                    "optimized_code": code,
                    "analysis": response.choices[0].message.content,
                    "analysis_type": "ai_optimization",
                    "optimization_focus": focus,
                    "note": "AI response was not in JSON format",
                }

        except Exception as e:
            return await self._static_optimize_code(code, language, optimization_type)

    async def _explain_code(
        self, code: str, language: str, explanation_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Explain code functionality and structure"""

        if not ai_analyzer.is_available():
            return self._static_explain_code(code, language)

        try:
            level = explanation_level or "intermediate"

            prompt = f"""
Explain the following {language} code in detail at a {level} level.

Code to Explain:
```{language}
{code}
```

Provide:
1. **Overview**: What this code does overall
2. **Step-by-Step Breakdown**: Line-by-line or block-by-block explanation
3. **Key Concepts**: Important programming concepts used
4. **Data Flow**: How data moves through the code
5. **Dependencies**: External libraries or modules used
6. **Potential Improvements**: Suggestions for enhancement
7. **Common Patterns**: Design patterns or coding patterns used

Adjust the explanation complexity for a {level} level programmer.
Return the response in JSON format with keys: overview, breakdown, key_concepts, data_flow, dependencies, improvements, patterns.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {language} developer and coding instructor. Always return valid JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            # Try to parse JSON response
            try:
                result = json.loads(response.choices[0].message.content)
                result["analysis_type"] = "ai_explanation"
                result["explanation_level"] = level
                return result
            except json.JSONDecodeError:
                # Fallback to text response
                return {
                    "explanation": response.choices[0].message.content,
                    "analysis_type": "ai_explanation",
                    "explanation_level": level,
                    "note": "AI response was not in JSON format",
                }

        except Exception as e:
            return self._static_explain_code(code, language)

    async def _refactor_code(
        self, code: str, full_file_content: str, language: str
    ) -> Dict[str, Any]:
        """Refactor code for better structure and maintainability"""

        if not ai_analyzer.is_available():
            return {"error": "AI analysis not available for refactoring"}

        try:
            prompt = f"""
Refactor the following {language} code to improve its structure, readability, and maintainability.

Code to Refactor:
```{language}
{code}
```

Full File Context:
```{language}
{full_file_content[:2000]}{'...' if len(full_file_content) > 2000 else ''}
```

Focus on:
1. **Code Structure**: Better organization and modularity
2. **Naming**: More descriptive variable and function names
3. **Functions**: Breaking down large functions into smaller ones
4. **Documentation**: Adding comments and docstrings
5. **Error Handling**: Proper exception handling
6. **Code Reuse**: Eliminating duplication

Provide:
- Refactored code
- Explanation of changes made
- Benefits of the refactoring

Return in JSON format with keys: refactored_code, changes_explained, benefits.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a senior {language} developer specializing in code refactoring. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            try:
                result = json.loads(response.choices[0].message.content)
                result["analysis_type"] = "ai_refactoring"
                return result
            except json.JSONDecodeError:
                return {
                    "refactoring_analysis": response.choices[0].message.content,
                    "analysis_type": "ai_refactoring",
                }

        except Exception as e:
            return {"error": f"Refactoring failed: {str(e)}"}

    async def _review_code(self, code: str, language: str) -> Dict[str, Any]:
        """Perform comprehensive code review"""

        if not ai_analyzer.is_available():
            return self._static_review_code(code, language)

        try:
            prompt = f"""
Perform a comprehensive code review for the following {language} code.

Code to Review:
```{language}
{code}
```

Analyze for:
1. **Code Quality**: Overall quality assessment
2. **Best Practices**: Adherence to language best practices
3. **Potential Bugs**: Possible issues or bugs
4. **Performance Issues**: Performance bottlenecks
5. **Security Concerns**: Security vulnerabilities
6. **Maintainability**: How easy it is to maintain and extend
7. **Testing**: Testing considerations
8. **Recommendations**: Specific improvement suggestions

Rate each category from 1-10 and provide specific feedback.
Return in JSON format with keys: quality_score, best_practices_score, bug_risks, performance_issues, security_concerns, maintainability_score, testing_notes, recommendations.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a senior {language} developer and code reviewer. Always return valid JSON.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            try:
                result = json.loads(response.choices[0].message.content)
                result["analysis_type"] = "ai_code_review"
                return result
            except json.JSONDecodeError:
                return {
                    "review": response.choices[0].message.content,
                    "analysis_type": "ai_code_review",
                }

        except Exception as e:
            return self._static_review_code(code, language)

    async def _analyze_file_structure(
        self, file_name: str, code: str, language: str
    ) -> Dict[str, Any]:
        """Analyze file structure and suggest improvements"""

        if not ai_analyzer.is_available():
            return self._static_analyze_file_structure(file_name, code, language)

        try:
            # Get file metrics
            file_metrics = self._get_file_metrics(file_name, code, language)

            prompt = f"""
Analyze the file structure and organization for the following {language} file.

File: {file_name}
Language: {language}

Code:
```{language}
{code}
```

File Metrics:
- Lines of code: {file_metrics['lines_of_code']}
- Functions/methods: {file_metrics['functions_count']}
- Classes: {file_metrics['classes_count']}
- Complexity score: {file_metrics['complexity_score']}

Analyze for:
1. **File Organization**: How well the code is organized within the file
2. **Naming Conventions**: Consistency and clarity of naming
3. **Structure Issues**: Problems with file structure or layout
4. **Best Practices**: Adherence to language-specific file organization standards
5. **Separation of Concerns**: Whether different responsibilities are properly separated
6. **Code Grouping**: How related code is grouped together
7. **Import/Include Organization**: How dependencies are organized
8. **Documentation Structure**: How comments and documentation are structured

Provide specific suggestions for improvement and rate the current structure from 1-10.
Return in JSON format with keys: organization_score, naming_score, structure_issues, best_practices_violations, suggestions, file_metrics.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a senior {language} developer and code organization expert. Always return valid JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            try:
                result = json.loads(response.choices[0].message.content)
                result["analysis_type"] = "ai_file_structure"
                result["file_name"] = file_name
                result["language"] = language
                result["computed_metrics"] = file_metrics
                return result
            except json.JSONDecodeError:
                return {
                    "analysis": response.choices[0].message.content,
                    "analysis_type": "ai_file_structure",
                    "file_name": file_name,
                    "language": language,
                    "computed_metrics": file_metrics,
                    "note": "AI response was not in JSON format",
                }

        except Exception as e:
            return self._static_analyze_file_structure(file_name, code, language)

    def _get_file_metrics(
        self, file_name: str, code: str, language: str
    ) -> Dict[str, Any]:
        """Calculate basic file metrics"""
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]

        metrics = {
            "total_lines": len(lines),
            "lines_of_code": len(non_empty_lines),
            "functions_count": 0,
            "classes_count": 0,
            "complexity_score": 0,
            "file_size": len(code.encode("utf-8")),
            "average_line_length": (
                sum(len(line) for line in lines) / len(lines) if lines else 0
            ),
        }

        # Language-specific analysis
        if language == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        metrics["functions_count"] += 1
                    elif isinstance(node, ast.ClassDef):
                        metrics["classes_count"] += 1

                # Simple complexity estimation
                metrics["complexity_score"] = self._calculate_python_complexity(tree)
            except:
                pass
        elif language in ["javascript", "typescript"]:
            # Basic regex-based counting for JS/TS
            metrics["functions_count"] = len(
                re.findall(r"function\s+\w+|const\s+\w+\s*=\s*\(.*?\)\s*=>", code)
            )
            metrics["classes_count"] = len(re.findall(r"class\s+\w+", code))
        elif language == "java":
            metrics["functions_count"] = len(
                re.findall(
                    r"(public|private|protected)?\s*(static)?\s*\w+\s+\w+\s*\(", code
                )
            )
            metrics["classes_count"] = len(re.findall(r"class\s+\w+", code))

        return metrics

    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate basic complexity score for Python code"""
        complexity = 1  # Base complexity

        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.Try):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(
                node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)
            ):
                complexity += 1

        return complexity

    async def analyze_project_structure(
        self, request: FileStructureAnalysisRequest
    ) -> FileStructureAnalysisResult:
        """Analyze entire project file structure and suggest improvements"""
        try:
            project_path = Path(request.project_path)
            if not project_path.exists():
                raise ValueError(f"Project path does not exist: {request.project_path}")

            # Collect all files
            all_files = self._collect_project_files(
                project_path,
                request.exclude_patterns,
                request.max_depth,
                request.include_hidden_files,
            )

            # Calculate metrics
            metrics = self._calculate_project_metrics(all_files, project_path)

            # Analyze structure issues
            issues = await self._analyze_structure_issues(
                all_files, project_path, request.focus_areas
            )

            # Generate recommendations
            recommendations = self._generate_structure_recommendations(issues, metrics)

            # Generate best practices suggestions
            best_practices = self._generate_best_practices_suggestions(
                all_files, project_path
            )

            # AI-powered insights
            ai_insights = None
            if ai_analyzer.is_available():
                ai_insights = await self._get_ai_structure_insights(
                    all_files, metrics, issues
                )

            return FileStructureAnalysisResult(
                project_info={
                    "project_path": str(project_path),
                    "project_name": project_path.name,
                    "total_files_analyzed": len(all_files),
                    "analysis_focus": request.focus_areas,
                },
                structure_metrics=metrics,
                issues_found=issues,
                recommendations=recommendations,
                best_practices_suggestions=best_practices,
                ai_insights=ai_insights,
                success=True,
            )

        except Exception as e:
            return FileStructureAnalysisResult(
                project_info={"project_path": request.project_path},
                structure_metrics=FileStructureMetrics(
                    total_files=0,
                    total_directories=0,
                    depth_levels=0,
                    largest_files=[],
                    file_type_distribution={},
                    naming_consistency_score=0.0,
                    organization_score=0.0,
                    structure_complexity="unknown",
                ),
                issues_found=[],
                recommendations=[],
                best_practices_suggestions=[],
                success=False,
                error_message=str(e),
            )

    def _collect_project_files(
        self,
        project_path: Path,
        exclude_patterns: List[str],
        max_depth: Optional[int],
        include_hidden: bool,
    ) -> List[Dict[str, Any]]:
        """Collect all files in the project for analysis"""
        files = []

        def should_exclude(path: Path) -> bool:
            path_str = str(path)
            if not include_hidden and any(part.startswith(".") for part in path.parts):
                return True
            return any(pattern in path_str for pattern in exclude_patterns)

        def collect_recursive(current_path: Path, current_depth: int = 0):
            if max_depth and current_depth > max_depth:
                return

            try:
                for item in current_path.iterdir():
                    if should_exclude(item):
                        continue

                    if item.is_file():
                        file_info = {
                            "path": item,
                            "relative_path": item.relative_to(project_path),
                            "size": item.stat().st_size,
                            "suffix": item.suffix,
                            "name": item.name,
                            "depth": current_depth,
                        }
                        files.append(file_info)
                    elif item.is_dir():
                        collect_recursive(item, current_depth + 1)
            except PermissionError:
                pass

        collect_recursive(project_path)
        return files

    def _calculate_project_metrics(
        self, files: List[Dict[str, Any]], project_path: Path
    ) -> FileStructureMetrics:
        """Calculate comprehensive project structure metrics"""
        if not files:
            return FileStructureMetrics(
                total_files=0,
                total_directories=0,
                depth_levels=0,
                largest_files=[],
                file_type_distribution={},
                naming_consistency_score=0.0,
                organization_score=0.0,
                structure_complexity="empty",
            )

        # Basic counts
        total_files = len(files)
        directories = set()
        max_depth = 0

        # File type distribution
        file_types = {}
        total_size = 0

        for file_info in files:
            # Directory tracking
            directories.add(file_info["path"].parent)
            max_depth = max(max_depth, file_info["depth"])

            # File type tracking
            suffix = file_info["suffix"] or "no_extension"
            file_types[suffix] = file_types.get(suffix, 0) + 1
            total_size += file_info["size"]

        # Largest files
        largest_files = sorted(files, key=lambda f: f["size"], reverse=True)[:10]
        largest_files_info = [
            {
                "path": str(f["relative_path"]),
                "size": f["size"],
                "size_mb": round(f["size"] / (1024 * 1024), 2),
            }
            for f in largest_files
        ]

        # Naming consistency score
        naming_score = self._calculate_naming_consistency(files)

        # Organization score
        organization_score = self._calculate_organization_score(files, project_path)

        # Structure complexity
        complexity = self._determine_structure_complexity(
            total_files, len(directories), max_depth, file_types
        )

        return FileStructureMetrics(
            total_files=total_files,
            total_directories=len(directories),
            depth_levels=max_depth,
            largest_files=largest_files_info,
            file_type_distribution=file_types,
            naming_consistency_score=naming_score,
            organization_score=organization_score,
            structure_complexity=complexity,
        )

    def _calculate_naming_consistency(self, files: List[Dict[str, Any]]) -> float:
        """Calculate naming consistency score"""
        if not files:
            return 0.0

        naming_patterns = {
            "snake_case": 0,
            "camelCase": 0,
            "kebab-case": 0,
            "PascalCase": 0,
            "mixed": 0,
        }

        for file_info in files:
            name = file_info["path"].stem  # filename without extension

            if re.match(r"^[a-z]+(_[a-z]+)*$", name):
                naming_patterns["snake_case"] += 1
            elif re.match(r"^[a-z]+([A-Z][a-z]*)*$", name):
                naming_patterns["camelCase"] += 1
            elif re.match(r"^[a-z]+(-[a-z]+)*$", name):
                naming_patterns["kebab-case"] += 1
            elif re.match(r"^[A-Z][a-z]*([A-Z][a-z]*)*$", name):
                naming_patterns["PascalCase"] += 1
            else:
                naming_patterns["mixed"] += 1

        # Calculate consistency as the percentage of the most common pattern
        max_pattern_count = max(naming_patterns.values())
        return (max_pattern_count / len(files)) * 100 if files else 0

    def _calculate_organization_score(
        self, files: List[Dict[str, Any]], project_path: Path
    ) -> float:
        """Calculate project organization score based on common patterns"""
        score = 50.0  # Base score

        file_paths = [str(f["relative_path"]) for f in files]

        # Check for common good practices
        if any("src" in path for path in file_paths):
            score += 10
        if any("test" in path or "spec" in path for path in file_paths):
            score += 10
        if any("doc" in path or "readme" in path.lower() for path in file_paths):
            score += 5
        if any("config" in path for path in file_paths):
            score += 5

        # Penalize for potential issues
        root_files = [f for f in files if f["depth"] == 0]
        if len(root_files) > 10:  # Too many files in root
            score -= 15

        # Check for deeply nested structures
        avg_depth = sum(f["depth"] for f in files) / len(files) if files else 0
        if avg_depth > 4:
            score -= 10

        return max(0, min(100, score))

    def _determine_structure_complexity(
        self,
        total_files: int,
        total_dirs: int,
        max_depth: int,
        file_types: Dict[str, int],
    ) -> str:
        """Determine overall structure complexity"""
        complexity_score = 0

        # File count factor
        if total_files > 1000:
            complexity_score += 3
        elif total_files > 500:
            complexity_score += 2
        elif total_files > 100:
            complexity_score += 1

        # Directory depth factor
        if max_depth > 8:
            complexity_score += 3
        elif max_depth > 5:
            complexity_score += 2
        elif max_depth > 3:
            complexity_score += 1

        # File type diversity factor
        if len(file_types) > 15:
            complexity_score += 2
        elif len(file_types) > 10:
            complexity_score += 1

        # Complexity mapping
        if complexity_score >= 6:
            return "very_high"
        elif complexity_score >= 4:
            return "high"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "low"

    async def _analyze_structure_issues(
        self, files: List[Dict[str, Any]], project_path: Path, focus_areas: List[str]
    ) -> List[FileStructureIssue]:
        """Analyze and identify structure issues"""
        issues = []

        if "naming" in focus_areas:
            issues.extend(self._check_naming_issues(files))

        if "organization" in focus_areas:
            issues.extend(self._check_organization_issues(files, project_path))

        if "structure" in focus_areas:
            issues.extend(self._check_structure_issues(files))

        if "best_practices" in focus_areas:
            issues.extend(self._check_best_practices_issues(files, project_path))

        return issues

    def _check_naming_issues(
        self, files: List[Dict[str, Any]]
    ) -> List[FileStructureIssue]:
        """Check for naming convention issues"""
        issues = []

        for file_info in files:
            name = file_info["name"]
            path = str(file_info["relative_path"])

            # Check for spaces in filenames
            if " " in name:
                issues.append(
                    FileStructureIssue(
                        type="naming",
                        severity="medium",
                        file_path=path,
                        description="Filename contains spaces",
                        suggestion="Replace spaces with underscores or hyphens",
                        impact="May cause issues in some environments",
                        effort_required="low",
                    )
                )

            # Check for special characters
            if re.search(r"[^\w\-\.]", name):
                issues.append(
                    FileStructureIssue(
                        type="naming",
                        severity="medium",
                        file_path=path,
                        description="Filename contains special characters",
                        suggestion="Use only letters, numbers, hyphens, and underscores",
                        impact="May cause cross-platform compatibility issues",
                        effort_required="low",
                    )
                )

            # Check for very long filenames
            if len(name) > 50:
                issues.append(
                    FileStructureIssue(
                        type="naming",
                        severity="low",
                        file_path=path,
                        description="Filename is very long",
                        suggestion="Consider shortening the filename while keeping it descriptive",
                        impact="Reduced readability and potential path length issues",
                        effort_required="low",
                    )
                )

        return issues

    def _check_organization_issues(
        self, files: List[Dict[str, Any]], project_path: Path
    ) -> List[FileStructureIssue]:
        """Check for organization issues"""
        issues = []

        # Check for too many files in root directory
        root_files = [f for f in files if f["depth"] == 0 and f["path"].is_file()]
        if len(root_files) > 8:
            issues.append(
                FileStructureIssue(
                    type="organization",
                    severity="medium",
                    file_path=".",
                    description=f"Too many files ({len(root_files)}) in root directory",
                    suggestion="Move files into appropriate subdirectories (src, docs, tests, etc.)",
                    impact="Cluttered project structure, harder to navigate",
                    effort_required="medium",
                )
            )

        # Check for missing common directories
        dir_names = set(f["path"].parent.name for f in files)

        has_source_dir = any(name in ["src", "source", "lib"] for name in dir_names)
        has_test_dir = any(
            name in ["test", "tests", "spec", "__tests__"] for name in dir_names
        )

        if not has_source_dir and len(files) > 10:
            issues.append(
                FileStructureIssue(
                    type="organization",
                    severity="low",
                    file_path=".",
                    description="No dedicated source code directory found",
                    suggestion="Consider creating a 'src' directory for source code",
                    impact="Less clear project structure",
                    effort_required="medium",
                )
            )

        if not has_test_dir:
            issues.append(
                FileStructureIssue(
                    type="organization",
                    severity="low",
                    file_path=".",
                    description="No test directory found",
                    suggestion="Create a tests directory for test files",
                    impact="Testing code mixed with production code",
                    effort_required="low",
                )
            )

        return issues

    def _check_structure_issues(
        self, files: List[Dict[str, Any]]
    ) -> List[FileStructureIssue]:
        """Check for structural issues"""
        issues = []

        # Check for deeply nested structures
        max_depth = max((f["depth"] for f in files), default=0)
        if max_depth > 6:
            deep_files = [f for f in files if f["depth"] > 6]
            issues.append(
                FileStructureIssue(
                    type="structure",
                    severity="medium",
                    file_path=f"Multiple files (e.g., {str(deep_files[0]['relative_path'])})",
                    description=f"Very deep directory nesting (max depth: {max_depth})",
                    suggestion="Consider flattening the directory structure",
                    impact="Harder to navigate, potential path length issues",
                    effort_required="high",
                )
            )

        # Check for large files
        large_files = [f for f in files if f["size"] > 1024 * 1024]  # > 1MB
        for file_info in large_files:
            issues.append(
                FileStructureIssue(
                    type="structure",
                    severity="medium",
                    file_path=str(file_info["relative_path"]),
                    description=f"Large file size ({file_info['size'] / (1024*1024):.1f} MB)",
                    suggestion="Consider breaking down into smaller files or moving to appropriate location",
                    impact="Slower loading times, harder to maintain",
                    effort_required="medium",
                )
            )

        return issues

    def _check_best_practices_issues(
        self, files: List[Dict[str, Any]], project_path: Path
    ) -> List[FileStructureIssue]:
        """Check for best practices violations"""
        issues = []

        # Check for missing README
        readme_files = [f for f in files if f["name"].lower().startswith("readme")]
        if not readme_files:
            issues.append(
                FileStructureIssue(
                    type="best_practices",
                    severity="medium",
                    file_path=".",
                    description="No README file found",
                    suggestion="Add a README.md file with project description and setup instructions",
                    impact="Poor project documentation and onboarding experience",
                    effort_required="low",
                )
            )

        # Check for missing .gitignore
        gitignore_files = [f for f in files if f["name"] == ".gitignore"]
        if not gitignore_files:
            issues.append(
                FileStructureIssue(
                    type="best_practices",
                    severity="low",
                    file_path=".",
                    description="No .gitignore file found",
                    suggestion="Add a .gitignore file to exclude unnecessary files from version control",
                    impact="Unnecessary files may be tracked in version control",
                    effort_required="low",
                )
            )

        # Check for duplicate file names in different directories
        file_names = {}
        for file_info in files:
            name = file_info["name"]
            if name in file_names:
                file_names[name].append(file_info)
            else:
                file_names[name] = [file_info]

        for name, file_list in file_names.items():
            if len(file_list) > 1 and not name.startswith("."):
                issues.append(
                    FileStructureIssue(
                        type="best_practices",
                        severity="low",
                        file_path=f"Multiple locations: {', '.join(str(f['relative_path']) for f in file_list)}",
                        description=f"Duplicate filename: {name}",
                        suggestion="Consider using more specific names or consolidating files",
                        impact="Potential confusion and maintenance issues",
                        effort_required="low",
                    )
                )

        return issues

    def _generate_structure_recommendations(
        self, issues: List[FileStructureIssue], metrics: FileStructureMetrics
    ) -> List[str]:
        """Generate high-level recommendations based on analysis"""
        recommendations = []

        # Naming recommendations
        if metrics.naming_consistency_score < 70:
            recommendations.append(
                f"Improve naming consistency (current score: {metrics.naming_consistency_score:.1f}%). "
                "Establish and follow a consistent naming convention across the project."
            )

        # Organization recommendations
        if metrics.organization_score < 60:
            recommendations.append(
                f"Improve project organization (current score: {metrics.organization_score:.1f}%). "
                "Consider restructuring directories to follow common conventions."
            )

        # Complexity recommendations
        if metrics.structure_complexity in ["high", "very_high"]:
            recommendations.append(
                "The project structure is complex. Consider simplifying by reducing directory depth "
                "and grouping related files more effectively."
            )

        # Issue-based recommendations
        high_severity_issues = [i for i in issues if i.severity == "high"]
        if high_severity_issues:
            recommendations.append(
                f"Address {len(high_severity_issues)} high-severity structural issues to improve "
                "project maintainability and developer experience."
            )

        # File count recommendations
        if metrics.total_files > 500:
            recommendations.append(
                "Large project detected. Consider implementing module boundaries and "
                "clear separation of concerns to maintain code quality."
            )

        return recommendations

    def _generate_best_practices_suggestions(
        self, files: List[Dict[str, Any]], project_path: Path
    ) -> List[str]:
        """Generate best practices suggestions"""
        suggestions = []

        # Common suggestions based on file analysis
        file_extensions = set(f["suffix"] for f in files)

        if ".py" in file_extensions:
            suggestions.extend(
                [
                    "Follow PEP 8 for Python code organization and naming conventions",
                    "Use __init__.py files to create proper Python packages",
                    "Consider using type hints and docstrings for better code documentation",
                ]
            )

        if any(ext in file_extensions for ext in [".js", ".ts", ".jsx", ".tsx"]):
            suggestions.extend(
                [
                    "Follow JavaScript/TypeScript naming conventions (camelCase for variables, PascalCase for classes)",
                    "Organize components and utilities into separate directories",
                    "Use index files for clean imports and exports",
                ]
            )

        if ".java" in file_extensions:
            suggestions.extend(
                [
                    "Follow Java package naming conventions (reverse domain notation)",
                    "Organize classes by functionality into appropriate packages",
                    "Use Maven or Gradle standard directory layout",
                ]
            )

        # General suggestions
        suggestions.extend(
            [
                "Keep related files together and separate different concerns",
                "Use descriptive directory and file names that reflect their purpose",
                "Maintain consistent indentation and formatting across all files",
                "Document your project structure in README.md for new developers",
            ]
        )

        return suggestions

    async def _get_ai_structure_insights(
        self,
        files: List[Dict[str, Any]],
        metrics: FileStructureMetrics,
        issues: List[FileStructureIssue],
    ) -> Dict[str, Any]:
        """Get AI-powered insights about the project structure"""
        try:
            # Prepare summary for AI analysis
            file_summary = {
                "total_files": len(files),
                "file_types": metrics.file_type_distribution,
                "naming_score": metrics.naming_consistency_score,
                "organization_score": metrics.organization_score,
                "complexity": metrics.structure_complexity,
                "issues_count": len(issues),
                "high_severity_issues": len(
                    [i for i in issues if i.severity == "high"]
                ),
            }

            prompt = f"""
Analyze this project structure and provide expert insights:

Project Metrics:
{json.dumps(file_summary, indent=2)}

Issues Found: {len(issues)} total
- High severity: {len([i for i in issues if i.severity == "high"])}
- Medium severity: {len([i for i in issues if i.severity == "medium"])}
- Low severity: {len([i for i in issues if i.severity == "low"])}

Provide insights on:
1. Overall structure assessment
2. Potential architecture patterns identified
3. Scalability considerations
4. Maintenance implications
5. Developer experience impact
6. Priority improvement areas

Return in JSON format with keys: overall_assessment, architecture_patterns, scalability_notes, maintenance_impact, developer_experience, priority_improvements.
"""

            response = ai_analyzer.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software architect and project structure expert. Always return valid JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1500,
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"error": f"AI analysis failed: {str(e)}"}

    def _static_analyze_file_structure(
        self, file_name: str, code: str, language: str
    ) -> Dict[str, Any]:
        """Static file structure analysis without AI (fallback)"""
        metrics = self._get_file_metrics(file_name, code, language)

        issues = []
        if metrics["lines_of_code"] > 500:
            issues.append("File is very long, consider breaking it down")
        if metrics["functions_count"] > 20:
            issues.append("High number of functions, consider splitting into modules")
        if metrics["complexity_score"] > 15:
            issues.append("High complexity, consider refactoring")

        return {
            "organization_score": 7,
            "naming_score": 8,
            "structure_issues": issues,
            "suggestions": [
                "Consider adding more comments and documentation",
                "Group related functions together",
                "Use consistent naming conventions",
            ],
            "file_metrics": metrics,
            "analysis_type": "static_file_structure",
            "note": "AI analysis not available, showing basic analysis",
        }

    async def _static_optimize_code(
        self, code: str, language: str, optimization_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Static optimization without AI (fallback)"""
        suggestions = []

        if language in self.optimization_patterns:
            patterns = self.optimization_patterns[language]
            focus = optimization_type or "performance"

            if focus in patterns:
                suggestions = patterns[focus]
            else:
                suggestions = patterns.get("performance", [])

        return {
            "optimized_code": code,
            "suggestions": suggestions,
            "analysis_type": "static_optimization",
            "note": "AI analysis not available, showing general suggestions",
        }

    def _static_explain_code(self, code: str, language: str) -> Dict[str, Any]:
        """Static code explanation without AI (fallback)"""
        lines = code.split("\n")
        line_count = len([line for line in lines if line.strip()])

        return {
            "overview": f"This is a {language} code snippet with {line_count} lines of code.",
            "breakdown": "Line-by-line analysis requires AI assistance.",
            "analysis_type": "static_explanation",
            "note": "AI analysis not available for detailed explanation",
        }

    def _static_review_code(self, code: str, language: str) -> Dict[str, Any]:
        """Static code review without AI (fallback)"""
        lines = code.split("\n")
        line_count = len([line for line in lines if line.strip()])

        basic_checks = []
        if line_count > 50:
            basic_checks.append("Function might be too long (>50 lines)")
        if any(len(line) > 120 for line in lines):
            basic_checks.append("Some lines exceed 120 characters")

        return {
            "quality_score": 7,
            "basic_checks": basic_checks,
            "analysis_type": "static_review",
            "note": "AI analysis not available for comprehensive review",
        }


# Global analyzer instance
file_analyzer = FileAnalyzer()


async def analyze_file(request: FileAnalysisRequest) -> FileAnalysisResult:
    """
    Main function to analyze file content

    Args:
        request: File analysis request

    Returns:
        File analysis result
    """
    return await file_analyzer.analyze_file(request)


async def analyze_project_structure(
    request: FileStructureAnalysisRequest,
) -> FileStructureAnalysisResult:
    """
    Main function to analyze project file structure

    Args:
        request: File structure analysis request

    Returns:
        File structure analysis result
    """
    return await file_analyzer.analyze_project_structure(request)
