import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart3,
  TrendingUp,
  Activity,
  Eye,
  RefreshCw,
  Download,
  Share,
  Leaf,
  Trophy,
} from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { useAuth } from "../contexts/AuthContext";
import {
  getAggregatedAnalytics,
  getRecentOptimizations,
  type AggregatedMetrics,
} from "../services/analyticsService";
import { Milestone } from "./Milestone";

export const AnalyticsPanel: React.FC = () => {
  const { user } = useAuth();
  const [viewMode, setViewMode] = useState<"charts" | "json" | "milestones">(
    "charts"
  );
  const [refreshing, setRefreshing] = useState(false);
  const [analytics, setAnalytics] = useState<AggregatedMetrics | null>(null);
  const [previousAnalytics, setPreviousAnalytics] =
    useState<AggregatedMetrics | null>(null);
  const [recentOptimizations, setRecentOptimizations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch analytics data
  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!user) return;

      setLoading(true);
      try {
        const [aggregatedData, recentData] = await Promise.all([
          getAggregatedAnalytics(user.uid),
          getRecentOptimizations(user.uid, 10),
        ]);

        setPreviousAnalytics(analytics);
        setAnalytics(aggregatedData);
        setRecentOptimizations(recentData);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [user]);

  // Transform data for charts
  const performanceData = analytics?.dailyOptimizations
    ?.slice(-7)
    .map((item) => ({
      name: new Date(item.date).toLocaleDateString("en-US", {
        weekday: "short",
      }),
      value: item.count,
      co2Saved: item.co2Saved,
    })) || [
    { name: "Mon", value: 0, co2Saved: 0 },
    { name: "Tue", value: 0, co2Saved: 0 },
    { name: "Wed", value: 0, co2Saved: 0 },
    { name: "Thu", value: 0, co2Saved: 0 },
    { name: "Fri", value: 0, co2Saved: 0 },
    { name: "Sat", value: 0, co2Saved: 0 },
    { name: "Sun", value: 0, co2Saved: 0 },
  ];

  const carbonSavingsData =
    analytics?.monthlyMetrics?.slice(-6).map((item) => ({
      month: new Date(item.month + "-01").toLocaleDateString("en-US", {
        month: "short",
      }),
      co2Saved: item.co2Saved,
      optimizations: item.optimizations,
    })) || [];

  const aiUsageData = analytics
    ? [
        {
          name: "Code Optimization",
          value:
            Math.round(
              (analytics.totalFilesOptimized / analytics.totalOptimizations) *
                100
            ) || 0,
          color: "#10B981",
        },
        {
          name: "Performance",
          value: Math.round(analytics.averagePerformanceImprovement) || 0,
          color: "#06B6D4",
        },
        {
          name: "Security",
          value:
            Math.round(
              (analytics.totalSecurityIssuesFixed /
                analytics.totalOptimizations) *
                10
            ) || 0,
          color: "#3B82F6",
        },
        {
          name: "Build Time",
          value: Math.round(analytics.averageBuildTimeReduction) || 0,
          color: "#8B5CF6",
        },
        {
          name: "Code Quality",
          value: Math.round(analytics.averageComplexityReduction) || 0,
          color: "#F59E0B",
        },
      ]
    : [
        { name: "Code Optimization", value: 0, color: "#10B981" },
        { name: "Performance", value: 0, color: "#06B6D4" },
        { name: "Security", value: 0, color: "#3B82F6" },
        { name: "Build Time", value: 0, color: "#8B5CF6" },
        { name: "Code Quality", value: 0, color: "#F59E0B" },
      ];

  const handleRefresh = async () => {
    setRefreshing(true);
    if (user) {
      try {
        const [aggregatedData, recentData] = await Promise.all([
          getAggregatedAnalytics(user.uid),
          getRecentOptimizations(user.uid, 10),
        ]);

        setPreviousAnalytics(analytics);
        setAnalytics(aggregatedData);
        setRecentOptimizations(recentData);
      } catch (error) {
        console.error("Error refreshing analytics:", error);
      }
    }
    setRefreshing(false);
  };

  const jsonData = {
    analytics: analytics || "No data available",
    recentOptimizations:
      recentOptimizations.slice(0, 3) || "No recent optimizations",
    summary: {
      totalOptimizations: analytics?.totalOptimizations || 0,
      co2Saved: analytics?.totalCO2SavedKg || 0,
      averageConfidence: analytics?.averageAIConfidenceScore || 0,
    },
  };

  return (
    <div className="h-full p-6 bg-gradient-to-br from-gray-900/50 to-black/50 overflow-y-auto">
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-2 border-green-500 border-t-transparent rounded-full"></div>
          <span className="ml-3 text-gray-400">Loading analytics...</span>
        </div>
      ) : (
        <>
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between mb-6"
          >
            <div>
              <h2 className="text-2xl font-bold text-white mb-2">
                Analytics & Insights
              </h2>
              <p className="text-gray-400">
                AI-generated flowcharts and performance metrics
              </p>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex bg-gray-800/50 rounded-lg p-1">
                <button
                  onClick={() => setViewMode("charts")}
                  className={`px-4 py-2 rounded text-sm font-medium transition-all duration-300 ${
                    viewMode === "charts"
                      ? "bg-green-500 text-black"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <BarChart3 className="w-4 h-4 inline mr-2" />
                  Charts
                </button>
                <button
                  onClick={() => setViewMode("json")}
                  className={`px-4 py-2 rounded text-sm font-medium transition-all duration-300 ${
                    viewMode === "json"
                      ? "bg-green-500 text-black"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <Eye className="w-4 h-4 inline mr-2" />
                  JSON
                </button>
                <button
                  onClick={() => setViewMode("milestones")}
                  className={`px-4 py-2 rounded text-sm font-medium transition-all duration-300 ${
                    viewMode === "milestones"
                      ? "bg-green-500 text-black"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  <Trophy className="w-4 h-4 inline mr-2" />
                  Milestones
                </button>
              </div>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleRefresh}
                disabled={refreshing}
                className="p-2 bg-gray-800/50 border border-green-500/30 rounded-lg hover:border-green-400/50 transition-all duration-300"
              >
                <RefreshCw
                  className={`w-4 h-4 text-green-400 ${
                    refreshing ? "animate-spin" : ""
                  }`}
                />
              </motion.button>

              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-lg transition-all duration-300">
                <Download className="w-4 h-4" />
              </button>

              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-lg transition-all duration-300">
                <Share className="w-4 h-4" />
              </button>
            </div>
          </motion.div>

          {viewMode === "charts" ? (
            <div className="space-y-6">
              {/* Key Metrics */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="grid grid-cols-1 md:grid-cols-3 gap-6"
              >
                <div className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-green-400 to-emerald-500 rounded-xl flex items-center justify-center">
                      <Activity className="w-6 h-6 text-black" />
                    </div>
                    <span className="text-green-400 text-sm font-medium">
                      {analytics?.averagePerformanceImprovement
                        ? `+${analytics.averagePerformanceImprovement.toFixed(
                            1
                          )}%`
                        : "+0%"}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-1">
                    {analytics?.averageAIConfidenceScore
                      ? (analytics.averageAIConfidenceScore * 100).toFixed(1)
                      : "0"}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    Average AI Confidence Score
                  </p>
                </div>

                <div className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-black" />
                    </div>
                    <span className="text-blue-400 text-sm font-medium">
                      {analytics?.averageBuildTimeReduction
                        ? `${analytics.averageBuildTimeReduction.toFixed(1)}%`
                        : "0%"}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-1">
                    {analytics?.totalOptimizations || 0}
                  </h3>
                  <p className="text-gray-400 text-sm">Total Optimizations</p>
                </div>

                <div className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-emerald-400 to-teal-500 rounded-xl flex items-center justify-center">
                      <Leaf className="w-6 h-6 text-black" />
                    </div>
                    <span className="text-emerald-400 text-sm font-medium">
                      {analytics?.totalTreesEquivalent
                        ? `${analytics.totalTreesEquivalent.toFixed(1)} trees`
                        : "0 trees"}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-1">
                    {analytics?.totalCO2SavedKg
                      ? analytics.totalCO2SavedKg.toFixed(1)
                      : "0"}
                  </h3>
                  <p className="text-gray-400 text-sm">CO₂ Saved (kg)</p>
                </div>
              </motion.div>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance Trend */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6"
                >
                  <h3 className="text-lg font-bold text-white mb-4">
                    Performance Trend
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="name" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#1F2937",
                          border: "1px solid #10B981",
                          borderRadius: "8px",
                          color: "#fff",
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#10B981"
                        strokeWidth={3}
                        dot={{ fill: "#10B981", strokeWidth: 2, r: 6 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </motion.div>

                {/* Carbon Savings Over Time */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6"
                >
                  <h3 className="text-lg font-bold text-white mb-4">
                    Carbon Savings Over Time
                  </h3>
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={carbonSavingsData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis
                        dataKey="month"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      />
                      <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: "#9CA3AF", fontSize: 12 }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#111827",
                          border: "1px solid #10B981",
                          borderRadius: "8px",
                          color: "#fff",
                        }}
                      />
                      <Bar
                        dataKey="co2Saved"
                        fill="#10B981"
                        radius={[4, 4, 0, 0]}
                      />
                    </BarChart>
                  </ResponsiveContainer>
                </motion.div>
              </div>

              {/* AI Usage Distribution */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-black/40 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6"
              >
                <h3 className="text-lg font-bold text-white mb-4">
                  AI Usage Distribution
                </h3>
                <div className="flex items-center justify-center">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={aiUsageData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={120}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {aiUsageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#1F2937",
                          border: "1px solid #10B981",
                          borderRadius: "8px",
                          color: "#fff",
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>

                  {/* Legend */}
                  <div className="ml-8 space-y-3">
                    {aiUsageData.map((item, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm text-gray-300">
                          {item.name}
                        </span>
                        <span className="text-sm text-gray-400">
                          {item.value}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            </div>
          ) : viewMode === "json" ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-black/60 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6"
            >
              <pre className="text-green-400 font-mono text-sm overflow-auto">
                {JSON.stringify(jsonData, null, 2)}
              </pre>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-black/60 backdrop-blur-sm border border-green-500/20 rounded-2xl p-6"
            >
              <Milestone
                analytics={{
                  totalCO2SavedKg: analytics?.totalCO2SavedKg || 0,
                  totalOptimizations: analytics?.totalOptimizations || 0,
                  averagePerformanceImprovement:
                    analytics?.averagePerformanceImprovement || 0,
                  totalSecurityIssuesFixed:
                    analytics?.totalSecurityIssuesFixed || 0,
                  averageBuildTimeReduction:
                    analytics?.averageBuildTimeReduction || 0,
                  totalRepositoriesOptimized:
                    analytics?.repositoriesOptimized || 0,
                }}
                previousAnalytics={
                  previousAnalytics
                    ? {
                        totalCO2SavedKg: previousAnalytics.totalCO2SavedKg || 0,
                        totalOptimizations:
                          previousAnalytics.totalOptimizations || 0,
                        averagePerformanceImprovement:
                          previousAnalytics.averagePerformanceImprovement || 0,
                        totalSecurityIssuesFixed:
                          previousAnalytics.totalSecurityIssuesFixed || 0,
                        averageBuildTimeReduction:
                          previousAnalytics.averageBuildTimeReduction || 0,
                        totalRepositoriesOptimized:
                          previousAnalytics.repositoriesOptimized || 0,
                      }
                    : undefined
                }
              />
            </motion.div>
          )}
        </>
      )}
    </div>
  );
};
