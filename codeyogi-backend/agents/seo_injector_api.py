"""
Alternative SEO optimizer using pure GitHub API (no git commands)
"""
import os
from typing import Dict, Any, Optional
from github import Github, GithubException
from datetime import datetime
import json
from agents.seo_injector import (
    parse_github_url,
    analyze_repository_content,
    generate_repository_seo_metadata,
    create_seo_optimized_readme,
)


def optimize_seo_via_api(
    github_url: str,
    github_token: str,
    branch_name: Optional[str] = None,
    model: str = "llama-3.3-70b-versatile",
) -> Dict[str, Any]:
    """
    Optimize repository SEO using GitHub API directly (no git clone)
    
    Args:
        github_url: GitHub repository URL
        github_token: GitHub personal access token
        branch_name: Optional branch name
        model: AI model to use
        
    Returns:
        Result dictionary with success status and PR details
    """
    try:
        # Parse GitHub URL
        print(f"[INFO] Starting API-based SEO optimization for: {github_url}")
        repo_info = parse_github_url(github_url)
        print(f"[INFO] Repository: {repo_info['owner']}/{repo_info['repo_name']}")
        
        # Initialize GitHub client
        g = Github(github_token)
        repo = g.get_repo(f"{repo_info['owner']}/{repo_info['repo_name']}")
        
        # Get default branch
        default_branch = repo.default_branch
        print(f"[INFO] Default branch: {default_branch}")
        
        # Get README content for analysis
        try:
            readme = repo.get_readme()
            readme_content = readme.decoded_content.decode('utf-8')
        except:
            readme_content = f"# {repo.name}\n\n{repo.description or 'Repository'}"
        
        # Create simple analysis
        repo_analysis = {
            "readme_content": readme_content,
            "combined_content": f"Repository: {repo.name}\nDescription: {repo.description}\nContent: {readme_content}",
        }
        
        # Generate SEO metadata
        print("[INFO] Generating SEO metadata...")
        seo_metadata = generate_repository_seo_metadata(repo_analysis, model=model)
        
        if "error" in seo_metadata:
            return {"success": False, "error": seo_metadata["error"]}
        
        print(f"[INFO] Generated SEO metadata:")
        print(f"  Title: {seo_metadata.get('title', 'N/A')}")
        print(f"  Description: {seo_metadata.get('description', 'N/A')}")
        
        # Create new README content
        new_readme_content = create_seo_optimized_readme(
            repo_analysis, seo_metadata, repo_info
        )
        
        # Create metadata file content
        metadata_content = json.dumps({
            "generated_at": datetime.now().isoformat(),
            "metadata": seo_metadata,
            "generated_by": "CodeYogi SEO Optimizer"
        }, indent=2)
        
        # Create unique branch name
        if not branch_name:
            branch_name = f"seo-optimization-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        print(f"[INFO] Creating branch: {branch_name}")
        
        # Get the base branch reference
        base_ref = repo.get_git_ref(f"heads/{default_branch}")
        base_sha = base_ref.object.sha
        
        # Create new branch
        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_sha)
            print(f"[SUCCESS] Branch created: {branch_name}")
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                print(f"[INFO] Branch {branch_name} already exists, using it")
            else:
                raise
        
        # Update README.md on new branch
        try:
            readme_file = repo.get_contents("README.md", ref=branch_name)
            repo.update_file(
                "README.md",
                f"feat: Update README with SEO optimization",
                new_readme_content,
                readme_file.sha,
                branch=branch_name
            )
            print("[SUCCESS] Updated README.md")
        except:
            # README doesn't exist, create it
            repo.create_file(
                "README.md",
                f"feat: Add SEO-optimized README",
                new_readme_content,
                branch=branch_name
            )
            print("[SUCCESS] Created README.md")
        
        # Create .seo-metadata.json on new branch
        try:
            repo.create_file(
                ".seo-metadata.json",
                f"feat: Add SEO metadata",
                metadata_content,
                branch=branch_name
            )
            print("[SUCCESS] Created .seo-metadata.json")
        except GithubException as e:
            print(f"[WARNING] Could not create metadata file: {e}")
        
        # Create Pull Request
        print("[INFO] Creating pull request...")
        pr = repo.create_pull(
            title="🚀 SEO Optimization: Enhanced README and Metadata",
            body=f"""## 🎯 SEO Optimization Summary

This pull request adds comprehensive SEO improvements to enhance the repository's discoverability.

### ✨ Changes Made

- **Enhanced README**: SEO-optimized content with keywords and descriptions
- **Metadata File**: Added `.seo-metadata.json` with structured SEO data

### 📊 Generated SEO Metadata

**Title:** {seo_metadata.get('title', 'N/A')}  
**Description:** {seo_metadata.get('description', 'N/A')}  
**Keywords:** {', '.join(seo_metadata.get('keywords', []))}

### 🔍 SEO Benefits

- ✅ Improved search engine visibility
- ✅ Better social media sharing
- ✅ Clear project description
- ✅ Keyword optimization

---
*Generated by CodeYogi SEO Optimizer*
""",
            head=branch_name,
            base=default_branch
        )
        
        print(f"[SUCCESS] Pull Request created: {pr.html_url}")
        
        return {
            "success": True,
            "repository": f"{repo_info['owner']}/{repo_info['repo_name']}",
            "seo_metadata": seo_metadata,
            "modified_files": 2,
            "html_files_processed": 0,
            "branch_name": branch_name,
            "pull_request_url": pr.html_url,
            "pull_request_number": pr.number,
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        print(f"[ERROR] API-based SEO optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
