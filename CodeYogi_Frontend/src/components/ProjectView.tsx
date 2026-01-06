import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FolderOpen,
  FileCode,
  ChevronRight,
  ChevronDown,
  Plus,
  Upload,
  Search,
  Filter,
  MoreVertical,
  GitBranch,
  Clock,
  Users,
  X,
  Menu,
  Zap,
} from "lucide-react";
import { useSelectedRepository } from "../hooks/useSelectedRepository";
import { auth } from "../config/firebase";
import { API_CONFIG, getApiUrl } from "../config/api";

const GITHUB_API = "https://api.github.com/repos";

interface GitHubRepoData {
  id: number;
  name: string;
  description: string | null;
  language: string | null;
  stargazers_count: number;
  updated_at: string;
  html_url: string;
  clone_url: string;
}

interface ProjectViewProps {
  // Props are now optional since we get selectedRepo from the hook
}

interface FileItem {
  id: string;
  name: string;
  type: "folder" | "file";
  children?: FileItem[];
  size?: string;
  modified?: string;
  path?: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  status: "active" | "deployed" | "draft";
  lastModified: string;
  collaborators: number;
  files: FileItem[];
  isActive: boolean;
}

interface TreeItem {
  path: string;
  type: string;
  size?: number;
  url: string;
}

interface ExplanationData {
  overview?: {
    description: string;
    purpose: string;
  };
  breakdown?: Array<{
    line: string;
    description: string;
  }>;
  key_concepts?: Array<
    | string
    | {
        concept: string;
        description?: string;
      }
  >;
  data_flow?: {
    description: string;
    flow: string;
  };
  dependencies?: {
    description: string;
    dependencies: string;
  };
  improvements?: Array<
    | string
    | {
        suggestion: string;
        description?: string;
      }
  >;
  patterns?: Array<
    | string
    | {
        pattern: string;
        description?: string;
      }
  >;
}

interface ApiResponse {
  success: boolean;
  result?: {
    explanation: string | ExplanationData;
    analysis_type: string;
    explanation_level: string;
    note?: string;
  };
  error_message?: string;
  file_name: string;
}

export const ProjectView: React.FC<ProjectViewProps> = () => {
  const { selectedRepo } = useSelectedRepository();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [showRepoListModal, setShowRepoListModal] = useState(false);
  const [availableRepos, setAvailableRepos] = useState<GitHubRepoData[]>([]);
  const [isLoadingRepos, setIsLoadingRepos] = useState(false);
  const [repoError, setRepoError] = useState<string | null>(null);
  const [searchRepoQuery, setSearchRepoQuery] = useState("");
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(
    new Set()
  );
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [treeData, setTreeData] = useState<TreeItem[]>([]);
  const [fileContent, setFileContent] = useState("");
  const [isFileSelected, setIsFileSelected] = useState(false);
  const [isCompactMode, setIsCompactMode] = useState(false);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [selectedCode, setSelectedCode] = useState<string>("");
  const [showExplainButton, setShowExplainButton] = useState(false);
  const [isExplaining, setIsExplaining] = useState(false);
  const [explanation, setExplanation] = useState<
    string | ExplanationData | null
  >(null);
  const [showExplanationPanel, setShowExplanationPanel] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimization, setOptimization] = useState<any>(null);
  const [showOptimizationPanel, setShowOptimizationPanel] = useState(false);

  // Check authentication status when opening modal
  useEffect(() => {
    if (showRepoListModal) {
      const user = auth.currentUser;
      if (!user) {
        setRepoError("Please sign in to access your GitHub repositories");
        return;
      }
      fetchGitHubRepos();
    }
  }, [showRepoListModal]);

  // Track file selection state without auto-expansion
  useEffect(() => {
    if (selectedFile) {
      setIsFileSelected(true);
    } else {
      setIsFileSelected(false);
      // Don't automatically change compact mode or clear pinned sections
      // setPinnedSections(new Set());
      // setIsCompactMode(false);
      // setExpandedSection(null);
    }
  }, [selectedFile]);

  // Toggle compact mode
  const toggleCompactMode = () => {
    setIsCompactMode(!isCompactMode);
    setExpandedSection(null);
  };

  // Handle code selection
  const handleTextSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 0) {
      setSelectedCode(selection.toString().trim());
      setShowExplainButton(true);
    } else {
      setSelectedCode("");
      setShowExplainButton(false);
    }
  };

  // Handle clicking outside to clear selection
  const handleClickOutside = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length === 0) {
      setSelectedCode("");
      setShowExplainButton(false);
    }
  };

  // Render explanation content
  const renderExplanation = (explanation: string | ExplanationData | null) => {
    if (!explanation) {
      return (
        <div className="text-sm text-gray-500">No explanation available</div>
      );
    }

    if (typeof explanation === "string") {
      return (
        <div className="text-sm text-gray-300 whitespace-pre-wrap">
          {explanation}
        </div>
      );
    }

    // Handle structured JSON response
    if (typeof explanation === "object" && explanation !== null) {
      const data = explanation as ExplanationData;

      return (
        <div className="space-y-4">
          {/* Overview Section */}
          {data.overview && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Overview
              </h5>
              <div className="text-sm text-gray-300 space-y-1">
                <p>
                  <strong>Description:</strong> {data.overview.description}
                </p>
                <p>
                  <strong>Purpose:</strong> {data.overview.purpose}
                </p>
              </div>
            </div>
          )}

          {/* Line-by-line breakdown */}
          {data.breakdown && Array.isArray(data.breakdown) && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Code Breakdown
              </h5>
              <div className="space-y-2">
                {data.breakdown.map((item: any, index: number) => (
                  <div key={index} className="bg-gray-800/50 rounded p-2">
                    <code className="text-xs text-yellow-400 block mb-1">
                      {item.line}
                    </code>
                    <p className="text-xs text-gray-300">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Key Concepts */}
          {data.key_concepts && Array.isArray(data.key_concepts) && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Key Concepts
              </h5>
              <div className="flex flex-wrap gap-2">
                {data.key_concepts.map((concept: any, index: number) => {
                  const conceptText =
                    typeof concept === "string"
                      ? concept
                      : concept.concept ||
                        concept.name ||
                        JSON.stringify(concept);
                  return (
                    <span
                      key={index}
                      className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded"
                    >
                      {conceptText}
                    </span>
                  );
                })}
              </div>
            </div>
          )}

          {/* Data Flow */}
          {data.data_flow && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Data Flow
              </h5>
              <div className="text-sm text-gray-300 space-y-1">
                <p>
                  <strong>Description:</strong> {data.data_flow.description}
                </p>
                <p>
                  <strong>Flow:</strong> {data.data_flow.flow}
                </p>
              </div>
            </div>
          )}

          {/* Dependencies */}
          {data.dependencies && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Dependencies
              </h5>
              <div className="text-sm text-gray-300 space-y-1">
                <p>
                  <strong>Description:</strong> {data.dependencies.description}
                </p>
                <p>
                  <strong>Dependencies:</strong>{" "}
                  {data.dependencies.dependencies}
                </p>
              </div>
            </div>
          )}

          {/* Improvements */}
          {data.improvements && Array.isArray(data.improvements) && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Suggested Improvements
              </h5>
              <ul className="space-y-1">
                {data.improvements.map((improvement: any, index: number) => {
                  const improvementText =
                    typeof improvement === "string"
                      ? improvement
                      : improvement.suggestion ||
                        improvement.improvement ||
                        improvement.text;
                  const description =
                    typeof improvement === "object"
                      ? improvement.description
                      : null;

                  return (
                    <li
                      key={index}
                      className="text-sm text-gray-300 flex items-start gap-2"
                    >
                      <span className="text-yellow-400 text-xs mt-1">•</span>
                      <div>
                        <div>{improvementText}</div>
                        {description && (
                          <div className="text-xs text-gray-400 mt-1">
                            {description}
                          </div>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}

          {/* Patterns */}
          {data.patterns && Array.isArray(data.patterns) && (
            <div>
              <h5 className="text-sm font-semibold text-green-400 mb-2">
                Design Patterns
              </h5>
              <ul className="space-y-1">
                {data.patterns.map((pattern: any, index: number) => {
                  const patternText =
                    typeof pattern === "string"
                      ? pattern
                      : pattern.pattern || pattern.name || pattern.text;
                  const description =
                    typeof pattern === "object" ? pattern.description : null;

                  return (
                    <li
                      key={index}
                      className="text-sm text-gray-300 flex items-start gap-2"
                    >
                      <span className="text-purple-400 text-xs mt-1">•</span>
                      <div>
                        <div>{patternText}</div>
                        {description && (
                          <div className="text-xs text-gray-400 mt-1">
                            {description}
                          </div>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="text-sm text-gray-500">Unable to display explanation</div>
    );
  };

  // Render optimization content
  const renderOptimization = (optimization: any) => {
    if (!optimization) {
      return (
        <div className="text-sm text-gray-500">No optimization available</div>
      );
    }

    if (typeof optimization === "string") {
      return (
        <div className="text-sm text-gray-300 whitespace-pre-wrap">
          {optimization}
        </div>
      );
    }

    // Handle structured JSON response
    if (typeof optimization === "object" && optimization !== null) {
      // Check if it's the nested structure with result
      if (optimization.result && optimization.result.optimized_code) {
        const result = optimization.result;

        return (
          <div className="space-y-4">
            {/* Optimized Code Section */}
            {result.optimized_code && (
              <div>
                <h5 className="text-sm font-semibold text-blue-400 mb-2">
                  Optimized Code
                </h5>
                <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-4 max-h-64 overflow-y-auto">
                  <pre className="text-sm text-green-400 whitespace-pre-wrap font-mono">
                    {result.optimized_code}
                  </pre>
                </div>
              </div>
            )}

            {/* Analysis Section */}
            {result.analysis && (
              <div>
                <h5 className="text-sm font-semibold text-blue-400 mb-2">
                  Analysis
                </h5>
                <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-4">
                  {(() => {
                    try {
                      const analysisData =
                        typeof result.analysis === "string"
                          ? JSON.parse(
                              result.analysis.replace(/```json\n?|\n?```/g, "")
                            )
                          : result.analysis;

                      return (
                        <div className="space-y-3">
                          {/* Optimized Code from Analysis */}
                          {analysisData.optimized_code && (
                            <div>
                              <h6 className="text-xs font-medium text-yellow-400 mb-2">
                                Clean Code:
                              </h6>
                              <div className="bg-gray-800/50 rounded p-3 max-h-48 overflow-y-auto">
                                <pre className="text-xs text-green-300 whitespace-pre-wrap font-mono">
                                  {Array.isArray(
                                    analysisData.optimized_code.javascript
                                  )
                                    ? analysisData.optimized_code.javascript.join(
                                        "\n"
                                      )
                                    : analysisData.optimized_code.javascript ||
                                      analysisData.optimized_code}
                                </pre>
                              </div>
                            </div>
                          )}

                          {/* Changes Made */}
                          {analysisData.changes_made &&
                            Array.isArray(analysisData.changes_made) && (
                              <div>
                                <h6 className="text-xs font-medium text-yellow-400 mb-2">
                                  Changes Made:
                                </h6>
                                <ul className="space-y-1">
                                  {analysisData.changes_made.map(
                                    (change: string, index: number) => (
                                      <li
                                        key={index}
                                        className="text-xs text-gray-300 flex items-start gap-2"
                                      >
                                        <span className="text-green-400 text-xs mt-1">
                                          ✓
                                        </span>
                                        <span>{change}</span>
                                      </li>
                                    )
                                  )}
                                </ul>
                              </div>
                            )}

                          {/* Performance Impact */}
                          {analysisData.performance_impact && (
                            <div>
                              <h6 className="text-xs font-medium text-yellow-400 mb-2">
                                Performance Impact:
                              </h6>
                              <div className="space-y-1">
                                {Object.entries(
                                  analysisData.performance_impact
                                ).map(([key, value]) => (
                                  <div
                                    key={key}
                                    className="text-xs text-gray-300"
                                  >
                                    <span className="text-purple-400 capitalize">
                                      {key.replace("_", " ")}:
                                    </span>{" "}
                                    {value as string}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Best Practices */}
                          {analysisData.best_practices &&
                            Array.isArray(analysisData.best_practices) && (
                              <div>
                                <h6 className="text-xs font-medium text-yellow-400 mb-2">
                                  Best Practices Applied:
                                </h6>
                                <ul className="space-y-1">
                                  {analysisData.best_practices.map(
                                    (practice: string, index: number) => (
                                      <li
                                        key={index}
                                        className="text-xs text-gray-300 flex items-start gap-2"
                                      >
                                        <span className="text-blue-400 text-xs mt-1">
                                          •
                                        </span>
                                        <span>{practice}</span>
                                      </li>
                                    )
                                  )}
                                </ul>
                              </div>
                            )}

                          {/* Potential Issues */}
                          {analysisData.potential_issues &&
                            Array.isArray(analysisData.potential_issues) && (
                              <div>
                                <h6 className="text-xs font-medium text-yellow-400 mb-2">
                                  Considerations:
                                </h6>
                                <ul className="space-y-1">
                                  {analysisData.potential_issues.map(
                                    (issue: string, index: number) => (
                                      <li
                                        key={index}
                                        className="text-xs text-gray-300 flex items-start gap-2"
                                      >
                                        <span className="text-yellow-400 text-xs mt-1">
                                          ⚠
                                        </span>
                                        <span>{issue}</span>
                                      </li>
                                    )
                                  )}
                                </ul>
                              </div>
                            )}
                        </div>
                      );
                    } catch (e) {
                      return (
                        <div className="text-sm text-gray-300 whitespace-pre-wrap">
                          {result.analysis}
                        </div>
                      );
                    }
                  })()}
                </div>
              </div>
            )}
          </div>
        );
      }

      // Handle other object structures
      return (
        <div className="text-sm text-gray-300 whitespace-pre-wrap">
          {JSON.stringify(optimization, null, 2)}
        </div>
      );
    }

    return (
      <div className="text-sm text-gray-500">
        Unable to display optimization
      </div>
    );
  };

  const handleOptimizeCode = async () => {
    if (!selectedCode || !selectedFile) return;

    setIsOptimizing(true);
    setShowOptimizationPanel(true);
    setOptimization(null);

    try {
      const requestBody = {
        file_name: selectedFile,
        file_content: fileContent,
        selected_code: selectedCode,
        command: "optimize",
        optimization_type: "performance",
        explanation_level: "beginner",
        context: {},
      };

      const response = await fetch(
        getApiUrl(API_CONFIG.ENDPOINTS.ANALYZE_FILE),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to optimize code: ${response.statusText}`);
      }

      const result = await response.json();
      setOptimization(result);
    } catch (error) {
      console.error("Error optimizing code:", error);
      setOptimization(
        `Error: ${
          error instanceof Error ? error.message : "Failed to optimize code"
        }`
      );
    } finally {
      setIsOptimizing(false);
    }
  };
  const handleExplainCode = async () => {
    if (!selectedCode || !selectedFile) return;

    setIsExplaining(true);
    setShowExplanationPanel(true);
    setExplanation(null);

    try {
      const requestBody = {
        file_name: selectedFile,
        file_content: fileContent,
        selected_code: selectedCode,
        command: "explain",
        optimization_type: "performance",
        explanation_level: "beginner",
        context: {},
      };

      const response = await fetch(
        getApiUrl(API_CONFIG.ENDPOINTS.ANALYZE_FILE),
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        throw new Error(`Failed to analyze code: ${response.statusText}`);
      }

      const result: ApiResponse = await response.json();

      // Handle the structured response format
      if (result.success && result.result && result.result.explanation) {
        try {
          // Try to parse the explanation as JSON if it's wrapped in code blocks
          let explanationData = result.result.explanation;
          if (
            typeof explanationData === "string" &&
            explanationData.includes("```json")
          ) {
            // Extract JSON from code blocks
            const jsonMatch = explanationData.match(/```json\n([\s\S]*?)\n```/);
            if (jsonMatch) {
              explanationData = JSON.parse(jsonMatch[1]);
            }
          }

          if (typeof explanationData === "object") {
            setExplanation(explanationData);
          } else {
            setExplanation(explanationData);
          }
        } catch (parseError) {
          console.warn(
            "Failed to parse explanation as JSON, using as text:",
            parseError
          );
          setExplanation(result.result.explanation);
        }
      } else if (result.error_message) {
        setExplanation(`Error: ${result.error_message}`);
      } else {
        setExplanation("No explanation available");
      }
    } catch (error) {
      console.error("Error explaining code:", error);
      setExplanation(
        `Error: ${
          error instanceof Error ? error.message : "Failed to explain code"
        }`
      );
    } finally {
      setIsExplaining(false);
    }
  };

  // Handle section expansion in compact mode
  const handleSectionExpand = (section: string) => {
    if (expandedSection === section) {
      setExpandedSection(null);
    } else {
      setExpandedSection(section);
    }
  };

  // Convert GitHub tree data to our file structure format
  const convertTreeToFileStructure = (treeData: any[]): FileItem[] => {
    const items: { [key: string]: FileItem } = {};
    const result: FileItem[] = [];

    treeData.forEach((item, index) => {
      const paths = item.path.split("/");
      let currentPath = "";

      paths.forEach((part: string, i: number) => {
        const prevPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;

        if (!items[currentPath]) {
          const isFile = i === paths.length - 1 && !item.type.includes("tree");
          const newItem: FileItem = {
            id: `file-${index}-${i}`,
            name: part,
            type: isFile ? "file" : "folder",
            children: isFile ? undefined : [],
            size: isFile ? `${(item.size / 1024).toFixed(1)}KB` : undefined,
            path: isFile ? item.path : undefined,
          };

          items[currentPath] = newItem;

          if (prevPath) {
            items[prevPath].children?.push(newItem);
          } else {
            result.push(newItem);
          }
        }
      });
    });

    return result;
  };

  // Handle selected repository changes
  useEffect(() => {
    console.log(
      "ProjectView useEffect - selectedRepo changed:",
      selectedRepo?.name
    );

    const updateProject = async () => {
      if (selectedRepo) {
        // Create initial project data even before tree data loads
        const initialProjectData: Project = {
          id: String(selectedRepo.id),
          name: selectedRepo.name,
          description: selectedRepo.description || "No description available",
          status: "active" as const,
          lastModified: new Date(selectedRepo.updated_at).toLocaleDateString(),
          collaborators: selectedRepo.stargazers_count ?? 0,
          files: [], // Empty files array initially
          isActive: true,
        };

        // Clear previous states
        setSelectedFile(null);
        setFileContent("");
        setTreeData([]);
        setExpandedFolders(new Set());
        setExpandedSection(null);

        // Update projects list and set active project
        setProjects((prevProjects) => {
          const otherProjects = prevProjects
            .filter((p) => p.id !== initialProjectData.id)
            .map((p) => ({ ...p, isActive: false }));
          return [...otherProjects, initialProjectData];
        });

        // Set as selected project immediately
        setSelectedProject(initialProjectData);

        // Start fetching the tree data immediately
        try {
          const repoRes = await fetch(
            `${GITHUB_API}/${selectedRepo.full_name}`
          );
          const repoData = await repoRes.json();
          const branch = repoData.default_branch;

          const branchRes = await fetch(
            `${GITHUB_API}/${selectedRepo.full_name}/branches/${branch}`
          );
          const branchData = await branchRes.json();
          const treeSha = branchData.commit.commit.tree.sha;

          const treeRes = await fetch(
            `${GITHUB_API}/${selectedRepo.full_name}/git/trees/${treeSha}?recursive=1`
          );
          const treeData = await treeRes.json();
          setTreeData(treeData.tree);
        } catch (error) {
          console.error("Error fetching repository data:", error);
        }
      }
    };

    updateProject();
  }, [selectedRepo]);

  // Update project files when tree data is loaded
  useEffect(() => {
    if (selectedRepo && treeData.length > 0) {
      const fileStructure = convertTreeToFileStructure(treeData);

      // Update the project with file structure
      setProjects((prevProjects) =>
        prevProjects.map((project) =>
          project.id === String(selectedRepo.id)
            ? { ...project, files: fileStructure }
            : project
        )
      );
    }
  }, [selectedRepo, treeData]);

  // Fetch repo tree (file structure)
  React.useEffect(() => {
    async function fetchTree() {
      if (!selectedRepo) return;

      try {
        // Get default branch
        const repoRes = await fetch(`${GITHUB_API}/${selectedRepo.full_name}`);
        const repoData = await repoRes.json();
        const branch = repoData.default_branch;

        // Get tree SHA
        const branchRes = await fetch(
          `${GITHUB_API}/${selectedRepo.full_name}/branches/${branch}`
        );
        const branchData = await branchRes.json();
        const treeSha = branchData.commit.commit.tree.sha;

        // Get tree structure
        const treeRes = await fetch(
          `${GITHUB_API}/${selectedRepo.full_name}/git/trees/${treeSha}?recursive=1`
        );
        const treeData = await treeRes.json();
        setTreeData(treeData.tree);
      } catch (error) {
        console.error("Error fetching repository data:", error);
      }
    }

    fetchTree();
  }, [selectedRepo]);

  // Fetch file content
  const onFileSelect = async (filePath: string) => {
    if (!selectedRepo) return;

    try {
      setSelectedFile(filePath);
      // Remove automatic file selection triggering
      const res = await fetch(
        `${GITHUB_API}/${selectedRepo.full_name}/contents/${filePath}`
      );
      const data = await res.json();
      setFileContent(atob(data.content));
    } catch (error) {
      console.error("Error fetching file content:", error);
    }
  };

  const toggleFolder = (folderId: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(folderId)) {
      newExpanded.delete(folderId);
    } else {
      newExpanded.add(folderId);
    }
    setExpandedFolders(newExpanded);
  };

  // Function to fetch GitHub repositories
  const fetchGitHubRepos = async () => {
    setIsLoadingRepos(true);
    setRepoError(null);
    try {
      const user = auth.currentUser;
      if (!user) {
        throw new Error("User not authenticated");
      }

      // Get the GitHub token from the user's provider data
      const githubProvider = user.providerData.find(
        (provider) => provider.providerId === "github.com"
      );

      if (!githubProvider) {
        throw new Error("GitHub account not linked");
      }

      // Get the user's access token
      const token = await user.getIdToken();

      const response = await fetch("https://api.github.com/user/repos", {
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/vnd.github.v3+json",
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error(
            "GitHub authentication failed. Please sign in again."
          );
        }
        throw new Error("Failed to fetch repositories");
      }

      const repos = await response.json();
      setAvailableRepos(Array.isArray(repos) ? repos : []);
    } catch (error) {
      console.error("Error fetching repositories:", error);
      setRepoError(
        error instanceof Error ? error.message : "Failed to fetch repositories"
      );
      setAvailableRepos([]);
    } finally {
      setIsLoadingRepos(false);
    }
  };

  // Function to add a selected repository to projects
  const handleAddRepository = (repo: GitHubRepoData) => {
    const projectData: Project = {
      id: String(repo.id),
      name: repo.name,
      description: repo.description || "No description available",
      status: "active",
      lastModified: new Date(repo.updated_at).toLocaleDateString(),
      collaborators: repo.stargazers_count ?? 0,
      files: [],
      isActive: true,
    };

    setProjects((prevProjects) => {
      // Filter out the project if it already exists and make all others inactive
      const otherProjects = prevProjects
        .filter((p) => p.id !== projectData.id)
        .map((p) => ({ ...p, isActive: false }));

      // Add the new project
      return [...otherProjects, projectData];
    });

    setSelectedProject(projectData);
    setShowRepoListModal(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "deployed":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "draft":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    }
  };

  const renderFileTree = (files: FileItem[], depth = 0) => {
    return files.map((file) => (
      <div key={file.id}>
        <motion.div
          whileHover={{ backgroundColor: "rgba(75, 85, 99, 0.3)" }}
          className={`flex items-center gap-2 p-2 rounded cursor-pointer transition-all duration-200 ${
            selectedFile === file.path
              ? "bg-green-500/20 border-l-2 border-green-500"
              : ""
          }`}
          style={{ paddingLeft: `${(depth + 1) * 16}px` }}
        >
          {file.type === "folder" ? (
            <>
              {/* Chevron icon for expand/collapse */}
              <span
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFolder(file.id);
                }}
                className="flex items-center justify-center"
                style={{ cursor: "pointer" }}
              >
                {expandedFolders.has(file.id) ? (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                )}
              </span>
              {/* Folder icon and name for selection */}
              <span
                onClick={() => {
                  // Optionally, you can select the folder here if needed
                  // setSelectedFile(null);
                }}
                className="flex items-center gap-2 select-none"
                style={{ userSelect: "none" }}
              >
                <FolderOpen className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-gray-200">{file.name}</span>
              </span>
              {file.size && (
                <span className="text-xs text-gray-500 ml-auto">
                  {file.size}
                </span>
              )}
            </>
          ) : (
            <>
              <div className="w-4" />
              <FileCode className="w-4 h-4 text-green-400" />
              <span
                onClick={() => {
                  onFileSelect(file.path!);
                  setSelectedFile(file.path!);
                }}
                className="text-sm text-gray-200"
                style={{ userSelect: "none" }}
              >
                {file.name}
              </span>
              {file.size && (
                <span className="text-xs text-gray-500 ml-auto">
                  {file.size}
                </span>
              )}
            </>
          )}
        </motion.div>

        {file.type === "folder" &&
          file.children &&
          expandedFolders.has(file.id) && (
            <AnimatePresence>
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
              >
                {renderFileTree(file.children, depth + 1)}
              </motion.div>
            </AnimatePresence>
          )}
      </div>
    ));
  };

  return (
    <div className="h-full flex bg-gradient-to-br from-gray-900/50 to-black/50">
      {/* Compact Mode Toggle Button */}
      {isFileSelected && (
        <div className="flex flex-col">
          {/* Compact Section Headers */}
          {isCompactMode && (
            <div className="flex flex-col border-r border-green-500/20 bg-black/20">
              {/* Projects Header */}
              <button
                onClick={() => handleSectionExpand("projects")}
                className={`w-12 h-16 flex items-center justify-center text-sm font-medium transition-all duration-300 border-b border-green-500/20 ${
                  expandedSection === "projects"
                    ? "bg-green-500/20 text-green-400"
                    : "bg-gray-800/30 text-gray-400 hover:text-white hover:bg-gray-700/50"
                }`}
                title="Projects"
              >
                <div className="transform -rotate-90 whitespace-nowrap text-xs py-2">
                  Projects
                </div>
              </button>

              {/* Repository Header */}
              {selectedRepo && (
                <button
                  onClick={() => handleSectionExpand("repository")}
                  className={`w-12 h-20 flex items-center justify-center text-sm font-medium transition-all duration-300 border-b border-green-500/20 ${
                    expandedSection === "repository"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-gray-800/30 text-gray-400 hover:text-white hover:bg-gray-700/50"
                  }`}
                  title="Repository"
                >
                  <div className="transform -rotate-90 whitespace-nowrap text-xs py-2">
                    Repository
                  </div>
                </button>
              )}

              {/* File Explorer Header */}
              {selectedProject && (
                <button
                  onClick={() => handleSectionExpand("fileExplorer")}
                  className={`w-12 h-16 flex items-center justify-center text-sm font-medium transition-all duration-300 border-b border-green-500/20 ${
                    expandedSection === "fileExplorer"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-gray-800/30 text-gray-400 hover:text-white hover:bg-gray-700/50"
                  }`}
                  title="Files"
                >
                  <div className="transform -rotate-90 whitespace-nowrap text-xs py-2">
                    Files
                  </div>
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Projects Sidebar */}
      <div
        className={`border-r border-green-500/20 bg-black/20 backdrop-blur-sm transition-all duration-300 ${
          isCompactMode
            ? expandedSection === "projects"
              ? "w-80"
              : "w-0 overflow-hidden"
            : "w-80"
        }`}
      >
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="p-4 border-b border-green-500/20"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-white">Projects</h2>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 bg-green-500 hover:bg-green-400 rounded-lg text-black transition-all duration-300"
              onClick={(e) => {
                e.stopPropagation();
                const user = auth.currentUser;
                if (!user) {
                  alert("Please sign in to access your GitHub repositories");
                  return;
                }
                setShowRepoListModal(true);
              }}
            >
              <Plus className="w-4 h-4" />
            </motion.button>
          </div>

          {/* Repository List Modal */}
          {showRepoListModal && (
            <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-gray-800 rounded-xl p-6 w-[600px] border border-green-500/20"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-white">
                    Add GitHub Repository
                  </h3>
                  <button
                    onClick={() => setShowRepoListModal(false)}
                    className="text-gray-400 hover:text-white"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="relative mb-4">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search repositories..."
                    value={searchRepoQuery}
                    onChange={(e) => setSearchRepoQuery(e.target.value)}
                    className="w-full bg-gray-900/50 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-green-500/50"
                  />
                </div>

                <div className="max-h-[400px] overflow-y-auto space-y-2">
                  {isLoadingRepos && (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-gray-400">
                        Loading repositories...
                      </div>
                    </div>
                  )}
                  {repoError && (
                    <div className="flex items-center justify-center py-8">
                      <div className="text-red-400">{repoError}</div>
                    </div>
                  )}
                  {!isLoadingRepos &&
                    !repoError &&
                    availableRepos.length === 0 && (
                      <div className="flex items-center justify-center py-8">
                        <div className="text-gray-400">
                          No repositories found
                        </div>
                      </div>
                    )}
                  {!isLoadingRepos &&
                    !repoError &&
                    availableRepos
                      .filter(
                        (repo) =>
                          repo.name
                            .toLowerCase()
                            .includes(searchRepoQuery.toLowerCase()) ||
                          (repo.description &&
                            repo.description
                              .toLowerCase()
                              .includes(searchRepoQuery.toLowerCase()))
                      )
                      .map((repo) => (
                        <motion.div
                          key={repo.id}
                          whileHover={{ scale: 1.01 }}
                          className="p-4 rounded-lg bg-gray-900/50 border border-gray-700 hover:border-green-500/30 cursor-pointer"
                          onClick={() => handleAddRepository(repo)}
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-medium text-white mb-1">
                                {repo.name}
                              </h4>
                              {repo.description && (
                                <p className="text-sm text-gray-400">
                                  {repo.description}
                                </p>
                              )}
                            </div>
                            <div className="flex items-center gap-2 text-xs text-gray-500">
                              {repo.language && (
                                <span className="flex items-center gap-1">
                                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                  {repo.language}
                                </span>
                              )}
                              <span>⭐ {repo.stargazers_count}</span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                </div>
              </motion.div>
            </div>
          )}

          {!isFileSelected && (
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-gray-800/50 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-green-500/50"
              />
            </div>
          )}
        </motion.div>

        <div className="p-4 space-y-3 overflow-y-auto">
          {projects.map((project) => (
            <motion.div
              key={project.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={(e) => {
                e.stopPropagation();
                // Set the clicked project as active and others as inactive
                setProjects((prevProjects) =>
                  prevProjects.map((p) => ({
                    ...p,
                    isActive: p.id === project.id,
                  }))
                );
                setSelectedProject(project);
              }}
              className={`p-4 rounded-xl cursor-pointer transition-all duration-300 ${
                project.isActive
                  ? "bg-green-500/20 border border-green-500/30"
                  : "bg-gray-800/30 border border-gray-700/50 hover:border-green-500/30"
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-white">{project.name}</h3>
                <span
                  className={`px-2 py-1 rounded text-xs border ${getStatusColor(
                    project.status
                  )}`}
                >
                  {project.status}
                </span>
              </div>
              <p className="text-sm text-gray-400 mb-3">
                {project.description}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {project.lastModified}
                  </div>
                  <div className="flex items-center gap-1">
                    <Users className="w-3 h-3" />
                    {project.collaborators}
                  </div>
                </div>
                <button
                  className="text-gray-400 hover:text-white"
                  onClick={(e) => e.stopPropagation()}
                >
                  <MoreVertical className="w-4 h-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Selected Repository Info */}
      {selectedRepo && (
        <div
          className={`border-r border-green-500/20 bg-black/10 backdrop-blur-sm transition-all duration-300 ${
            isCompactMode
              ? expandedSection === "repository"
                ? "w-80"
                : "w-0 overflow-hidden"
              : "w-80"
          }`}
        >
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="p-4 border-b border-green-500/20"
          >
            <div className="flex items-center gap-2 mb-3">
              <GitBranch className="w-5 h-5 text-green-400" />
              <h3 className="font-medium text-white">Selected Repository</h3>
            </div>

            <div className="bg-gray-800/50 rounded-lg p-4 space-y-3">
              <div>
                <h4 className="font-semibold text-green-400 mb-1">
                  {selectedRepo.name}
                </h4>
                {selectedRepo.description && (
                  <p className="text-sm text-gray-400">
                    {selectedRepo.description}
                  </p>
                )}
              </div>

              <div className="flex items-center gap-4 text-xs text-gray-500">
                {selectedRepo.language && (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span>{selectedRepo.language}</span>
                  </div>
                )}
                <div className="flex items-center gap-1">
                  <span>⭐ {selectedRepo.stargazers_count}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>🍴 {selectedRepo.forks_count}</span>
                </div>
              </div>

              <div className="pt-2 border-t border-gray-700">
                <p className="text-xs text-gray-500">
                  {selectedRepo.private ? "Private" : "Public"} repository
                </p>
                {selectedRepo.updated_at && (
                  <p className="text-xs text-gray-500">
                    Updated:{" "}
                    {new Date(selectedRepo.updated_at).toLocaleDateString()}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <button
                  className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400 border border-green-500/30 rounded-lg py-2 px-3 text-sm transition-all duration-300"
                  onClick={async (e) => {
                    e.stopPropagation();
                    try {
                      // Get the download URL for the repository
                      const downloadUrl = `https://github.com/${selectedRepo.full_name}/archive/refs/heads/main.zip`;

                      // Create a link element
                      const link = document.createElement("a");
                      link.href = downloadUrl;
                      link.download = `${selectedRepo.name}.zip`; // Set the filename

                      // Append to document, click, and remove
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);

                      // Show success message
                      alert(
                        "Repository download started! Check your downloads folder."
                      );
                    } catch (err) {
                      console.error("Failed to download repository:", err);
                      alert("Failed to download repository. Please try again.");
                    }
                  }}
                >
                  Clone Repository
                </button>
                <button
                  className="w-full bg-gray-700/50 hover:bg-gray-700/70 text-gray-300 border border-gray-600 rounded-lg py-2 px-3 text-sm transition-all duration-300"
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(
                      selectedRepo.html_url,
                      "_blank",
                      "noopener,noreferrer"
                    );
                  }}
                >
                  View on GitHub
                </button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* File Explorer */}
      <div
        className={`border-r border-green-500/20 bg-black/10 backdrop-blur-sm transition-all duration-300 ${
          isCompactMode
            ? expandedSection === "fileExplorer"
              ? "w-80"
              : "w-0 overflow-hidden"
            : "w-80"
        }`}
      >
        {selectedProject && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="h-full flex flex-col"
          >
            <div className="p-4 border-b border-green-500/20">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium text-white">
                    {selectedProject.name}
                  </h3>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    className="p-1 text-gray-400 hover:text-white"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Filter className="w-4 h-4" />
                  </button>
                  <button
                    className="p-1 text-gray-400 hover:text-white"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <Upload className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <GitBranch className="w-4 h-4" />
                <span>main</span>
              </div>
            </div>

            <div
              className="flex-1 overflow-y-auto p-2"
              onClick={(e) => e.stopPropagation()}
            >
              {renderFileTree(selectedProject.files)}
            </div>
          </motion.div>
        )}
      </div>

      {/* Code Editor */}
      <div className="flex-1 flex flex-col">
        {selectedFile ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="h-full flex flex-col"
          >
            <div className="p-4 border-b border-green-500/20 bg-black/20 backdrop-blur-sm">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileCode className="w-5 h-5 text-green-400" />
                  <span className="font-medium text-white">{selectedFile}</span>
                </div>
                <div className="flex items-center">
                  <button
                    onClick={toggleCompactMode}
                    className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-all duration-300"
                    title={
                      isCompactMode ? "Expand sections" : "Compact sections"
                    }
                  >
                    {isCompactMode ? (
                      <ChevronRight className="w-4 h-4" />
                    ) : (
                      <Menu className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedFile(null);
                      setIsFileSelected(false);
                      setFileContent("");
                      setShowExplainButton(false);
                      setShowExplanationPanel(false);
                      setShowOptimizationPanel(false);
                      setSelectedCode("");
                      setExplanation(null);
                      setOptimization(null);
                    }}
                    className="p-2 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-lg transition-all duration-300"
                    title="Close file"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>

            <div
              className="flex-1 bg-gray-900 p-6 font-mono text-sm overflow-auto relative"
              onClick={handleClickOutside}
            >
              {fileContent ? (
                <>
                  <pre
                    className="text-gray-300 whitespace-pre-wrap select-text"
                    onMouseUp={handleTextSelection}
                    onKeyUp={handleTextSelection}
                  >
                    {fileContent}
                  </pre>

                  {/* Action Buttons */}
                  {showExplainButton && (
                    <div className="fixed bottom-4 right-4 flex gap-2 z-10">
                      <motion.button
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        onClick={handleExplainCode}
                        disabled={isExplaining || isOptimizing}
                        className="bg-green-500 hover:bg-green-400 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg shadow-lg transition-all duration-300 flex items-center gap-2"
                      >
                        {isExplaining ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Explaining...
                          </>
                        ) : (
                          <>
                            <FileCode className="w-4 h-4" />
                            Explain Code
                          </>
                        )}
                      </motion.button>

                      <motion.button
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        onClick={handleOptimizeCode}
                        disabled={isExplaining || isOptimizing}
                        className="bg-blue-500 hover:bg-blue-400 disabled:bg-gray-600 text-white px-4 py-2 rounded-lg shadow-lg transition-all duration-300 flex items-center gap-2"
                      >
                        {isOptimizing ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Optimizing...
                          </>
                        ) : (
                          <>
                            <Zap className="w-4 h-4" />
                            Optimize Code
                          </>
                        )}
                      </motion.button>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-400">
                  Loading file content...
                </div>
              )}
            </div>

            {/* Explanation Panel */}
            {showExplanationPanel && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-green-500/20 bg-gray-800/50 backdrop-blur-sm max-h-[50vh] overflow-y-auto"
              >
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <FileCode className="w-5 h-5 text-green-400" />
                      <h3 className="font-medium text-white">
                        Code Explanation
                      </h3>
                    </div>
                    <button
                      onClick={() => {
                        setShowExplanationPanel(false);
                        setShowExplainButton(false);
                        setSelectedCode("");
                        setExplanation(null);
                      }}
                      className="p-1 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded transition-all duration-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {selectedCode && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-300 mb-2">
                        Selected Code:
                      </h4>
                      <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-3 max-h-32 overflow-y-auto">
                        <pre className="text-sm text-green-400 whitespace-pre-wrap font-mono">
                          {selectedCode}
                        </pre>
                      </div>
                    </div>
                  )}

                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">
                      Explanation:
                    </h4>
                    <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-4 max-h-80 overflow-y-auto">
                      {isExplaining ? (
                        <div className="flex items-center gap-2 text-gray-400">
                          <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                          Analyzing code...
                        </div>
                      ) : (
                        renderExplanation(explanation)
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Optimization Panel */}
            {showOptimizationPanel && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="border-t border-blue-500/20 bg-gray-800/50 backdrop-blur-sm max-h-[50vh] overflow-y-auto"
              >
                <div className="p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-blue-400" />
                      <h3 className="font-medium text-white">
                        Code Optimization
                      </h3>
                    </div>
                    <button
                      onClick={() => {
                        setShowOptimizationPanel(false);
                        setShowExplainButton(false);
                        setSelectedCode("");
                        setOptimization(null);
                      }}
                      className="p-1 text-gray-400 hover:text-white hover:bg-gray-700/50 rounded transition-all duration-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  {selectedCode && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-300 mb-2">
                        Original Code:
                      </h4>
                      <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-3 max-h-32 overflow-y-auto">
                        <pre className="text-sm text-red-400 whitespace-pre-wrap font-mono">
                          {selectedCode}
                        </pre>
                      </div>
                    </div>
                  )}

                  <div>
                    <h4 className="text-sm font-medium text-gray-300 mb-2">
                      Optimization Result:
                    </h4>
                    <div className="bg-gray-900/70 border border-gray-700 rounded-lg p-4 max-h-80 overflow-y-auto">
                      {isOptimizing ? (
                        <div className="flex items-center gap-2 text-gray-400">
                          <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                          Optimizing code...
                        </div>
                      ) : (
                        renderOptimization(optimization)
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-900/20">
            <div className="text-center">
              <FileCode className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <p className="text-gray-400">
                Select a file to view its contents
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
