import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  ExternalLink,
  GitBranch,
  Search,
  CheckCircle,
  Copy,
  Eye,
  EyeOff,
  Calendar,
  FileText,
  Tag,
  Globe,
  Hash,
  MessageSquare,
  Code,
} from "lucide-react";

interface SEOOptimizationData {
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

interface SEOOptimizationViewProps {
  data: SEOOptimizationData;
  repoName: string;
}

const SEOOptimizationView: React.FC<SEOOptimizationViewProps> = ({
  data,
}) => {
  const [showMetadataDetails, setShowMetadataDetails] = useState(false);
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedText(label);
      setTimeout(() => setCopiedText(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="bg-gray-900/95 border border-purple-500/30 rounded-2xl p-6 shadow-2xl backdrop-blur-sm">
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
            className="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full flex items-center justify-center"
          >
            <Search className="w-5 h-5 text-black" />
          </motion.div>
          <div>
            <h3 className="text-xl font-bold text-purple-400 flex items-center gap-2">
              <CheckCircle className="w-5 h-5" />
              SEO Optimization Complete
            </h3>
            <p className="text-gray-400 text-sm">
              Enhanced SEO for {data.repository}
            </p>
          </div>
        </div>
        <motion.a
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          href={data.pull_request_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all duration-300"
        >
          <ExternalLink className="w-4 h-4" />
          View PR #{data.pull_request_number}
        </motion.a>
      </motion.div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-black/30 rounded-xl p-4 border border-purple-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <GitBranch className="w-4 h-4 text-purple-400" />
            <span className="text-purple-400 font-semibold">Branch</span>
          </div>
          <p className="text-white font-mono text-sm">{data.branch_name}</p>
          <button
            onClick={() => copyToClipboard(data.branch_name, "branch")}
            className="mt-2 text-xs text-gray-400 hover:text-purple-400 flex items-center gap-1"
          >
            <Copy className="w-3 h-3" />
            {copiedText === "branch" ? "Copied!" : "Copy"}
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-black/30 rounded-xl p-4 border border-blue-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <FileText className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 font-semibold">Files Modified</span>
          </div>
          <p className="text-white text-xl font-bold">{data.modified_files}</p>
          <p className="text-gray-400 text-xs mt-1">
            {data.html_files_processed} HTML files processed
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-black/30 rounded-xl p-4 border border-green-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Tag className="w-4 h-4 text-green-400" />
            <span className="text-green-400 font-semibold">Keywords</span>
          </div>
          <p className="text-white text-xl font-bold">
            {data.seo_metadata.keywords.length}
          </p>
          <p className="text-gray-400 text-xs mt-1">SEO keywords added</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-black/30 rounded-xl p-4 border border-orange-500/20"
        >
          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4 text-orange-400" />
            <span className="text-orange-400 font-semibold">Optimized</span>
          </div>
          <p className="text-white text-sm">
            {formatTimestamp(data.timestamp)}
          </p>
        </motion.div>
      </div>

      {/* SEO Metadata Preview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-black/30 rounded-xl p-4 border border-purple-500/20 mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-purple-400 flex items-center gap-2">
            <Search className="w-5 h-5" />
            SEO Metadata Overview
          </h4>
          <button
            onClick={() => setShowMetadataDetails(!showMetadataDetails)}
            className="flex items-center gap-2 px-3 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-sm transition-all duration-300"
          >
            {showMetadataDetails ? (
              <EyeOff className="w-4 h-4" />
            ) : (
              <Eye className="w-4 h-4" />
            )}
            {showMetadataDetails ? "Hide" : "Show"} Details
          </button>
        </div>

        {/* Basic SEO Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <h5 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
              <FileText className="w-4 h-4" />
              Title
            </h5>
            <p className="text-white text-sm bg-gray-800/50 p-3 rounded-lg border border-purple-500/10">
              {data.seo_metadata.title}
            </p>
          </div>

          <div>
            <h5 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
              <MessageSquare className="w-4 h-4" />
              Description
            </h5>
            <p className="text-white text-sm bg-gray-800/50 p-3 rounded-lg border border-purple-500/10">
              {data.seo_metadata.description}
            </p>
          </div>
        </div>

        {/* Keywords */}
        <div className="mb-4">
          <h5 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
            <Hash className="w-4 h-4" />
            Keywords
          </h5>
          <div className="flex flex-wrap gap-2">
            {data.seo_metadata.keywords.map((keyword, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-purple-600/20 text-purple-300 rounded-md text-xs border border-purple-500/30"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>

        {/* Detailed Metadata */}
        {showMetadataDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h5 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  Open Graph Title
                </h5>
                <p className="text-white text-sm bg-gray-800/50 p-3 rounded-lg border border-blue-500/10">
                  {data.seo_metadata.og_title}
                </p>
              </div>

              <div>
                <h5 className="text-sm font-semibold text-gray-300 mb-2 flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  Open Graph Description
                </h5>
                <p className="text-white text-sm bg-gray-800/50 p-3 rounded-lg border border-blue-500/10">
                  {data.seo_metadata.og_description}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <h5 className="text-sm font-semibold text-gray-300 mb-2">
                  OG Type
                </h5>
                <p className="text-white text-sm bg-gray-800/50 p-2 rounded border border-gray-600">
                  {data.seo_metadata.og_type}
                </p>
              </div>

              <div>
                <h5 className="text-sm font-semibold text-gray-300 mb-2">
                  Twitter Card
                </h5>
                <p className="text-white text-sm bg-gray-800/50 p-2 rounded border border-gray-600">
                  {data.seo_metadata.twitter_card}
                </p>
              </div>

              <div>
                <h5 className="text-sm font-semibold text-gray-300 mb-2">
                  Schema Type
                </h5>
                <p className="text-white text-sm bg-gray-800/50 p-2 rounded border border-gray-600">
                  {data.seo_metadata.schema_type}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="flex flex-wrap gap-3 pt-6 border-t border-purple-500/20"
      >
        <motion.a
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          href={data.pull_request_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-all duration-300"
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
          <Code className="w-4 h-4" />
          View Repository
        </motion.a>

        <button
          onClick={() =>
            copyToClipboard(
              JSON.stringify(data.seo_metadata, null, 2),
              "metadata"
            )
          }
          className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-medium transition-all duration-300"
        >
          <Copy className="w-4 h-4" />
          {copiedText === "metadata" ? "Copied!" : "Copy Metadata"}
        </button>
      </motion.div>
    </div>
  );
};

export default SEOOptimizationView;
