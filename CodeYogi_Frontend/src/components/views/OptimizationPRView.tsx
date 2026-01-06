import React from "react";
import { OptimizationPR } from "../../types/chat";
import { motion } from "framer-motion";
import {
  GitPullRequest,
  CheckCircle,
  XCircle,
  Code,
  FileText,
  Clock,
} from "lucide-react";

interface OptimizationPRViewProps {
  data: OptimizationPR;
  repoName: string;
}

const OptimizationPRView: React.FC<OptimizationPRViewProps> = ({
  data,
  repoName,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="bg-gray-800/70 border border-green-500/20 rounded-2xl p-6 backdrop-blur-sm shadow-lg shadow-green-500/10 w-full"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-3 bg-green-500/20 rounded-full">
          <GitPullRequest className="h-6 w-6 text-green-400" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">
            Optimization PR for {repoName}
          </h3>
          <p className="text-gray-400 text-sm">
            {data.timestamp
              ? new Date(data.timestamp).toLocaleString()
              : "Just now"}
          </p>
        </div>
      </div>

      {/* PR Status Banner */}
      <div
        className={`p-4 rounded-xl mb-6 flex items-center gap-3 ${
          data.success ? "bg-green-500/20" : "bg-red-500/20"
        }`}
      >
        {data.success ? (
          <CheckCircle className="h-6 w-6 text-green-400" />
        ) : (
          <XCircle className="h-6 w-6 text-red-400" />
        )}
        <div>
          <h4
            className={`font-bold ${
              data.success ? "text-green-400" : "text-red-400"
            }`}
          >
            {data.success
              ? "Pull Request Created Successfully!"
              : "Failed to Create Pull Request"}
          </h4>
          <p className="text-gray-300 text-sm">
            {data.success
              ? `PR #${data.pr_number} is ready for review`
              : data.error_message || "An error occurred during PR creation"}
          </p>
        </div>
      </div>

      {/* PR Details */}
      {data.success && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-700/40 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">Files Optimized</p>
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-blue-400" />
                <p className="text-2xl font-bold text-white">
                  {data.files_optimized}
                </p>
              </div>
            </div>
            <div className="bg-gray-700/40 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">Total Optimizations</p>
              <div className="flex items-center gap-2">
                <Code className="h-4 w-4 text-green-400" />
                <p className="text-2xl font-bold text-green-400">
                  {data.optimizations_count}
                </p>
              </div>
            </div>
            <div className="bg-gray-700/40 rounded-xl p-4">
              <p className="text-gray-400 text-xs mb-1">Auto-Merged</p>
              <div className="flex items-center gap-2">
                {data.auto_merged ? (
                  <CheckCircle className="h-4 w-4 text-green-400" />
                ) : (
                  <Clock className="h-4 w-4 text-yellow-400" />
                )}
                <p className="text-xl font-bold text-white">
                  {data.auto_merged ? "Yes" : "Awaiting Review"}
                </p>
              </div>
            </div>
          </div>

          {/* PR Link */}
          <div className="bg-gray-700/40 rounded-xl p-4">
            <p className="text-gray-400 text-xs mb-2">Pull Request Link</p>
            <a
              href={data.pr_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-2"
            >
              <GitPullRequest className="h-4 w-4" />
              <span className="break-all">{data.pr_url}</span>
            </a>
          </div>

          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              The pull request has been created with optimizations to improve
              code quality and performance.
              {!data.auto_merged && " Please review and merge when ready."}
            </p>
          </div>
        </>
      )}

      {/* Error Details */}
      {!data.success && data.error_message && (
        <div className="bg-gray-700/40 rounded-xl p-4 mt-4">
          <p className="text-gray-400 text-xs mb-2">Error Details</p>
          <p className="text-gray-300 whitespace-pre-wrap font-mono text-sm">
            {data.error_message}
          </p>
        </div>
      )}
    </motion.div>
  );
};

export default OptimizationPRView;
