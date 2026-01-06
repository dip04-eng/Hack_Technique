import {
  doc,
  setDoc,
  getDoc,
  updateDoc,
  serverTimestamp,
  increment,
  collection,
  addDoc,
} from "firebase/firestore";
import { db } from "../config/firebase";

// Interfaces for analytics data
export interface WorkflowMetrics {
  total_ai_completions: number;
  ai_processing_time: number;
  ai_model_used: string;
  ai_confidence_score: number;
  ai_suggestions_applied: number;
  files_optimized: number;
  lines_of_code_improved: number;
  performance_improvement_percent: number;
  complexity_reduction_percent: number;
  security_issues_fixed: number;
  code_duplication_reduced_percent: number;
  test_coverage_improvement: number;
  build_time_reduction_percent: number;
  total_co2_saved_kg: number;
  co2_saved_build_process: number;
  co2_saved_runtime: number;
  co2_saved_development: number;
  trees_equivalent: number;
  car_miles_equivalent: number;
  energy_saved_kwh: number;
  monthly_savings_estimate: number;
  carbon_footprint_reduction_percent: number;
  repo_size: number;
  repo_language: string;
  stars_count: number;
  forks_count: number;
  open_issues: number;
  optimization_timestamp: string;
  session_id: string;
  optimization_type: string;
  pr_number: number;
  pr_url: string;
  branch_name: string;
  commit_sha: string;
  workflow_path: string;
}

export interface AggregatedMetrics {
  // AI Metrics
  totalAICompletions: number;
  totalAIProcessingTime: number;
  averageAIConfidenceScore: number;
  totalAISuggestionsApplied: number;

  // Code Optimization Metrics
  totalFilesOptimized: number;
  totalLinesImproved: number;
  averagePerformanceImprovement: number;
  averageComplexityReduction: number;
  totalSecurityIssuesFixed: number;
  averageCodeDuplicationReduced: number;
  averageTestCoverageImprovement: number;
  averageBuildTimeReduction: number;

  // Carbon Savings
  totalCO2SavedKg: number;
  totalCO2SavedBuild: number;
  totalCO2SavedRuntime: number;
  totalCO2SavedDevelopment: number;
  totalTreesEquivalent: number;
  totalCarMilesEquivalent: number;
  totalEnergySavedKwh: number;
  totalMonthlySavingsEstimate: number;

  // Repository Stats
  totalOptimizations: number;
  repositoriesOptimized: number;
  languagesOptimized: string[];

  // Session Info
  lastOptimization: string;
  firstOptimization: string;
  optimizationTypes: string[];

  // Time-based data for charts
  dailyOptimizations: { date: string; count: number; co2Saved: number }[];
  monthlyMetrics: {
    month: string;
    optimizations: number;
    performance: number;
    co2Saved: number;
  }[];
}

/**
 * Save workflow deployment metrics to Firebase
 */
export const saveWorkflowMetrics = async (
  userId: string,
  metricsData: any
): Promise<void> => {
  try {
    // Save individual session data
    const sessionRef = collection(db, "users", userId, "optimization_sessions");
    await addDoc(sessionRef, {
      ...metricsData,
      timestamp: serverTimestamp(),
      createdAt: serverTimestamp(),
    });

    // Update aggregated metrics
    const userMetricsRef = doc(db, "users", userId, "analytics", "aggregated");
    const userMetricsSnapshot = await getDoc(userMetricsRef);

    // Helper function to safely get nested values with defaults
    const safeGet = (obj: any, path: string, defaultValue: any = 0) => {
      const keys = path.split('.');
      let result = obj;
      for (const key of keys) {
        if (result === undefined || result === null) return defaultValue;
        result = result[key];
      }
      return result ?? defaultValue;
    };

    // Extract values with safe defaults for both complex and simple data structures
    const aiCompletions = safeGet(metricsData, 'ai_completion_metrics.total_ai_completions', 1);
    const aiProcessingTime = safeGet(metricsData, 'ai_completion_metrics.ai_processing_time', 0);
    const aiConfidenceScore = safeGet(metricsData, 'confidence_score', safeGet(metricsData, 'ai_completion_metrics.ai_confidence_score', 0));
    const aiSuggestionsApplied = safeGet(metricsData, 'ai_completion_metrics.ai_suggestions_applied', 0);
    
    const filesOptimized = safeGet(metricsData, 'code_optimization_metrics.files_optimized', 0);
    const linesImproved = safeGet(metricsData, 'code_optimization_metrics.lines_of_code_improved', 0);
    const performanceImprovement = safeGet(metricsData, 'code_optimization_metrics.performance_improvement_percent', 0);
    const complexityReduction = safeGet(metricsData, 'code_optimization_metrics.complexity_reduction_percent', 0);
    const securityIssuesFixed = safeGet(metricsData, 'code_optimization_metrics.security_issues_fixed', 0);
    const codeDuplicationReduced = safeGet(metricsData, 'code_optimization_metrics.code_duplication_reduced_percent', 0);
    const testCoverageImprovement = safeGet(metricsData, 'code_optimization_metrics.test_coverage_improvement', 0);
    const buildTimeReduction = safeGet(metricsData, 'code_optimization_metrics.build_time_reduction_percent', 0);
    
    const totalCO2Saved = safeGet(metricsData, 'carbon_savings_metrics.total_co2_saved_kg', 0);
    const co2SavedBuild = safeGet(metricsData, 'carbon_savings_metrics.co2_saved_build_process', 0);
    const co2SavedRuntime = safeGet(metricsData, 'carbon_savings_metrics.co2_saved_runtime', 0);
    const co2SavedDevelopment = safeGet(metricsData, 'carbon_savings_metrics.co2_saved_development', 0);
    const treesEquivalent = safeGet(metricsData, 'carbon_savings_metrics.trees_equivalent', 0);
    const carMilesEquivalent = safeGet(metricsData, 'carbon_savings_metrics.car_miles_equivalent', 0);
    const energySavedKwh = safeGet(metricsData, 'carbon_savings_metrics.energy_saved_kwh', 0);
    const monthlySavingsEstimate = safeGet(metricsData, 'carbon_savings_metrics.monthly_savings_estimate', 0);
    
    const repoLanguage = safeGet(metricsData, 'repository_statistics.repo_language', safeGet(metricsData, 'repo_language', 'unknown'));
    const optimizationType = safeGet(metricsData, 'session_information.optimization_type', safeGet(metricsData, 'optimization_type', 'workflow'));
    const optimizationTimestamp = safeGet(metricsData, 'session_information.optimization_timestamp', safeGet(metricsData, 'timestamp', new Date().toISOString()));

    if (!userMetricsSnapshot.exists()) {
      // Create initial aggregated metrics
      const initialMetrics: AggregatedMetrics = {
        // AI Metrics
        totalAICompletions: aiCompletions,
        totalAIProcessingTime: aiProcessingTime,
        averageAIConfidenceScore: aiConfidenceScore,
        totalAISuggestionsApplied: aiSuggestionsApplied,

        // Code Optimization
        totalFilesOptimized: filesOptimized,
        totalLinesImproved: linesImproved,
        averagePerformanceImprovement: performanceImprovement,
        averageComplexityReduction: complexityReduction,
        totalSecurityIssuesFixed: securityIssuesFixed,
        averageCodeDuplicationReduced: codeDuplicationReduced,
        averageTestCoverageImprovement: testCoverageImprovement,
        averageBuildTimeReduction: buildTimeReduction,

        // Carbon Savings
        totalCO2SavedKg: totalCO2Saved,
        totalCO2SavedBuild: co2SavedBuild,
        totalCO2SavedRuntime: co2SavedRuntime,
        totalCO2SavedDevelopment: co2SavedDevelopment,
        totalTreesEquivalent: treesEquivalent,
        totalCarMilesEquivalent: carMilesEquivalent,
        totalEnergySavedKwh: energySavedKwh,
        totalMonthlySavingsEstimate: monthlySavingsEstimate,

        // Repository Stats
        totalOptimizations: 1,
        repositoriesOptimized: 1,
        languagesOptimized: repoLanguage ? [repoLanguage] : [],

        // Session Info
        lastOptimization: optimizationTimestamp,
        firstOptimization: optimizationTimestamp,
        optimizationTypes: optimizationType ? [optimizationType] : [],

        // Time-based data
        dailyOptimizations: [
          {
            date: new Date().toISOString().split("T")[0],
            count: 1,
            co2Saved: totalCO2Saved,
          },
        ],
        monthlyMetrics: [
          {
            month: new Date().toISOString().slice(0, 7), // YYYY-MM
            optimizations: 1,
            performance: performanceImprovement,
            co2Saved: totalCO2Saved,
          },
        ],
      };

      await setDoc(userMetricsRef, {
        ...initialMetrics,
        lastUpdated: serverTimestamp(),
        createdAt: serverTimestamp(),
      });
    } else {
      // Update existing aggregated metrics
      const existingData = userMetricsSnapshot.data() as AggregatedMetrics;
      const today = new Date().toISOString().split("T")[0];
      const currentMonth = new Date().toISOString().slice(0, 7);

      // Update daily optimizations
      const dailyOptimizations = existingData.dailyOptimizations || [];
      const todayIndex = dailyOptimizations.findIndex((d) => d.date === today);

      if (todayIndex >= 0) {
        dailyOptimizations[todayIndex].count += 1;
        dailyOptimizations[todayIndex].co2Saved += totalCO2Saved;
      } else {
        dailyOptimizations.push({
          date: today,
          count: 1,
          co2Saved: totalCO2Saved,
        });
      }

      // Update monthly metrics
      const monthlyMetrics = existingData.monthlyMetrics || [];
      const monthIndex = monthlyMetrics.findIndex(
        (m) => m.month === currentMonth
      );

      if (monthIndex >= 0) {
        monthlyMetrics[monthIndex].optimizations += 1;
        monthlyMetrics[monthIndex].co2Saved += totalCO2Saved;
        monthlyMetrics[monthIndex].performance =
          (monthlyMetrics[monthIndex].performance + performanceImprovement) / 2;
      } else {
        monthlyMetrics.push({
          month: currentMonth,
          optimizations: 1,
          performance: performanceImprovement,
          co2Saved: totalCO2Saved,
        });
      }

      // Update languages optimized
      const languagesOptimized = existingData.languagesOptimized || [];
      if (repoLanguage && !languagesOptimized.includes(repoLanguage)) {
        languagesOptimized.push(repoLanguage);
      }

      // Update optimization types
      const optimizationTypes = existingData.optimizationTypes || [];
      if (optimizationType && !optimizationTypes.includes(optimizationType)) {
        optimizationTypes.push(optimizationType);
      }

      // Calculate new averages
      const totalOptimizations = existingData.totalOptimizations + 1;
      const newAverageAIConfidence =
        (existingData.averageAIConfidenceScore *
          existingData.totalOptimizations +
          aiConfidenceScore) /
        totalOptimizations;

      const updateData = {
        // Increment counters
        totalAICompletions: increment(aiCompletions),
        totalAIProcessingTime: increment(aiProcessingTime),
        totalAISuggestionsApplied: increment(aiSuggestionsApplied),
        totalFilesOptimized: increment(filesOptimized),
        totalLinesImproved: increment(linesImproved),
        totalSecurityIssuesFixed: increment(securityIssuesFixed),
        totalCO2SavedKg: increment(totalCO2Saved),
        totalCO2SavedBuild: increment(co2SavedBuild),
        totalCO2SavedRuntime: increment(co2SavedRuntime),
        totalCO2SavedDevelopment: increment(co2SavedDevelopment),
        totalTreesEquivalent: increment(treesEquivalent),
        totalCarMilesEquivalent: increment(carMilesEquivalent),
        totalEnergySavedKwh: increment(energySavedKwh),
        totalMonthlySavingsEstimate: increment(monthlySavingsEstimate),
        totalOptimizations: increment(1),

        // Update averages and other fields
        averageAIConfidenceScore: newAverageAIConfidence,
        lastOptimization: optimizationTimestamp,
        languagesOptimized,
        optimizationTypes,
        dailyOptimizations,
        monthlyMetrics,
        lastUpdated: serverTimestamp(),
      };

      await updateDoc(userMetricsRef, updateData);
    }

    console.log("Workflow metrics saved successfully");
  } catch (error) {
    console.error("Error saving workflow metrics:", error);
    throw error;
  }
};

/**
 * Get aggregated analytics for a user
 */
export const getAggregatedAnalytics = async (
  userId: string
): Promise<AggregatedMetrics | null> => {
  try {
    const userMetricsRef = doc(db, "users", userId, "analytics", "aggregated");
    const snapshot = await getDoc(userMetricsRef);

    if (snapshot.exists()) {
      return snapshot.data() as AggregatedMetrics;
    }
    return null;
  } catch (error) {
    console.error("Error fetching aggregated analytics:", error);
    return null;
  }
};

/**
 * Get recent optimization sessions
 */
export const getRecentOptimizations = async (
  userId: string,
  limit: number = 10
) => {
  try {
    const { query, orderBy, limitToLast, getDocs } = await import(
      "firebase/firestore"
    );

    const sessionsRef = collection(
      db,
      "users",
      userId,
      "optimization_sessions"
    );
    const q = query(
      sessionsRef,
      orderBy("timestamp", "desc"),
      limitToLast(limit)
    );
    const snapshot = await getDocs(q);

    return snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }));
  } catch (error) {
    console.error("Error fetching recent optimizations:", error);
    return [];
  }
};

/**
 * Demo function to test saving workflow metrics
 * This can be used in development to populate analytics data
 */
export const saveDemoWorkflowMetrics = async (userId: string) => {
  const demoData = {
    success: true,
    pr_number: 109,
    pr_url: "https://github.com/RajBhattacharyya/pv_app_api/pull/109",
    branch_name: "codeyogi-workflow-optimization",
    commit_sha: "1683d29200a5a75beb11f346c4569cef0e677b3e",
    workflow_path: ".github/workflows/codeyogi-optimized.yml",
    ai_completion_metrics: {
      total_ai_completions: 1,
      ai_processing_time: 1753562364.7988932,
      ai_model_used: "CodeYogi AI v2.0",
      ai_confidence_score: 0.92,
      ai_suggestions_applied: 1,
    },
    code_optimization_metrics: {
      files_optimized: 1,
      lines_of_code_improved: 150,
      performance_improvement_percent: 35,
      complexity_reduction_percent: 25,
      security_issues_fixed: 3,
      code_duplication_reduced_percent: 15,
      test_coverage_improvement: 12,
      build_time_reduction_percent: 40,
    },
    carbon_savings_metrics: {
      total_co2_saved_kg: 88.327,
      co2_saved_build_process: 0.09,
      co2_saved_runtime: 88.2,
      co2_saved_development: 0.037,
      trees_equivalent: 4.06,
      car_miles_equivalent: 218.6,
      energy_saved_kwh: 176.65,
      monthly_savings_estimate: 1059.93,
      carbon_footprint_reduction_percent: 883.3,
    },
    repository_statistics: {
      repo_size: 213,
      repo_language: "JavaScript",
      stars_count: 0,
      forks_count: 0,
      open_issues: 6,
    },
    session_information: {
      optimization_timestamp: "2025-07-26T20:39:24.798893",
      session_id: "codeyogi-1753562364",
      optimization_type: "workflow",
    },
  };

  return await saveWorkflowMetrics(userId, demoData);
};
