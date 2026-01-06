import React from "react";
import { motion } from "framer-motion";
import { Github, Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export const Login: React.FC = () => {
  const { signInWithGitHub, loading, error } = useAuth();

  const handleGitHubLogin = async () => {
    try {
      await signInWithGitHub();
    } catch (err) {
      console.error("Login failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-900 to-black flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-black/50 backdrop-blur-xl border border-green-500/20 rounded-2xl p-8 shadow-2xl">
          {/* Logo and Title */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-16 h-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-4"
            >
              <Github className="w-8 h-8 text-black" />
            </motion.div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent mb-2">
              CodeYogi
            </h1>
            <p className="text-gray-400 text-sm">
              Sign in with GitHub to continue
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-3"
            >
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
              <p className="text-red-400 text-sm">{error}</p>
            </motion.div>
          )}

          {/* GitHub Login Button */}
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleGitHubLogin}
            disabled={loading}
            className="w-full flex items-center justify-center gap-3 py-3 px-4 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:from-gray-600 disabled:to-gray-700 rounded-lg font-medium text-black transition-all duration-300 shadow-lg hover:shadow-green-500/25"
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Github className="w-5 h-5" />
            )}
            {loading ? "Signing in..." : "Continue with GitHub"}
          </motion.button>

          {/* Features */}
          <div className="mt-8 space-y-3">
            <h3 className="text-sm font-medium text-gray-400 text-center mb-4">
              What you'll get:
            </h3>
            <div className="space-y-2">
              {[
                "AI-powered development assistant",
                "Project analytics and insights",
                "Automated code generation",
                "Real-time collaboration tools",
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-center gap-3 text-sm text-gray-300"
                >
                  <div className="w-1.5 h-1.5 bg-green-400 rounded-full"></div>
                  {feature}
                </motion.div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-700/50 text-center">
            <p className="text-xs text-gray-500">
              By signing in, you agree to our Terms of Service and Privacy
              Policy
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
