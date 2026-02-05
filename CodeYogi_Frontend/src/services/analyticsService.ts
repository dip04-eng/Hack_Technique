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

    if (!userMetricsSnapshot.exists()) {
      // Create initial aggregated metrics
      const initialMetrics: AggregatedMetrics = {
        // AI Metrics
        totalAICompletions:
          metricsData.ai_completion_metrics.total_ai_completions,
        totalAIProcessingTime:
          metricsData.ai_completion_metrics.ai_processing_time,
        averageAIConfidenceScore:
          metricsData.ai_completion_metrics.ai_confidence_score,
        totalAISuggestionsApplied:
          metricsData.ai_completion_metrics.ai_suggestions_applied,

        // Code Optimization
        totalFilesOptimized:
          metricsData.code_optimization_metrics.files_optimized,
        totalLinesImproved:
          metricsData.code_optimization_metrics.lines_of_code_improved,
        averagePerformanceImprovement:
          metricsData.code_optimization_metrics.performance_improvement_percent,
        averageComplexityReduction:
          metricsData.code_optimization_metrics.complexity_reduction_percent,
        totalSecurityIssuesFixed:
          metricsData.code_optimization_metrics.security_issues_fixed,
        averageCodeDuplicationReduced:
          metricsData.code_optimization_metrics
            .code_duplication_reduced_percent,
        averageTestCoverageImprovement:
          metricsData.code_optimization_metrics.test_coverage_improvement,
        averageBuildTimeReduction:
          metricsData.code_optimization_metrics.build_time_reduction_percent,

        // Carbon Savings
        totalCO2SavedKg: metricsData.carbon_savings_metrics.total_co2_saved_kg,
        totalCO2SavedBuild:
          metricsData.carbon_savings_metrics.co2_saved_build_process,
        totalCO2SavedRuntime:
          metricsData.carbon_savings_metrics.co2_saved_runtime,
        totalCO2SavedDevelopment:
          metricsData.carbon_savings_metrics.co2_saved_development,
        totalTreesEquivalent:
          metricsData.carbon_savings_metrics.trees_equivalent,
        totalCarMilesEquivalent:
          metricsData.carbon_savings_metrics.car_miles_equivalent,
        totalEnergySavedKwh:
          metricsData.carbon_savings_metrics.energy_saved_kwh,
        totalMonthlySavingsEstimate:
          metricsData.carbon_savings_metrics.monthly_savings_estimate,

        // Repository Stats
        totalOptimizations: 1,
        repositoriesOptimized: 1,
        languagesOptimized: [metricsData.repository_statistics.repo_language],

        // Session Info
        lastOptimization:
          metricsData.session_information.optimization_timestamp,
        firstOptimization:
          metricsData.session_information.optimization_timestamp,
        optimizationTypes: [metricsData.session_information.optimization_type],

        // Time-based data
        dailyOptimizations: [
          {
            date: new Date().toISOString().split("T")[0],
            count: 1,
            co2Saved: metricsData.carbon_savings_metrics.total_co2_saved_kg,
          },
        ],
        monthlyMetrics: [
          {
            month: new Date().toISOString().slice(0, 7), // YYYY-MM
            optimizations: 1,
            performance:
              metricsData.code_optimization_metrics
                .performance_improvement_percent,
            co2Saved: metricsData.carbon_savings_metrics.total_co2_saved_kg,
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
        dailyOptimizations[todayIndex].co2Saved +=
          metricsData.carbon_savings_metrics.total_co2_saved_kg;
      } else {
        dailyOptimizations.push({
          date: today,
          count: 1,
          co2Saved: metricsData.carbon_savings_metrics.total_co2_saved_kg,
        });
      }

      // Update monthly metrics
      const monthlyMetrics = existingData.monthlyMetrics || [];
      const monthIndex = monthlyMetrics.findIndex(
        (m) => m.month === currentMonth
      );

      if (monthIndex >= 0) {
        monthlyMetrics[monthIndex].optimizations += 1;
        monthlyMetrics[monthIndex].co2Saved +=
          metricsData.carbon_savings_metrics.total_co2_saved_kg;
        monthlyMetrics[monthIndex].performance =
          (monthlyMetrics[monthIndex].performance +
            metricsData.code_optimization_metrics
              .performance_improvement_percent) /
          2;
      } else {
        monthlyMetrics.push({
          month: currentMonth,
          optimizations: 1,
          performance:
            metricsData.code_optimization_metrics
              .performance_improvement_percent,
          co2Saved: metricsData.carbon_savings_metrics.total_co2_saved_kg,
        });
      }

      // Update languages optimized
      const languagesOptimized = existingData.languagesOptimized || [];
      if (
        !languagesOptimized.includes(
          metricsData.repository_statistics.repo_language
        )
      ) {
        languagesOptimized.push(
          metricsData.repository_statistics.repo_language
        );
      }

      // Update optimization types
      const optimizationTypes = existingData.optimizationTypes || [];
      if (
        !optimizationTypes.includes(
          metricsData.session_information.optimization_type
        )
      ) {
        optimizationTypes.push(
          metricsData.session_information.optimization_type
        );
      }

      // Calculate new averages
      const totalOptimizations = existingData.totalOptimizations + 1;
      const newAverageAIConfidence =
        (existingData.averageAIConfidenceScore *
          existingData.totalOptimizations +
          metricsData.ai_completion_metrics.ai_confidence_score) /
        totalOptimizations;

      const updateData = {
        // Increment counters
        totalAICompletions: increment(
          metricsData.ai_completion_metrics.total_ai_completions
        ),
        totalAIProcessingTime: increment(
          metricsData.ai_completion_metrics.ai_processing_time
        ),
        totalAISuggestionsApplied: increment(
          metricsData.ai_completion_metrics.ai_suggestions_applied
        ),
        totalFilesOptimized: increment(
          metricsData.code_optimization_metrics.files_optimized
        ),
        totalLinesImproved: increment(
          metricsData.code_optimization_metrics.lines_of_code_improved
        ),
        totalSecurityIssuesFixed: increment(
          metricsData.code_optimization_metrics.security_issues_fixed
        ),
        totalCO2SavedKg: increment(
          metricsData.carbon_savings_metrics.total_co2_saved_kg
        ),
        totalCO2SavedBuild: increment(
          metricsData.carbon_savings_metrics.co2_saved_build_process
        ),
        totalCO2SavedRuntime: increment(
          metricsData.carbon_savings_metrics.co2_saved_runtime
        ),
        totalCO2SavedDevelopment: increment(
          metricsData.carbon_savings_metrics.co2_saved_development
        ),
        totalTreesEquivalent: increment(
          metricsData.carbon_savings_metrics.trees_equivalent
        ),
        totalCarMilesEquivalent: increment(
          metricsData.carbon_savings_metrics.car_miles_equivalent
        ),
        totalEnergySavedKwh: increment(
          metricsData.carbon_savings_metrics.energy_saved_kwh
        ),
        totalMonthlySavingsEstimate: increment(
          metricsData.carbon_savings_metrics.monthly_savings_estimate
        ),
        totalOptimizations: increment(1),

        // Update averages and other fields
        averageAIConfidenceScore: newAverageAIConfidence,
        lastOptimization:
          metricsData.session_information.optimization_timestamp,
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
