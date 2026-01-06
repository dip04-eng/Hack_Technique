"""
Rollback Intelligence Agent

Provides intelligent, human-friendly rollback capabilities:
- Fetches recent deployments/commits
- AI-powered safety analysis
- Number-based selection (no commit hashes)
- One-click rollback execution
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import requests
from github import Github
import groq


class RollbackIntelligenceAgent:
    """
    Intelligent rollback system that simplifies deployment rollback with AI safety checks.
    
    Key Features:
    - Number-based commit selection
    - AI analysis for rollback safety
    - Automatic best candidate recommendation
    - Safe rollback execution
    """
    
    def __init__(self, github_token: Optional[str] = None, groq_api_key: Optional[str] = None):
        """
        Initialize Rollback Intelligence Agent.
        
        Args:
            github_token: GitHub personal access token
            groq_api_key: Groq API key for AI analysis
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        
        if not self.github_token:
            raise ValueError("GitHub token is required")
        
        self.github_client = Github(self.github_token)
        
        if self.groq_api_key:
            self.groq_client = groq.Client(api_key=self.groq_api_key)
        else:
            self.groq_client = None
    
    def get_rollback_candidates(
        self, 
        repo_owner: str, 
        repo_name: str,
        branch: str = "main",
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch recent commits as numbered rollback candidates.
        
        Args:
            repo_owner: GitHub repository owner
            repo_name: Repository name
            branch: Branch to fetch commits from
            limit: Number of recent commits to fetch
        
        Returns:
            Dictionary with numbered candidates and AI recommendation
        """
        try:
            # Get repository
            repo = self.github_client.get_repo(f"{repo_owner}/{repo_name}")
            
            # Fetch recent commits
            commits = repo.get_commits(sha=branch)[:limit]
            
            # Convert to numbered candidates
            candidates = []
            for idx, commit in enumerate(commits, start=1):
                commit_data = {
                    "number": idx,
                    "sha": commit.sha,
                    "short_sha": commit.sha[:7],
                    "message": commit.commit.message.split('\n')[0][:100],  # First line, max 100 chars
                    "author": commit.commit.author.name,
                    "author_email": commit.commit.author.email,
                    "timestamp": commit.commit.author.date.isoformat(),
                    "timestamp_readable": self._format_timestamp(commit.commit.author.date),
                    "is_current": idx == 1,  # First commit is current deployment
                    "files_changed": commit.stats.total,
                    "additions": commit.stats.additions,
                    "deletions": commit.stats.deletions,
                }
                
                # Check if commit has deployment info (skip to avoid timeout - can be slow)
                # This is optional and removed to speed up the response
                commit_data["deployment_status"] = "unknown"  # Default to unknown for faster response
                
                candidates.append(commit_data)
            
            # AI analysis for best rollback candidate (with timeout handling)
            ai_recommendation = None
            if self.groq_client:
                try:
                    import signal
                    
                    # Wrap AI analysis with timeout
                    def timeout_handler(signum, frame):
                        raise TimeoutError("AI analysis timeout")
                    
                    # Skip signal on Windows (not supported)
                    if hasattr(signal, 'SIGALRM'):
                        signal.signal(signal.SIGALRM, timeout_handler)
                        signal.alarm(15)  # 15 second timeout
                    
                    ai_recommendation = self._analyze_best_candidate(candidates, repo_owner, repo_name)
                    
                    if hasattr(signal, 'SIGALRM'):
                        signal.alarm(0)  # Cancel alarm
                except (TimeoutError, Exception) as e:
                    print(f"AI analysis skipped or failed: {e}")
                    ai_recommendation = None
            
            return {
                "success": True,
                "repository": f"{repo_owner}/{repo_name}",
                "branch": branch,
                "total_candidates": len(candidates),
                "candidates": candidates,
                "ai_recommendation": ai_recommendation,
                "current_commit": candidates[0] if candidates else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _format_timestamp(self, dt: datetime) -> str:
        """
        Format timestamp in human-readable format.
        
        Args:
            dt: Datetime object
        
        Returns:
            Human-readable time string (e.g., "2 hours ago", "3 days ago")
        """
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff < timedelta(minutes=1):
            return "just now"
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff < timedelta(days=7):
            days = int(diff.total_seconds() / 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
        elif diff < timedelta(days=30):
            weeks = int(diff.total_seconds() / 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = int(diff.total_seconds() / 2592000)
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    def _analyze_best_candidate(
        self, 
        candidates: List[Dict[str, Any]],
        repo_owner: str,
        repo_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Use AI to analyze and recommend the best rollback candidate.
        
        Args:
            candidates: List of commit candidates
            repo_owner: Repository owner
            repo_name: Repository name
        
        Returns:
            AI recommendation with safety analysis
        """
        if not self.groq_client or len(candidates) < 2:
            return None
        
        try:
            # Prepare context for AI
            candidates_summary = "\n".join([
                f"#{c['number']}: {c['message']} by {c['author']} ({c['timestamp_readable']}) - "
                f"{c['files_changed']} files changed (+{c['additions']}/-{c['deletions']}) - "
                f"Status: {c.get('deployment_status', 'unknown')}"
                for c in candidates[:6]  # Analyze top 6 to keep context manageable
            ])
            
            prompt = f"""You are an expert DevOps engineer analyzing deployment rollback candidates.

Repository: {repo_owner}/{repo_name}

Recent Commits (numbered for rollback):
{candidates_summary}

Analyze these commits and provide:
1. The BEST rollback candidate number (if rollback is needed)
2. Safety level: SAFE, CAUTION, or RISKY
3. Brief reason (max 100 chars)
4. Any warnings about the rollback

Consider:
- Commit #1 is the CURRENT deployment (can't rollback to itself)
- Prefer recent, stable commits with successful deployments
- Warn if commit is very old (>7 days)
- Warn if large code changes (high file count/line changes)
- Warn if unknown deployment status

Respond in this EXACT format:
RECOMMENDED: [number]
SAFETY: [SAFE/CAUTION/RISKY]
REASON: [brief reason]
WARNING: [warning message or NONE]
"""
            
            # Set a shorter timeout for AI analysis to prevent hanging
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150,  # Reduced for faster response
                timeout=10.0  # 10 second timeout
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Parse AI response
            lines = ai_response.split('\n')
            recommendation = {}
            
            for line in lines:
                if line.startswith("RECOMMENDED:"):
                    try:
                        num_str = line.split(':')[1].strip()
                        recommendation["recommended_number"] = int(''.join(filter(str.isdigit, num_str)))
                    except:
                        pass
                elif line.startswith("SAFETY:"):
                    recommendation["safety_level"] = line.split(':')[1].strip()
                elif line.startswith("REASON:"):
                    recommendation["reason"] = line.split(':', 1)[1].strip()
                elif line.startswith("WARNING:"):
                    warning = line.split(':', 1)[1].strip()
                    recommendation["warning"] = None if warning == "NONE" else warning
            
            # Get the recommended candidate details
            if "recommended_number" in recommendation:
                rec_num = recommendation["recommended_number"]
                if 1 <= rec_num <= len(candidates):
                    recommendation["recommended_commit"] = candidates[rec_num - 1]
            
            return recommendation if recommendation else None
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return None
    
    def analyze_rollback_safety(
        self,
        repo_owner: str,
        repo_name: str,
        rollback_number: int,
        candidates: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform detailed safety analysis for a specific rollback candidate.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            rollback_number: The candidate number to analyze
            candidates: List of available candidates
        
        Returns:
            Safety analysis results
        """
        if rollback_number < 1 or rollback_number > len(candidates):
            return {
                "safe": False,
                "error": f"Invalid rollback number. Must be between 1 and {len(candidates)}"
            }
        
        if rollback_number == 1:
            return {
                "safe": False,
                "error": "Cannot rollback to current deployment (commit #1)"
            }
        
        target = candidates[rollback_number - 1]
        
        # Safety checks
        warnings = []
        risk_level = "SAFE"
        
        # Check 1: Age of commit
        commit_time = datetime.fromisoformat(target['timestamp'].replace('Z', '+00:00'))
        age_days = (datetime.now(commit_time.tzinfo) - commit_time).days
        
        if age_days > 30:
            warnings.append(f"Commit is {age_days} days old - may be outdated")
            risk_level = "RISKY"
        elif age_days > 7:
            warnings.append(f"Commit is {age_days} days old")
            risk_level = "CAUTION"
        
        # Check 2: Large changes
        if target['files_changed'] > 50:
            warnings.append(f"Large change: {target['files_changed']} files modified")
            risk_level = "CAUTION" if risk_level == "SAFE" else "RISKY"
        
        # Check 3: Deployment status
        if target.get('deployment_status') == 'failure':
            warnings.append("This commit had a failed deployment")
            risk_level = "RISKY"
        elif target.get('deployment_status') == 'unknown':
            warnings.append("Deployment status unknown")
        
        return {
            "safe": risk_level == "SAFE",
            "risk_level": risk_level,
            "target_commit": target,
            "warnings": warnings,
            "age_days": age_days,
            "requires_confirmation": risk_level in ["CAUTION", "RISKY"]
        }
    
    def execute_rollback(
        self,
        repo_owner: str,
        repo_name: str,
        rollback_number: int,
        branch: str = "main",
        create_rollback_commit: bool = True,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Execute rollback to the specified commit number.
        
        This performs a SAFE rollback by creating a new commit that reverts to the target state,
        rather than destructively rewriting history.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            rollback_number: The candidate number to rollback to
            branch: Branch to rollback
            create_rollback_commit: If True, creates a revert commit; if False, returns instructions
            force: Skip safety checks (use with caution)
        
        Returns:
            Rollback execution results
        """
        try:
            # Get candidates first
            candidates_result = self.get_rollback_candidates(repo_owner, repo_name, branch)
            
            if not candidates_result.get("success"):
                return candidates_result
            
            candidates = candidates_result["candidates"]
            
            # Validate rollback number
            if rollback_number < 1 or rollback_number > len(candidates):
                return {
                    "success": False,
                    "error": f"Invalid rollback number. Must be between 1 and {len(candidates)}"
                }
            
            if rollback_number == 1:
                return {
                    "success": False,
                    "error": "Cannot rollback to current deployment (commit #1). Already on this version."
                }
            
            # Safety check (unless forced)
            if not force:
                safety = self.analyze_rollback_safety(repo_owner, repo_name, rollback_number, candidates)
                if not safety["safe"] and safety.get("requires_confirmation"):
                    return {
                        "success": False,
                        "requires_confirmation": True,
                        "safety_analysis": safety,
                        "message": "This rollback requires confirmation due to safety concerns"
                    }
            
            target_commit = candidates[rollback_number - 1]
            
            # Execute rollback
            repo = self.github_client.get_repo(f"{repo_owner}/{repo_name}")
            
            if create_rollback_commit:
                # Create a rollback by creating a new branch and PR
                # This is safer and allows review before merging
                
                current_sha = candidates[0]["sha"]
                target_sha = target_commit["sha"]
                
                # Create unique rollback branch name
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                rollback_branch = f"rollback/to-commit-{rollback_number}-{timestamp}"
                
                # Create rollback message
                rollback_msg = f"""Rollback to commit #{rollback_number}

Target: {target_commit['short_sha']} - {target_commit['message']}
Author: {target_commit['author']}
Reason: Manual rollback via CodeYogi Rollback Intelligence

This commit reverts changes made after {target_commit['timestamp_readable']}
"""
                
                try:
                    # Use PyGithub's API to create a proper revert
                    # Get the current HEAD of the base branch
                    base_branch_obj = repo.get_branch(branch)
                    base_sha = base_branch_obj.commit.sha
                    
                    # Create new branch from current HEAD (not from target commit)
                    new_ref = repo.create_git_ref(
                        ref=f"refs/heads/{rollback_branch}",
                        sha=base_sha  # Start from current HEAD
                    )
                    
                    # Get the tree of the target commit (what we want to revert to)
                    target_tree = repo.get_commit(target_sha).commit.tree
                    
                    # Create a new commit on the rollback branch with the target tree
                    # This effectively "reverts" to the target state
                    new_commit = repo.create_git_commit(
                        message=rollback_msg,
                        tree=target_tree,
                        parents=[repo.get_git_commit(base_sha)]
                    )
                    
                    # Update the branch reference to point to the new commit
                    new_ref.edit(sha=new_commit.sha, force=True)
                    
                    print(f"[SUCCESS] Created rollback branch with revert commit")
                    
                    # Create Pull Request
                    pr = repo.create_pull(
                        title=f"🔄 Rollback to commit #{rollback_number} ({target_commit['short_sha']})",
                        body=f"""## Rollback Information

**Target Commit:** `{target_commit['short_sha']}`  
**Message:** {target_commit['message']}  
**Author:** {target_commit['author']}  
**Date:** {target_commit['timestamp_readable']}  

### Changes
- **Files Changed:** {target_commit['files_changed']}
- **Additions:** +{target_commit['additions']}
- **Deletions:** -{target_commit['deletions']}

### What This PR Does
This PR reverts the codebase to the state of commit `{target_commit['short_sha']}`, effectively undoing all changes made after that point.

### How to Complete the Rollback
1. ✅ Review the changes in the "Files changed" tab
2. ✅ Merge this PR to apply the rollback
3. 🚀 Your deployment will automatically use the reverted code

### Git Instructions (if you want to do it manually)
```bash
git checkout {branch}
git revert --no-commit {target_sha}..{base_sha}
git commit -m "Rollback via CodeYogi"
git push origin {branch}
```

---
*Generated by CodeYogi Rollback Intelligence*
""",
                        head=rollback_branch,
                        base=branch
                    )
                    
                    return {
                        "success": True,
                        "execution_method": "pull_request",
                        "target_commit": target_commit,
                        "current_commit": candidates[0],
                        "rollback_number": rollback_number,
                        "message": f"Rollback Pull Request created successfully!",
                        "pull_request": {
                            "number": pr.number,
                            "url": pr.html_url,
                            "title": pr.title,
                            "branch": rollback_branch,
                            "state": pr.state
                        },
                        "next_steps": [
                            f"✅ Pull Request #{pr.number} created",
                            f"🔗 Review at: {pr.html_url}",
                            "👀 Review the changes",
                            "✅ Merge the PR when ready",
                            "🚀 Deployment will trigger automatically"
                        ]
                    }
                except Exception as pr_error:
                    # If PR creation fails, log the error and return details
                    error_msg = str(pr_error)
                    print(f"[ERROR] Failed to create PR: {error_msg}")
                    
                    # Alternative approach: Create instructions for manual PR with comparison link
                    comparison_url = f"https://github.com/{repo_owner}/{repo_name}/compare/{target_commit['short_sha']}...{branch}"
                    pr_url = f"https://github.com/{repo_owner}/{repo_name}/compare/{branch}...{target_commit['short_sha']}?expand=1&title=Rollback%20to%20commit%20%23{rollback_number}&body=Rollback%20via%20CodeYogi"
                    
                    return {
                        "success": True,
                        "execution_method": "manual_pr",
                        "target_commit": target_commit,
                        "current_commit": candidates[0],
                        "rollback_number": rollback_number,
                        "message": f"Automatic PR creation encountered an issue. Please create the PR manually.",
                        "manual_pr_link": pr_url,
                        "comparison_link": comparison_url,
                        "git_instructions": {
                            "commands": [
                                f"# Option 1: Via GitHub Web Interface",
                                f"# Click the 'Create PR' button below",
                                f"",
                                f"# Option 2: Via Git Commands",
                                f"git fetch origin",
                                f"git checkout {branch}",
                                f"git checkout -b {rollback_branch}",
                                f"git reset --hard {target_sha}",
                                f"git push -f origin {rollback_branch}",
                                f"# Then create PR: {pr_url}"
                            ],
                            "description": "Choose one of the methods below to create the rollback PR"
                        },
                        "next_steps": [
                            "⚠️ Automatic PR creation failed due to API limitations",
                            f"🔗 Click 'Create PR Manually' button below",
                            "📝 Review and submit the PR on GitHub",
                            "✅ Merge when ready"
                        ],
                        "error_details": error_msg,
                        "repository_url": f"https://github.com/{repo_owner}/{repo_name}"
                    }
            else:
                # Return rollback plan without execution
                return {
                    "success": True,
                    "execution_method": "plan_only",
                    "target_commit": target_commit,
                    "rollback_number": rollback_number,
                    "message": "Rollback plan generated (not executed)",
                    "plan": {
                        "action": "rollback",
                        "from_commit": candidates[0]["short_sha"],
                        "to_commit": target_commit["short_sha"],
                        "commits_to_revert": rollback_number - 1
                    }
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def trigger_deployment_workflow(
        self,
        repo_owner: str,
        repo_name: str,
        target_sha: str,
        workflow_file: str = "deploy.yml"
    ) -> Dict[str, Any]:
        """
        Trigger GitHub Actions workflow for deployment of specific commit.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            target_sha: Commit SHA to deploy
            workflow_file: Workflow file name
        
        Returns:
            Workflow trigger results
        """
        try:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_file}/dispatches"
            
            headers = {
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "ref": target_sha
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": "Deployment workflow triggered successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to trigger workflow: {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
