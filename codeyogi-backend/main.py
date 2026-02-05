import sys
import os
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, Header, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import logging

from agents import (
    repo_analyzer,
    workflow_optimizer,
    repo_description_agent,
    file_analyzer,
    multi_language_optimizer,
    seo_injector,
    readme_generator,
)
from models.schemas import (
    RepoAnalysisRequest,
    RepoAnalysisResult,
    RepoDescriptionRequest,
    RepoDescriptionResult,
    FileAnalysisRequest,
    FileAnalysisResult,
    FileStructureAnalysisRequest,
    FileStructureAnalysisResult,
    WorkflowOptimizationWithDeploymentRequest,
    WorkflowOptimizationWithDeploymentResult,
    RepoStructureAnalysisRequest,
    RepoStructureAnalysisResult,
    QuickStructureCheckRequest,
    QuickStructureCheckResult,
    GitHubOptimizationRequest,
    GitHubOptimizationResult,
    GitHubOptimizationPRRequest,
    GitHubOptimizationPRResult,
    FileOptimizationResult,
    SEOOptimizationRequest,
    SEOOptimizationResult,
    SEOAnalysisRequest,
    SEOAnalysisResult,
    SEOMetadata,
    ReadmeGeneratorRequest,
    ReadmeGeneratorResult,
    ReadmeAnalysisRequest,
    ReadmeAnalysisResult,
    ReadmeContent,
)
from models.events import GitHubWebhookPayload, RepositoryState, EventProcessingResult
from core.event_manager import event_manager
from utils.github_ops import check_for_new_push, get_github_token
from utils.pr_creator import GitHubPRCreator
from services.github_structure_service import structure_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CodeYogi Backend",
    description="AI-powered agentic repository monitoring and optimization",
    version="2.0.0",
)
origins = [
    "http://localhost",
    "http://localhost:5173",  # If your frontend is on React dev server
    "https://code-yogi-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins (can be ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods like GET, POST, etc.
    allow_headers=["*"],  # Allows all headers
)


class WorkflowOptimizationRequest(BaseModel):
    repo_url: str
    github_token: str = None
    custom_input: Optional[str] = None


class RepoRegistrationRequest(BaseModel):
    repo_url: str
    user_id: str
    github_token: Optional[str] = None


class UserActionRequest(BaseModel):
    repo_url: str
    user_id: str
    github_token: Optional[str] = None


@app.get("/")
def root():
    return {
        "message": "CodeYogi is meditating 🧘‍♂️ - Agentic AI System Active",
        "version": "2.0.0",
        "endpoints": {
            "analysis": "/analyze/",
            "workflow_optimization": "/optimize-workflow/",
            "workflow_optimization_with_deployment": "/optimize-workflow-deployment/",
            "repository_description": "/describe-repository/",
            "file_analysis": "/analyze-file/",
            "file_structure_analysis": "/analyze-file-structure/",
            "github_structure_analysis": "/analyze-github-structure/",
            "quick_structure_check": "/quick-structure-check/",
            "github_code_optimization": {
                "analyze": "/analyze-github-code/",
                "create_pr": "/create-optimization-pr/",
            },
            "seo_optimization": {
                "analyze": "/seo/analyze/",
                "optimize": "/seo/optimize/",
                "get_metadata": "/seo/metadata/{owner}/{repo}",
            },
            "readme_generator": {
                "analyze": "/readme/analyze/",
                "generate": "/readme/generate/",
                "get_current": "/readme/current/{owner}/{repo}",
            },
            "agentic_monitoring": {
                "register": "/repos/register",
                "status": "/repos/{owner}/{repo}/status",
                "optimize": "/repos/optimize-workflow",
                "analyze": "/repos/analyze",
                "deploy": "/repos/deploy",
                "describe": "/repos/describe",
            },
        },
        "documentation": {
            "workflow_optimization_deployment": "/docs - See WORKFLOW_OPTIMIZATION_DEPLOYMENT.md",
            "agentic_system": "See AGENTIC_SYSTEM.md",
            "file_analyzer": "See FILE_ANALYZER.md",
            "github_optimization": "New GitHub code optimization features with AI-powered suggestions",
        },
    }


# ========== ORIGINAL ENDPOINTS (Backward Compatible) ==========


@app.post("/analyze/", response_model=RepoAnalysisResult)
async def analyze_repo(request: RepoAnalysisRequest):
    """
    Analyze a GitHub repository for structure optimization and cleanup suggestions
    """
    try:
        result = await repo_analyzer.analyze(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/optimize-workflow/")
async def optimize_workflow(request: WorkflowOptimizationRequest):
    """
    Analyze a GitHub repository and generate optimized CI/CD workflow
    """
    try:
        result = await workflow_optimizer.optimize(
            request.repo_url, custom_input=request.custom_input
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/optimize-workflow-deployment/",
    response_model=WorkflowOptimizationWithDeploymentResult,
)
async def workflow_optimization_with_deployment(
    request: WorkflowOptimizationWithDeploymentRequest,
):
    """
    Analyze a GitHub repository, generate optimized CI/CD workflow, and automatically create a PR

    This endpoint:
    1. Analyzes the repository structure and existing workflows
    2. Generates an optimized GitHub Actions workflow using AI
    3. Creates a new branch with the optimized workflow
    4. Automatically submits a pull request with detailed improvements

    The PR will include:
    - Comprehensive workflow optimization analysis
    - AI-generated improvements and recommendations
    - Performance enhancement details
    - Security best practices implementation
    """
    try:
        # Accept custom_input if present in request (for backward compatibility, add to model if needed)
        custom_input = getattr(request, "custom_input", None)
        result = await workflow_optimizer.optimize_and_deploy(
            repo_url=request.repo_url,
            github_token=request.github_token,
            branch_name=request.branch_name,
            workflow_path=request.workflow_path,
            commit_message=request.commit_message,
            auto_merge=request.auto_merge,
            custom_input=custom_input,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/describe-repository/", response_model=RepoDescriptionResult)
async def describe_repository(request: RepoDescriptionRequest):
    """
    Analyze a GitHub repository and provide comprehensive description with flowchart

    This endpoint analyzes the codebase structure, tech stack, architecture,
    and generates a detailed description along with a project flowchart.
    """
    try:
        result = await repo_description_agent.analyze_repository_description(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze-file/", response_model=FileAnalysisResult)
async def analyze_file_endpoint(request: FileAnalysisRequest):
    """
    Analyze a file or selected code portion for optimization, explanation, refactoring, or review

    This endpoint allows you to:
    - Optimize code for performance, readability, or security
    - Get detailed explanations of how code works
    - Refactor code for better structure and maintainability
    - Perform comprehensive code reviews

    You can analyze either the entire file or just a selected portion.
    """
    try:
        result = await file_analyzer.analyze_file(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/analyze-file-structure/", response_model=FileStructureAnalysisResult)
async def analyze_file_structure_endpoint(request: FileStructureAnalysisRequest):
    """
    Analyze project file structure and suggest improvements

    This endpoint analyzes the overall organization and structure of your project files and provides:
    - File structure metrics and analysis
    - Naming convention consistency checks
    - Organization and best practices assessment
    - Specific improvement suggestions
    - AI-powered insights about project architecture

    Focus areas can include:
    - File organization and directory structure
    - Naming conventions and consistency
    - Best practices adherence
    - Structural improvements
    """
    try:
        result = await file_analyzer.analyze_project_structure(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ========== GITHUB REPOSITORY STRUCTURE ANALYSIS ENDPOINTS ==========


@app.post("/analyze-github-structure/", response_model=RepoStructureAnalysisResult)
async def analyze_github_repository_structure(request: RepoStructureAnalysisRequest):
    """
    Analyze GitHub repository structure and provide improvement suggestions

    This endpoint analyzes a GitHub repository's folder structure and provides:
    - Project type detection (web app, API, data science, etc.)
    - Organization score (0-100) with detailed metrics
    - File distribution analysis across directories
    - Intelligent folder structure recommendations
    - Quick wins and improvement suggestions
    - Best practices for the detected project type

    Features:
    - Works with any public GitHub repository
    - No local cloning required
    - Supports private repos with GitHub token
    - Detailed or quick analysis modes
    - Smart project type detection
    - Actionable recommendations

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name",
        "detailed_analysis": true,
        "exclude_patterns": [".git", "node_modules", "__pycache__"]
    }
    ```
    """
    try:
        result = await structure_service.analyze_repository_structure(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Structure analysis failed: {str(e)}"
        )


@app.post("/quick-structure-check/", response_model=QuickStructureCheckResult)
async def quick_github_structure_check(request: QuickStructureCheckRequest):
    """
    Quick structure check for GitHub repositories

    This endpoint provides a fast, lightweight analysis of a GitHub repository's structure:
    - Organization score and level
    - Project type detection
    - Total file count
    - Main structural issues
    - Top 3 improvement suggestions

    Perfect for:
    - Quick repository assessment
    - Batch analysis of multiple repositories
    - CI/CD pipeline integration
    - API rate limit conscious applications

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name"
    }
    ```

    Response includes:
    - Immediate results (< 10 seconds)
    - Organization score and level
    - Key issues and quick wins
    - Minimal data transfer
    """
    try:
        result = await structure_service.quick_structure_check(request)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Quick structure check failed: {str(e)}"
        )


# ========== GITHUB CODE OPTIMIZATION ENDPOINTS ==========


@app.post("/analyze-github-code/", response_model=GitHubOptimizationResult)
async def analyze_github_code_optimization(request: GitHubOptimizationRequest):
    """
    Analyze GitHub repository for code optimization opportunities

    This endpoint analyzes a GitHub repository's source code and provides:
    - Multi-language code optimization suggestions
    - Identification of important files for optimization
    - AI-powered code improvement recommendations
    - Performance, readability, and best practice suggestions

    Features:
    - Supports multiple programming languages (Python, JavaScript, TypeScript, Java, C/C++, etc.)
    - Uses Groq AI for intelligent optimization suggestions
    - Identifies and prioritizes the most important files
    - Provides detailed diff views of suggested changes
    - Optional PR creation with optimization suggestions

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name",
        "create_pr": false,
        "max_files": 20,
        "target_languages": ["python", "javascript"]
    }
    ```

    Response includes:
    - File-by-file optimization suggestions
    - Importance scoring for analyzed files
    - Detailed optimization explanations
    - Code diffs showing suggested improvements
    """
    try:
        from datetime import datetime

        result = multi_language_optimizer.analyze_github_repository_for_optimization(
            github_url=str(request.github_url),
            github_token=request.github_token,
            create_pr=request.create_pr,
            auto_merge=request.auto_merge,
        )

        if result.get("status") == "success":
            # Convert to API response format
            file_optimizations = []
            for file_opt in result.get("file_optimizations", []):
                file_optimizations.append(
                    FileOptimizationResult(
                        file_path=file_opt["file"],
                        language=file_opt["language"],
                        importance_score=file_opt["importance_score"],
                        importance_reasons=file_opt["importance_reasons"],
                        optimizations=file_opt["optimizations"],
                        has_diff=bool(file_opt.get("diff")),
                        diff_preview=(
                            file_opt.get("diff", "")[:500] + "..."
                            if file_opt.get("diff")
                            and len(file_opt.get("diff", "")) > 500
                            else file_opt.get("diff")
                        ),
                    )
                )

            return GitHubOptimizationResult(
                success=True,
                repository_url=str(request.github_url),
                total_files_analyzed=result.get("total_files_analyzed", 0),
                files_with_optimizations=result.get("files_with_optimizations", 0),
                total_optimizations=result.get("total_optimizations", 0),
                file_optimizations=file_optimizations,
                pr_result=result.get("pr_result"),
                timestamp=datetime.now().isoformat(),
            )
        else:
            return GitHubOptimizationResult(
                success=False,
                repository_url=str(request.github_url),
                total_files_analyzed=0,
                files_with_optimizations=0,
                total_optimizations=0,
                file_optimizations=[],
                error_message=result.get("error", "Unknown error occurred"),
                timestamp=datetime.now().isoformat(),
            )

    except Exception as e:
        from datetime import datetime

        return GitHubOptimizationResult(
            success=False,
            repository_url=str(request.github_url),
            total_files_analyzed=0,
            files_with_optimizations=0,
            total_optimizations=0,
            file_optimizations=[],
            error_message=str(e),
            timestamp=datetime.now().isoformat(),
        )


@app.post("/create-optimization-pr/", response_model=GitHubOptimizationPRResult)
async def create_optimization_pr(request: GitHubOptimizationPRRequest):
    """
    Analyze GitHub repository and create a PR with optimization suggestions

    This endpoint combines code analysis with automatic PR creation:
    - Analyzes the repository for optimization opportunities
    - Creates a new branch with optimization suggestions
    - Submits a pull request with detailed optimization report
    - Optionally auto-merges the PR if requested

    Requirements:
    - Valid GitHub token with repo access
    - Repository must be accessible with the provided token

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name",
        "github_token": "ghp_your_token_here",
        "auto_merge": false,
        "branch_name": "codeyogi-optimization-2024"
    }
    ```

    Response includes:
    - PR creation status and URL
    - Number of optimizations found
    - Auto-merge status if requested
    """
    try:
        from datetime import datetime

        # Analyze repository for optimizations
        result = multi_language_optimizer.analyze_github_repository_for_optimization(
            github_url=str(request.github_url),
            github_token=request.github_token,
            create_pr=True,
            auto_merge=request.auto_merge,
        )

        if result.get("status") == "success":
            pr_result = result.get("pr_result", {})

            return GitHubOptimizationPRResult(
                success=pr_result.get("status") == "success",
                pr_created=pr_result.get("pr_created", False),
                pr_url=pr_result.get("pr_url"),
                pr_number=pr_result.get("pr_number"),
                optimizations_count=result.get("total_optimizations", 0),
                files_optimized=result.get("files_with_optimizations", 0),
                auto_merged=pr_result.get("auto_merged", False),
                error_message=(
                    pr_result.get("error")
                    if pr_result.get("status") != "success"
                    else None
                ),
                timestamp=datetime.now().isoformat(),
            )
        else:
            return GitHubOptimizationPRResult(
                success=False,
                pr_created=False,
                optimizations_count=0,
                files_optimized=0,
                auto_merged=False,
                error_message=result.get("error", "Analysis failed"),
                timestamp=datetime.now().isoformat(),
            )

    except Exception as e:
        from datetime import datetime

        return GitHubOptimizationPRResult(
            success=False,
            pr_created=False,
            optimizations_count=0,
            files_optimized=0,
            auto_merged=False,
            error_message=str(e),
            timestamp=datetime.now().isoformat(),
        )


# ========== SEO OPTIMIZATION ENDPOINTS ==========


@app.post("/seo/analyze/", response_model=SEOAnalysisResult)
async def analyze_repository_seo(request: SEOAnalysisRequest):
    """
    🔍 Analyze Repository SEO Potential

    Analyzes a GitHub repository to understand its current SEO status and potential improvements.
    This endpoint only analyzes without making any changes.

    Features:
    - Scans HTML files for existing meta tags
    - Analyzes repository content for SEO opportunities
    - Generates AI-powered SEO recommendations
    - Evaluates current social media optimization

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name",
        "github_token": "ghp_your_token_here",
        "analyze_only": true
    }
    ```

    Response includes:
    - Current SEO status assessment
    - Generated SEO metadata suggestions
    - Number of HTML files found
    - Specific recommendations for improvement
    """
    try:
        from datetime import datetime
        import asyncio

        # Use the SEO analyzer function (analysis only mode)
        result = await seo_injector.analyze_repository_seo_only(
            github_url=str(request.github_url), github_token=request.github_token
        )

        if result.get("success"):
            return SEOAnalysisResult(
                success=True,
                repository=result.get("repository", ""),
                seo_metadata=(
                    SEOMetadata(**result.get("seo_metadata", {}))
                    if result.get("seo_metadata")
                    else None
                ),
                html_files_found=result.get("html_files_found", 0),
                current_seo_status=result.get("current_seo_status", {}),
                recommendations=result.get("recommendations", []),
                timestamp=datetime.now().isoformat(),
            )
        else:
            return SEOAnalysisResult(
                success=False,
                repository="",
                error_message=result.get("error", "SEO analysis failed"),
                timestamp=datetime.now().isoformat(),
            )

    except Exception as e:
        from datetime import datetime

        return SEOAnalysisResult(
            success=False,
            repository="",
            error_message=str(e),
            timestamp=datetime.now().isoformat(),
        )


@app.post("/seo/optimize/", response_model=SEOOptimizationResult)
async def optimize_repository_seo(request: SEOOptimizationRequest):
    """
    🚀 Complete SEO Optimization with Pull Request

    Performs comprehensive SEO optimization on a GitHub repository and creates a pull request with all improvements.

    Features:
    - AI-powered SEO metadata generation using Google Gemini
    - HTML meta tag injection (title, description, keywords)
    - Open Graph and Twitter Card optimization
    - SEO-optimized README.md creation
    - Automatic pull request creation with detailed changes

    Example Usage:
    ```json
    {
        "github_url": "https://github.com/username/repo-name",
        "github_token": "ghp_your_token_here",
        "create_pr": true,
        "auto_merge": false,
        "branch_name": "seo-optimization-custom"
    }
    ```

    Response includes:
    - Generated SEO metadata
    - Number of files modified
    - Pull request URL and details
    - Optimization summary
    """
    try:
        from datetime import datetime
        import asyncio

        # Run the full SEO optimization
        result = await seo_injector.optimize_github_repository_seo(
            github_url=str(request.github_url),
            github_token=request.github_token,
            branch_name=request.branch_name,
            create_pr=request.create_pr,
            auto_merge=request.auto_merge,
        )

        if result.get("success"):
            seo_data = result.get("seo_metadata", {})

            return SEOOptimizationResult(
                success=True,
                repository=result.get("repository", ""),
                seo_metadata=SEOMetadata(**seo_data) if seo_data else None,
                modified_files=result.get("modified_files", 0),
                html_files_processed=result.get("html_files_processed", 0),
                branch_name=result.get("branch_name"),
                pull_request_url=result.get("pull_request_url"),
                pull_request_number=result.get("pull_request_number"),
                timestamp=datetime.now().isoformat(),
                temp_directory=result.get("temp_directory"),
            )
        else:
            return SEOOptimizationResult(
                success=False,
                repository="",
                error_message=result.get("error", "SEO optimization failed"),
                timestamp=datetime.now().isoformat(),
            )

    except Exception as e:
        from datetime import datetime

        return SEOOptimizationResult(
            success=False,
            repository="",
            error_message=str(e),
            timestamp=datetime.now().isoformat(),
        )


@app.get("/seo/metadata/{owner}/{repo}")
async def get_repository_seo_metadata(
    owner: str,
    repo: str,
    github_token: Optional[str] = Header(None, alias="Authorization"),
):
    """
    📊 Get Current SEO Metadata for Repository

    Retrieves the current SEO metadata from a GitHub repository's HTML files and README.
    This is a read-only endpoint that doesn't modify anything.

    Path Parameters:
    - owner: GitHub repository owner/organization
    - repo: Repository name

    Headers:
    - Authorization: Bearer github_token (optional)

    Example: GET /seo/metadata/microsoft/vscode

    Response includes current meta tags, titles, descriptions found in the repository.
    """
    try:
        github_url = f"https://github.com/{owner}/{repo}"

        # Extract token from Bearer format if provided
        token = None
        if github_token and github_token.startswith("Bearer "):
            token = github_token[7:]
        elif github_token:
            token = github_token

        result = await seo_injector.get_current_seo_metadata(
            github_url=github_url, github_token=token
        )

        return {
            "repository": f"{owner}/{repo}",
            "current_metadata": result.get("metadata", {}),
            "html_files": result.get("html_files", []),
            "readme_analysis": result.get("readme_analysis", {}),
            "timestamp": result.get("timestamp"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== README GENERATOR API ENDPOINTS ==========


@app.post("/readme/analyze/")
async def analyze_readme_requirements(request: ReadmeGeneratorRequest):
    """
    🔍 Analyze Repository for README Requirements

    Analyzes a GitHub repository to determine README requirements and quality.
    This is a read-only analysis that doesn't modify anything.

    Body Parameters:
    - github_url: GitHub repository URL (required)
    - github_token: GitHub token for private repos (optional)

    Example: POST /readme/analyze/
    {
        "github_url": "https://github.com/microsoft/vscode",
        "github_token": "ghp_..."
    }

    Returns analysis of repository structure, current README quality, and recommendations.
    """
    try:
        analysis_result = await readme_generator.analyze_existing_readme(
            request.github_url, request.github_token
        )

        repo_info = readme_generator.readme_generator.parse_github_url(
            request.github_url
        )
        repository = f"{repo_info['owner']}/{repo_info['repo_name']}"

        return ReadmeAnalysisResult(
            success=analysis_result.get("success", True),
            repository=repository,
            current_readme=analysis_result.get("current_readme"),
            improvement_suggestions=analysis_result.get("improvement_suggestions", []),
            completeness_score=analysis_result.get("completeness_score"),
            error_message=(
                analysis_result.get("error")
                if not analysis_result.get("success", True)
                else None
            ),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/readme/generate/")
async def generate_readme(request: ReadmeGeneratorRequest):
    """
    🚀 Generate Professional README with Auto PR

    Generates a comprehensive README file for a GitHub repository and creates a pull request.
    This endpoint analyzes the repository, generates AI-powered content, and submits a PR.

    Body Parameters:
    - github_url: GitHub repository URL (required)
    - github_token: GitHub token with repo permissions (required)
    - branch_name: Custom branch name (optional, default: "feature/auto-readme-generation")
    - commit_message: Custom commit message (optional)
    - pr_title: Custom PR title (optional)
    - pr_description: Custom PR description (optional)

    Example: POST /readme/generate/
    {
        "github_url": "https://github.com/yourusername/yourrepo",
        "github_token": "ghp_...",
        "branch_name": "docs/readme-improvement",
        "pr_title": "📚 Add comprehensive README documentation"
    }

    Creates a new branch, generates README content, commits changes, and opens a pull request.
    """
    try:
        result = await readme_generator.generate_readme_for_repository(
            github_url=request.github_url,
            github_token=request.github_token,
            branch_name=request.branch_name,
            create_pr=True,
            style="comprehensive",
        )

        repo_info = readme_generator.readme_generator.parse_github_url(
            request.github_url
        )
        repository = f"{repo_info['owner']}/{repo_info['repo_name']}"

        return ReadmeGeneratorResult(
            success=result.get("success", True),
            repository=repository,
            readme_markdown=result.get("readme_markdown"),
            branch_name=result.get("branch_name"),
            pull_request_url=result.get("pull_request_url"),
            pull_request_number=result.get("pull_request_number"),
            analysis_summary=result.get("analysis_summary", {}),
            error_message=(
                result.get("error") if not result.get("success", True) else None
            ),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/readme/current/{owner}/{repo}")
async def get_current_readme(
    owner: str,
    repo: str,
    github_token: Optional[str] = Header(None, alias="Authorization"),
):
    """
    📖 Get Current README Content

    Retrieves the current README content from a GitHub repository.
    This is a read-only endpoint for viewing existing README files.

    Path Parameters:
    - owner: GitHub repository owner/organization
    - repo: Repository name

    Headers:
    - Authorization: Bearer github_token (optional)

    Example: GET /readme/current/microsoft/vscode

    Returns the current README content and metadata about the repository.
    """
    try:
        github_url = f"https://github.com/{owner}/{repo}"

        # Extract token from Bearer format if provided
        token = None
        if github_token and github_token.startswith("Bearer "):
            token = github_token[7:]
        elif github_token:
            token = github_token

        current_readme = await readme_generator.get_current_readme_content(
            github_url, token
        )

        return {
            "repository": f"{owner}/{repo}",
            "has_readme": current_readme is not None,
            "readme_content": current_readme,
            "github_url": github_url,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== NEW AGENTIC EVENT-DRIVEN ENDPOINTS ==========


@app.post("/repos/register", response_model=RepositoryState)
async def register_repository(request: RepoRegistrationRequest):
    """
    Register a repository for monitoring by the agentic AI system
    """
    try:
        repo_state = await event_manager.register_repository(
            repo_url=request.repo_url,
            user_id=request.user_id,
            github_token=request.github_token,
        )
        return repo_state
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/repos/{repo_owner}/{repo_name}/status", response_model=RepositoryState)
async def get_repo_status(repo_owner: str, repo_name: str):
    """
    Get the current status of a monitored repository
    """
    repo_url = f"https://github.com/{repo_owner}/{repo_name}"
    repo_state = event_manager.get_repo_status(repo_url)

    if not repo_state:
        raise HTTPException(
            status_code=404, detail="Repository not found or not being monitored"
        )

    return repo_state


@app.post("/repos/optimize-workflow", response_model=List[EventProcessingResult])
async def request_workflow_optimization(request: UserActionRequest):
    """
    User requests workflow optimization for a repository
    """
    try:
        results = await event_manager.request_workflow_optimization(
            repo_url=request.repo_url,
            user_id=request.user_id,
            github_token=request.github_token,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/repos/analyze", response_model=List[EventProcessingResult])
async def request_repo_analysis(request: UserActionRequest):
    """
    User requests repository analysis
    """
    try:
        results = await event_manager.request_repo_analysis(
            repo_url=request.repo_url,
            user_id=request.user_id,
            github_token=request.github_token,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/repos/deploy", response_model=List[EventProcessingResult])
async def request_deployment(request: UserActionRequest):
    """
    User requests deployment (triggers flowchart generation and deployment)
    """
    try:
        results = await event_manager.request_deployment(
            repo_url=request.repo_url,
            user_id=request.user_id,
            github_token=request.github_token,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/repos/describe", response_model=List[EventProcessingResult])
async def request_repo_description(request: UserActionRequest):
    """
    User requests repository description with flowchart generation
    """
    try:
        results = await event_manager.request_repo_description(
            repo_url=request.repo_url,
            user_id=request.user_id,
            github_token=request.github_token,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class PushCheckRequest(BaseModel):
    repo_url: str
    last_known_sha: Optional[str] = None
    github_token: Optional[str] = None


@app.post("/repos/check-push")
async def check_latest_push(
    request: PushCheckRequest, background_tasks: BackgroundTasks
):
    """
    Check for the latest push to a repository and trigger optimization if new commits found
    """
    try:
        # Use provided token or get from environment
        token = request.github_token or get_github_token()

        # Check for new push
        push_status = check_for_new_push(
            repo_url=request.repo_url,
            last_known_sha=request.last_known_sha,
            token=token,
        )

        if push_status.get("error"):
            return {"success": False, "error": push_status["error"]}

        if push_status["has_new_push"]:
            latest_commit = push_status["latest_commit"]

            # For now, just return the result without triggering background processing
            # This avoids the I/O error while we debug
            return {
                "success": True,
                "has_new_push": True,
                "latest_commit": latest_commit,
                "previous_sha": push_status["previous_sha"],
                "message": "New push detected (background processing disabled for testing)",
            }
        else:
            return {
                "success": True,
                "has_new_push": False,
                "latest_commit": push_status["latest_commit"],
                "message": "No new pushes detected",
            }

    except Exception as e:
        logger.error(f"Error checking for latest push: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/repos/check-and-optimize")
async def check_push_and_create_pr(
    request: PushCheckRequest, background_tasks: BackgroundTasks
):
    """
    Check for the latest push and automatically create optimization PR if new commits found
    """
    try:
        # Use provided token or get from environment
        token = request.github_token or get_github_token()

        # Check for new push
        push_status = check_for_new_push(
            repo_url=request.repo_url,
            last_known_sha=request.last_known_sha,
            token=token,
        )

        if push_status.get("error"):
            return {"success": False, "error": push_status["error"]}

        if push_status["has_new_push"]:
            latest_commit = push_status["latest_commit"]

            # Extract repo name from URL
            repo_name = request.repo_url.replace("https://github.com/", "").rstrip("/")

            try:
                # Create PR with optimized workflow
                pr_creator = GitHubPRCreator(token)
                optimized_yaml = pr_creator.get_optimized_workflow_yaml()
                improvement_summary = pr_creator.create_improvement_summary()

                pr_result = pr_creator.create_optimization_pr(
                    repo_name=repo_name,
                    optimized_yaml=optimized_yaml,
                    improvement_summary=improvement_summary,
                )

                if pr_result and pr_result.get("success"):
                    return {
                        "success": True,
                        "has_new_push": True,
                        "latest_commit": latest_commit,
                        "previous_sha": push_status["previous_sha"],
                        "pr_created": True,
                        "pr_url": pr_result["pr_url"],
                        "pr_number": pr_result["pr_number"],
                        "message": "New push detected and optimization PR created!",
                    }
                else:
                    return {
                        "success": True,
                        "has_new_push": True,
                        "latest_commit": latest_commit,
                        "previous_sha": push_status["previous_sha"],
                        "pr_created": False,
                        "pr_error": pr_result.get("error", "Unknown error"),
                        "message": "New push detected but PR creation failed",
                    }

            except Exception as pr_error:
                logger.error(f"Error creating PR: {str(pr_error)}")
                return {
                    "success": True,
                    "has_new_push": True,
                    "latest_commit": latest_commit,
                    "previous_sha": push_status["previous_sha"],
                    "pr_created": False,
                    "pr_error": str(pr_error),
                    "message": "New push detected but PR creation failed",
                }
        else:
            return {
                "success": True,
                "has_new_push": False,
                "latest_commit": push_status["latest_commit"],
                "pr_created": False,
                "message": "No new pushes detected",
            }

    except Exception as e:
        logger.error(f"Error in push check and optimization: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(...),
    x_github_delivery: str = Header(...),
):
    """
    Handle GitHub webhook events for repository monitoring
    """
    try:
        payload_data = await request.json()

        # Parse the webhook payload
        webhook_payload = GitHubWebhookPayload(**payload_data)

        # Process the webhook in the background
        background_tasks.add_task(
            process_github_webhook_background, x_github_event, webhook_payload
        )

        return {
            "status": "received",
            "event_type": x_github_event,
            "delivery_id": x_github_delivery,
            "message": "Webhook event queued for processing",
        }

    except Exception as e:
        logger.error(f"Error processing GitHub webhook: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def process_github_webhook_background(
    event_type: str, payload: GitHubWebhookPayload
):
    """Background task to process GitHub webhooks"""
    try:
        results = await event_manager.handle_github_webhook(event_type, payload)
        logger.info(f"Processed {event_type} webhook, {len(results)} agents triggered")

        # Store results in event history
        event_manager.event_history.extend(results)

    except Exception as e:
        logger.error(f"Error in background webhook processing: {str(e)}")


@app.get("/events/history")
async def get_event_history(repo_url: Optional[str] = None, limit: int = 50):
    """
    Get event processing history
    """
    try:
        history = event_manager.get_event_history(repo_url=repo_url, limit=limit)
        return {"total_events": len(history), "events": history}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/repos/monitored")
async def get_monitored_repos():
    """
    Get all repositories being monitored
    """
    return {
        "total_repos": len(event_manager.monitored_repos),
        "repositories": list(event_manager.monitored_repos.values()),
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "CodeYogi Backend"}
