import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ExternalLink,
  GitBranch,
  FileText,
  CheckCircle,
  Copy,
  Eye,
  EyeOff,
  Calendar,
  Folder,
  Code,
  Package,
} from "lucide-react";

interface ReadmeGeneratorData {
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

interface ReadmeGeneratorViewProps {
  data: ReadmeGeneratorData;
  repoName: string;
}

const ReadmeGeneratorView: React.FC<ReadmeGeneratorViewProps> = ({ data }) => {
  const [showReadmePreview, setShowReadmePreview] = useState(false);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const copyToClipboard = async (text: string | null, label: string) => {
    if (!text) {
      console.warn("No text to copy");
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(label);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  // Convert markdown to basic HTML for preview
  const markdownToHtml = (markdown: string | null) => {
    if (!markdown) {
      return '<p class="text-gray-500">No README content available</p>';
    }
    return markdown
      .replace(
        /^# (.*$)/gim,
        '<h1 class="text-2xl font-bold text-green-400 mb-4">$1</h1>'
      )
      .replace(
        /^## (.*$)/gim,
        '<h2 class="text-xl font-semibold text-green-300 mb-3 mt-6">$1</h2>'
      )
      .replace(
        /^### (.*$)/gim,
        '<h3 class="text-lg font-semibold text-green-200 mb-2 mt-4">$1</h3>'
      )
      .replace(
        /\*\*(.*?)\*\*/g,
        '<strong class="font-semibold text-white">$1</strong>'
      )
      .replace(/\*(.*?)\*/g, '<em class="italic text-gray-300">$1</em>')
      .replace(
        /`(.*?)`/g,
        '<code class="bg-gray-800 px-2 py-1 rounded text-green-400 font-mono text-sm">$1</code>'
      )
      .replace(
        /```([^`]+)```/g,
        '<pre class="bg-gray-900 p-4 rounded-lg border border-gray-700 my-4 overflow-x-auto"><code class="text-green-400 font-mono text-sm">$1</code></pre>'
      )
      .replace(/^\- (.*$)/gim, '<li class="text-gray-300 mb-1">$1</li>')
      .replace(
        /\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-green-400 hover:text-green-300 underline">$1</a>'
      )
      .replace(
        /!\[([^\]]*)\]\(([^)]+)\)/g,
        '<img src="$2" alt="$1" class="inline-block mr-2 mb-1" />'
      )
      .replace(/\n/g, "<br />");
  };

  return (
    <div className="bg-gray-900/95 border border-green-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur-sm">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-6"
      >
        <div className="flex items-center gap-3">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            className="w-10 h-10 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full flex items-center justify-center"
          >
            <FileText className="w-5 h-5 text-black" />
          </motion.div>
          <div>
            <h3 className="text-xl font-bold text-green-400 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              README Generated Successfully
            </h3>
            <p className="text-gray-400 text-sm">
              Pull Request created for {data.repository || "repository"}
            </p>
          </div>
        </div>
        {data.pull_request_url && (
          <motion.a
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            href={data.pull_request_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-black rounded-lg font-medium hover:shadow-lg hover:shadow-green-500/25 transition-all duration-300"
          >
            <ExternalLink className="w-4 h-4" />
            View PR #{data.pull_request_number}
          </motion.a>
        )}
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-black/30 rounded-xl p-4 border border-green-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <GitBranch className="w-4 h-4 text-green-400" />
            <span className="text-green-400 font-semibold">Branch</span>
          </div>
          <p className="text-white font-mono text-sm">{data.branch_name || "N/A"}</p>
          <button
            onClick={() => copyToClipboard(data.branch_name, "branch")}
            className="mt-2 text-xs text-gray-400 hover:text-green-400 flex items-center gap-1"
          >
            <Copy className="w-3 h-3" />
            {copiedText === "branch" ? "Copied!" : "Copy"}
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-black/30 rounded-xl p-4 border border-green-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Code className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 font-semibold">Project Type</span>
          </div>
          <p className="text-white text-sm">
            {data.analysis_summary?.project_type || "Unknown"}
          </p>
          <p className="text-gray-400 text-xs mt-1">
            {data.analysis_summary?.total_files || 0} files •{" "}
            {formatFileSize(data.analysis_summary?.total_size || 0)}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-black/30 rounded-xl p-4 border border-green-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4 text-purple-400" />
            <span className="text-purple-400 font-semibold">Generated</span>
          </div>
          <p className="text-white text-sm">
            {formatTimestamp(data.timestamp)}
          </p>
        </motion.div>
      </div>

      {/* Technologies & Dependencies */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-black/30 rounded-xl p-4 border border-green-500/20 mb-6"
      >
        <h4 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
          <Package className="w-5 h-5" />
          Technologies Detected
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <h5 className="text-sm font-semibold text-gray-300 mb-2">
              Languages
            </h5>
            <div className="flex flex-wrap gap-2">
              {data.analysis_summary?.languages && Object.keys(data.analysis_summary.languages).length > 0 ? (
                Object.entries(data.analysis_summary.languages).map(
                  ([lang, count]) => (
                    <span
                      key={lang}
                      className="px-2 py-1 bg-blue-600/20 text-blue-300 rounded-md text-xs border border-blue-500/30"
                    >
                      {lang} ({count})
                    </span>
                  )
                )
              ) : (
                <span className="text-gray-500 text-xs">No languages detected</span>
              )}
            </div>
          </div>

          <div>
            <h5 className="text-sm font-semibold text-gray-300 mb-2">
              Frameworks
            </h5>
            <div className="flex flex-wrap gap-2">
              {data.analysis_summary?.frameworks && data.analysis_summary.frameworks.length > 0 ? (
                data.analysis_summary.frameworks.map((framework) => (
                  <span
                    key={framework}
                    className="px-2 py-1 bg-green-600/20 text-green-300 rounded-md text-xs border border-green-500/30"
                  >
                    {framework}
                  </span>
                ))
              ) : (
                <span className="text-gray-500 text-xs">No frameworks detected</span>
              )}
            </div>
          </div>
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm">
          <div
            className={`flex items-center gap-1 ${
              data.analysis_summary?.has_tests
                ? "text-green-400"
                : "text-gray-500"
            }`}
          >
            <CheckCircle className="w-4 h-4" />
            Tests: {data.analysis_summary?.has_tests ? "Found" : "None"}
          </div>
          <div
            className={`flex items-center gap-1 ${
              data.analysis_summary?.has_docs
                ? "text-green-400"
                : "text-gray-500"
            }`}
          >
            <FileText className="w-4 h-4" />
            Docs: {data.analysis_summary?.has_docs ? "Found" : "None"}
          </div>
          <div
            className={`flex items-center gap-1 ${
              data.analysis_summary?.has_ci ? "text-green-400" : "text-gray-500"
            }`}
          >
            <GitBranch className="w-4 h-4" />
            CI/CD: {data.analysis_summary?.has_ci ? "Found" : "None"}
          </div>
        </div>
      </motion.div>

      {/* README Preview Toggle */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="mb-4"
      >
        <button
          onClick={() => setShowReadmePreview(!showReadmePreview)}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-all duration-300"
        >
          {showReadmePreview ? (
            <EyeOff className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
          {showReadmePreview ? "Hide" : "Show"} README Preview
        </button>
      </motion.div>

      {/* README Preview */}
      {showReadmePreview && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="bg-black/40 rounded-xl p-6 border border-green-500/20 overflow-hidden"
        >
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-green-400">
              README.md Preview
            </h4>
            <button
              onClick={() => copyToClipboard(data.readme_markdown, "readme")}
              className="flex items-center gap-1 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-all duration-300"
            >
              <Copy className="w-3 h-3" />
              {copiedText === "readme" ? "Copied!" : "Copy Markdown"}
            </button>
          </div>

          <div
            className="prose prose-invert max-w-none text-gray-300 leading-relaxed max-h-96 overflow-y-auto scrollbar-thin scrollbar-thumb-green-500/20 scrollbar-track-gray-800"
            dangerouslySetInnerHTML={{
              __html: markdownToHtml(data.readme_markdown),
            }}
          />
        </motion.div>
      )}

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex flex-wrap gap-3 mt-6 pt-6 border-t border-green-500/20"
      >
        <motion.a
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={data.pull_request_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all duration-300"
        >
          <ExternalLink className="w-4 h-4" />
          Open Pull Request
        </motion.a>

        <motion.a
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={`https://github.com/${data.repository}`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-all duration-300"
        >
          <Folder className="w-4 h-4" />
          View Repository
        </motion.a>
      </motion.div>
    </div>
  );
};

export default ReadmeGeneratorView;
