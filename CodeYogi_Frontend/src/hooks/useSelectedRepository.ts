import { useState, useEffect } from "react";
import { GitHubRepository } from "../services/githubService";

export const useSelectedRepository = () => {
  const [selectedRepo, setSelectedRepo] = useState<GitHubRepository | null>(
    null
  );

  // Load saved repository from localStorage on mount
  useEffect(() => {
    try {
      const savedRepo = localStorage.getItem("selectedRepo");
      if (savedRepo) {
        const repo = JSON.parse(savedRepo);
        console.log("Loaded repository from localStorage:", repo.name);
        setSelectedRepo(repo);
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
    }
  }, [selectedRepo]);

  return {
    selectedRepo,
    setSelectedRepo,
  };
};
