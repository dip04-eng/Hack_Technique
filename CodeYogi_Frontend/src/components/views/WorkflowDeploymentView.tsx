import React, { useState, useEffect } from "react";
import { WorkflowDeployment } from "../../types/chat";
import { saveWorkflowMetrics } from "../../services/analyticsService";
import { useAuth } from "../../contexts/AuthContext";
import { useNotifications } from "../Notifications";

const WorkflowDeploymentView: React.FC<{
  data: WorkflowDeployment;
  repoName: string;
}> = ({ data, repoName }) => {
  const { user } = useAuth();
  const { addNotification } = useNotifications();
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [showComparison, setShowComparison] = useState(true);
  const [metricsSaved, setMetricsSaved] = useState(false);

  // Safely access nested properties with defaults
  const prInfo = data?.pr_info || {};
  const optimizationAnalysis = data?.optimization_analysis || {};
  const analysis = optimizationAnalysis?.analysis || {};
  const aiInsights = optimizationAnalysis?.ai_insights || {};
  const optimizedWorkflow = optimizationAnalysis?.optimized_workflow || {};
  const recommendations = optimizationAnalysis?.recommendations || {};
  const existingWorkflows = analysis?.existing_workflows || [];

  // Save metrics to Firebase when component mounts with new data
  useEffect(() => {
    const saveMetrics = async () => {
      if (user && prInfo?.success && !metricsSaved) {
        try {
          console.log("=== WorkflowDeploymentView: Starting metrics save ===");
          console.log("User ID:", user.uid);
          console.log("PR Info:", prInfo);
          
          // Build a complete metrics object from available data
          const metricsToSave = {
            // PR Info
            pr_number: prInfo?.pr_number || 0,
            pr_url: prInfo?.pr_url || '',
            branch_name: prInfo?.branch_name || '',
            commit_sha: prInfo?.commit_sha || '',
            workflow_path: prInfo?.workflow_path || '',
            success: prInfo?.success || false,
            
            // Repository info
            repo_name: repoName,
            
            // Optimization details
            optimization_type: optimizedWorkflow?.optimization_type || 'workflow',
            confidence_score: optimizedWorkflow?.confidence_score || 0,
            estimated_time_savings: optimizedWorkflow?.estimated_time_savings || 'N/A',
            improvements: optimizedWorkflow?.improvements || [],
            
            // AI insights
            model_used: aiInsights?.model_used || 'unknown',
            
            // Timestamps
            timestamp: new Date().toISOString(),
          };
          
          console.log("Metrics to save:", metricsToSave);
          await saveWorkflowMetrics(user.uid, metricsToSave);
          setMetricsSaved(true);
          console.log("=== Workflow metrics saved successfully ===");

          // Show success notification when PR is created
          addNotification({
            type: "success",
            title: "Pull Request Created!",
            message: `Successfully created PR for ${repoName}. Optimization metrics saved.`,
            duration: 5000,
          });
        } catch (error) {
          console.error("=== Failed to save workflow metrics ===");
          console.error("Error type:", error?.constructor?.name);
          console.error("Error message:", error?.message);
          console.error("Full error:", error);
          // Error notification removed - silently fail
        }
      }
    };

    saveMetrics();
  }, [user, prInfo, metricsSaved, optimizedWorkflow, aiInsights, repoName]);

  const copyToClipboard = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Get the old workflow content from existing workflows
  const oldWorkflow = existingWorkflows.find(
    (w: any) => w.type === "github-actions"
  );

  // If there's no valid data, show an error state
  if (!data || (!data.success && data.error_message)) {
    return (
      <div className="workflow-deployment">
        <div className="deployment-header">
          <h2 className="deployment-title">❌ Deployment Failed</h2>
          <div className="deployment-subtitle">
            Failed to optimize workflow for {repoName}
          </div>
          <div className="error-badge">
            {data?.error_message || "An unknown error occurred"}
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="workflow-deployment">
        <div className="deployment-header">
          <h2 className="deployment-title">
            🚀 Workflow Deployed Successfully!
          </h2>
          <div className="deployment-subtitle">
            CI/CD pipeline optimized and deployed to {repoName}
          </div>

          {/* Success/Error Status */}
          {prInfo?.success ? (
            <div className="success-badge">
              ✅ Pull Request Created Successfully
            </div>
          ) : (
            <div className="error-badge">❌ Deployment Failed</div>
          )}
        </div>

        {/* Pull Request Information */}
        {prInfo?.pr_number && (
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">📋</span>
            Pull Request Details
          </h3>

          <div className="pr-info-card">
            <div className="pr-details">
              <div className="detail-item">
                <span className="detail-label">🔄 PR Number:</span>
                <span className="detail-value">#{prInfo?.pr_number || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">🌿 Branch:</span>
                <span className="detail-value">{prInfo?.branch_name || 'N/A'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">📁 Workflow File:</span>
                <span className="detail-value">
                  {prInfo?.workflow_path || 'N/A'}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">🔗 Commit SHA:</span>
                <span className="detail-value">
                  {prInfo?.commit_sha ? prInfo.commit_sha.substring(0, 8) + '...' : 'N/A'}
                </span>
              </div>
            </div>

            <div className="pr-actions">
              {prInfo?.pr_url && (
              <a
                href={prInfo.pr_url}
                target="_blank"
                rel="noopener noreferrer"
                className="pr-link-button"
              >
                🔗 View Pull Request
              </a>
              )}
              {prInfo?.pr_url && (
              <button
                onClick={() => copyToClipboard(prInfo.pr_url, "pr_url")}
                className="copy-pr-button"
              >
                {copiedSection === "pr_url" ? "✅ Copied!" : "📋 Copy PR URL"}
              </button>
              )}
            </div>
          </div>
        </div>
        )}

        {/* AI Analysis Section */}
        {aiInsights?.ai_analysis && (
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">🤖</span>
            AI Analysis & Insights
          </h3>
          <div className="analysis-content">
            <div
              className="analysis-text"
              dangerouslySetInnerHTML={{
                __html: (aiInsights?.ai_analysis || '')
                  .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
                  .replace(/### ([^\n]+)/g, "<h4>$1</h4>")
                  .replace(/#### ([^\n]+)/g, "<h5>$1</h5>")
                  .replace(/\n\n/g, "<br><br>")
                  .replace(/\n/g, "<br>"),
              }}
            />
          </div>
        </div>
        )}

        {/* Workflow Comparison Section */}
        {optimizedWorkflow?.workflow_content && (
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">⚡</span>
            Workflow Comparison
            <div className="workflow-meta">
              <span className="workflow-type">
                {optimizedWorkflow?.optimization_type || 'Optimized'}
              </span>
              <span className="confidence-score">
                {optimizedWorkflow?.confidence_score || 0}% Confidence
              </span>
            </div>
          </h3>

          <div className="comparison-toggle">
            <button
              onClick={() => setShowComparison(!showComparison)}
              className="toggle-button"
            >
              {showComparison
                ? "Hide Comparison"
                : "Show Old vs New Comparison"}
            </button>
          </div>

          {showComparison && oldWorkflow ? (
            <div className="workflow-comparison">
              <div className="comparison-grid">
                <div className="comparison-panel old-workflow">
                  <div className="panel-header">
                    <h4>🔴 Old Workflow</h4>
                    <span className="workflow-name">{oldWorkflow.name}</span>
                  </div>
                  <pre className="workflow-code old">
                    <code>{oldWorkflow.content}</code>
                  </pre>
                </div>

                <div className="comparison-panel new-workflow">
                  <div className="panel-header">
                    <h4>🟢 Optimized Workflow</h4>
                    <span className="workflow-name">
                      {optimizedWorkflow?.workflow_name || 'Optimized Workflow'}
                    </span>
                  </div>
                  <pre className="workflow-code new">
                    <code>
                      {optimizedWorkflow?.workflow_content || ''}
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="workflow-file">
              <div className="file-header">
                <span className="file-name">
                  {optimizedWorkflow?.workflow_name || 'Optimized Workflow'}
                </span>
                <button
                  onClick={() =>
                    copyToClipboard(
                      optimizedWorkflow?.workflow_content || '',
                      "workflow"
                    )
                  }
                  className="copy-button"
                >
                  {copiedSection === "workflow" ? "✅ Copied!" : "📋 Copy"}
                </button>
              </div>
              <pre className="workflow-code">
                <code>
                  {optimizedWorkflow?.workflow_content || ''}
                </code>
              </pre>
            </div>
          )}

          {/* Improvements List */}
          {optimizedWorkflow?.improvements && optimizedWorkflow.improvements.length > 0 && (
          <div className="improvements-grid">
            <h4 className="improvements-title">✨ Applied Improvements</h4>
            <div className="improvements-list">
              {(optimizedWorkflow?.improvements || []).map(
                (improvement: string, index: number) => (
                  <div key={index} className="improvement-item">
                    <span className="improvement-icon">🔧</span>
                    {improvement}
                  </div>
                )
              )}
            </div>
          </div>
          )}
        </div>
        )}

        {/* Next Steps */}
        {recommendations?.implementation_steps && (
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">🎯</span>
            Next Steps
          </h3>

          <div className="next-steps-grid">
            {recommendations?.implementation_steps && recommendations.implementation_steps.length > 0 && (
            <div className="next-step-card">
              <h4 className="card-title">📝 Implementation Steps</h4>
              <ol className="steps-list">
                {(recommendations?.implementation_steps || []).map(
                  (step: string, index: number) => (
                    <li key={index} className="step-item">
                      {step}
                    </li>
                  )
                )}
              </ol>
            </div>
            )}

            {recommendations?.required_secrets && recommendations.required_secrets.length > 0 && (
            <div className="next-step-card">
              <h4 className="card-title">⚙️ Configure Secrets</h4>
              <ul className="secrets-list">
                {(recommendations?.required_secrets || []).map(
                  (secret: string, index: number) => (
                    <li key={index} className="secret-item">
                      <span className="secret-icon">🔐</span>
                      <code>{secret}</code>
                    </li>
                  )
                )}
              </ul>
            </div>
            )}

            {recommendations?.testing_checklist && recommendations.testing_checklist.length > 0 && (
            <div className="next-step-card">
              <h4 className="card-title">✅ Testing Checklist</h4>
              <ul className="checklist">
                {(recommendations?.testing_checklist || []).map(
                  (item: string, index: number) => (
                    <li key={index} className="checklist-item">
                      <span className="checkbox">☐</span>
                      {item}
                    </li>
                  )
                )}
              </ul>
            </div>
            )}
          </div>

          <div className="meta-info">
            {recommendations?.estimated_setup_time && (
            <div className="meta-item">
              <span className="meta-label">⏱️ Estimated Setup Time:</span>
              <span className="meta-value">
                {recommendations?.estimated_setup_time || 'N/A'}
              </span>
            </div>
            )}
            {optimizedWorkflow?.estimated_time_savings && (
            <div className="meta-item">
              <span className="meta-label">📊 Performance Gain:</span>
              <span className="meta-value">
                {optimizedWorkflow?.estimated_time_savings || 'N/A'}
              </span>
            </div>
            )}
            {aiInsights?.model_used && (
            <div className="meta-item">
              <span className="meta-label">🤖 Model Used:</span>
              <span className="meta-value">
                {aiInsights?.model_used || 'N/A'}
              </span>
            </div>
            )}
          </div>
        </div>
        )}

        {/* Error Message if any */}
        {data?.error_message && (
          <div className="deployment-section error-section">
            <h3 className="section-title">
              <span className="section-icon">⚠️</span>
              Error Details
            </h3>
            <div className="error-content">
              <p className="error-message">{data.error_message}</p>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default WorkflowDeploymentView;
