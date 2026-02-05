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

  // Save metrics to Firebase when component mounts with new data
  useEffect(() => {
    const saveMetrics = async () => {
      if (user && data.pr_info && data.pr_info.success && !metricsSaved) {
        try {
          console.log("Saving workflow metrics to Firebase...");
          await saveWorkflowMetrics(user.uid, data.pr_info);
          setMetricsSaved(true);
          console.log("Workflow metrics saved successfully");

          // Show success notification when PR is created
          addNotification({
            type: "success",
            title: "Pull Request Created!",
            message: `Successfully created PR for ${repoName}. Optimization metrics saved.`,
            duration: 5000,
          });
        } catch (error) {
          console.error("Failed to save workflow metrics:", error);

          // Show error notification if saving fails
          addNotification({
            type: "error",
            title: "Failed to Save Metrics",
            message: "Could not save optimization metrics to database.",
            duration: 5000,
          });
        }
      }
    };

    saveMetrics();
  }, [user, data.pr_info, metricsSaved]);

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
  const oldWorkflow =
    data.optimization_analysis.analysis.existing_workflows.find(
      (w) => w.type === "github-actions"
    );

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
          {data.pr_info.success ? (
            <div className="success-badge">
              ✅ Pull Request Created Successfully
            </div>
          ) : (
            <div className="error-badge">❌ Deployment Failed</div>
          )}
        </div>

        {/* Pull Request Information */}
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">📋</span>
            Pull Request Details
          </h3>

          <div className="pr-info-card">
            <div className="pr-details">
              <div className="detail-item">
                <span className="detail-label">🔄 PR Number:</span>
                <span className="detail-value">#{data.pr_info.pr_number}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">🌿 Branch:</span>
                <span className="detail-value">{data.pr_info.branch_name}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">📁 Workflow File:</span>
                <span className="detail-value">
                  {data.pr_info.workflow_path}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">🔗 Commit SHA:</span>
                <span className="detail-value">
                  {data.pr_info.commit_sha.substring(0, 8)}...
                </span>
              </div>
            </div>

            <div className="pr-actions">
              <a
                href={data.pr_info.pr_url}
                target="_blank"
                rel="noopener noreferrer"
                className="pr-link-button"
              >
                🔗 View Pull Request
              </a>
              <button
                onClick={() => copyToClipboard(data.pr_info.pr_url, "pr_url")}
                className="copy-pr-button"
              >
                {copiedSection === "pr_url" ? "✅ Copied!" : "📋 Copy PR URL"}
              </button>
            </div>
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">🤖</span>
            AI Analysis & Insights
          </h3>
          <div className="analysis-content">
            <div
              className="analysis-text"
              dangerouslySetInnerHTML={{
                __html: data.optimization_analysis.ai_insights.ai_analysis
                  .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
                  .replace(/### ([^\n]+)/g, "<h4>$1</h4>")
                  .replace(/#### ([^\n]+)/g, "<h5>$1</h5>")
                  .replace(/\n\n/g, "<br><br>")
                  .replace(/\n/g, "<br>"),
              }}
            />
          </div>
        </div>

        {/* Workflow Comparison Section */}
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">⚡</span>
            Workflow Comparison
            <div className="workflow-meta">
              <span className="workflow-type">
                {
                  data.optimization_analysis.optimized_workflow
                    .optimization_type
                }
              </span>
              <span className="confidence-score">
                {data.optimization_analysis.optimized_workflow.confidence_score}
                % Confidence
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
                      {
                        data.optimization_analysis.optimized_workflow
                          .workflow_name
                      }
                    </span>
                  </div>
                  <pre className="workflow-code new">
                    <code>
                      {
                        data.optimization_analysis.optimized_workflow
                          .workflow_content
                      }
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          ) : (
            <div className="workflow-file">
              <div className="file-header">
                <span className="file-name">
                  {data.optimization_analysis.optimized_workflow.workflow_name}
                </span>
                <button
                  onClick={() =>
                    copyToClipboard(
                      data.optimization_analysis.optimized_workflow
                        .workflow_content,
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
                  {
                    data.optimization_analysis.optimized_workflow
                      .workflow_content
                  }
                </code>
              </pre>
            </div>
          )}

          {/* Improvements List */}
          <div className="improvements-grid">
            <h4 className="improvements-title">✨ Applied Improvements</h4>
            <div className="improvements-list">
              {data.optimization_analysis.optimized_workflow.improvements.map(
                (improvement: string, index: number) => (
                  <div key={index} className="improvement-item">
                    <span className="improvement-icon">🔧</span>
                    {improvement}
                  </div>
                )
              )}
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="deployment-section">
          <h3 className="section-title">
            <span className="section-icon">🎯</span>
            Next Steps
          </h3>

          <div className="next-steps-grid">
            <div className="next-step-card">
              <h4 className="card-title">📝 Implementation Steps</h4>
              <ol className="steps-list">
                {data.optimization_analysis.recommendations.implementation_steps.map(
                  (step: string, index: number) => (
                    <li key={index} className="step-item">
                      {step}
                    </li>
                  )
                )}
              </ol>
            </div>

            <div className="next-step-card">
              <h4 className="card-title">⚙️ Configure Secrets</h4>
              <ul className="secrets-list">
                {data.optimization_analysis.recommendations.required_secrets.map(
                  (secret: string, index: number) => (
                    <li key={index} className="secret-item">
                      <span className="secret-icon">🔐</span>
                      <code>{secret}</code>
                    </li>
                  )
                )}
              </ul>
            </div>

            <div className="next-step-card">
              <h4 className="card-title">✅ Testing Checklist</h4>
              <ul className="checklist">
                {data.optimization_analysis.recommendations.testing_checklist.map(
                  (item: string, index: number) => (
                    <li key={index} className="checklist-item">
                      <span className="checkbox">☐</span>
                      {item}
                    </li>
                  )
                )}
              </ul>
            </div>
          </div>

          <div className="meta-info">
            <div className="meta-item">
              <span className="meta-label">⏱️ Estimated Setup Time:</span>
              <span className="meta-value">
                {
                  data.optimization_analysis.recommendations
                    .estimated_setup_time
                }
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">📊 Performance Gain:</span>
              <span className="meta-value">
                {
                  data.optimization_analysis.optimized_workflow
                    .estimated_time_savings
                }
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">🤖 Model Used:</span>
              <span className="meta-value">
                {data.optimization_analysis.ai_insights.model_used}
              </span>
            </div>
          </div>
        </div>

        {/* Error Message if any */}
        {data.error_message && (
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
