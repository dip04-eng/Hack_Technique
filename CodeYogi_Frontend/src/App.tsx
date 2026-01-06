import React from "react";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { SelectedRepositoryProvider } from "./contexts/SelectedRepositoryContext";
import { ThemeProvider } from "./contexts/ThemeContext";
import { MonitoringProvider } from "./contexts/MonitoringContext";
import { ChatProvider } from "./contexts/ChatContext";
import { NotificationProvider } from "./components/Notifications";
import { Dashboard } from "./components/Dashboard";
import { Login } from "./components/Login";

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black flex items-center justify-center">
        <div className="text-green-400 text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black">
      {user ? <Dashboard /> : <Login />}
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <SelectedRepositoryProvider>
          <ChatProvider>
            <MonitoringProvider>
              <NotificationProvider>
                <AppContent />
              </NotificationProvider>
            </MonitoringProvider>
          </ChatProvider>
        </SelectedRepositoryProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
