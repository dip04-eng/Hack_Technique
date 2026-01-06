import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AlertTriangle,
  Search,
  FileCode,
  TrendingUp,
  CheckCircle,
  XCircle,
  GitBranch,
  Terminal,
  Loader2,
} from "lucide-react";

interface AnalysisResult {
  summary: string;
  root_cause: string;
  affected_file: string;
  affected_line: string;
  impact: string;
  confidence: number;
  suggested_fix: string;
  detected_patterns?: Record<string, any>;
}

export const DeployFailureAnalysis: React.FC = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [gitDiff, setGitDiff] = useState("");
  const [pipelineLogs, setPipelineLogs] = useState("");
  const [runtimeLogs, setRuntimeLogs] = useState("");
  const [deploymentEnv, setDeploymentEnv] = useState("production");

  const handleAnalysis = async () => {
    if (!gitDiff || !runtimeLogs) {
      alert("Please provide at least Git Diff and Runtime Logs");
      return;
    }

    setIsAnalyzing(true);

    try {
      const response = await fetch("http://localhost:8000/api/post-deploy-analysis", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          git_diff: gitDiff,
          pipeline_logs: pipelineLogs,
          runtime_logs: runtimeLogs,
          deployment_env: deploymentEnv,
        }),
      });

      if (!response.ok) {
        throw new Error("Analysis failed");
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error("Analysis error:", error);
      alert("Failed to analyze deployment failure. Check console for details.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setGitDiff("");
    setPipelineLogs("");
    setRuntimeLogs("");
    setAnalysisResult(null);
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.7) return "text-green-400";
    if (confidence >= 0.5) return "text-yellow-400";
    return "text-red-400";
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.7) return "High";
    if (confidence >= 0.5) return "Medium";
    return "Low";
  };

  return (
    <div className="h-full overflow-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/20">
            <AlertTriangle className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">
              Post-Deploy Failure Analysis
            </h2>
            <p className="text-sm text-gray-400">
              SRE AI-powered root cause analysis
            </p>
          </div>
        </div>
        <button
          onClick={handleClear}
          className="px-4 py-2 rounded-lg bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 hover:text-white transition-all"
        >
          Clear All
        </button>
      </div>

      {!analysisResult ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Input Form */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Git Diff */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
                <GitBranch className="w-4 h-4" />
                Git Diff (Required)
              </label>
              <textarea
                value={gitDiff}
                onChange={(e) => setGitDiff(e.target.value)}
                placeholder="Paste git diff between last successful and current deployment..."
                className="w-full h-48 px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700/50 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-accent-theme/50 resize-none font-mono text-sm"
              />
            </div>

            {/* Runtime Logs */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
                <Terminal className="w-4 h-4" />
                Runtime/Production Logs (Required)
              </label>
              <textarea
                value={runtimeLogs}
                onChange={(e) => setRuntimeLogs(e.target.value)}
                placeholder="Paste production error logs, stack traces, metrics..."
                className="w-full h-48 px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700/50 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-accent-theme/50 resize-none font-mono text-sm"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pipeline Logs */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
                <FileCode className="w-4 h-4" />
                CI/CD Pipeline Logs (Optional)
              </label>
              <textarea
                value={pipelineLogs}
                onChange={(e) => setPipelineLogs(e.target.value)}
                placeholder="Paste CI/CD pipeline logs..."
                className="w-full h-32 px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700/50 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-accent-theme/50 resize-none font-mono text-sm"
              />
            </div>

            {/* Environment */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-300">
                <TrendingUp className="w-4 h-4" />
                Deployment Environment
              </label>
              <select
                value={deploymentEnv}
                onChange={(e) => setDeploymentEnv(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-gray-800/50 border border-gray-700/50 text-gray-200 focus:outline-none focus:border-accent-theme/50"
              >
                <option value="production">Production</option>
                <option value="staging">Staging</option>
                <option value="development">Development</option>
              </select>
            </div>
          </div>

          {/* Analyze Button */}
          <div className="flex justify-center pt-4">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleAnalysis}
              disabled={isAnalyzing || !gitDiff || !runtimeLogs}
              className={`
                flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-white
                ${
                  isAnalyzing || !gitDiff || !runtimeLogs
                    ? "bg-gray-700 cursor-not-allowed opacity-50"
                    : "bg-gradient-to-r from-red-500 to-orange-500 hover:shadow-lg hover:shadow-red-500/20"
                }
                transition-all duration-300
              `}
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Analyzing Deployment Failure...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Analyze Root Cause
                </>
              )}
            </motion.button>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
              <h4 className="text-sm font-semibold text-blue-400 mb-2">
                🔍 Pattern Detection
              </h4>
              <p className="text-xs text-gray-400">
                Automatically detects blocking loops, DB queries, memory leaks,
                and more
              </p>
            </div>
            <div className="p-4 rounded-xl bg-green-500/10 border border-green-500/20">
              <h4 className="text-sm font-semibold text-green-400 mb-2">
                🎯 AI-Powered
              </h4>
              <p className="text-xs text-gray-400">
                Uses Groq Llama 3.3 70B for expert SRE-level analysis
              </p>
            </div>
            <div className="p-4 rounded-xl bg-purple-500/10 border border-purple-500/20">
              <h4 className="text-sm font-semibold text-purple-400 mb-2">
                💡 Actionable Fixes
              </h4>
              <p className="text-xs text-gray-400">
                Provides concrete solutions with confidence scores
              </p>
            </div>
          </div>
        </motion.div>
      ) : (
        <AnimatePresence>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            {/* Result Header */}
            <div className="p-6 rounded-2xl bg-gradient-to-br from-gray-800/50 to-gray-900/50 border border-gray-700/50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <AlertTriangle className="w-6 h-6 text-orange-400" />
                    <h3 className="text-xl font-bold text-white">
                      Analysis Complete
                    </h3>
                  </div>
                  <p className="text-lg text-gray-300">
                    {analysisResult.summary}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <div
                    className={`px-4 py-2 rounded-lg bg-gray-800/50 border ${
                      analysisResult.confidence >= 0.7
                        ? "border-green-500/30"
                        : analysisResult.confidence >= 0.5
                        ? "border-yellow-500/30"
                        : "border-red-500/30"
                    }`}
                  >
                    <div className="text-xs text-gray-400">Confidence</div>
                    <div
                      className={`text-2xl font-bold ${getConfidenceColor(
                        analysisResult.confidence
                      )}`}
                    >
                      {(analysisResult.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-400">
                      {getConfidenceLabel(analysisResult.confidence)}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Root Cause */}
            <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20">
              <h4 className="flex items-center gap-2 text-lg font-semibold text-red-400 mb-3">
                <XCircle className="w-5 h-5" />
                Root Cause
              </h4>
              <p className="text-gray-300 leading-relaxed">
                {analysisResult.root_cause}
              </p>
            </div>

            {/* Affected Code */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h5 className="text-sm font-semibold text-gray-400 mb-2">
                  Affected File
                </h5>
                <p className="text-white font-mono text-sm">
                  {analysisResult.affected_file}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-gray-800/50 border border-gray-700/50">
                <h5 className="text-sm font-semibold text-gray-400 mb-2">
                  Affected Location
                </h5>
                <p className="text-white font-mono text-sm">
                  {analysisResult.affected_line}
                </p>
              </div>
            </div>

            {/* User Impact */}
            <div className="p-6 rounded-2xl bg-orange-500/10 border border-orange-500/20">
              <h4 className="flex items-center gap-2 text-lg font-semibold text-orange-400 mb-3">
                <AlertTriangle className="w-5 h-5" />
                User Impact
              </h4>
              <p className="text-gray-300">{analysisResult.impact}</p>
            </div>

            {/* Suggested Fix */}
            <div className="p-6 rounded-2xl bg-green-500/10 border border-green-500/20">
              <h4 className="flex items-center gap-2 text-lg font-semibold text-green-400 mb-3">
                <CheckCircle className="w-5 h-5" />
                Suggested Fix
              </h4>
              <p className="text-gray-300 leading-relaxed">
                {analysisResult.suggested_fix}
              </p>
            </div>

            {/* Detected Patterns */}
            {analysisResult.detected_patterns &&
              Object.keys(analysisResult.detected_patterns).length > 0 && (
                <div className="p-6 rounded-2xl bg-purple-500/10 border border-purple-500/20">
                  <h4 className="flex items-center gap-2 text-lg font-semibold text-purple-400 mb-3">
                    🔎 Detected Patterns
                  </h4>
                  <div className="space-y-2">
                    {Object.entries(analysisResult.detected_patterns).map(
                      ([pattern, data]: [string, any]) => (
                        <div
                          key={pattern}
                          className="flex items-center justify-between p-3 rounded-lg bg-gray-800/30"
                        >
                          <span className="text-gray-300 font-medium">
                            {pattern.replace(/_/g, " ").toUpperCase()}
                          </span>
                          <span
                            className={`text-sm px-2 py-1 rounded ${
                              data.severity === "critical"
                                ? "bg-red-500/20 text-red-400"
                                : data.severity === "high"
                                ? "bg-orange-500/20 text-orange-400"
                                : "bg-yellow-500/20 text-yellow-400"
                            }`}
                          >
                            {data.severity}
                          </span>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

            {/* Action Buttons */}
            <div className="flex justify-center gap-4 pt-4">
              <button
                onClick={handleClear}
                className="px-6 py-3 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 hover:text-white font-semibold transition-all"
              >
                New Analysis
              </button>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(
                    JSON.stringify(analysisResult, null, 2)
                  );
                  alert("Analysis copied to clipboard!");
                }}
                className="px-6 py-3 rounded-xl bg-accent-theme/20 hover:bg-accent-theme/30 text-accent-theme font-semibold transition-all"
              >
                Copy Results
              </button>
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
};
