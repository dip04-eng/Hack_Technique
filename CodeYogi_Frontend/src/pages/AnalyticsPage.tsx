import React from "react";
import { Header } from "../components/Header";
import { useSelectedRepository } from "../hooks/useSelectedRepository";

export const AnalyticsPage: React.FC = () => {
  const { selectedRepo } = useSelectedRepository();

  const handleRunAgent = () => {
    console.log("Run agent clicked from Analytics page");
    // Add your logic here
  };

  const handleProfileClick = () => {
    console.log("Profile clicked from Analytics page");
    // Add your navigation logic here
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black text-white">
      {/* Reusable Header */}
      <Header onRunAgent={handleRunAgent} onProfileClick={handleProfileClick} />

      {/* Page Content */}
      <div className="p-6">
        <h1 className="text-3xl font-bold text-green-400 mb-6">Analytics</h1>

        {selectedRepo ? (
          <div className="bg-gray-800/50 border border-green-500/30 rounded-lg p-4 mb-6">
            <h2 className="text-xl font-semibold text-green-300 mb-2">
              Repository: {selectedRepo.name}
            </h2>
            <p className="text-gray-400">
              {selectedRepo.description || "No description available"}
            </p>
            <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
              <span>Language: {selectedRepo.language || "Not specified"}</span>
              <span>Stars: {selectedRepo.stargazers_count}</span>
              <span>Forks: {selectedRepo.forks_count}</span>
            </div>
          </div>
        ) : (
          <div className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-4 mb-6">
            <p className="text-yellow-300">
              No repository selected. Please select a repository from the header
              dropdown.
            </p>
          </div>
        )}

        <p className="text-gray-300">
          This analytics page demonstrates how the selected repository state is
          shared across different routes using the useSelectedRepository hook.
        </p>
      </div>
    </div>
  );
};
