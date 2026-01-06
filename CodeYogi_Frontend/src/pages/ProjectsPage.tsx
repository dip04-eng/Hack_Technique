import React from "react";
import { Header } from "../components/Header";

export const ProjectsPage: React.FC = () => {
  const handleRunAgent = () => {
    console.log("Run agent clicked from Projects page");
    // Add your logic here
  };

  const handleProfileClick = () => {
    console.log("Profile clicked from Projects page");
    // Add your navigation logic here
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black text-white">
      {/* Reusable Header */}
      <Header onRunAgent={handleRunAgent} onProfileClick={handleProfileClick} />

      {/* Page Content */}
      <div className="p-6">
        <h1 className="text-3xl font-bold text-green-400 mb-6">Projects</h1>
        <p className="text-gray-300">
          This is a standalone projects page using the reusable Header
          component. The header maintains the same repository selection state
          across all routes.
        </p>
      </div>
    </div>
  );
};
