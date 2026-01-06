"""
Post-Deploy Failure Root Cause Analysis Agent

Expert DevOps SRE AI agent that performs post-deployment failure analysis.
Identifies root causes by correlating code changes with runtime failures.

Author: CodeYogi Platform
"""

import os
import json
import re
from typing import Dict, Any, Optional
from groq import Groq


class DeployFailureAnalyzer:
    """
    Advanced SRE agent for post-deployment failure root cause analysis.
    
    This agent:
    - Analyzes git diffs between deployments
    - Correlates code changes with runtime failures
    - Identifies root causes using AI-powered pattern recognition
    - Provides actionable fixes with confidence scores
    """
    
    # Common failure patterns for pattern matching
    FAILURE_PATTERNS = {
        "blocking_operations": {
            "keywords": ["sleep(", "time.sleep", "Thread.sleep", "await sleep", "blocking"],
            "impact": "latency / timeout",
            "severity": "high"
        },
        "database_in_loop": {
            "keywords": ["for.*query", "while.*select", "loop.*db", "for.*cursor"],
            "impact": "performance degradation",
            "severity": "critical"
        },
        "new_dependency": {
            "keywords": ["import ", "require(", "from ", "package.json", "requirements.txt"],
            "impact": "startup failure",
            "severity": "high"
        },
        "missing_env_var": {
            "keywords": ["os.getenv", "process.env", "ENV[", "config["],
            "impact": "crash on startup",
            "severity": "critical"
        },
        "sync_to_async": {
            "keywords": ["async def", "await ", "asyncio", "Promise", "async/await"],
            "impact": "request backlog",
            "severity": "medium"
        },
        "memory_intensive": {
            "keywords": ["large array", "buffer", "cache", "in-memory", "load all"],
            "impact": "OOM crash",
            "severity": "critical"
        },
        "file_io_in_request": {
            "keywords": ["open(", "read()", "write()", "file.read", "fs.read"],
            "impact": "slow API response",
            "severity": "medium"
        }
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Deploy Failure Analyzer.
        
        Args:
            api_key: Groq API key. If None, reads from GROQ_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Best model for analytical tasks
    
    def analyze_failure(
        self,
        git_diff: str,
        pipeline_logs: str,
        runtime_logs: str,
        deployment_env: str = "production"
    ) -> Dict[str, Any]:
        """
        Perform root cause analysis on a deployment failure.
        
        Args:
            git_diff: Git diff between last successful and current deployment
            pipeline_logs: CI/CD pipeline logs
            runtime_logs: Production/runtime error logs
            deployment_env: Target environment (production, staging, etc.)
        
        Returns:
            Dict containing root cause analysis with the following keys:
            - summary: One-line explanation
            - root_cause: Detailed explanation
            - affected_file: File that caused the issue
            - affected_line: Line number or function name
            - impact: User-facing impact
            - confidence: Float between 0.0-1.0
            - suggested_fix: Concrete fix recommendation
        """
        # Pre-analyze for known patterns
        pattern_hints = self._detect_patterns(git_diff, runtime_logs)
        
        # Construct expert SRE prompt
        prompt = self._build_analysis_prompt(
            git_diff=git_diff,
            pipeline_logs=pipeline_logs,
            runtime_logs=runtime_logs,
            deployment_env=deployment_env,
            pattern_hints=pattern_hints
        )
        
        # Get AI analysis
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Low temperature for consistent, analytical responses
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and enhance result
            result = self._validate_and_enhance_result(result, pattern_hints)
            
            return result
            
        except Exception as e:
            # Fallback to pattern-based analysis if AI fails
            return self._fallback_analysis(git_diff, runtime_logs, pattern_hints, str(e))
    
    def _get_system_prompt(self) -> str:
        """Generate the system prompt for the AI agent."""
        return """You are an expert DevOps SRE AI agent specializing in Post-Deploy Failure Root Cause Analysis.

CRITICAL RULES:
1. You DO NOT summarize logs - you explain WHY things broke
2. You DO NOT restate errors - you identify ROOT CAUSES
3. You MUST correlate code changes with runtime failures
4. Think like a senior Site Reliability Engineer
5. Prefer CODE CHANGES over infrastructure assumptions
6. Be concise, clear, and confident

ANALYSIS APPROACH:
1. Examine git diff for risky changes
2. Correlate changes with runtime errors
3. Identify the MOST LIKELY root cause
4. Provide concrete, actionable fix

COMMON FAILURE PATTERNS:
- Blocking loops/sleep → latency/timeout
- Database calls in loops → performance degradation
- New dependencies → startup failure
- Missing env variables → crashes
- Heavy computation → CPU spikes
- Async-to-sync conversion → request backlog
- File I/O in request path → slow API
- Memory-intensive operations → OOM

OUTPUT STRICT JSON:
{
  "summary": "One-line explanation",
  "root_cause": "Clear explanation of exact cause",
  "affected_file": "filename",
  "affected_line": "line number or function name",
  "impact": "User-facing impact",
  "confidence": 0.0-1.0,
  "suggested_fix": "Concrete fix"
}

Ask yourself before responding:
- Can a junior dev understand this?
- Does this clearly explain WHY production broke?
- Would a DevOps engineer trust this?"""
    
    def _build_analysis_prompt(
        self,
        git_diff: str,
        pipeline_logs: str,
        runtime_logs: str,
        deployment_env: str,
        pattern_hints: Dict[str, Any]
    ) -> str:
        """Build the analysis prompt with all context."""
        
        # Truncate logs if too long (keep most relevant parts)
        git_diff = self._truncate_smart(git_diff, max_lines=200)
        pipeline_logs = self._truncate_smart(pipeline_logs, max_lines=100)
        runtime_logs = self._truncate_smart(runtime_logs, max_lines=100)
        
        prompt = f"""DEPLOYMENT FAILURE ANALYSIS REQUEST

Environment: {deployment_env}

=== GIT DIFF (Changes Deployed) ===
{git_diff}

=== CI/CD PIPELINE LOGS ===
{pipeline_logs}

=== RUNTIME/PRODUCTION ERROR LOGS ===
{runtime_logs}
"""
        
        if pattern_hints:
            prompt += f"\n=== DETECTED PATTERNS ===\n{json.dumps(pattern_hints, indent=2)}\n"
        
        prompt += """
=== YOUR TASK ===
Analyze the above data and identify the ROOT CAUSE of the deployment failure.

Focus on:
1. What code changed (git diff)
2. What broke in production (runtime logs)
3. The DIRECT correlation between 1 and 2

Respond with STRICT JSON format as specified in your system prompt.
"""
        
        return prompt
    
    def _detect_patterns(self, git_diff: str, runtime_logs: str) -> Dict[str, Any]:
        """
        Pre-analyze code for known failure patterns.
        
        Returns hints that can help the AI focus on likely causes.
        """
        detected = {}
        
        for pattern_name, pattern_info in self.FAILURE_PATTERNS.items():
            matches = []
            for keyword in pattern_info["keywords"]:
                try:
                    # Try as regex pattern first
                    # Check in git diff
                    if re.search(keyword, git_diff, re.IGNORECASE):
                        matches.append(f"Found in code changes: {keyword}")
                    # Check in runtime logs
                    if re.search(keyword, runtime_logs, re.IGNORECASE):
                        matches.append(f"Found in runtime logs: {keyword}")
                except re.error:
                    # If regex fails, treat as literal string
                    escaped_keyword = re.escape(keyword)
                    if re.search(escaped_keyword, git_diff, re.IGNORECASE):
                        matches.append(f"Found in code changes: {keyword}")
                    if re.search(escaped_keyword, runtime_logs, re.IGNORECASE):
                        matches.append(f"Found in runtime logs: {keyword}")
            
            if matches:
                detected[pattern_name] = {
                    "matches": matches,
                    "impact": pattern_info["impact"],
                    "severity": pattern_info["severity"]
                }
        
        return detected
    
    def _truncate_smart(self, text: str, max_lines: int = 100) -> str:
        """
        Intelligently truncate logs while preserving error context.
        """
        if not text:
            return ""
        
        lines = text.split('\n')
        if len(lines) <= max_lines:
            return text
        
        # Keep first 30% and last 70% (errors usually at end)
        split_point = int(max_lines * 0.3)
        header = lines[:split_point]
        footer = lines[-(max_lines - split_point):]
        
        return '\n'.join(header) + '\n\n[... truncated ...]\n\n' + '\n'.join(footer)
    
    def _validate_and_enhance_result(
        self,
        result: Dict[str, Any],
        pattern_hints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate AI response and enhance with pattern data.
        """
        # Ensure all required fields exist
        required_fields = [
            "summary", "root_cause", "affected_file",
            "affected_line", "impact", "confidence", "suggested_fix"
        ]
        
        for field in required_fields:
            if field not in result:
                result[field] = "Unknown - analysis incomplete"
        
        # Ensure confidence is a float between 0 and 1
        try:
            confidence = float(result.get("confidence", 0.5))
            result["confidence"] = max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            result["confidence"] = 0.5
        
        # Add detected patterns to metadata
        if pattern_hints:
            result["detected_patterns"] = pattern_hints
        
        return result
    
    def _fallback_analysis(
        self,
        git_diff: str,
        runtime_logs: str,
        pattern_hints: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """
        Provide basic pattern-based analysis if AI call fails.
        """
        # Use detected patterns to make a best guess
        if pattern_hints:
            # Get highest severity pattern
            critical_patterns = [
                name for name, info in pattern_hints.items()
                if info["severity"] == "critical"
            ]
            
            if critical_patterns:
                pattern_name = critical_patterns[0]
                pattern_data = pattern_hints[pattern_name]
                
                return {
                    "summary": f"Deployment likely failed due to {pattern_name.replace('_', ' ')}",
                    "root_cause": f"Pattern detection identified {pattern_name.replace('_', ' ')} in code changes. {pattern_data['matches'][0]}",
                    "affected_file": "See git diff",
                    "affected_line": "Multiple locations",
                    "impact": pattern_data["impact"],
                    "confidence": 0.6,
                    "suggested_fix": f"Review code changes for {pattern_name.replace('_', ' ')} and apply standard remediation.",
                    "fallback_mode": True,
                    "ai_error": error
                }
        
        # Ultimate fallback
        return {
            "summary": "Unable to determine root cause automatically",
            "root_cause": "AI analysis failed and no clear patterns detected. Manual investigation required.",
            "affected_file": "Unknown",
            "affected_line": "Unknown",
            "impact": "Service degradation or failure",
            "confidence": 0.3,
            "suggested_fix": "Manually review git diff and correlate with runtime errors. Consider rollback.",
            "fallback_mode": True,
            "ai_error": error
        }
    
    def analyze_from_json(self, input_json: str) -> Dict[str, Any]:
        """
        Analyze failure from JSON string input.
        
        Args:
            input_json: JSON string with keys: git_diff, pipeline_logs, runtime_logs, deployment_env
        
        Returns:
            Analysis result dictionary
        """
        try:
            data = json.loads(input_json)
            return self.analyze_failure(
                git_diff=data.get("git_diff", ""),
                pipeline_logs=data.get("pipeline_logs", ""),
                runtime_logs=data.get("runtime_logs", ""),
                deployment_env=data.get("deployment_env", "production")
            )
        except json.JSONDecodeError as e:
            return {
                "summary": "Invalid input format",
                "root_cause": f"Failed to parse input JSON: {str(e)}",
                "affected_file": "N/A",
                "affected_line": "N/A",
                "impact": "Analysis not performed",
                "confidence": 0.0,
                "suggested_fix": "Provide valid JSON input with required fields"
            }
    
    def analyze_from_file(self, input_file: str) -> Dict[str, Any]:
        """
        Analyze failure from JSON file.
        
        Args:
            input_file: Path to JSON file containing analysis inputs
        
        Returns:
            Analysis result dictionary
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                return self.analyze_from_json(f.read())
        except FileNotFoundError:
            return {
                "summary": "Input file not found",
                "root_cause": f"File {input_file} does not exist",
                "affected_file": "N/A",
                "affected_line": "N/A",
                "impact": "Analysis not performed",
                "confidence": 0.0,
                "suggested_fix": "Provide valid file path"
            }
        except Exception as e:
            return {
                "summary": "Error reading input file",
                "root_cause": str(e),
                "affected_file": "N/A",
                "affected_line": "N/A",
                "impact": "Analysis not performed",
                "confidence": 0.0,
                "suggested_fix": "Check file permissions and format"
            }


def main():
    """Demo usage of the Deploy Failure Analyzer."""
    
    # Example failure scenario
    sample_input = {
        "git_diff": """
diff --git a/api/users.py b/api/users.py
index 123abc..456def 100644
--- a/api/users.py
+++ b/api/users.py
@@ -10,7 +10,12 @@ def get_users():
     try:
         users = []
         for user_id in range(1, 1000):
-            users.append(fetch_user_cache(user_id))
+            # Changed to fetch from database for accuracy
+            db_user = db.query(f"SELECT * FROM users WHERE id={user_id}")
+            users.append(db_user)
+            # Add small delay for rate limiting
+            time.sleep(0.1)
         return jsonify(users)
     except Exception as e:
""",
        "pipeline_logs": """
[2026-01-05 10:30:15] Starting deployment...
[2026-01-05 10:30:45] Tests passed ✓
[2026-01-05 10:31:00] Build completed ✓
[2026-01-05 10:31:30] Deploying to production...
[2026-01-05 10:32:00] Deployment successful ✓
""",
        "runtime_logs": """
[2026-01-05 10:35:22] ERROR: Request timeout on /api/users
[2026-01-05 10:35:45] WARNING: High database connection pool usage (95%)
[2026-01-05 10:36:10] ERROR: Request timeout on /api/users
[2026-01-05 10:36:30] CRITICAL: API response time: 45s (threshold: 2s)
[2026-01-05 10:37:00] ERROR: 503 Service Unavailable - /api/users
""",
        "deployment_env": "production"
    }
    
    # Initialize analyzer
    analyzer = DeployFailureAnalyzer(api_key=os.getenv("GROQ_API_KEY", "your_groq_api_key_here"))
    
    # Perform analysis
    print("🔍 Analyzing deployment failure...\n")
    result = analyzer.analyze_failure(**sample_input)
    
    # Display results
    print("=" * 70)
    print("POST-DEPLOY FAILURE ANALYSIS REPORT")
    print("=" * 70)
    print(json.dumps(result, indent=2))
    print("=" * 70)


if __name__ == "__main__":
    main()
