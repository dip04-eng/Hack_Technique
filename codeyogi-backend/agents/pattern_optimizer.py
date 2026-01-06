import re
import difflib
from typing import Dict, List, Any, Optional
from pathlib import Path


class PatternBasedOptimizer:
    """Pattern-based multi-language code optimizer"""

    def __init__(self):
        self.optimizations = []

    def optimize_code(
        self, source_code: str, language: str = None, file_path: str = None
    ) -> Dict[str, Any]:
        """Main optimization entry point"""
        try:
            if file_path and not language:
                language = self.detect_language(file_path)

            if not language or language == "unknown":
                return {
                    "error": "Unable to detect or unsupported language",
                    "status": "error",
                }

            self.optimizations = []  # Reset optimizations

            # Apply language-specific optimizations
            if language == "python":
                optimized_code = self.optimize_python(source_code)
            elif language in ["c", "cpp"]:
                optimized_code = self.optimize_c_cpp(source_code)
            elif language == "java":
                optimized_code = self.optimize_java(source_code)
            elif language in ["javascript", "typescript"]:
                optimized_code = self.optimize_js_ts(source_code)
            else:
                return {
                    "error": f"Language '{language}' not supported",
                    "status": "error",
                }

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
        }

        return ext_map.get(ext, "unknown")

    def get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        ext_map = {
            "python": "py",
            "c": "c",
            "cpp": "cpp",
            "java": "java",
            "javascript": "js",
            "typescript": "ts",
        }
        return ext_map.get(language, "txt")

    # ===== PYTHON OPTIMIZATIONS =====
    def optimize_python(self, source_code: str) -> str:
        """Python-specific optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            line_optimized = False

            # Optimize range(len()) patterns
            range_len_pattern = r"for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):"
            match = re.search(range_len_pattern, line)
            if match:
                loop_var, list_var = match.groups()
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent
                    + f"# [OPTIMIZED] Changed from range(len({list_var})) to direct iteration"
                )
                new_line = re.sub(
                    range_len_pattern, f"for {loop_var} in {list_var}:", line
                )
                optimized_lines.append(new_line)
                self.optimizations.append(
                    f"Optimized range(len({list_var})) to direct iteration at line {i+1}"
                )
                line_optimized = True

            # Remove dead code (if False)
            elif re.search(r"if\s+False\s*:", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent
                    + "# [OPTIMIZED] Removed dead code (always-false condition)"
                )
                self.optimizations.append(f"Removed dead code (if False) at line {i+1}")
                line_optimized = True

            # Simplify always true conditions
            elif re.search(r"if\s+True\s*:", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "# [OPTIMIZED] Removed always-true if condition"
                )
                self.optimizations.append(
                    f"Simplified always-true condition at line {i+1}"
                )
                line_optimized = True

            # Remove impossible conditions
            elif re.search(r"if\s+\d+\s*>\s*\d+\s*:", line):
                numbers = re.findall(r"\d+", line)
                if len(numbers) >= 2 and int(numbers[0]) <= int(numbers[1]):
                    indent = len(line) - len(line.lstrip())
                    optimized_lines.append(
                        " " * indent + "# [OPTIMIZED] Removed impossible condition"
                    )
                    self.optimizations.append(
                        f"Removed impossible condition at line {i+1}"
                    )
                    line_optimized = True

            if not line_optimized:
                optimized_lines.append(line)

        return "\n".join(optimized_lines)

    # ===== C/C++ OPTIMIZATIONS =====
    def optimize_c_cpp(self, source_code: str) -> str:
        """C/C++ specific optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            line_optimized = False

            # Optimize strlen in loops
            if re.search(r"for\s*\([^;]*;\s*\w+\s*<\s*strlen\(", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "// [OPTIMIZED] Consider caching strlen() result"
                )
                optimized_lines.append(line)
                self.optimizations.append(
                    f"Suggested strlen optimization at line {i+1}"
                )
                line_optimized = True

            # Remove self-assignments
            elif re.search(r"^\s*(\w+)\s*=\s*\1\s*;", line):
                var_match = re.search(r"^\s*(\w+)\s*=\s*\1\s*;", line)
                if var_match:
                    indent = len(line) - len(line.lstrip())
                    optimized_lines.append(
                        " " * indent + "// [OPTIMIZED] Removed self-assignment"
                    )
                    self.optimizations.append(f"Removed self-assignment at line {i+1}")
                    line_optimized = True

            # Suggest const for unchanging variables
            elif re.search(r"^\s*int\s+\w+\s*=\s*\d+\s*;", line) and i < len(lines) - 1:
                var_match = re.search(r"^\s*int\s+(\w+)\s*=", line)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if variable is modified in next few lines
                    is_modified = False
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if re.search(f"{var_name}\\s*=", lines[j]):
                            is_modified = True
                            break

                    if not is_modified:
                        indent = len(line) - len(line.lstrip())
                        optimized_lines.append(
                            " " * indent
                            + "// [OPTIMIZED] Consider using const for unchanging variable"
                        )
                        optimized_lines.append(line)
                        self.optimizations.append(
                            f"Suggested const for variable {var_name} at line {i+1}"
                        )
                        line_optimized = True

            if not line_optimized:
                optimized_lines.append(line)

        return "\n".join(optimized_lines)

    # ===== JAVA OPTIMIZATIONS =====
    def optimize_java(self, source_code: str) -> str:
        """Java-specific optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            line_optimized = False

            # Optimize traditional for loops to enhanced for loops
            if re.search(
                r"for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\.length\s*;\s*\w+\+\+\s*\)",
                line,
            ):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "// [OPTIMIZED] Consider using enhanced for loop"
                )
                optimized_lines.append(line)
                self.optimizations.append(f"Suggested enhanced for loop at line {i+1}")
                line_optimized = True

            # String concatenation in loops
            elif "+=" in line and "String" in line:
                # Check if we're in a loop context
                in_loop = False
                for j in range(max(0, i - 5), i):
                    if "for" in lines[j]:
                        in_loop = True
                        break

                if in_loop:
                    indent = len(line) - len(line.lstrip())
                    optimized_lines.append(
                        " " * indent
                        + "// [OPTIMIZED] Consider using StringBuilder for string concatenation in loops"
                    )
                    optimized_lines.append(line)
                    self.optimizations.append(
                        f"Suggested StringBuilder optimization at line {i+1}"
                    )
                    line_optimized = True

            # Suggest Collections.sort() for array sorting
            elif re.search(r"Arrays\.sort\s*\(", line):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "// [OPTIMIZED] Good use of Arrays.sort()"
                )
                optimized_lines.append(line)
                line_optimized = True

            if not line_optimized:
                optimized_lines.append(line)

        return "\n".join(optimized_lines)

    # ===== JAVASCRIPT/TYPESCRIPT OPTIMIZATIONS =====
    def optimize_js_ts(self, source_code: str) -> str:
        """JavaScript/TypeScript specific optimizations"""
        lines = source_code.split("\n")
        optimized_lines = []

        for i, line in enumerate(lines):
            line_optimized = False

            # Optimize traditional for loops to for...of
            if re.search(
                r"for\s*\(\s*let\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\w+\.length\s*;\s*\w+\+\+\s*\)",
                line,
            ):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent + "// [OPTIMIZED] Consider using for...of loop"
                )
                optimized_lines.append(line)
                self.optimizations.append(f"Suggested for...of loop at line {i+1}")
                line_optimized = True

            # Use const instead of let for non-reassigned variables
            elif re.search(r"^\s*let\s+(\w+)\s*=", line):
                var_match = re.search(r"^\s*let\s+(\w+)\s*=", line)
                if var_match:
                    var_name = var_match.group(1)
                    # Check if variable is reassigned in next few lines
                    is_reassigned = False
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if (
                            re.search(f"{var_name}\\s*=", lines[j])
                            and "===" not in lines[j]
                            and "!==" not in lines[j]
                        ):
                            is_reassigned = True
                            break

                    if not is_reassigned:
                        indent = len(line) - len(line.lstrip())
                        optimized_lines.append(
                            " " * indent
                            + "// [OPTIMIZED] Changed let to const for non-reassigned variable"
                        )
                        new_line = line.replace("let ", "const ")
                        optimized_lines.append(new_line)
                        self.optimizations.append(
                            f"Changed let to const for variable {var_name} at line {i+1}"
                        )
                        line_optimized = True

            # Suggest template literals for string concatenation
            elif "+" in line and '"' in line and "console.log" in line:
                if re.search(r'"\s*\+\s*\w+\s*\+\s*"', line):
                    indent = len(line) - len(line.lstrip())
                    optimized_lines.append(
                        " " * indent
                        + "// [OPTIMIZED] Consider using template literals for string interpolation"
                    )
                    optimized_lines.append(line)
                    self.optimizations.append(
                        f"Suggested template literals at line {i+1}"
                    )
                    line_optimized = True

            # Suggest array methods over traditional loops
            elif re.search(
                r"for\s*\(\s*let\s+\w+\s*=\s*0.*\.push\(", " ".join(lines[i : i + 3])
            ):
                indent = len(line) - len(line.lstrip())
                optimized_lines.append(
                    " " * indent
                    + "// [OPTIMIZED] Consider using array methods like map(), filter(), or reduce()"
                )
                optimized_lines.append(line)
                self.optimizations.append(f"Suggested array methods at line {i+1}")
                line_optimized = True

            if not line_optimized:
                optimized_lines.append(line)

        return "\n".join(optimized_lines)


# Create singleton instance
_pattern_optimizer = PatternBasedOptimizer()


def optimize_pattern_based(
    source_code: str, language: str = None, file_path: str = None
) -> Dict[str, Any]:
    """Optimize code using pattern-based approach"""
    return _pattern_optimizer.optimize_code(source_code, language, file_path)
