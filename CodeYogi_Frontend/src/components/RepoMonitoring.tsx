import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Square,
  GitBranch,
  GitCommit,
  Activity,
  Clock,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  User,
  Calendar,
  Hash,
  TrendingUp,
  Monitor,
  RefreshCw,
  Settings,
} from "lucide-react";
import { useMonitoring } from "../contexts/MonitoringContext";
import { useSelectedRepository } from "../hooks/useSelectedRepository";

export const RepoMonitoring: React.FC = () => {
  const { selectedRepo } = useSelectedRepository();
  const {
    state,
    startMonitoring,
    stopMonitoring,
    updateConfig,
    checkNow,
    logs,
  } = useMonitoring();
  const [localRepoUrl, setLocalRepoUrl] = useState(state.repoUrl);
  const [localLastKnownSha, setLocalLastKnownSha] = useState(
    state.lastKnownSha
  );
  const [localGithubToken, setLocalGithubToken] = useState(state.githubToken);
  const [showGetStarted, setShowGetStarted] = useState(!state.isActive);

  // Auto-fill repository URL when a repo is selected
  useEffect(() => {
    if (selectedRepo && selectedRepo.html_url) {
      setLocalRepoUrl(selectedRepo.html_url);
      console.log("Auto-filled repo URL:", selectedRepo.html_url);
    }
  }, [selectedRepo]);

  // Update local state when context state changes
  useEffect(() => {
    setLocalRepoUrl(state.repoUrl);
    setLocalLastKnownSha(state.lastKnownSha);
    setLocalGithubToken(state.githubToken);
    setShowGetStarted(!state.isActive);
  }, [state]);

  const handleStartMonitoring = () => {
    if (!localRepoUrl.trim()) {
      return;
    }

    // Update context with local values
    startMonitoring({
      repoUrl: localRepoUrl,
      lastKnownSha: localLastKnownSha,
      githubToken: localGithubToken,
    });
    setShowGetStarted(false);
  };

  const handleStopMonitoring = () => {
    stopMonitoring();
    setShowGetStarted(true);
  };

  const handleConfigChange = () => {
    updateConfig({
      repoUrl: localRepoUrl,
      lastKnownSha: localLastKnownSha,
      githubToken: localGithubToken,
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "monitoring":
        return "text-green-400";
      case "error":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "monitoring":
        return <RefreshCw className="w-4 h-4 animate-spin" />;
      case "error":
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Monitor className="w-4 h-4" />;
    }
  };

  return (
    <div className="h-full bg-theme-primary text-theme-primary p-6 overflow-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Repository Monitoring</h1>
              <p className="text-theme-secondary">
                Real-time monitoring for repository changes
              </p>
            </div>
          </div>

          <div
            className={`flex items-center gap-2 px-3 py-2 rounded-lg bg-theme-secondary ${getStatusColor(
              state.status
            )}`}
          >
            {getStatusIcon(state.status)}
            <span className="text-sm font-medium">
              {state.status === "monitoring"
                ? "Monitoring..."
                : state.status === "error"
                ? "Error"
                : "Idle"}
            </span>
          </div>
        </div>

        {/* Get Started Message */}
        {showGetStarted && !state.isActive && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-xl p-6 mb-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-green-500/20 rounded-lg">
                <Monitor className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold text-green-400">
                Welcome to Repository Monitoring!
              </h3>
            </div>
            <p className="text-theme-secondary mb-4">
              Start monitoring your repository for new pushes and automatic
              optimization PR creation. Configure your repository settings below
              and click "Start Monitoring" to begin.
            </p>
            <div className="flex items-center gap-2 text-sm text-theme-secondary">
              <Clock className="w-4 h-4" />
              <span>Monitoring checks every 1 minute for new changes</span>
            </div>
          </motion.div>
        )}

        {/* Configuration Panel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-theme-secondary rounded-xl p-6 mb-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Configuration
          </h3>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-theme-secondary mb-2">
                Repository URL
              </label>
              <input
                type="text"
                value={localRepoUrl}
                onChange={(e) => setLocalRepoUrl(e.target.value)}
                onBlur={handleConfigChange}
                className="w-full px-3 py-2 bg-theme-primary border border-theme rounded-lg focus:ring-2 focus:ring-accent-theme focus:border-transparent"
                placeholder={selectedRepo ? selectedRepo.html_url : "https://github.com/owner/repo"}
                disabled={state.isActive}
              />
              {selectedRepo && (
                <p className="mt-1 text-xs text-green-400">
                  ✓ Auto-filled from selected repository: {selectedRepo.name}
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-theme-secondary mb-2">
                Last Known SHA (optional)
              </label>
              <input
                type="text"
                value={localLastKnownSha}
                onChange={(e) => setLocalLastKnownSha(e.target.value)}
                onBlur={handleConfigChange}
                className="w-full px-3 py-2 bg-theme-primary border border-theme rounded-lg focus:ring-2 focus:ring-accent-theme focus:border-transparent"
                placeholder="Enter last commit SHA"
                disabled={state.isActive}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-theme-secondary mb-2">
                GitHub Token (optional)
              </label>
              <input
                type="password"
                value={localGithubToken}
                onChange={(e) => setLocalGithubToken(e.target.value)}
                onBlur={handleConfigChange}
                className="w-full px-3 py-2 bg-theme-primary border border-theme rounded-lg focus:ring-2 focus:ring-accent-theme focus:border-transparent"
                placeholder="Enter GitHub token"
                disabled={state.isActive}
              />
            </div>
          </div>

          <div className="flex gap-3">
            {!state.isActive ? (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleStartMonitoring}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-600 transition-all"
              >
                <Play className="w-4 h-4" />
                Start Monitoring
              </motion.button>
            ) : (
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleStopMonitoring}
                className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-all"
              >
                <Square className="w-4 h-4" />
                Stop Monitoring
              </motion.button>
            )}

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={checkNow}
              disabled={!localRepoUrl.trim() || state.status === "monitoring"}
              className="flex items-center gap-2 px-4 py-2 bg-theme-accent text-white rounded-lg font-medium hover:bg-opacity-80 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className="w-4 h-4" />
              Check Now
            </motion.button>
          </div>
        </motion.div>

        {/* Stats Dashboard */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
        >
          <div className="bg-theme-secondary rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-theme-secondary text-sm">Total Checks</p>
                <p className="text-2xl font-bold">{state.totalChecks}</p>
              </div>
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Clock className="w-5 h-5 text-blue-400" />
              </div>
            </div>
          </div>

          <div className="bg-theme-secondary rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-theme-secondary text-sm">New Pushes</p>
                <p className="text-2xl font-bold text-green-400">
                  {state.newPushesDetected}
                </p>
              </div>
              <div className="p-2 bg-green-500/20 rounded-lg">
                <TrendingUp className="w-5 h-5 text-green-400" />
              </div>
            </div>
          </div>

          <div className="bg-theme-secondary rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-theme-secondary text-sm">PRs Created</p>
                <p className="text-2xl font-bold text-purple-400">
                  {state.prsCreated}
                </p>
              </div>
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <GitBranch className="w-5 h-5 text-purple-400" />
              </div>
            </div>
          </div>

          <div className="bg-theme-secondary rounded-xl p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-theme-secondary text-sm">Last Check</p>
                <p className="text-sm font-medium">
                  {state.lastCheck || "Never"}
                </p>
              </div>
              <div className="p-2 bg-yellow-500/20 rounded-lg">
                <Activity className="w-5 h-5 text-yellow-400" />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Latest Commit Info */}
        {state.latestCommit && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-theme-secondary rounded-xl p-6 mb-6"
          >
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <GitCommit className="w-5 h-5" />
              Latest Commit
            </h3>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Hash className="w-4 h-4 text-theme-secondary" />
                  <span className="text-sm text-theme-secondary">SHA:</span>
                  <code className="text-sm bg-theme-primary px-2 py-1 rounded">
                    {state.latestCommit.sha.substring(0, 8)}
                  </code>
                </div>

                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-theme-secondary" />
                  <span className="text-sm text-theme-secondary">Author:</span>
                  <span className="text-sm">{state.latestCommit.author}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-theme-secondary" />
                  <span className="text-sm text-theme-secondary">Date:</span>
                  <span className="text-sm">
                    {new Date(state.latestCommit.date).toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <span className="text-sm text-theme-secondary mb-1 block">
                    Message:
                  </span>
                  <p className="text-sm bg-theme-primary p-3 rounded-lg">
                    {state.latestCommit.message}
                  </p>
                </div>

                {state.lastResponse?.pr_created && (
                  <a
                    href={state.lastResponse.pr_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-3 py-2 bg-green-500/20 text-green-400 rounded-lg text-sm hover:bg-green-500/30 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                    View PR #{state.lastResponse.pr_number}
                  </a>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* Activity Logs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-theme-secondary rounded-xl p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Activity Logs
          </h3>

          <div className="space-y-2 max-h-60 overflow-y-auto">
            <AnimatePresence>
              {logs.length === 0 ? (
                <p className="text-theme-secondary text-sm">No activity yet</p>
              ) : (
                logs.map((log, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className={`flex items-start gap-3 p-3 rounded-lg text-sm ${
                      log.type === "success"
                        ? "bg-green-500/20 text-green-400"
                        : log.type === "error"
                        ? "bg-red-500/20 text-red-400"
                        : "bg-theme-primary text-theme-secondary"
                    }`}
                  >
                    <span className="text-xs opacity-70 min-w-[60px]">
                      {log.timestamp}
                    </span>
                    <span className="flex-1">{log.message}</span>
                    {log.type === "success" && (
                      <CheckCircle className="w-4 h-4 mt-0.5" />
                    )}
                    {log.type === "error" && (
                      <AlertCircle className="w-4 h-4 mt-0.5" />
                    )}
                  </motion.div>
                ))
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};
