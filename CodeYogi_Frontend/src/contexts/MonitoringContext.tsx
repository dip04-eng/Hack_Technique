import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
  ReactNode,
} from "react";
import { getApiUrl } from "../config/api";

interface CommitInfo {
  sha: string;
  author: string;
  email: string;
  message: string;
  date: string;
  url: string;
  tree_sha: string;
}

interface MonitoringResponse {
  success: boolean;
  has_new_push: boolean;
  latest_commit: CommitInfo;
  previous_sha: string;
  pr_created: boolean;
  pr_url: string;
  pr_number: number;
  message: string;
}

interface MonitoringState {
  isActive: boolean;
  repoUrl: string;
  lastKnownSha: string;
  githubToken: string;
  totalChecks: number;
  newPushesDetected: number;
  prsCreated: number;
  lastCheck: string;
  status: "idle" | "monitoring" | "error";
  latestCommit?: CommitInfo;
  lastResponse?: MonitoringResponse;
}

interface MonitoringContextType {
  state: MonitoringState;
  startMonitoring: (config: {
    repoUrl: string;
    lastKnownSha?: string;
    githubToken?: string;
  }) => void;
  stopMonitoring: () => void;
  updateConfig: (
    config: Partial<{
      repoUrl: string;
      lastKnownSha: string;
      githubToken: string;
    }>
  ) => void;
  checkNow: () => Promise<void>;
  logs: Array<{
    timestamp: string;
    message: string;
    type: "info" | "success" | "error";
  }>;
}

const MonitoringContext = createContext<MonitoringContextType | undefined>(
  undefined
);

export const useMonitoring = () => {
  const context = useContext(MonitoringContext);
  if (!context) {
    throw new Error("useMonitoring must be used within a MonitoringProvider");
  }
  return context;
};

interface MonitoringProviderProps {
  children: ReactNode;
}

export const MonitoringProvider: React.FC<MonitoringProviderProps> = ({
  children,
}) => {
  const [state, setState] = useState<MonitoringState>({
    isActive: false,
    repoUrl: "https://github.com/RajBhattacharyya/test-repo",
    lastKnownSha: "",
    githubToken: "",
    totalChecks: 0,
    newPushesDetected: 0,
    prsCreated: 0,
    lastCheck: "",
    status: "idle",
  });

  const [logs, setLogs] = useState<
    Array<{
      timestamp: string;
      message: string;
      type: "info" | "success" | "error";
    }>
  >([
    {
      timestamp: new Date().toLocaleTimeString(),
      message: "Repository monitoring service ready",
      type: "info",
    },
  ]);

  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const addLog = (
    message: string,
    type: "info" | "success" | "error" = "info"
  ) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev.slice(-19), { timestamp, message, type }]);
  };

  const checkRepository = async (): Promise<void> => {
    try {
      setState((prev) => ({
        ...prev,
        status: "monitoring",
        totalChecks: prev.totalChecks + 1,
        lastCheck: new Date().toLocaleString(),
      }));

      addLog("Checking repository for new pushes...", "info");

      const response = await fetch(getApiUrl("/repos/check-and-optimize"), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: state.repoUrl,
          last_known_sha: state.lastKnownSha,
          github_token: state.githubToken,
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data: MonitoringResponse = await response.json();

      setState((prev) => ({
        ...prev,
        status: "idle",
        latestCommit: data.latest_commit,
        lastResponse: data,
        newPushesDetected: data.has_new_push
          ? prev.newPushesDetected + 1
          : prev.newPushesDetected,
        prsCreated: data.pr_created ? prev.prsCreated + 1 : prev.prsCreated,
        lastKnownSha: data.has_new_push
          ? data.latest_commit.sha
          : prev.lastKnownSha,
      }));

      if (data.has_new_push) {
        addLog(`New push detected! ${data.message}`, "success");
        if (data.pr_created) {
          addLog(`PR #${data.pr_number} created successfully`, "success");
        }
      } else {
        addLog("No new pushes detected", "info");
      }
    } catch (error) {
      setState((prev) => ({ ...prev, status: "error" }));
      addLog(
        `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
        "error"
      );
    }
  };

  const startMonitoring = (config: {
    repoUrl: string;
    lastKnownSha?: string;
    githubToken?: string;
  }) => {
    if (!config.repoUrl.trim()) {
      addLog("Please enter a repository URL", "error");
      return;
    }

    setState((prev) => ({
      ...prev,
      isActive: true,
      repoUrl: config.repoUrl,
      lastKnownSha: config.lastKnownSha || "",
      githubToken: config.githubToken || "",
      status: "monitoring",
    }));

    addLog("Monitoring started", "success");

    // Initial check
    checkRepository();

    // Set up polling every 1 minute (60000ms)
    intervalRef.current = setInterval(checkRepository, 60000);
  };

  const stopMonitoring = () => {
    setState((prev) => ({
      ...prev,
      isActive: false,
      status: "idle",
    }));

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    addLog("Monitoring stopped", "info");
  };

  const updateConfig = (
    config: Partial<{
      repoUrl: string;
      lastKnownSha: string;
      githubToken: string;
    }>
  ) => {
    setState((prev) => ({ ...prev, ...config }));
  };

  const checkNow = async () => {
    if (!state.repoUrl.trim()) {
      addLog("Please configure a repository URL first", "error");
      return;
    }
    await checkRepository();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const value: MonitoringContextType = {
    state,
    startMonitoring,
    stopMonitoring,
    updateConfig,
    checkNow,
    logs,
  };

  return (
    <MonitoringContext.Provider value={value}>
      {children}
    </MonitoringContext.Provider>
  );
};
