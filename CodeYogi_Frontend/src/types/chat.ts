export interface RepoAnalysis {
  repo_info: Record<string, any>;
  description: string;
  tech_stack: Record<string, string[]>;
  architecture_summary: string;
  key_features: string[];
  project_type: string;
  complexity_analysis: Record<string, any>;
  flowchart: {
    title: string;
    description: string;
    mermaid_diagram: string;
    complexity_score: number;
  };
  ai_insights: {
    strategic_analysis?: string;
    model_used: string;
    analysis_type: string;
    [key: string]: any;
  };
}

// Define structure for GitHub structure analysis
export interface GithubStructureAnalysis {
  success: boolean;
  github_url: string;
  project_type: string;
  structure_metrics: {
    total_files: number;
    total_directories: number;
    max_depth: number;
    average_depth: number;
    files_per_directory: number;
    organization_score: number;
    large_directories_count: number;
  };
  file_distribution: {
    root_files: number;
    max_files_in_directory: number;
    type_distribution: Record<string, number>;
    directories_with_mixed_types: Array<{
      directory: string;
      types: string[];
      file_count: number;
    }>;
    scattered_types: Array<{
      type: string;
      locations: string[];
      location_count: number;
    }>;
  };
  structure_suggestions: Array<{
    type: string;
    folder: string;
    reason: string;
    priority: string;
    suggested_subfolders: string[] | null;
  }>;
  recommended_folders: Record<string, string>;
  summary: {
    organization_level: string;
    main_issues: string[];
    quick_wins: string[];
    estimated_improvement_time: string;
  };
  error_message: string | null;
  timestamp: string;
}

// Update the Message interface to hold analysis data directly
// GitHub code analysis structure
export interface GithubCodeAnalysis {
  success: boolean;
  repository_url: string;
  total_files_analyzed: number;
  files_with_optimizations: number;
  total_optimizations: number;
  file_optimizations: Array<{
    file_path: string;
    language: string;
    importance_score: number;
    importance_reasons: string[];
    optimizations: string[];
    has_diff: boolean;
    diff_preview: string;
  }>;
  pr_result: any | null;
  error_message: string | null;
  timestamp: string;
}

// GitHub Optimization PR response
export interface OptimizationPR {
  success: boolean;
  pr_created: boolean;
  pr_url: string;
  pr_number: number;
  optimizations_count: number;
  files_optimized: number;
  auto_merged: boolean;
  error_message: string | null;
  timestamp: string;
}

export interface ReadmeGenerator {
  success: boolean;
  repository: string;
  readme_content: string | null;
  readme_markdown: string;
  branch_name: string;
  pull_request_url: string;
  pull_request_number: number;
  analysis_summary: {
    files: Array<{
      path: string;
      size: number;
      extension: string;
    }>;
    directories: string[];
    languages: Record<string, number>;
    frameworks: string[];
    dependencies: Record<string, Record<string, string>>;
    has_tests: boolean;
    has_docs: boolean;
    has_ci: boolean;
    project_type: string;
    main_files: string[];
    config_files: string[];
    total_files: number;
    total_size: number;
  };
  error_message: string | null;
  timestamp: string;
}

export interface SEOOptimization {
  success: boolean;
  repository: string;
  seo_metadata: {
    title: string;
    description: string;
    keywords: string[];
    og_title: string;
    og_description: string;
    og_type: string;
    twitter_card: string;
    canonical_url: string;
    schema_type: string;
  };
  modified_files: number;
  html_files_processed: number;
  branch_name: string;
  pull_request_url: string;
  pull_request_number: number;
  error_message: string | null;
  timestamp: string;
  temp_directory: string;
}

export interface Message {
  id: string;
  type: "user" | "ai";
  content: string;
  timestamp: Date;
  streaming?: boolean;
  isLoading?: boolean;
  analysis?: {
    data: RepoAnalysis;
    repoName: string;
  };
  isStrategicAnalysis?: boolean; // ✨ ADDED for special formatting
  workflowOptimization?: {
    data: WorkflowOptimization;
    repoName: string;
  };
  workflowDeployment?: {
    data: WorkflowDeployment;
    repoName: string;
  };
  githubStructureAnalysis?: {
    data: GithubStructureAnalysis;
    repoName: string;
  };
  githubCodeAnalysis?: {
    data: GithubCodeAnalysis;
    repoName: string;
  };
  optimizationPR?: {
    data: OptimizationPR;
    repoName: string;
  };
  readmeGenerator?: {
    data: ReadmeGenerator;
    repoName: string;
  };
  seoOptimization?: {
    data: SEOOptimization;
    repoName: string;
  };
  rollbackIntelligence?: {
    repoOwner: string;
    repoName: string;
    branch?: string;
  };
}

export interface WorkflowOptimization {
  ai_insights: {
    ai_analysis: string;
    model_used: string;
    analysis_type: string;
  };
  optimized_workflow: {
    workflow_name: string;
    workflow_content: string;
    optimization_type: string;
    improvements: string[];
    estimated_time_savings: string;
    confidence_score: number;
  };
  recommendations: {
    implementation_steps: string[];
    required_secrets: string[];
    estimated_setup_time: string;
    difficulty_level: string;
    prerequisites: string[];
    testing_checklist: string[];
  };
  timestamp: string;
}

export interface WorkflowDeployment {
  success: boolean;
  optimization_analysis: {
    repository: {
      name: string;
      full_name: string;
      description: string | null;
      language: string;
      languages: Record<string, number>;
      size: number;
      stars: number;
      forks: number;
      default_branch: string;
      topics: string[];
      has_issues: boolean;
      has_projects: boolean;
      visibility: string;
    };
    analysis: {
      repo_language: string;
      framework_type: string;
      dependencies: string[];
      existing_workflows: Array<{
        name: string;
        type: string;
        content: string;
        parsed?: any;
        path: string;
      }>;
      project_structure: {
        has_tests: boolean;
        has_docs: boolean;
        has_docker: boolean;
        has_ci: boolean;
        has_security: boolean;
        directory_count: number;
        file_count: number;
        main_directories: string[];
      };
      recommended_actions: string[];
      optimization_score: number;
    };
    ai_insights: {
      ai_analysis: string;
      model_used: string;
      analysis_type: string;
    };
    optimized_workflow: {
      workflow_name: string;
      workflow_content: string;
      optimization_type: string;
      improvements: string[];
      estimated_time_savings: string;
      confidence_score: number;
    };
    recommendations: {
      implementation_steps: string[];
      required_secrets: string[];
      estimated_setup_time: string;
      difficulty_level: string;
      prerequisites: string[];
      testing_checklist: string[];
    };
    timestamp: string;
  };
  pr_info: {
    success: boolean;
    pr_number: number;
    pr_url: string;
    branch_name: string;
    commit_sha: string;
    workflow_path: string;
  };
  error_message: string | null;
  timestamp: string;
}
