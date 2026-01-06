import React, { createContext, useContext, useState, useEffect } from "react";
import { GitHubRepository } from "../services/githubService";

interface SelectedRepositoryContextType {
  selectedRepo: GitHubRepository | null;
  setSelectedRepo: (repo: GitHubRepository | null) => void;
}

const SelectedRepositoryContext = createContext<SelectedRepositoryContextType | undefined>(undefined);

export const SelectedRepositoryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [selectedRepo, _setSelectedRepo] = useState<GitHubRepository | null>(null);
  const [version, setVersion] = useState(0);

  const setSelectedRepo = (repo: GitHubRepository | null) => {
    _setSelectedRepo(repo);
    setVersion(v => v + 1); // Increment version to force re-render
  };

  // Load saved repository from localStorage on mount
  useEffect(() => {
    try {
      const savedRepo = localStorage.getItem("selectedRepo");
      if (savedRepo) {
        const repo = JSON.parse(savedRepo);
        console.log("Loaded repository from localStorage:", repo.name);
        _setSelectedRepo(repo);
      }
    } catch (error) {
      console.error("Failed to load repository from localStorage:", error);
    }
  }, []);

  // Save to localStorage whenever selectedRepo changes
  useEffect(() => {
    if (selectedRepo) {
      try {
        localStorage.setItem("selectedRepo", JSON.stringify(selectedRepo));
        console.log("Repository saved to localStorage:", selectedRepo.name);
      } catch (error) {
        console.error("Failed to save repository to localStorage:", error);
      }
    } else {
      localStorage.removeItem("selectedRepo");
    }
  }, [selectedRepo, version]);

  return (
    <SelectedRepositoryContext.Provider value={{ selectedRepo, setSelectedRepo }}>
      {children}
    </SelectedRepositoryContext.Provider>
  );
};

export const useSelectedRepository = () => {
  const context = useContext(SelectedRepositoryContext);
  if (context === undefined) {
    throw new Error("useSelectedRepository must be used within a SelectedRepositoryProvider");
  }
  return context;
};
