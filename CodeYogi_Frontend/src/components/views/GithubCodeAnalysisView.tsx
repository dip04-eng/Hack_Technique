import React, { useState } from "react";
import { GithubCodeAnalysis } from "../../types/chat";
import { motion } from "framer-motion";
import {
  Code,
  ArrowRight,
  FileText,
  Languages,
  Cpu,
  GitPullRequest,
  Star,
} from "lucide-react";

interface GithubCodeAnalysisViewProps {
  data: GithubCodeAnalysis;
  repoName: string;
}

const GithubCodeAnalysisView: React.FC<GithubCodeAnalysisViewProps> = ({
  data,
  repoName,
}) => {
  const [expandedFile, setExpandedFile] = useState<string | null>(null);
  const [showAllFiles, setShowAllFiles] = useState(false);

  // Sort files by importance score in descending order
  const sortedFiles = [...data.file_optimizations].sort(
    (a, b) => b.importance_score - a.importance_score
  );

  // Initially show only top 5 files
  const filesToShow = showAllFiles ? sortedFiles : sortedFiles.slice(0, 5);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-gray-800/70 border border-green-500/20 rounded-2xl p-6 backdrop-blur-sm shadow-lg shadow-green-500/10 w-full"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-green-500/20 rounded-full">
          <Code className="h-6 w-6 text-green-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">
            Code Analysis for {repoName}
          </h3>
          <p className="text-gray-400 text-sm">
            {data.timestamp
              ? new Date(data.timestamp).toLocaleString()
              : "Analysis complete"}
          </p>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-700/40 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">Files Analyzed</p>
          <p className="text-2xl font-bold text-white">
            {data.total_files_analyzed}
          </p>
        </div>
        <div className="bg-gray-700/40 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">Files Optimized</p>
          <p className="text-2xl font-bold text-green-400">
            {data.files_with_optimizations}
          </p>
        </div>
        <div className="bg-gray-700/40 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">Total Optimizations</p>
          <p className="text-2xl font-bold text-green-400">
            {data.total_optimizations}
          </p>
        </div>
        <div className="bg-gray-700/40 rounded-xl p-4">
          <p className="text-gray-400 text-xs mb-1">Repository</p>
          <p className="text-sm font-semibold text-white truncate">
            {data.repository_url}
          </p>
        </div>
      </div>

      {/* Optimizations List */}
      <div className="space-y-4">
        <h4 className="text-white font-bold flex items-center gap-2">
          <FileText className="h-4 w-4" />
          File Optimizations
        </h4>

        {filesToShow.map((file) => (
          <motion.div
            key={file.file_path}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-gray-700/40 border border-gray-600/50 rounded-xl p-4"
          >
            <div
              className="flex justify-between items-start cursor-pointer"
              onClick={() =>
                setExpandedFile(
                  expandedFile === file.file_path ? null : file.file_path
                )
              }
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <div
                    className={`p-1 rounded-md ${getLanguageColor(
                      file.language
                    )}`}
                  >
                    <Languages className="h-4 w-4" />
                  </div>
                  <h5 className="font-medium text-white truncate">
                    {file.file_path}
                  </h5>
                </div>

                <div className="flex items-center gap-2 mt-1">
                  <span
                    className={`text-xs px-2 py-1 rounded-md ${getImportanceColor(
                      file.importance_score
                    )}`}
                  >
                    Importance: {file.importance_score}/5
                  </span>
                  <span className="text-xs text-gray-400">
                    {file.optimizations.length} optimizations
                  </span>
                </div>
              </div>
              <ArrowRight
                className={`h-4 w-4 text-gray-400 transition-transform ${
                  expandedFile === file.file_path ? "rotate-90" : ""
                }`}
              />
            </div>

            {expandedFile === file.file_path && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="mt-4 border-t border-gray-600/30 pt-4"
              >
                <div className="mb-4">
                  <h6 className="text-sm text-gray-300 mb-2 flex items-center gap-1">
                    <Cpu className="h-3 w-3" />
                    Importance Reasons:
                  </h6>
                  <ul className="list-disc list-inside text-xs text-gray-400">
                    {file.importance_reasons.map((reason, idx) => (
                      <li key={idx}>{reason}</li>
                    ))}
                  </ul>
                </div>

                <div className="mb-4">
                  <h6 className="text-sm text-gray-300 mb-2 flex items-center gap-1">
                    <Star className="h-3 w-3" />
                    Optimizations:
                  </h6>
                  <ul className="space-y-2">
                    {file.optimizations.map((opt, idx) => (
                      <li key={idx} className="text-xs text-gray-300">
                        {opt}
                      </li>
                    ))}
                  </ul>
                </div>

                {file.has_diff && (
                  <div>
                    <h6 className="text-sm text-gray-300 mb-2 flex items-center gap-1">
                      <GitPullRequest className="h-3 w-3" />
                      Code Diff Preview:
                    </h6>
                    <div className="bg-gray-900/50 p-3 rounded-md text-xs text-gray-300 font-mono overflow-x-auto whitespace-pre">
                      {file.diff_preview}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </motion.div>
        ))}

        {data.file_optimizations.length > 5 && (
          <button
            className="text-green-400 text-sm hover:text-green-300 transition-colors mt-2 flex items-center gap-1 mx-auto"
            onClick={() => setShowAllFiles(!showAllFiles)}
          >
            {showAllFiles
              ? "Show fewer files"
              : `Show all ${data.file_optimizations.length} files`}
            <ArrowRight
              className={`h-3 w-3 transition-transform ${
                showAllFiles ? "rotate-90" : ""
              }`}
            />
          </button>
        )}
      </div>
    </motion.div>
  );
};

// Helper function to get color based on language
const getLanguageColor = (language: string): string => {
  const languages: Record<string, string> = {
    javascript: "bg-yellow-500/20 text-yellow-300",
    typescript: "bg-blue-500/20 text-blue-300",
    python: "bg-blue-700/20 text-blue-400",
    java: "bg-orange-600/20 text-orange-300",
    ruby: "bg-red-600/20 text-red-300",
    go: "bg-cyan-500/20 text-cyan-300",
    rust: "bg-orange-700/20 text-orange-400",
    php: "bg-purple-500/20 text-purple-300",
  };

  return languages[language.toLowerCase()] || "bg-gray-500/20 text-gray-300";
};

// Helper function to get color based on importance score
const getImportanceColor = (score: number): string => {
  if (score >= 5) return "bg-red-500/20 text-red-300";
  if (score >= 4) return "bg-orange-500/20 text-orange-300";
  if (score >= 3) return "bg-yellow-500/20 text-yellow-300";
  if (score >= 2) return "bg-green-500/20 text-green-300";
  return "bg-blue-500/20 text-blue-300";
};

export default GithubCodeAnalysisView;
