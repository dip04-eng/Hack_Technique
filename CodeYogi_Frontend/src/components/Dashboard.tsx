import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Terminal,
  FolderOpen,
  BarChart3,
  Settings,
  MessageCircle,
  Activity,
  User,
  Monitor,
  AlertTriangle,
  RotateCcw,
} from "lucide-react";
import { Header } from "./Header";
import { ChatInterface } from "./ChatInterface";
import { CommandConsole } from "./CommandConsole";
import { ProjectView } from "./ProjectView";
import { AnalyticsPanel } from "./AnalyticsPanel";
import { SettingsPanel } from "./SettingsPanel";
import { UserProfile } from "./UserProfile";
import { RepoMonitoring } from "./RepoMonitoring";
import { DeployFailureAnalysis } from "./DeployFailureAnalysis";

type PanelType =
  | "chat"
  | "console"
  | "projects"
  | "analytics"
  | "settings"
  | "profile"
  | "monitoring"
  | "failure-analysis";

export const Dashboard: React.FC = () => {
  const [activePanel, setActivePanel] = useState<PanelType>("chat");
  const [isConsoleActive, setIsConsoleActive] = useState(false);

  const navItems = [
    {
      id: "chat",
      icon: MessageCircle,
      label: "AI Assistant",
      color: "from-green-400 to-emerald-500",
    },
    {
      id: "console",
      icon: Terminal,
      label: "Agent Console",
      color: "from-green-500 to-teal-500",
    },
    {
      id: "projects",
      icon: FolderOpen,
      label: "Projects",
      color: "from-emerald-400 to-green-500",
    },
    // Hidden for now - can be re-enabled later
    // {
    //   id: "monitoring",
    //   icon: Monitor,
    //   label: "Repo Monitor",
    //   color: "from-blue-400 to-cyan-500",
    // },
    {
      id: "analytics",
      icon: BarChart3,
      label: "Analytics",
      color: "from-teal-400 to-green-400",
    },
    {
      id: "settings",
      icon: Settings,
      label: "Settings",
      color: "from-green-600 to-emerald-600",
    },
    {
      id: "profile",
      icon: User,
      label: "Profile",
      color: "from-emerald-500 to-green-500",
    },
  ];

  const handleRunAgent = () => {
    setIsConsoleActive(true);
    setActivePanel("console");
  };

  const handleProfileClick = () => {
    setActivePanel("profile");
  };

  const handleRepoStatusClick = () => {
    setActivePanel("monitoring");
  };

  const handleFailureAnalysisClick = () => {
    setActivePanel("failure-analysis");
  };

  const handleRollbackClick = () => {
    // When Rollback Intelligence is clicked, switch to chat and trigger rollback
    setActivePanel("chat");
    // Dispatch a custom event that ChatInterface can listen to
    window.dispatchEvent(new CustomEvent('trigger-rollback'));
  };

  return (
    <div className="min-h-screen bg-theme-primary text-theme-primary relative overflow-hidden">
      {/* 3D Background */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0 bg-gradient-to-br from-accent-theme/20 via-transparent to-accent-theme/20" />
      </div>

      {/* Header */}
      <Header onRunAgent={handleRunAgent} onProfileClick={handleProfileClick} />

      <div className="flex h-[calc(100vh-80px)] relative z-10">
        {/* Sidebar Navigation */}
        <motion.nav
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-64 bg-theme-secondary border-r border-theme p-4"
        >
          <div className="space-y-2">
            {navItems.map((item) => (
              <motion.button
                key={item.id}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActivePanel(item.id as PanelType)}
                className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
                  activePanel === item.id
                    ? `bg-gradient-to-r ${item.color} text-theme-primary font-medium shadow-lg`
                    : "hover:bg-theme-secondary text-theme-secondary hover:text-theme-primary"
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </motion.button>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="mt-8 space-y-3">
            <h3 className="text-sm font-medium text-gray-400 mb-3">
              Quick Actions
            </h3>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleRepoStatusClick}
              className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-800/50 hover:bg-gray-700/50 text-gray-300 hover:text-white transition-all duration-300"
            >
              <Activity className="w-4 h-4" />
              <span className="text-sm">Repo Status</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleFailureAnalysisClick}
              className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-800/50 hover:bg-red-900/20 text-gray-300 hover:text-red-400 transition-all duration-300 border border-transparent hover:border-red-500/30"
            >
              <AlertTriangle className="w-4 h-4" />
              <span className="text-sm">Deploy Failure Analysis</span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleRollbackClick}
              className="w-full flex items-center gap-3 p-3 rounded-xl bg-gray-800/50 hover:bg-blue-900/20 text-gray-300 hover:text-blue-400 transition-all duration-300 border border-transparent hover:border-blue-500/30"
            >
              <RotateCcw className="w-4 h-4" />
              <span className="text-sm">Rollback Intelligence</span>
            </motion.button>
          </div>
        </motion.nav>

        {/* Main Content */}
        <div className="flex-1 relative">
          <AnimatePresence mode="wait">
            <motion.div
              key={activePanel}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="h-full"
            >
              {activePanel === "chat" && <ChatInterface />}
              {activePanel === "console" && (
                <CommandConsole isActive={isConsoleActive} />
              )}
              {activePanel === "projects" && <ProjectView />}
              {activePanel === "analytics" && <AnalyticsPanel />}
              {activePanel === "settings" && <SettingsPanel />}
              {activePanel === "profile" && <UserProfile />}
              {activePanel === "monitoring" && <RepoMonitoring />}
              {activePanel === "failure-analysis" && <DeployFailureAnalysis />}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};
