from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any
from enum import Enum


class AnalysisType(str, Enum):
    STRUCTURE = "structure"
    CLEANUP = "cleanup"
    OPTIMIZATION = "optimization"
    FULL = "full"


class AnalysisCommand(str, Enum):
    OPTIMIZE = "optimize"
    EXPLAIN = "explain"
    REFACTOR = "refactor"
    REVIEW = "review"
    ANALYZE_STRUCTURE = "analyze_structure"


class OptimizationType(str, Enum):
    PERFORMANCE = "performance"
    READABILITY = "readability"
    SECURITY = "security"
    MEMORY = "memory"
    GENERAL = "general"


class ExplanationLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class GroqModel(str, Enum):
    """Available Groq models for AI-powered analysis"""

    LLAMA_3_1_70B_VERSATILE = "meta-llama/llama-4-scout-17b-16e-instruct"
    LLAMA_3_1_8B_INSTANT = "llama-3.1-8b-instant"
    LLAMA_3_2_90B_TEXT_PREVIEW = "llama-3.2-90b-text-preview"
    LLAMA_3_2_11B_TEXT_PREVIEW = "llama-3.2-11b-text-preview"
    LLAMA_3_2_3B_PREVIEW = "llama-3.2-3b-preview"
    LLAMA_3_2_1B_PREVIEW = "llama-3.2-1b-preview"
    MIXTRAL_8X7B_32768 = "mixtral-8x7b-32768"
    GEMMA_7B_IT = "gemma-7b-it"
    GEMMA2_9B_IT = "gemma2-9b-it"


class FileType(str, Enum):
    SOURCE_CODE = "source_code"
    CONFIG = "config"
    DOCUMENTATION = "documentation"
    BUILD = "build"
    TEST = "test"
    ASSET = "asset"
    DEPENDENCY = "dependency"
    UNKNOWN = "unknown"


class FileInfo(BaseModel):
    path: str
    size: int
    type: FileType
    language: Optional[str] = None
    complexity_score: Optional[float] = None
    last_modified: Optional[str] = None
    is_necessary: bool = True
    reason: Optional[str] = None


class DirectoryStructure(BaseModel):
    path: str
    files: List[FileInfo]
    subdirectories: List["DirectoryStructure"] = []
    total_files: int
    total_size: int


class StructureSuggestion(BaseModel):
    current_path: str
    suggested_path: str
    reason: str
    priority: int  # 1-5, where 5 is highest priority


class CleanupSuggestion(BaseModel):
    file_path: str
    action: str  # "delete", "move", "rename", "merge"
    reason: str
    size_savings: int
    risk_level: str  # "low", "medium", "high"


class RepoAnalysisRequest(BaseModel):
    github_url: Optional[HttpUrl] = None
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    analysis_type: AnalysisType = AnalysisType.FULL
    include_dependencies: bool = True
    exclude_patterns: List[str] = [".git", "node_modules", "__pycache__", ".vscode"]
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class RepoAnalysisResult(BaseModel):
    repo_info: Dict[str, Any]
    directory_structure: DirectoryStructure
    structure_suggestions: List[StructureSuggestion]
    cleanup_suggestions: List[CleanupSuggestion]
    metrics: Dict[str, Any]
    recommendations: List[str]
    ai_insights: Optional[Dict[str, Any]] = None


class RepoDescriptionRequest(BaseModel):
    github_url: Optional[HttpUrl] = None
    repo_owner: Optional[str] = None
    repo_name: Optional[str] = None
    include_tech_stack: bool = True
    include_architecture: bool = True
    include_features: bool = True
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class FlowchartNode(BaseModel):
    id: str
    label: str
    type: str  # "start", "process", "decision", "end", "data"
    description: Optional[str] = None


class FlowchartEdge(BaseModel):
    from_node: str
    to_node: str
    label: Optional[str] = None
    condition: Optional[str] = None


class ProjectFlowchart(BaseModel):
    title: str
    description: str
    nodes: List[FlowchartNode]
    edges: List[FlowchartEdge]
    mermaid_diagram: str
    complexity_score: Optional[float] = None


class RepoDescriptionResult(BaseModel):
    repo_info: Dict[str, Any]
    description: str
    tech_stack: Dict[str, Any]
    architecture_summary: str
    key_features: List[str]
    project_type: str
    complexity_analysis: Dict[str, Any]
    flowchart: ProjectFlowchart
    ai_insights: Optional[Dict[str, Any]] = None


class FileAnalysisRequest(BaseModel):
    file_name: Optional[str] = None
    file_content: str
    selected_code: Optional[str] = None
    command: AnalysisCommand
    optimization_type: Optional[OptimizationType] = None
    explanation_level: Optional[ExplanationLevel] = None
    context: Optional[Dict[str, Any]] = None


class FileStructureAnalysisRequest(BaseModel):
    project_path: str
    github_url: Optional[HttpUrl] = None
    include_hidden_files: bool = False
    exclude_patterns: List[str] = [
        ".git",
        "node_modules",
        "__pycache__",
        ".vscode",
        "dist",
        "build",
    ]
    max_depth: Optional[int] = None
    focus_areas: List[str] = ["organization", "naming", "structure", "best_practices"]


class FileStructureIssue(BaseModel):
    type: str  # "naming", "organization", "duplication", "structure", "security"
    severity: str  # "low", "medium", "high", "critical"
    file_path: str
    description: str
    suggestion: str
    impact: str
    effort_required: str  # "low", "medium", "high"


class FileStructureMetrics(BaseModel):
    total_files: int
    total_directories: int
    depth_levels: int
    largest_files: List[Dict[str, Any]]
    file_type_distribution: Dict[str, int]
    naming_consistency_score: float
    organization_score: float
    structure_complexity: str


class FileStructureAnalysisResult(BaseModel):
    project_info: Dict[str, Any]
    structure_metrics: FileStructureMetrics
    issues_found: List[FileStructureIssue]
    recommendations: List[str]
    best_practices_suggestions: List[str]
    ai_insights: Optional[Dict[str, Any]] = None
    success: bool
    error_message: Optional[str] = None
    timestamp: Optional[str] = None


class OptimizationSuggestion(BaseModel):
    type: str
    description: str
    impact: str  # "high", "medium", "low"
    effort: str  # "high", "medium", "low"
    example: Optional[str] = None


class CodeExplanation(BaseModel):
    overview: str
    detailed_breakdown: List[str]
    key_concepts: List[str]
    complexity_level: str
    learning_resources: Optional[List[str]] = None


class FileAnalysisResult(BaseModel):
    original_code: str
    language: str
    command: AnalysisCommand
    result: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    file_name: Optional[str] = None
    timestamp: Optional[str] = None


class WorkflowOptimizationWithDeploymentRequest(BaseModel):
    repo_url: str
    github_token: str
    branch_name: Optional[str] = "codeyogi-workflow-optimization"
    workflow_path: Optional[str] = ".github/workflows/codeyogi-optimized.yml"
    commit_message: Optional[str] = (
        "🚀 CodeYogi: Optimize CI/CD workflow for better performance"
    )
    auto_merge: Optional[bool] = False


class WorkflowOptimizationWithDeploymentResult(BaseModel):
    success: bool
    optimization_analysis: Dict[str, Any]
    pr_info: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str


class RepoStructureAnalysisRequest(BaseModel):
    github_url: HttpUrl
    exclude_patterns: List[str] = [
        ".git",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        "venv",
        ".venv",
    ]
    detailed_analysis: bool = False
    github_token: Optional[str] = None


class StructureRecommendation(BaseModel):
    type: str  # "create_directory", "organize_root", "separate_types", etc.
    folder: str
    reason: str
    priority: str  # "high", "medium", "low"
    suggested_subfolders: Optional[List[str]] = None


class StructureMetrics(BaseModel):
    total_files: int
    total_directories: int
    max_depth: int
    average_depth: float
    files_per_directory: float
    organization_score: int
    large_directories_count: int


class FileDistribution(BaseModel):
    root_files: int
    max_files_in_directory: int
    type_distribution: Dict[str, int]
    directories_with_mixed_types: List[Dict[str, Any]]
    scattered_types: List[Dict[str, Any]]


class StructureAnalysisSummary(BaseModel):
    organization_level: str
    main_issues: List[str]
    quick_wins: List[Dict[str, str]]
    estimated_improvement_time: str


class RepoStructureAnalysisResult(BaseModel):
    success: bool
    github_url: str
    project_type: str
    structure_metrics: StructureMetrics
    file_distribution: FileDistribution
    structure_suggestions: List[StructureRecommendation]
    recommended_folders: Dict[str, str]
    summary: Optional[StructureAnalysisSummary] = None
    error_message: Optional[str] = None
    timestamp: str


# Quick structure check request (minimal)
class QuickStructureCheckRequest(BaseModel):
    github_url: HttpUrl
    github_token: Optional[str] = None


class QuickStructureCheckResult(BaseModel):
    success: bool
    github_url: str
    organization_score: int
    organization_level: str
    project_type: str
    total_files: int
    main_issues: List[str]
    top_suggestions: List[str]
    error_message: Optional[str] = None


# Update forward references
DirectoryStructure.model_rebuild()


# ========== GITHUB CODE OPTIMIZATION SCHEMAS ==========


class GitHubOptimizationRequest(BaseModel):
    github_url: HttpUrl
    github_token: Optional[str] = None
    create_pr: bool = False
    auto_merge: bool = False
    target_languages: Optional[List[str]] = None  # Filter specific languages
    max_files: int = 20  # Maximum files to analyze
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class FileOptimizationResult(BaseModel):
    file_path: str
    language: str
    importance_score: int
    importance_reasons: List[str]
    optimizations: List[str]
    has_diff: bool
    diff_preview: Optional[str] = None  # First few lines of diff for preview


class GitHubOptimizationResult(BaseModel):
    success: bool
    repository_url: str
    total_files_analyzed: int
    files_with_optimizations: int
    total_optimizations: int
    file_optimizations: List[FileOptimizationResult]
    pr_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: str


class GitHubOptimizationPRRequest(BaseModel):
    github_url: HttpUrl
    github_token: str
    auto_merge: bool = False
    branch_name: Optional[str] = "codeyogi-code-optimization"
    commit_message: Optional[str] = (
        "🤖 CodeYogi: Multi-language code optimization suggestions"
    )


class GitHubOptimizationPRResult(BaseModel):
    success: bool
    pr_created: bool
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    optimizations_count: int
    files_optimized: int
    auto_merged: bool = False
    error_message: Optional[str] = None
    timestamp: str


# SEO Optimization Schemas
class SEOOptimizationRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = None
    branch_name: Optional[str] = None
    create_pr: bool = True
    auto_merge: bool = False
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class SEOMetadata(BaseModel):
    title: str
    description: str
    keywords: List[str]
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_type: Optional[str] = "website"
    twitter_card: Optional[str] = "summary"
    canonical_url: Optional[str] = None
    schema_type: Optional[str] = "SoftwareApplication"


class SEOOptimizationResult(BaseModel):
    success: bool
    repository: str
    seo_metadata: Optional[SEOMetadata] = None
    modified_files: int = 0
    html_files_processed: int = 0
    branch_name: Optional[str] = None
    pull_request_url: Optional[str] = None
    pull_request_number: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: str
    temp_directory: Optional[str] = None


class SEOAnalysisRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = None
    analyze_only: bool = True
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class SEOAnalysisResult(BaseModel):
    success: bool
    repository: str
    seo_metadata: Optional[SEOMetadata] = None
    html_files_found: int = 0
    current_seo_status: Dict[str, Any] = {}
    recommendations: List[str] = []
    error_message: Optional[str] = None
    timestamp: str


# README Generator Schemas
class ReadmeGeneratorRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = None
    branch_name: Optional[str] = None
    create_pr: bool = True
    auto_merge: bool = False
    readme_style: Optional[str] = (
        "comprehensive"  # comprehensive, minimal, professional
    )
    include_badges: bool = True
    include_installation: bool = True
    include_usage_examples: bool = True
    include_contributing: bool = True
    include_license: bool = True
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class ReadmeContent(BaseModel):
    title: str
    description: str
    badges: List[str] = []
    installation_section: Optional[str] = None
    usage_section: Optional[str] = None
    features_section: Optional[str] = None
    api_documentation: Optional[str] = None
    contributing_section: Optional[str] = None
    license_section: Optional[str] = None
    contact_section: Optional[str] = None
    acknowledgments: Optional[str] = None


class ReadmeGeneratorResult(BaseModel):
    success: bool
    repository: str
    readme_content: Optional[ReadmeContent] = None
    readme_markdown: Optional[str] = None
    branch_name: Optional[str] = None
    pull_request_url: Optional[str] = None
    pull_request_number: Optional[int] = None
    analysis_summary: Dict[str, Any] = {}
    error_message: Optional[str] = None
    timestamp: str


class ReadmeAnalysisRequest(BaseModel):
    github_url: str
    github_token: Optional[str] = None
    analyze_only: bool = True
    model: Optional[GroqModel] = GroqModel.LLAMA_3_1_70B_VERSATILE


class ReadmeAnalysisResult(BaseModel):
    success: bool
    repository: str
    current_readme: Optional[Dict[str, Any]] = None
    code_analysis: Dict[str, Any] = {}
    suggested_readme: Optional[ReadmeContent] = None
    improvement_suggestions: List[str] = []
    completeness_score: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: str
