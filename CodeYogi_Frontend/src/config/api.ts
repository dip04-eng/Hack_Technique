// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  ENDPOINTS: {
    CHECK_AND_OPTIMIZE: "/repos/check-and-optimize",
    ANALYZE_GITHUB_STRUCTURE: "/analyze-github-structure/",
    ANALYZE_GITHUB_CODE: "/analyze-github-code/",
    ANALYZE_FILE: "/analyze-file/",
    DESCRIBE_REPOSITORY: "/describe-repository/",
    OPTIMIZE_WORKFLOW_DEPLOYMENT: "/optimize-workflow-deployment/",
  },
  // Polling interval in milliseconds (1 minute)
  MONITORING_INTERVAL: 60000,
};

// Helper function to construct full API URLs
export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`;
};

export default API_CONFIG;
