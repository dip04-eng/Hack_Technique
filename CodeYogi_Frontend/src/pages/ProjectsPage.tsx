import React from "react";
import { Header } from "../components/Header";
import { ProjectView } from "../components/ProjectView";

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

      {/* Projects View - Shows GitHub Repositories */}
      <ProjectView />
    </div>
  );
};
