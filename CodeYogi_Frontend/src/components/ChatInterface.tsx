import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Bot,
  User,
  Mic,
  MicOff,
  Copy,
  ThumbsUp,
  ThumbsDown,
  GitBranch,
  Globe,
  Trash2,
} from "lucide-react";
import { useSelectedRepository } from "../hooks/useSelectedRepository";
import { useChatContext } from "../contexts/ChatContext";

// Import the view components
import AIStrategicAnalysisView from "./views/AIStrategicAnalysisView";
import RepoAnalysisView from "./views/RepoAnalysisView";
import GithubStructureAnalysisView from "./views/GithubStructureAnalysisView";
import WorkflowDeploymentView from "./views/WorkflowDeploymentView";
import WorkflowOptimizationView from "./views/WorkflowOptimizationView";
import GithubCodeAnalysisView from "./views/GithubCodeAnalysisView";
import OptimizationPRView from "./views/OptimizationPRView";
import ReadmeGeneratorView from "./views/ReadmeGeneratorView";
import SEOOptimizationView from "./views/SEOOptimizationView";
import RollbackIntelligence from "./RollbackIntelligence";
import {
  GithubStructureAnalysis,
  Message,
  RepoAnalysis,
  WorkflowDeployment,
  WorkflowOptimization,
  GithubCodeAnalysis,
  OptimizationPR,
  ReadmeGenerator,
  SEOOptimization,
} from "../types/chat";

// Utility function to generate unique message IDs
const generateMessageId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

export const ChatInterface: React.FC = () => {
  const { selectedRepo } = useSelectedRepository();
  const { messages, setMessages, clearChat } = useChatContext();
  const [inputValue, setInputValue] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [showRepoOptions, setShowRepoOptions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Listen for rollback trigger from Dashboard
  useEffect(() => {
    const handleRollbackTrigger = () => {
      setInputValue("Rollback Intelligence");
      // Automatically trigger the action
      setTimeout(() => {
        const btn = document.querySelector<HTMLButtonElement>('[data-action="Rollback Intelligence"]');
        if (btn) btn.click();
      }, 100);
    };

    window.addEventListener('trigger-rollback', handleRollbackTrigger);
    return () => window.removeEventListener('trigger-rollback', handleRollbackTrigger);
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userInput = inputValue.toLowerCase().trim();

    // Check if user wants to clear chat
    if (
      userInput === "/clear" ||
      userInput === "clear chat" ||
      userInput === "clear"
    ) {
      clearChat();
      setInputValue("");
      setShowRepoOptions(true);
      // Add a brief notification that chat was cleared
      setTimeout(() => {
        const clearMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "✨ Chat cleared! How can I help you today?",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, clearMessage]);
      }, 100);
      return;
    }

    const newMessage: Message = {
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue("");
    setShowRepoOptions(false);

    // Check if user is asking to create an optimization PR
    if (
      (userInput.includes("create optimization pr") ||
        userInput.includes("create pr") ||
        userInput.includes("make pull request") ||
        userInput.includes("create pull request")) &&
      selectedRepo
    ) {
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Creating optimization Pull Request for "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/create-optimization-pr/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              github_url: selectedRepo.html_url,
              github_token: "", // Token would need to be provided by the user or stored securely
              auto_merge: false,
              branch_name: `codeyogi-optimization-${new Date().getFullYear()}`,
            }),
          }
        );

        if (!response.ok) throw new Error("Failed to create optimization PR");

        const data: OptimizationPR = await response.json();

        // Create a message with PR creation data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the OptimizationPRView component
          timestamp: new Date(),
          optimizationPR: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the PR view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error creating the optimization Pull Request. Please check your GitHub token and permissions, then try again.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if user is asking to generate a README PR
    if (
      (userInput.includes("generate readme pr") ||
        userInput.includes("create readme pr") ||
        userInput.includes("generate readme pull request") ||
        userInput.includes("create readme pull request") ||
        userInput.includes("generate readme")) &&
      selectedRepo
    ) {
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Generating a comprehensive README and creating a Pull Request for "${selectedRepo.name}"... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch("http://localhost:8000/readme/generate/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            github_token: "", // Token would need to be provided by the user or stored securely
            branch_name: "",
            create_pr: true,
            auto_merge: false,
            readme_style: "comprehensive",
            include_badges: true,
            include_installation: true,
            include_usage_examples: true,
            include_contributing: true,
            include_license: true,
          }),
        });

        if (!response.ok) throw new Error("Failed to generate README PR");

        const data: ReadmeGenerator = await response.json();

        // Create a message with README generator data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the ReadmeGeneratorView component
          timestamp: new Date(),
          readmeGenerator: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the PR view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error generating the README Pull Request. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if user is asking for SEO optimization
    if (
      (userInput.includes("optimize seo") ||
        userInput.includes("seo optimize") ||
        userInput.includes("seo optimization") ||
        userInput.includes("improve seo")) &&
      selectedRepo
    ) {
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Optimizing SEO for "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch("http://localhost:8000/seo/optimize/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            github_url: selectedRepo.html_url,
            github_token: "", // Token would need to be provided by the user or stored securely
            branch_name: "",
            create_pr: true,
            auto_merge: false,
          }),
        });

        if (!response.ok) throw new Error("Failed to optimize SEO");

        const data: SEOOptimization = await response.json();

        // Create a message with SEO optimization data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the SEOOptimizationView component
          timestamp: new Date(),
          seoOptimization: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the SEO optimization view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error optimizing SEO. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if user is asking for Rollback Intelligence
    if (
      (userInput.includes("rollback") ||
        userInput.includes("revert") ||
        userInput.includes("rollback intelligence") ||
        userInput.includes("show rollback") ||
        userInput.includes("deployment history")) &&
      selectedRepo
    ) {
      // Extract repo owner and name from selectedRepo
      const repoOwner = selectedRepo.owner.login;
      const repoName = selectedRepo.name;

      const aiResponse: Message = {
        id: generateMessageId(),
        type: "ai",
        content: "", // Content is handled by the RollbackIntelligence component
        timestamp: new Date(),
        rollbackIntelligence: {
          repoOwner,
          repoName,
          branch: "main", // Default branch, can be made configurable
        },
      };

      setMessages((prev) => [...prev, aiResponse]);
      return;
    }

    // Check if user is asking for GitHub code analysis
    if (
      (userInput.includes("analyze github code") ||
        userInput.includes("analyze code") ||
        userInput.includes("optimize code")) &&
      selectedRepo
    ) {
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Analyzing code in "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/analyze-github-code/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              github_url: selectedRepo.html_url,
              create_pr: false,
              max_files: 20,
              target_languages: ["python", "javascript", "typescript"],
            }),
          }
        );

        if (!response.ok) throw new Error("Failed to analyze GitHub code");

        const data: GithubCodeAnalysis = await response.json();

        // Create a message with GitHub code analysis data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the GithubCodeAnalysisView component
          timestamp: new Date(),
          githubCodeAnalysis: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the code analysis view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error analyzing the code. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if user is asking for workflow optimization
    if (
      userInput.includes("optimize workflow") &&
      !userInput.includes("deployment")
    ) {
      if (!selectedRepo) {
        const errorMessage: Message = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: "ai",
          content: "Please select a repository first using the dropdown at the top.",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }

      const loadingMessage: Message = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: "ai",
        content: `Analyzing and optimizing the workflow for "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/optimize-workflow/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              repo_url: selectedRepo.html_url,
            }),
          }
        );

        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(`Backend error: ${response.status} - ${errorData}`);
        }

        const data: WorkflowOptimization = await response.json();

        // Create a message with workflow optimization data
        const aiResponse: Message = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: "ai",
          content: "", // Content is handled by the WorkflowOptimizationView component
          timestamp: new Date(),
          workflowOptimization: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the optimization view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error("Workflow optimization error:", error);
        const errorMessage: Message = {
          id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          type: "ai",
          content:
            "Sorry, there was an error optimizing the workflow. Make sure the backend is running at http://localhost:8000. Error: " + (error instanceof Error ? error.message : String(error)),
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if the user is requesting GitHub structure analysis
    if (
      userInput.includes("analyze github structure") ||
      userInput.includes("analyze repository structure")
    ) {
      if (!selectedRepo) {
        alert("Please select a repository first");
        return;
      }

      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Analyzing the structure of "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/analyze-github-structure/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              github_url: selectedRepo.html_url,
              detailed_analysis: true,
              exclude_patterns: [".git", "node_modules", "__pycache__"],
            }),
          }
        );

        if (!response.ok)
          throw new Error("Failed to analyze repository structure");

        const data: GithubStructureAnalysis = await response.json();

        // Create a message with GitHub structure analysis data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the GithubStructureAnalysisView component
          timestamp: new Date(),
          githubStructureAnalysis: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the analysis view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error analyzing the repository structure. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Check if the message is a workflow deployment request
    if (inputValue.toLowerCase().includes("optimize workflow deployment")) {
      if (!selectedRepo) {
        alert("Please select a repository first");
        return;
      }

      // Add loading message only (do not add user message again)
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: "🚀 Deploying optimized workflow to your repository...",
        timestamp: new Date(),
        isLoading: true,
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/optimize-workflow-deployment/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              repo_url: selectedRepo.html_url,
              github_token: "",
            }),
          }
        );

        if (!response.ok) throw new Error("Failed to deploy workflow");

        const data: WorkflowDeployment = await response.json();

        // Create a message with workflow deployment data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the WorkflowDeploymentView component
          timestamp: new Date(),
          workflowDeployment: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the deployment view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error deploying the workflow. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
      return;
    }

    // Default AI response for other queries
    setIsTyping(true);
    setTimeout(() => {
      const aiResponse: Message = {
        id: generateMessageId(),
        type: "ai",
        content: "I'm processing your request...",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRepoOptionSelect = async (
    option: "repository" | "general" | "select"
  ) => {
    setShowRepoOptions(false);

    if (option === "repository" && selectedRepo) {
      const loadingMessage: Message = {
        id: generateMessageId(),
        type: "ai",
        content: `Analyzing the "${selectedRepo.name}" repository... This may take a moment.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, loadingMessage]);

      try {
        const response = await fetch(
          "http://localhost:8000/describe-repository/",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              github_url: selectedRepo.html_url,
              repo_owner: selectedRepo.owner.login,
              repo_name: selectedRepo.name,
              include_tech_stack: true,
              include_architecture: true,
              include_features: true,
            }),
          }
        );

        if (!response.ok) throw new Error("Failed to analyze repository");

        const data: RepoAnalysis = await response.json();

        // Create a message with structured data
        const aiResponse: Message = {
          id: generateMessageId(),
          type: "ai",
          content: "", // Content is handled by the RepoAnalysisView component
          timestamp: new Date(),
          analysis: { data, repoName: selectedRepo.name },
        };

        // Replace the loading message with the analysis view
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? aiResponse : msg))
        );

        // Add AI Insights as a separate, specially formatted message
        if (data.ai_insights?.strategic_analysis) {
          // The backend should return an HTML string in `strategic_analysis`
          const aiInsightsMessage: Message = {
            id: generateMessageId(),
            type: "ai",
            content: data.ai_insights.strategic_analysis,
            timestamp: new Date(),
            isStrategicAnalysis: true, // Mark this for special rendering
          };

          // Add a slight delay before showing insights
          setTimeout(() => {
            setMessages((prev) => [...prev, aiInsightsMessage]);
          }, 1000);
        }
      } catch (error) {
        console.error(error);
        const errorMessage: Message = {
          id: generateMessageId(),
          type: "ai",
          content:
            "Sorry, there was an error analyzing the repository. Please try again later.",
          timestamp: new Date(),
        };
        setMessages((prev) =>
          prev.map((msg) => (msg.id === loadingMessage.id ? errorMessage : msg))
        );
      }
    } else if (option === "general") {
      const aiResponse: Message = {
        id: generateMessageId(),
        type: "ai",
        content:
          "Perfect! Ask me anything about code optimization, deployment, or general development practices.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    } else if (option === "select") {
      const aiResponse: Message = {
        id: generateMessageId(),
        type: "ai",
        content:
          "Please select a repository from the Projects page for targeted assistance.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }
  };

  return (
    <div className="h-full flex flex-col bg-theme-primary">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-8 border-b border-theme bg-theme-secondary"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full flex items-center justify-center"
            >
              <Bot className="w-6 h-6 text-black" />
            </motion.div>
            <div>
              <h2 className="text-xl font-bold text-white">
                CodeYogi AI Assistant
              </h2>
              <p className="text-green-400 text-sm">Online • Ready to help</p>
            </div>
          </div>
          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={clearChat}
              className="flex items-center gap-2 px-4 py-2 bg-red-600/20 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-600/30 hover:text-red-300 transition-all duration-300"
              title="Clear chat history"
            >
              <Trash2 className="w-4 h-4" />
              <span className="text-sm">Clear Chat</span>
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={async () => {
                if (!selectedRepo) {
                  alert("Please select a repository first");
                  return;
                }
                setShowRepoOptions(false);
                // 1. Describe Repository
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Describing the \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/describe-repository/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        repo_owner: selectedRepo.owner.login,
                        repo_name: selectedRepo.name,
                        include_tech_stack: true,
                        include_architecture: true,
                        include_features: true,
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      analysis: { data, repoName: selectedRepo.name },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error describing the repository. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error describing the repository. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 2. Analyze GitHub Structure
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Analyzing the structure of \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/analyze-github-structure/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        detailed_analysis: true,
                        exclude_patterns: [
                          ".git",
                          "node_modules",
                          "__pycache__",
                        ],
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      githubStructureAnalysis: {
                        data,
                        repoName: selectedRepo.name,
                      },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error analyzing the repository structure. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error analyzing the repository structure. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 3. Analyze GitHub Code
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Analyzing code in \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/analyze-github-code/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        create_pr: false,
                        max_files: 20,
                        target_languages: [
                          "python",
                          "javascript",
                          "typescript",
                        ],
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      githubCodeAnalysis: { data, repoName: selectedRepo.name },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error analyzing the code. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error analyzing the code. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 4. Create Optimization PR
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Creating optimization Pull Request for \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/create-optimization-pr/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        github_token: "",
                        auto_merge: false,
                        branch_name: `codeyogi-optimization-${new Date().getFullYear()}`,
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      optimizationPR: { data, repoName: selectedRepo.name },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error creating the optimization Pull Request. Please check your GitHub token and permissions, then try again.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error creating the optimization Pull Request. Please check your GitHub token and permissions, then try again.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 5. Optimize Workflow
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Analyzing and optimizing the workflow for \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/optimize-workflow/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        repo_url: selectedRepo.html_url,
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      workflowOptimization: {
                        data,
                        repoName: selectedRepo.name,
                      },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error optimizing the workflow. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error optimizing the workflow. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 6. Generate README PR
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Generating a comprehensive README and creating a Pull Request for \"${selectedRepo.name}\"... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/readme/generate/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        github_token: "",
                        branch_name: "",
                        create_pr: true,
                        auto_merge: false,
                        readme_style: "comprehensive",
                        include_badges: true,
                        include_installation: true,
                        include_usage_examples: true,
                        include_contributing: true,
                        include_license: true,
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      readmeGenerator: { data, repoName: selectedRepo.name },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error generating the README Pull Request. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error generating the README Pull Request. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
                // 7. Optimize SEO
                setMessages((prev) => [
                  ...prev,
                  {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: `Optimizing SEO for \"${selectedRepo.name}\" repository... This may take a moment.`,
                    timestamp: new Date(),
                  },
                ]);
                try {
                  const response = await fetch(
                    "http://localhost:8000/seo/optimize/",
                    {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        github_url: selectedRepo.html_url,
                        github_token: "",
                        branch_name: "",
                        create_pr: true,
                        auto_merge: false,
                      }),
                    }
                  );
                  let aiResponse: Message;
                  if (response.ok) {
                    const data = await response.json();
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content: "",
                      timestamp: new Date(),
                      seoOptimization: { data, repoName: selectedRepo.name },
                    };
                  } else {
                    aiResponse = {
                      id: generateMessageId(),
                      type: "ai",
                      content:
                        "Sorry, there was an error optimizing SEO. Please try again later.",
                      timestamp: new Date(),
                    };
                  }
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1 ? aiResponse : msg
                    )
                  );
                } catch (error) {
                  setMessages((prev) =>
                    prev.map((msg, i, arr) =>
                      i === arr.length - 1
                        ? {
                            id: generateMessageId(),
                            type: "ai",
                            content:
                              "Sorry, there was an error optimizing SEO. Please try again later.",
                            timestamp: new Date(),
                          }
                        : msg
                    )
                  );
                }
              }}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700/50 border border-slate-600/30 rounded-lg text-slate-200 hover:bg-slate-600/50 hover:text-white transition-all duration-300"
              title="Run all optimizations automatically"
            >
              <span className="text-sm font-semibold">
                Super Agent Optimizer
              </span>
            </motion.button>
          </div>
        </div>
      </motion.div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className={`flex gap-5 ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.type === "ai" && (
                <div className="w-10 h-10 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-black" />
                </div>
              )}
              <div
                className={`max-w-5xl w-full ${
                  message.type === "user" ? "order-1" : ""
                }`}
              >
                <motion.div
                  whileHover={{ scale: 1.01 }}
                  className={`p-6 rounded-2xl ${
                    message.type === "user"
                      ? "bg-gradient-to-r from-blue-600 to-blue-500 text-white ml-auto shadow-xl shadow-blue-500/20"
                      : message.analysis ||
                        message.isStrategicAnalysis ||
                        message.workflowOptimization ||
                        message.workflowDeployment ||
                        message.githubStructureAnalysis ||
                        message.githubCodeAnalysis ||
                        message.optimizationPR ||
                        message.readmeGenerator ||
                        message.seoOptimization ||
                        message.rollbackIntelligence
                      ? "bg-transparent p-0" // No background for custom components
                      : "bg-gradient-to-br from-gray-800/90 to-gray-900/90 border-2 border-slate-600/50 text-white backdrop-blur-lg"
                  } ${
                    message.type === "ai" &&
                    !message.analysis &&
                    !message.isStrategicAnalysis &&
                    !message.workflowOptimization &&
                    !message.workflowDeployment &&
                    !message.githubStructureAnalysis &&
                    !message.githubCodeAnalysis &&
                    !message.optimizationPR &&
                    !message.readmeGenerator &&
                    !message.seoOptimization &&
                    !message.rollbackIntelligence
                      ? "shadow-2xl shadow-slate-500/15"
                      : ""
                  }`}
                >
                  {/* ✨ UPDATED: Conditionally render based on message type */}
                  {message.analysis ? (
                    <RepoAnalysisView
                      data={message.analysis.data}
                      repoName={message.analysis.repoName}
                    />
                  ) : message.isStrategicAnalysis ? (
                    <AIStrategicAnalysisView content={message.content} />
                  ) : message.workflowOptimization ? (
                    <WorkflowOptimizationView
                      data={message.workflowOptimization.data}
                      repoName={message.workflowOptimization.repoName}
                    />
                  ) : message.workflowDeployment ? (
                    <WorkflowDeploymentView
                      data={message.workflowDeployment.data}
                      repoName={message.workflowDeployment.repoName}
                    />
                  ) : message.githubStructureAnalysis ? (
                    <GithubStructureAnalysisView
                      data={message.githubStructureAnalysis.data}
                      repoName={message.githubStructureAnalysis.repoName}
                    />
                  ) : message.githubCodeAnalysis ? (
                    <GithubCodeAnalysisView
                      data={message.githubCodeAnalysis.data}
                      repoName={message.githubCodeAnalysis.repoName}
                    />
                  ) : message.optimizationPR ? (
                    <OptimizationPRView
                      data={message.optimizationPR.data}
                      repoName={message.optimizationPR.repoName}
                    />
                  ) : message.readmeGenerator ? (
                    <ReadmeGeneratorView
                      data={message.readmeGenerator.data}
                      repoName={message.readmeGenerator.repoName}
                    />
                  ) : message.seoOptimization ? (
                    <SEOOptimizationView
                      data={message.seoOptimization.data}
                      repoName={message.seoOptimization.repoName}
                    />
                  ) : message.rollbackIntelligence ? (
                    <RollbackIntelligence
                      repoOwner={message.rollbackIntelligence.repoOwner}
                      repoName={message.rollbackIntelligence.repoName}
                      branch={message.rollbackIntelligence.branch}
                    />
                  ) : (
                    <p className="text-base leading-relaxed whitespace-pre-wrap font-medium text-gray-100">
                      {message.content}
                    </p>
                  )}

                  {/* Timestamp and actions */}
                  {!message.analysis &&
                    !message.isStrategicAnalysis &&
                    !message.workflowOptimization &&
                    !message.workflowDeployment &&
                    !message.githubStructureAnalysis &&
                    !message.githubCodeAnalysis &&
                    !message.optimizationPR &&
                    !message.readmeGenerator &&
                    !message.seoOptimization &&
                    !message.rollbackIntelligence && (
                      <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-700/50">
                        <span
                          className={`text-sm font-medium ${
                            message.type === "user"
                              ? "text-white/70"
                              : "text-slate-400"
                          }`}
                        >
                          {message.timestamp.toLocaleTimeString()}
                        </span>
                        {message.type === "ai" && (
                          <div className="flex items-center gap-3">
                            <button className="text-gray-400 hover:text-slate-300 transition-all hover:scale-110">
                              <Copy className="w-4 h-4" />
                            </button>
                            <button className="text-gray-400 hover:text-slate-300 transition-all hover:scale-110">
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button className="text-gray-400 hover:text-red-400 transition-all hover:scale-110">
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </div>
                    )}
                </motion.div>
              </div>
              {message.type === "user" && (
                <div className="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <User className="w-5 h-5 text-white" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Typing indicator... */}
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-4"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-black" />
            </div>
            <div className="bg-gray-800/50 border border-slate-600/20 rounded-2xl p-4 backdrop-blur-sm">
              <div className="flex gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  className="w-2 h-2 bg-slate-400 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  className="w-2 h-2 bg-slate-400 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  className="w-2 h-2 bg-slate-400 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        )}

        {/* Repository Selection Options */}
        {showRepoOptions && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-4"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-slate-600 to-slate-500 rounded-full flex items-center justify-center">
              <Bot className="w-4 h-4 text-black" />
            </div>
            <div className="bg-gray-800/50 border border-slate-600/20 rounded-2xl p-4 backdrop-blur-sm">
              <p className="text-white text-sm mb-4">
                How would you like to proceed?
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                {selectedRepo ? (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRepoOptionSelect("repository")}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-blue-500 text-white rounded-lg font-medium hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-300"
                  >
                    <GitBranch className="w-4 h-4" />
                    Use "{selectedRepo.name}" repo
                  </motion.button>
                ) : (
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRepoOptionSelect("select")}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all duration-300"
                  >
                    <GitBranch className="w-4 h-4" />
                    Select a repository
                  </motion.button>
                )}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => handleRepoOptionSelect("general")}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg font-medium hover:bg-gray-700 transition-all duration-300"
                >
                  <Globe className="w-4 h-4" />
                  General assistance
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 border-t border-slate-600/20 bg-black/20 backdrop-blur-xl"
      >
        <div className="flex gap-4 items-end">
          <div className="flex-1 relative">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me to optimize code, deploy apps, analyze data... (Type '/clear' to clear chat)"
              className="w-full bg-gray-800/50 border border-gray-600 rounded-2xl px-6 py-4 pr-20 text-white placeholder-gray-400 resize-none focus:outline-none focus:border-slate-500/50 focus:shadow-lg focus:shadow-slate-500/10 transition-all duration-300 min-h-[60px] max-h-32"
              rows={1}
            />
            <button
              onClick={() => setIsListening(!isListening)}
              className={`absolute right-14 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all duration-300 ${
                isListening
                  ? "bg-red-500 text-white"
                  : "text-gray-400 hover:text-slate-300 hover:bg-gray-700/50"
              }`}
            >
              {isListening ? (
                <MicOff className="w-4 h-4" />
              ) : (
                <Mic className="w-4 h-4" />
              )}
            </button>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSendMessage}
            disabled={!inputValue.trim()}
            data-send-button
            className="bg-gradient-to-r from-blue-600 to-blue-500 rounded-2xl p-4 hover:shadow-lg hover:shadow-blue-500/20 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5 text-white" />
          </motion.button>
        </div>
        <div className="flex gap-2 mt-4 flex-wrap">
          {/* New Describe Repository API button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={async () => {
              if (!selectedRepo) {
                alert("Please select a repository first");
                return;
              }
              setShowRepoOptions(false);
              const loadingMessage = {
                id: generateMessageId(),
                type: "ai" as const,
                content: `Analyzing the \"${selectedRepo.name}\" repository... This may take a moment.`,
                timestamp: new Date(),
              };
              setMessages((prev) => [...prev, loadingMessage]);
              try {
                const response = await fetch(
                  "http://localhost:8000/describe-repository/",
                  {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      github_url: selectedRepo.html_url,
                      repo_owner: selectedRepo.owner.login,
                      repo_name: selectedRepo.name,
                      include_tech_stack: true,
                      include_architecture: true,
                      include_features: true,
                    }),
                  }
                );
                if (!response.ok)
                  throw new Error("Failed to analyze repository");
                const data = await response.json();
                const aiResponse = {
                  id: generateMessageId(),
                  type: "ai" as const,
                  content: "",
                  timestamp: new Date(),
                  analysis: { data, repoName: selectedRepo.name },
                };
                setMessages(
                  (prev) =>
                    prev.map((msg) =>
                      msg.id === loadingMessage.id ? aiResponse : msg
                    ) as Message[]
                );
                if (data.ai_insights?.strategic_analysis) {
                  const aiInsightsMessage = {
                    id: generateMessageId(),
                    type: "ai" as const,
                    content: data.ai_insights.strategic_analysis,
                    timestamp: new Date(),
                    isStrategicAnalysis: true,
                  };
                  setTimeout(() => {
                    setMessages(
                      (prev) => [...prev, aiInsightsMessage] as Message[]
                    );
                  }, 1000);
                }
              } catch (error) {
                console.error(error);
                const errorMessage = {
                  id: generateMessageId(),
                  type: "ai" as const,
                  content:
                    "Sorry, there was an error analyzing the repository. Please try again later.",
                  timestamp: new Date(),
                };
                setMessages(
                  (prev) =>
                    prev.map((msg) =>
                      msg.id === loadingMessage.id ? errorMessage : msg
                    ) as Message[]
                );
              }
            }}
            className="px-4 py-2 bg-blue-800/50 border border-blue-500/30 rounded-lg text-sm text-blue-300 hover:text-blue-200 hover:border-blue-400/50 transition-all duration-300"
          >
            Describe Repository
          </motion.button>
          {[
            "Optimize workflow",
            "Optimize workflow deployment",
            "Analyze GitHub structure",
            "Analyze GitHub code",
            "Create optimization PR",
            // Hidden for now - can be re-enabled later
            // "Generate README PR",
            "Optimize SEO",
          ].map((action) => (
            <motion.button
              key={action}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              data-action={action}
              onClick={() => {
                setInputValue(action);
                // Trigger the send after a short delay to allow state to update
                setTimeout(() => {
                  const sendButton = document.querySelector<HTMLButtonElement>('[data-send-button]');
                  if (sendButton) sendButton.click();
                }, 50);
              }}
              className="px-4 py-2 bg-gray-800/50 border border-slate-600/30 rounded-lg text-sm text-gray-300 hover:text-white hover:border-slate-500/50 transition-all duration-300"
            >
              {action}
            </motion.button>
          ))}

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setInputValue("/clear")}
            className="px-4 py-2 bg-red-800/50 border border-red-500/30 rounded-lg text-sm text-red-300 hover:text-red-200 hover:border-red-400/50 transition-all duration-300"
          >
            Clear Chat
          </motion.button>
        </div>
      </motion.div>
    </div>
  );
};
