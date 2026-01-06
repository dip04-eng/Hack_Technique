import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createPortal } from "react-dom";
import {
  Bot,
  Play,
  Zap,
  ChevronDown,
  GitBranch,
  Star,
  GitFork,
  Monitor,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import type { GitHubRepository } from "../services/githubService";
import { useSelectedRepository } from "../hooks/useSelectedRepository";
import { useMonitoring } from "../contexts/MonitoringContext";

interface HeaderProps {
  onRunAgent?: () => void;
  onProfileClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onRunAgent,
  onProfileClick,
}) => {
  const {
    user,
    userProfile,
    refreshGitHubRepos,
    loading: authLoading,
  } = useAuth();
  const { selectedRepo, setSelectedRepo } = useSelectedRepository();
  const { state: monitoringState } = useMonitoring();
  const [repositories, setRepositories] = useState<GitHubRepository[]>([]);
  const [isRepoDropdownOpen, setIsRepoDropdownOpen] = useState(false);
  const [manualFetchLoading, setManualFetchLoading] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const dropdownRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Use repositories from userProfile or fetch directly if needed
  useEffect(() => {
    const loadRepositories = async () => {
      console.log("Header: Loading repositories...");
      console.log("Header: userProfile:", userProfile);
      console.log("Header: user:", user);
      
      if (userProfile && Array.isArray(userProfile.repositories) && userProfile.repositories.length > 0) {
        console.log("Loading repos from userProfile:", userProfile.repositories.length);
        setRepositories(userProfile.repositories);
      } else if (userProfile && userProfile.githubUsername) {
        // Fallback: Fetch directly from GitHub API if Firestore doesn't have repos
        console.log("No repos in profile, fetching from GitHub API for:", userProfile.githubUsername);
        try {
          const { fetchGitHubRepositories } = await import("../services/githubService");
          const repos = await fetchGitHubRepositories(userProfile.githubUsername);
          console.log("Fetched repos from GitHub API:", repos.length);
          setRepositories(repos);
        } catch (err) {
          console.error("Failed to fetch repositories from GitHub API:", err);
          setRepositories([]);
        }
      } else if (user) {
        // Last resort: Try to extract GitHub username from user object
        console.log("Attempting to extract GitHub username from user object");
        let githubUsername = "";
        
        const userWithInfo = user as any;
        if (userWithInfo.reloadUserInfo && userWithInfo.reloadUserInfo.screenName) {
          githubUsername = userWithInfo.reloadUserInfo.screenName;
          console.log("Extracted username from screenName:", githubUsername);
        } else if (user.providerData[0]) {
          const githubData = user.providerData[0];
          if (githubData.providerId === "github.com" && githubData.uid) {
            if (!/^\d+$/.test(githubData.uid)) {
              githubUsername = githubData.uid;
              console.log("Extracted username from providerData:", githubUsername);
            }
          }
        }
        
        if (githubUsername) {
          console.log("Fetching repos for extracted username:", githubUsername);
          try {
            const { fetchGitHubRepositories } = await import("../services/githubService");
            const repos = await fetchGitHubRepositories(githubUsername);
            console.log("Fetched repos from GitHub API:", repos.length);
            setRepositories(repos);
          } catch (err) {
            console.error("Failed to fetch repositories from GitHub API:", err);
            setRepositories([]);
          }
        } else {
          console.log("No GitHub username available");
          setRepositories([]);
        }
      } else {
        console.log("No user authenticated");
        setRepositories([]);
      }
    };

    loadRepositories();
  }, [userProfile, user]);

  // Manual fetch handler
  const handleManualFetchRepos = async () => {
    setManualFetchLoading(true);
    try {
      await refreshGitHubRepos();
    } catch (err) {
      // error already handled in context
    } finally {
      setManualFetchLoading(false);
    }
  };

  const handleRepoSelect = (repo: GitHubRepository) => {
    try {
      const completeRepo: GitHubRepository = {
        ...repo,
        full_name: `${repo.owner?.login ?? ""}/${repo.name}`,
        html_url:
          repo.html_url ||
          `https://github.com/${repo.owner?.login ?? ""}/${repo.name}`,
        clone_url:
          repo.clone_url ||
          `https://github.com/${repo.owner?.login ?? ""}/${repo.name}.git`,
        private: repo.private || false,
        description: repo.description || "",
        stargazers_count: repo.stargazers_count || 0,
        forks_count: repo.forks_count || 0,
        language: repo.language || undefined,
        updated_at: repo.updated_at || new Date().toISOString(),
        default_branch: repo.default_branch || "main",
        id: repo.id,
        name: repo.name,
        owner: repo.owner || {
          login: "",
          id: 0,
          avatar_url: "",
        },
      };

      // Update the selected repo in the global context
      setSelectedRepo(completeRepo);

      // Close dropdown
      setIsRepoDropdownOpen(false);
    } catch (error) {
      console.error("Error selecting repository:", error);
    }
  };

  // Debug: Log when selectedRepo changes
  useEffect(() => {
    console.log("Header: selectedRepo state changed:", selectedRepo);
    if (selectedRepo) {
      console.log("Header: selectedRepo name:", selectedRepo.name);
    }
  }, [selectedRepo]);

  const handleDropdownToggle = () => {
    console.log("Dropdown toggle clicked. Current state:", isRepoDropdownOpen);
    console.log("Repositories available:", repositories.length);
    console.log(
      "Repository names:",
      repositories.map((r) => r.name)
    );
    if (!isRepoDropdownOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom + window.scrollY + 8,
        left: rect.left + window.scrollX,
      });
    }
    setIsRepoDropdownOpen(!isRepoDropdownOpen);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsRepoDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleRunAgent = () => {
    if (onRunAgent) {
      onRunAgent();
    }
  };

  const handleProfileClick = () => {
    if (onProfileClick) {
      onProfileClick();
    }
  };

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative z-10 border-b border-theme bg-theme-secondary p-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 bg-gradient-to-r from-green-400 to-emerald-500 rounded-lg flex items-center justify-center"
            >
              <Bot className="w-6 h-6 text-black" />
            </motion.div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">
              CodeYogi
            </h1>
            {/* Monitoring Status Indicator */}
            {monitoringState.isActive && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-1 px-2 py-1 bg-green-500/20 border border-green-500/30 rounded-lg"
              >
                <Monitor className="w-3 h-3 text-green-400" />
                <span className="text-xs text-green-400 font-medium">
                  Monitoring
                </span>
                <div className="w-1 h-1 bg-green-400 rounded-full animate-pulse"></div>
              </motion.div>
            )}
          </div>

          {/* GitHub Repository Dropdown */}
          <div className="relative z-[100]" ref={dropdownRef}>
            <motion.button
              ref={buttonRef}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleDropdownToggle}
              disabled={
                manualFetchLoading || authLoading || repositories.length === 0
              }
              className={`flex items-center gap-2 px-4 py-2 border rounded-lg transition-all duration-300 min-w-[200px] disabled:opacity-50 disabled:cursor-not-allowed ${
                selectedRepo
                  ? "bg-green-500/20 border-green-400/50 hover:border-green-400/70"
                  : "bg-gray-800/80 border-green-500/30 hover:border-green-400/50"
              }`}
            >
              <GitBranch className="w-4 h-4 text-green-400" />
              <span
                className={`text-sm truncate ${
                  selectedRepo ? "text-green-300 font-medium" : "text-gray-300"
                }`}
              >
                {manualFetchLoading || authLoading
                  ? "Loading repos..."
                  : selectedRepo && selectedRepo.name
                  ? selectedRepo.name
                  : selectedRepo
                  ? "Unnamed Repo"
                  : repositories.length > 0
                  ? "Select Repository"
                  : "No repositories"}
              </span>
              <ChevronDown
                className={`w-4 h-4 text-gray-400 transition-transform ${
                  isRepoDropdownOpen ? "rotate-180" : ""
                }`}
              />
            </motion.button>

            {/* Dropdown Menu - Rendered via Portal */}
            {isRepoDropdownOpen &&
              createPortal(
                <AnimatePresence>
                  <motion.div
                    ref={dropdownRef}
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="fixed w-80 bg-black/95 backdrop-blur-xl border border-green-500/30 rounded-lg shadow-2xl shadow-green-500/20 max-h-80 overflow-y-auto"
                    style={{
                      top: dropdownPosition.top,
                      left: dropdownPosition.left,
                      zIndex: 9999999,
                    }}
                  >
                    {/* Fetch Repos Button inside dropdown */}
                    <div className="p-3 border-b border-gray-700/50">
                      <button
                        className="w-full px-3 py-2 bg-gray-800/80 border border-green-500/30 rounded-lg text-green-300 text-sm hover:border-green-400/50 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={() => {
                          console.log("Fetch Repos button clicked");
                          handleManualFetchRepos();
                        }}
                        disabled={manualFetchLoading || authLoading}
                      >
                        {manualFetchLoading || authLoading
                          ? "Fetching..."
                          : "Fetch Repos"}
                      </button>
                    </div>

                    {manualFetchLoading || authLoading ? (
                      <div className="p-4 text-center text-gray-400">
                        <div className="animate-spin w-5 h-5 border-2 border-green-500 border-t-transparent rounded-full mx-auto mb-2"></div>
                        Loading repositories...
                      </div>
                    ) : repositories.length === 0 ? (
                      <div className="p-4 text-center text-gray-400">
                        No repositories found
                      </div>
                    ) : (
                      repositories.map((repo, index) => {
                        console.log(
                          `Rendering repository ${index}:`,
                          repo.name
                        );
                        return (
                          <button
                            key={
                              repo.id
                                ? String(repo.id)
                                : repo.name
                                ? repo.name
                                : `repo-${index}`
                            }
                            onClick={() => {
                              console.log("Repository clicked:", repo.name);
                              handleRepoSelect(repo);
                            }}
                            className="w-full p-3 text-left border-b border-gray-700/50 last:border-b-0 hover:bg-green-500/10 transition-colors"
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1 min-w-0">
                                <h3 className="text-sm font-medium text-white truncate">
                                  {repo.name || "Unnamed Repo"}
                                </h3>
                                {repo.description && (
                                  <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                                    {repo.description}
                                  </p>
                                )}
                                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                  {repo.language && (
                                    <span className="flex items-center gap-1">
                                      <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                                      {repo.language}
                                    </span>
                                  )}
                                  <span className="flex items-center gap-1">
                                    <Star className="w-3 h-3" />
                                    {repo.stargazers_count}
                                  </span>
                                  <span className="flex items-center gap-1">
                                    <GitFork className="w-3 h-3" />
                                    {repo.forks_count}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </button>
                        );
                      })
                    )}
                  </motion.div>
                </AnimatePresence>,
                document.body
              )}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleRunAgent}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg font-medium hover:shadow-lg hover:shadow-green-500/25 transition-all duration-300"
          >
            <Play className="w-4 h-4" />
            Run Agent
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800/80 border border-green-500/30 rounded-lg hover:border-green-400/50 transition-all duration-300"
          >
            <Zap className="w-4 h-4 text-green-400" />
            Deploy Flow
          </motion.button>

          {/* User Avatar */}
          {user && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleProfileClick}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-800/50 transition-all duration-300"
            >
              <img
                src={user.photoURL || "/default-avatar.png"}
                alt="Profile"
                className="w-8 h-8 rounded-full border-2 border-green-500/30"
              />
              <span className="text-sm text-gray-300 hidden md:block">
                {userProfile?.displayName || user.email?.split("@")[0]}
              </span>
            </motion.button>
          )}
        </div>
      </div>
    </motion.header>
  );
};
