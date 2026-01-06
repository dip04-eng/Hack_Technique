import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Terminal,
  Play,
  Square,
  RotateCcw,
  Download,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { useSelectedRepository } from "../hooks/useSelectedRepository";
import {
  GithubStructureAnalysis,
  RepoAnalysis,
  WorkflowDeployment,
  WorkflowOptimization,
  GithubCodeAnalysis,
  OptimizationPR,
} from "../types/chat";

interface ConsoleLog {
  id: string;
  type: "info" | "success" | "error" | "warning" | "command";
  message: string;
  timestamp: Date;
  data?: any; // For storing API response data
}

interface CommandConsoleProps {
  isActive: boolean;
}

export const CommandConsole: React.FC<CommandConsoleProps> = ({ isActive }) => {
  const { selectedRepo } = useSelectedRepository();
  const [logs, setLogs] = useState<ConsoleLog[]>([
    {
      id: "1",
      type: "info",
      message: "CodeYogi Agent Console v2.1.0 initialized",
      timestamp: new Date(),
    },
    {
      id: "2",
      type: "success",
      message: "Connection to AI services established",
      timestamp: new Date(),
    },
    {
      id: "3",
      type: "info",
      message: "Type 'help' for available commands",
      timestamp: new Date(),
    },
  ]);
  const [command, setCommand] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [expandedLogs, setExpandedLogs] = useState<Record<string, boolean>>({});
  const consoleRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    consoleRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  useEffect(() => {
    if (isActive && !isRunning) {
      simulateAgentExecution();
    }
  }, [isActive]);

  // Analyze repository structure
  const analyzeRepoStructure = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ analyze repo-structure --repo="${selectedRepo.name}"`);
    addLog(
      "info",
      `Analyzing structure of "${selectedRepo.name}" repository...`
    );
    setIsRunning(true);

    try {
      const response = await fetch(
        "http://localhost:8000/analyze-github-structure/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            detailed_analysis: true,
            exclude_patterns: [".git", "node_modules", "__pycache__"],
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to analyze repository structure");
      }

      const data: GithubStructureAnalysis = await response.json();

      // Add log entries with key information
      addLog("success", "Repository structure analysis complete");
      addLog("info", `Project type: ${data.project_type}`);
      addLog("info", `Total files: ${data.structure_metrics.total_files}`);
      addLog(
        "info",
        `Total directories: ${data.structure_metrics.total_directories}`
      );
      addLog(
        "info",
        `Organization score: ${data.structure_metrics.organization_score}/10`
      );

      // Add important suggestions
      if (data.structure_suggestions && data.structure_suggestions.length > 0) {
        addLog("info", "Key suggestions:");
        data.structure_suggestions.slice(0, 3).forEach((suggestion) => {
          addLog("info", `- ${suggestion.folder}: ${suggestion.reason}`);
        });
      }

      // Store the full data for potential use
      addLog("success", "Full analysis data available", data);
    } catch (error) {
      console.error(error);
      addLog(
        "error",
        "Failed to analyze repository structure. See console for details."
      );
    }

    setIsRunning(false);
  };

  // Analyze code for optimizations
  const analyzeCode = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ analyze code --repo="${selectedRepo.name}"`);
    addLog("info", `Analyzing code in "${selectedRepo.name}" repository...`);
    setIsRunning(true);

    try {
      const response = await fetch(
        "http://localhost:8000/analyze-github-code/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            create_pr: false,
            max_files: 20,
            target_languages: ["python", "javascript", "typescript"],
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to analyze GitHub code");
      }

      const data: GithubCodeAnalysis = await response.json();

      // Add log entries with key information
      addLog("success", "Code analysis complete");
      addLog("info", `Files analyzed: ${data.total_files_analyzed}`);
      addLog(
        "info",
        `Files with optimizations: ${data.files_with_optimizations}`
      );
      addLog("info", `Total optimizations: ${data.total_optimizations}`);

      // Show a few optimization examples
      if (data.file_optimizations && data.file_optimizations.length > 0) {
        addLog("info", "Key optimization opportunities:");
        data.file_optimizations.slice(0, 3).forEach((file) => {
          addLog(
            "info",
            `- ${file.file_path}: ${file.optimizations.length} optimizations`
          );
          file.optimizations.slice(0, 2).forEach((opt) => {
            addLog(
              "info",
              `  • ${opt.substring(0, 80)}${opt.length > 80 ? "..." : ""}`
            );
          });
        });
      }

      // Store the full data for potential use
      addLog("success", "Full optimization data available", data);
    } catch (error) {
      console.error(error);
      addLog("error", "Failed to analyze code. See console for details.");
    }

    setIsRunning(false);
  };

  // Optimize workflow
  const optimizeWorkflow = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ optimize workflow --repo="${selectedRepo.name}"`);
    addLog(
      "info",
      `Optimizing workflow for "${selectedRepo.name}" repository...`
    );
    setIsRunning(true);

    try {
      const response = await fetch("http://localhost:8000/optimize-workflow/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          repo_url: selectedRepo.html_url,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to optimize workflow");
      }

      const data: WorkflowOptimization = await response.json();

      // Add log entries with key information
      addLog("success", "Workflow optimization complete");
      addLog("info", `Workflow: ${data.optimized_workflow.workflow_name}`);
      addLog(
        "info",
        `Optimization type: ${data.optimized_workflow.optimization_type}`
      );
      addLog(
        "info",
        `Time savings: ${data.optimized_workflow.estimated_time_savings}`
      );

      // Show improvements
      if (
        data.optimized_workflow.improvements &&
        data.optimized_workflow.improvements.length > 0
      ) {
        addLog("info", "Key improvements:");
        data.optimized_workflow.improvements.forEach((improvement) => {
          addLog("info", `- ${improvement}`);
        });
      }

      // Show implementation steps
      if (
        data.recommendations.implementation_steps &&
        data.recommendations.implementation_steps.length > 0
      ) {
        addLog("info", "Implementation steps:");
        data.recommendations.implementation_steps
          .slice(0, 3)
          .forEach((step, i) => {
            addLog("info", `${i + 1}. ${step}`);
          });
      }

      // Store the full data for potential use
      addLog("success", "Full workflow optimization data available", data);
    } catch (error) {
      console.error(error);
      addLog("error", "Failed to optimize workflow. See console for details.");
    }

    setIsRunning(false);
  };

  // Create optimization PR
  const createOptimizationPR = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ create optimization-pr --repo="${selectedRepo.name}"`);
    addLog(
      "info",
      `Creating optimization PR for "${selectedRepo.name}" repository...`
    );
    setIsRunning(true);

    try {
      const response = await fetch(
        "http://localhost:8000/create-optimization-pr/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            github_token: "", // Token would need to be provided by the user or stored securely
            auto_merge: false,
            branch_name: `codeyogi-optimization-${new Date().getFullYear()}`,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create optimization PR");
      }

      const data: OptimizationPR = await response.json();

      // Add log entries with key information
      addLog(
        "success",
        `PR #${data.pr_number} created successfully: ${data.pr_url}`
      );
      addLog("info", `Files optimized: ${data.files_optimized}`);
      addLog("info", `Optimizations: ${data.optimizations_count}`);
      addLog("info", `Auto-merged: ${data.auto_merged ? "Yes" : "No"}`);

      // Store the full data for potential use
      addLog("success", "Full PR data available", data);
    } catch (error) {
      console.error(error);
      addLog(
        "error",
        "Failed to create optimization PR. See console for details."
      );
    }

    setIsRunning(false);
  };

  // Deploy workflow
  const deployWorkflow = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ deploy workflow --repo="${selectedRepo.name}"`);
    addLog(
      "info",
      `Deploying optimized workflow to "${selectedRepo.name}" repository...`
    );
    setIsRunning(true);

    try {
      const response = await fetch(
        "http://localhost:8000/optimize-workflow-deployment/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            repo_url: selectedRepo.html_url,
            github_token: "",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to deploy workflow");
      }

      const data: WorkflowDeployment = await response.json();

      // Add log entries with key information
      addLog("success", "Workflow deployment complete");

      if (data.pr_info) {
        addLog(
          "success",
          `PR #${data.pr_info.pr_number} created: ${data.pr_info.pr_url}`
        );
        addLog("info", `Branch: ${data.pr_info.branch_name}`);
        addLog("info", `Workflow path: ${data.pr_info.workflow_path}`);
      }

      // Add recommendations
      const recommendations = data.optimization_analysis?.recommendations;
      if (recommendations) {
        addLog("info", "Implementation steps:");
        recommendations.implementation_steps.slice(0, 3).forEach((step, i) => {
          addLog("info", `${i + 1}. ${step}`);
        });
      }

      // Store the full data for potential use
      addLog("success", "Full deployment data available", data);
    } catch (error) {
      console.error(error);
      addLog("error", "Failed to deploy workflow. See console for details.");
    }

    setIsRunning(false);
  };

  // Describe repository
  const describeRepo = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    addLog("command", `$ describe repo --repo="${selectedRepo.name}"`);
    addLog("info", `Analyzing "${selectedRepo.name}" repository...`);
    setIsRunning(true);

    try {
      const response = await fetch(
        "http://localhost:8000/describe-repository/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            repo_owner: selectedRepo.owner.login,
            repo_name: selectedRepo.name,
            include_tech_stack: true,
            include_architecture: true,
            include_features: true,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to analyze repository");
      }

      const data: RepoAnalysis = await response.json();

      // Add log entries with key information
      addLog("success", "Repository analysis complete");
      addLog("info", `Project type: ${data.project_type}`);

      // Tech stack
      if (data.tech_stack) {
        addLog("info", "Tech stack:");
        Object.entries(data.tech_stack)
          .slice(0, 3)
          .forEach(([category, techs]) => {
            addLog("info", `- ${category}: ${techs.join(", ")}`);
          });
      }

      // Key features
      if (data.key_features && data.key_features.length > 0) {
        addLog("info", "Key features:");
        data.key_features.slice(0, 5).forEach((feature) => {
          addLog("info", `- ${feature}`);
        });
      }

      // Architecture
      if (data.architecture_summary) {
        addLog(
          "info",
          `Architecture: ${data.architecture_summary.substring(0, 100)}...`
        );
      }

      // Store the full data for potential use
      addLog("success", "Full analysis data available", data);
    } catch (error) {
      console.error(error);
      addLog("error", "Failed to analyze repository. See console for details.");
    }

    setIsRunning(false);
  };

  // Helper function to add logs
  const addLog = (type: ConsoleLog["type"], message: string, data?: any) => {
    setLogs((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        type,
        message,
        timestamp: new Date(),
        data,
      },
    ]);
  };

  // Toggle expanded state of a log
  const toggleLogExpand = (logId: string) => {
    setExpandedLogs((prev) => ({
      ...prev,
      [logId]: !prev[logId],
    }));
  };

  // Demo functionality
  const simulateAgentExecution = async () => {
    if (!selectedRepo) {
      addLog(
        "error",
        "No repository selected. Please select a repository first."
      );
      return;
    }

    setIsRunning(true);
    addLog(
      "command",
      `$ codeyogi agent run --optimize --repo="${selectedRepo.name}"`
    );

    const executionSteps = [
      { type: "info", message: "Initializing optimization agent..." },
      { type: "info", message: "Analyzing codebase structure..." },
      { type: "success", message: "Found 15 optimization opportunities" },
      { type: "info", message: "Applying performance improvements..." },
      { type: "success", message: "Bundle size reduced by 23%" },
      { type: "success", message: "Load time improved by 1.2s" },
      { type: "info", message: "Running automated tests..." },
      { type: "success", message: "All tests passed ✓" },
      { type: "success", message: "Optimization complete! 🚀" },
    ];

    for (let i = 0; i < executionSteps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 800));
      const step = executionSteps[i];
      addLog(step.type as ConsoleLog["type"], step.message);
    }

    setIsRunning(false);
  };

  const handleRunCommand = async () => {
    if (!command.trim()) return;

    const cmdLower = command.toLowerCase().trim();
    addLog("command", `$ ${command}`);
    setCommand("");
    setIsRunning(true);

    // Process different commands
    if (cmdLower === "help" || cmdLower === "--help" || cmdLower === "-h") {
      addLog("info", "Available commands:");
      addLog(
        "info",
        "  analyze repo-structure - Analyze repository file structure"
      );
      addLog(
        "info",
        "  analyze code - Analyze code for optimization opportunities"
      );
      addLog("info", "  optimize workflow - Optimize CI/CD workflows");
      addLog(
        "info",
        "  create optimization-pr - Create a PR with optimizations"
      );
      addLog("info", "  deploy workflow - Deploy optimized workflow");
      addLog("info", "  describe repo - Get repository overview");
      addLog("info", "  clear - Clear the console");
    } else if (
      cmdLower.includes("analyze repo-structure") ||
      cmdLower.includes("analyze structure")
    ) {
      await analyzeRepoStructure();
    } else if (cmdLower.includes("analyze code")) {
      await analyzeCode();
    } else if (cmdLower.includes("optimize workflow")) {
      await optimizeWorkflow();
    } else if (
      cmdLower.includes("create optimization-pr") ||
      cmdLower.includes("create pr")
    ) {
      await createOptimizationPR();
    } else if (cmdLower.includes("deploy workflow")) {
      await deployWorkflow();
    } else if (cmdLower.includes("describe repo")) {
      await describeRepo();
    } else if (cmdLower === "clear") {
      clearConsole();
      addLog("info", "Console cleared");
    } else {
      addLog("error", `Unknown command: ${command}`);
      addLog("info", "Type 'help' to see available commands");
    }

    if (cmdLower !== "clear") {
      setIsRunning(false);
    }
  };

  const clearConsole = () => {
    setLogs([]);
  };

  const getLogColor = (type: string) => {
    switch (type) {
      case "success":
        return "text-green-400";
      case "error":
        return "text-red-400";
      case "warning":
        return "text-yellow-400";
      case "command":
        return "text-cyan-400";
      default:
        return "text-gray-300";
    }
  };

  const getLogPrefix = (type: string) => {
    switch (type) {
      case "success":
        return "[✓]";
      case "error":
        return "[✗]";
      case "warning":
        return "[!]";
      case "command":
        return "";
      default:
        return "[i]";
    }
  };

  return (
    <div className="h-full flex flex-col bg-black/90">
      {/* Console Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 border-b border-green-500/30 bg-gray-900/50"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: isRunning ? 360 : 0 }}
              transition={{
                duration: 2,
                repeat: isRunning ? Infinity : 0,
                ease: "linear",
              }}
              className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center"
            >
              <Terminal className="w-4 h-4 text-black" />
            </motion.div>
            <div>
              <h2 className="text-lg font-bold text-green-400">
                Agent Command Console
              </h2>
              <p className="text-xs text-gray-400">
                Execute AI agents and monitor operations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={simulateAgentExecution}
              disabled={isRunning}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 rounded-lg text-black font-medium transition-all duration-300"
            >
              {isRunning ? (
                <Square className="w-4 h-4" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {isRunning ? "Running..." : "Run Agent"}
            </motion.button>

            <button
              onClick={clearConsole}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-300"
            >
              <RotateCcw className="w-4 h-4" />
            </button>

            <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all duration-300">
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Console Output */}
      <div className="flex-1 overflow-y-auto p-4 font-mono text-sm bg-black">
        <AnimatePresence>
          {logs.map((log, index) => (
            <React.Fragment key={log.id}>
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
                className={`flex items-start gap-2 mb-1.5 ${getLogColor(
                  log.type
                )}`}
              >
                <span className="text-xs text-gray-500 w-16 flex-shrink-0 opacity-70">
                  {log.timestamp.toLocaleTimeString().split(" ")[0]}
                </span>
                <span className="w-8 flex-shrink-0 text-xs font-bold">
                  {getLogPrefix(log.type)}
                </span>
                <span className="flex-1 font-mono">
                  {log.type === "command" ? (
                    <span className="text-cyan-400">{log.message}</span>
                  ) : (
                    log.message
                  )}
                  {log.data && log.data.timestamp && (
                    <span className="text-xs text-gray-500 ml-2">
                      {new Date(log.data.timestamp).toLocaleString()}
                    </span>
                  )}
                </span>
                {isRunning && index === logs.length - 1 && (
                  <motion.div
                    animate={{ opacity: [1, 0] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="w-2 h-4 bg-green-400 ml-1"
                  />
                )}
                {log.data && (
                  <button
                    onClick={() => toggleLogExpand(log.id)}
                    className="text-xs text-green-500 hover:text-green-400 ml-1 p-1 rounded hover:bg-gray-800"
                    title={
                      expandedLogs[log.id]
                        ? "Collapse details"
                        : "Expand details"
                    }
                  >
                    {expandedLogs[log.id] ? (
                      <ChevronUp size={14} />
                    ) : (
                      <ChevronDown size={14} />
                    )}
                  </button>
                )}
              </motion.div>

              {/* Expanded Log Content */}
              {expandedLogs[log.id] && log.data && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="ml-24 mb-3 pl-3 border-l-2 border-green-700 bg-gray-900/30 rounded-r-md mt-1"
                >
                  {/* Display Different Data Types */}
                  {log.data.file_optimizations && (
                    <div className="text-gray-300 text-xs">
                      <div className="text-green-400 mb-1">
                        Optimization Details:
                      </div>
                      {log.data.file_optimizations
                        .slice(0, 10)
                        .map((file: any, i: number) => (
                          <div key={i} className="mb-2">
                            <div className="text-cyan-400">
                              {file.file_path} ({file.optimizations.length}{" "}
                              optimizations)
                            </div>
                            <ul className="pl-4">
                              {file.optimizations.map(
                                (opt: string, j: number) => (
                                  <li
                                    key={j}
                                    className="text-gray-400 mb-1 list-disc"
                                  >
                                    {opt}
                                  </li>
                                )
                              )}
                            </ul>
                          </div>
                        ))}
                      {log.data.file_optimizations.length > 10 && (
                        <div className="text-gray-500 mt-1">
                          And {log.data.file_optimizations.length - 10} more
                          files...
                        </div>
                      )}
                    </div>
                  )}

                  {log.data.structure_suggestions && (
                    <div className="text-gray-300 text-xs">
                      <div className="text-green-400 mb-1">
                        Structure Suggestions:
                      </div>
                      {log.data.structure_suggestions.map(
                        (suggestion: any, i: number) => (
                          <div key={i} className="mb-2">
                            <div className="text-cyan-400">
                              {suggestion.folder} ({suggestion.priority})
                            </div>
                            <div className="text-gray-400 mb-1">
                              {suggestion.reason}
                            </div>
                            {suggestion.suggested_subfolders && (
                              <div className="text-gray-500">
                                Suggested subfolders:{" "}
                                {suggestion.suggested_subfolders.join(", ")}
                              </div>
                            )}
                          </div>
                        )
                      )}
                    </div>
                  )}

                  {log.data.optimized_workflow && (
                    <div className="text-gray-300 text-xs">
                      <div className="text-green-400 mb-1">
                        Workflow Details:
                      </div>
                      <div className="text-gray-400 whitespace-pre-wrap">
                        <code className="bg-gray-800 p-2 block rounded">
                          {log.data.optimized_workflow.workflow_content}
                        </code>
                      </div>
                    </div>
                  )}

                  {log.data.pr_info && (
                    <div className="text-gray-300 text-xs">
                      <div className="text-green-400 mb-1">PR Details:</div>
                      <div>PR Number: {log.data.pr_info.pr_number}</div>
                      <div>Branch: {log.data.pr_info.branch_name}</div>
                      <div>
                        <a
                          href={log.data.pr_info.pr_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 underline"
                        >
                          View PR
                        </a>
                      </div>
                    </div>
                  )}

                  {/* Generic JSON Viewer */}
                  {!log.data.file_optimizations &&
                    !log.data.structure_suggestions &&
                    !log.data.optimized_workflow &&
                    !log.data.pr_info && (
                      <pre className="text-gray-300 text-xs overflow-auto max-h-80 whitespace-pre-wrap bg-gray-900 p-2 rounded">
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    )}
                </motion.div>
              )}
            </React.Fragment>
          ))}
        </AnimatePresence>
        <div ref={consoleRef} />
      </div>

      {/* Command Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-4 border-t border-green-500/30 bg-gray-900/50"
      >
        <div className="flex items-center gap-3">
          <span className="text-green-400 font-mono">$</span>
          <input
            type="text"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleRunCommand()}
            placeholder="Enter agent command..."
            className="flex-1 bg-transparent border-none outline-none text-green-300 font-mono placeholder-gray-500"
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRunCommand}
            disabled={!command.trim() || isRunning}
            className="px-4 py-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 rounded text-black font-medium transition-all duration-300"
          >
            Execute
          </motion.button>
        </div>

        {/* Quick Commands */}
        <div className="flex gap-2 mt-3">
          {[
            "analyze code",
            "analyze repo-structure",
            "optimize workflow",
            "create optimization-pr",
            "describe repo",
          ].map((cmd) => (
            <motion.button
              key={cmd}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setCommand(cmd)}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded text-xs text-gray-300 hover:text-white transition-all duration-300"
            >
              {cmd}
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
};
