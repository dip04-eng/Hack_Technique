import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  RotateCcw,
  AlertTriangle,
  CheckCircle,
  Clock,
  User,
  GitCommit,
  Activity,
  Shield,
  Loader,
  RefreshCw,
  Info,
  XCircle,
} from 'lucide-react';

interface RollbackCandidate {
  number: number;
  sha: string;
  short_sha: string;
  message: string;
  author: string;
  author_email: string;
  timestamp: string;
  timestamp_readable: string;
  is_current: boolean;
  files_changed: number;
  additions: number;
  deletions: number;
  deployment_status: string;
}

interface AIRecommendation {
  recommended_number: number;
  safety_level: 'SAFE' | 'CAUTION' | 'RISKY';
  reason: string;
  warning: string | null;
  recommended_commit?: RollbackCandidate;
}

interface RollbackData {
  success: boolean;
  repository: string;
  branch: string;
  total_candidates: number;
  candidates: RollbackCandidate[];
  ai_recommendation: AIRecommendation | null;
  current_commit: RollbackCandidate | null;
}

interface RollbackIntelligenceProps {
  repoOwner: string;
  repoName: string;
  branch?: string;
}

const RollbackIntelligence: React.FC<RollbackIntelligenceProps> = ({
  repoOwner,
  repoName,
  branch = 'main',
}) => {
  const [loading, setLoading] = useState(true);
  const [rollbackData, setRollbackData] = useState<RollbackData | null>(null);
  const [selectedNumber, setSelectedNumber] = useState<number | null>(null);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [safetyWarnings, setSafetyWarnings] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRollbackCandidates();
  }, [repoOwner, repoName, branch]);

  const fetchRollbackCandidates = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/rollback/candidates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_owner: repoOwner,
          repo_name: repoName,
          branch: branch,
          limit: 10,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch rollback candidates');
      }

      const data = await response.json();
      setRollbackData(data);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleRollbackClick = async (number: number) => {
    if (number === 1) {
      alert('Cannot rollback to current deployment');
      return;
    }

    setSelectedNumber(number);

    // Check safety first
    try {
      const safetyResponse = await fetch('http://localhost:8000/api/rollback/safety-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_owner: repoOwner,
          repo_name: repoName,
          rollback_number: number,
          branch: branch,
        }),
      });

      const safetyData = await safetyResponse.json();

      if (safetyData.safety_analysis?.requires_confirmation) {
        setSafetyWarnings(safetyData.safety_analysis);
        setShowConfirmation(true);
      } else {
        executeRollback(number, false);
      }
    } catch (err) {
      console.error('Safety check error:', err);
      executeRollback(number, false);
    }
  };

  const executeRollback = async (number: number, force: boolean = false) => {
    setExecuting(true);
    setExecutionResult(null);
    setShowConfirmation(false);

    try {
      const response = await fetch('http://localhost:8000/api/rollback/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          repo_owner: repoOwner,
          repo_name: repoName,
          rollback_number: number,
          branch: branch,
          force: force,
        }),
      });

      const data = await response.json();
      setExecutionResult(data);
    } catch (err: any) {
      setExecutionResult({
        success: false,
        error: err.message || 'Rollback execution failed',
      });
    } finally {
      setExecuting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-400';
      case 'failure':
        return 'text-red-400';
      case 'pending':
        return 'text-yellow-400';
      default:
        return 'text-gray-400';
    }
  };

  const getSafetyColor = (level: string) => {
    switch (level) {
      case 'SAFE':
        return 'text-green-400 bg-green-500/10 border-green-500/30';
      case 'CAUTION':
        return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
      case 'RISKY':
        return 'text-red-400 bg-red-500/10 border-red-500/30';
      default:
        return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <Loader className="w-8 h-8 text-blue-400 animate-spin" />
        <span className="ml-3 text-gray-300">Loading rollback candidates...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-red-500/10 border border-red-500/30 rounded-2xl">
        <div className="flex items-center gap-3 mb-4">
          <XCircle className="w-6 h-6 text-red-400" />
          <h3 className="text-lg font-semibold text-red-400">Error</h3>
        </div>
        <p className="text-gray-300">{error}</p>
        <button
          onClick={fetchRollbackCandidates}
          className="mt-4 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-500/30 transition-all"
        >
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Retry
        </button>
      </div>
    );
  }

  if (!rollbackData || rollbackData.candidates.length === 0) {
    return (
      <div className="p-8 bg-gray-800/50 border border-gray-600 rounded-2xl">
        <p className="text-gray-300">No rollback candidates available</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <div className="flex items-center gap-3 mb-2">
          <RotateCcw className="w-8 h-8 text-blue-400" />
          <h2 className="text-2xl font-bold text-white">Rollback Intelligence</h2>
        </div>
        <p className="text-gray-400">
          {rollbackData.repository} • {rollbackData.branch} branch
        </p>
      </motion.div>

      {/* AI Recommendation Banner */}
      {rollbackData.ai_recommendation && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className={`p-6 rounded-2xl border-2 mb-6 ${getSafetyColor(
            rollbackData.ai_recommendation.safety_level
          )}`}
        >
          <div className="flex items-start gap-4">
            <Shield className="w-6 h-6 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold mb-2">AI Recommendation</h3>
              <p className="text-sm mb-3">{rollbackData.ai_recommendation.reason}</p>
              <div className="flex items-center gap-4 text-sm">
                <span className="font-medium">
                  Recommended: #{rollbackData.ai_recommendation.recommended_number}
                </span>
                <span className="px-3 py-1 bg-black/30 rounded-full">
                  {rollbackData.ai_recommendation.safety_level}
                </span>
              </div>
              {rollbackData.ai_recommendation.warning && (
                <div className="mt-3 p-3 bg-black/30 rounded-lg flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span className="text-sm">{rollbackData.ai_recommendation.warning}</span>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      )}

      {/* Rollback Candidates List */}
      <div className="space-y-4">
        <AnimatePresence>
          {rollbackData.candidates.map((candidate, index) => {
            const isRecommended =
              rollbackData.ai_recommendation?.recommended_number === candidate.number;
            const isCurrent = candidate.is_current;

            return (
              <motion.div
                key={candidate.sha}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className={`p-6 rounded-2xl border-2 transition-all ${
                  isCurrent
                    ? 'bg-blue-500/10 border-blue-500/50'
                    : isRecommended
                    ? 'bg-green-500/10 border-green-500/50 shadow-lg shadow-green-500/10'
                    : 'bg-gray-800/50 border-gray-600 hover:border-gray-500'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Left: Number and Commit Info */}
                  <div className="flex gap-4 flex-1">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg flex-shrink-0 ${
                        isCurrent
                          ? 'bg-blue-500 text-white'
                          : isRecommended
                          ? 'bg-green-500 text-black'
                          : 'bg-gray-700 text-gray-300'
                      }`}
                    >
                      #{candidate.number}
                    </div>

                    <div className="flex-1">
                      {/* Commit Message */}
                      <h3 className="text-white font-semibold text-lg mb-2">
                        {candidate.message}
                        {isCurrent && (
                          <span className="ml-3 px-3 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">
                            CURRENT
                          </span>
                        )}
                        {isRecommended && !isCurrent && (
                          <span className="ml-3 px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">
                            RECOMMENDED
                          </span>
                        )}
                      </h3>

                      {/* Meta Information */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-3">
                        <div className="flex items-center gap-2 text-gray-400">
                          <User className="w-4 h-4" />
                          <span>{candidate.author}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-400">
                          <Clock className="w-4 h-4" />
                          <span>{candidate.timestamp_readable}</span>
                        </div>
                        <div className="flex items-center gap-2 text-gray-400">
                          <GitCommit className="w-4 h-4" />
                          <span className="font-mono">{candidate.short_sha}</span>
                        </div>
                        <div
                          className={`flex items-center gap-2 ${getStatusColor(
                            candidate.deployment_status
                          )}`}
                        >
                          <Activity className="w-4 h-4" />
                          <span className="capitalize">{candidate.deployment_status}</span>
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>{candidate.files_changed} files</span>
                        <span className="text-green-400">+{candidate.additions}</span>
                        <span className="text-red-400">-{candidate.deletions}</span>
                      </div>
                    </div>
                  </div>

                  {/* Right: Rollback Button */}
                  <div className="flex-shrink-0">
                    {!isCurrent ? (
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => handleRollbackClick(candidate.number)}
                        disabled={executing}
                        className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-blue-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        <RotateCcw className="w-4 h-4" />
                        Rollback
                      </motion.button>
                    ) : (
                      <div className="px-6 py-3 bg-gray-700/50 text-gray-500 rounded-xl font-medium cursor-not-allowed">
                        Current
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Confirmation Modal */}
      <AnimatePresence>
        {showConfirmation && safetyWarnings && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowConfirmation(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-gray-900 border-2 border-yellow-500/50 rounded-2xl p-8 max-w-2xl w-full"
            >
              <div className="flex items-center gap-3 mb-6">
                <AlertTriangle className="w-8 h-8 text-yellow-400" />
                <h2 className="text-2xl font-bold text-white">Confirm Rollback</h2>
              </div>

              <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <p className="text-yellow-400 font-medium mb-3">
                  Risk Level: {safetyWarnings.risk_level}
                </p>
                {safetyWarnings.warnings && safetyWarnings.warnings.length > 0 && (
                  <ul className="space-y-2">
                    {safetyWarnings.warnings.map((warning: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-gray-300">
                        <Info className="w-4 h-4 flex-shrink-0 mt-0.5 text-yellow-400" />
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <p className="text-gray-400 mb-6">
                This rollback requires confirmation due to safety concerns. Do you want to proceed?
              </p>

              <div className="flex gap-4">
                <button
                  onClick={() => setShowConfirmation(false)}
                  className="flex-1 px-6 py-3 bg-gray-700 text-white rounded-xl font-medium hover:bg-gray-600 transition-all"
                >
                  Cancel
                </button>
                <button
                  onClick={() => executeRollback(selectedNumber!, true)}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-xl font-medium hover:shadow-lg hover:shadow-yellow-500/20 transition-all"
                >
                  Confirm Rollback
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Execution Result */}
      <AnimatePresence>
        {executionResult && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`mt-6 p-6 rounded-2xl border-2 ${
              executionResult.success
                ? 'bg-green-500/10 border-green-500/50'
                : 'bg-red-500/10 border-red-500/50'
            }`}
          >
            <div className="flex items-start gap-4">
              {executionResult.success ? (
                <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0" />
              ) : (
                <XCircle className="w-6 h-6 text-red-400 flex-shrink-0" />
              )}
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-white mb-2">
                  {executionResult.success ? 'Rollback Prepared' : 'Rollback Failed'}
                </h3>
                <p className="text-gray-300 mb-4">{executionResult.message || executionResult.error}</p>

                {executionResult.success && executionResult.target_commit && (
                  <div className="bg-black/30 rounded-lg p-4 mb-4">
                    <p className="text-sm text-gray-400 mb-2">Target Commit:</p>
                    <p className="text-white font-mono">
                      {executionResult.target_commit.short_sha} - {executionResult.target_commit.message}
                    </p>
                  </div>
                )}

                {executionResult.success && executionResult.next_steps && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-400">Next Steps:</p>
                    <ol className="list-decimal list-inside space-y-1 text-sm text-gray-300">
                      {executionResult.next_steps.map((step: string, idx: number) => (
                        <li key={idx}>{step}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Executing Indicator */}
      {executing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed bottom-8 right-8 bg-blue-500 text-white px-6 py-4 rounded-2xl shadow-2xl flex items-center gap-3"
        >
          <Loader className="w-5 h-5 animate-spin" />
          <span className="font-medium">Executing rollback...</span>
        </motion.div>
      )}
    </div>
  );
};

export default RollbackIntelligence;
