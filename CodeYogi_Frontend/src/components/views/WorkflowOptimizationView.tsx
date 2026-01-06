import React, { useState } from "react";
import axios from "axios";
import { WorkflowOptimization } from "../../types/chat";
import { useSelectedRepository } from "../../hooks/useSelectedRepository";

interface Props {
  data: WorkflowOptimization;
  repoName: string;
}

const WorkflowOptimizationView: React.FC<Props> = ({
  data: initialData,
  repoName,
}) => {
  const { selectedRepo } = useSelectedRepository();
  const [copiedSection, setCopiedSection] = useState<string | null>(null);
  const [showActionButtons, setShowActionButtons] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [customPrompt, setCustomPrompt] = useState("");
  const [showCustomPrompt, setShowCustomPrompt] = useState(false);
  const [optimizationData, setOptimizationData] =
    useState<WorkflowOptimization>(initialData);

  const copyToClipboard = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedSection(section);
      setTimeout(() => setCopiedSection(null), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  };

  // Accept: Call analyze-github-structure API with required payload
  const handleAccept = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Use repoName as the github_url (should be the repo's URL)
      const response = await fetch(
        "http://localhost:8000/optimize-workflow-deployment/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            repo_url: selectedRepo?.html_url,
            github_token: "",
          }),
        }
      );
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.message || "Failed to analyze GitHub structure."
        );
      }
      const result = await response.json();
      setOptimizationData(result);
      setShowActionButtons(false);
    } catch (err: any) {
      setError(err?.message || "Failed to analyze GitHub structure.");
    } finally {
      setIsLoading(false);
    }
  };

  // Reject: Show custom prompt input
  const handleReject = () => {
    setShowCustomPrompt(true);
    setShowActionButtons(false);
  };

  // Submit custom prompt
  const handleCustomPromptSubmit = async () => {
    if (!customPrompt.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await axios.post("http://localhost:8000/optimize-workflow/", {
        repo_url: selectedRepo?.html_url,
        custom_input: customPrompt,
      });
      setOptimizationData(res.data);
      setShowCustomPrompt(false);
      setShowActionButtons(true);
    } catch (err: any) {
      setError(
        err?.response?.data?.message ||
          "Failed to run workflow-with-deployment API."
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to determine if we have multiple workflows
  const workflowsArray = Array.isArray(optimizationData.optimized_workflow) 
    ? optimizationData.optimized_workflow 
    : [optimizationData.optimized_workflow];

  const hasMultipleWorkflows = workflowsArray.length > 1;

  return (
    <>
      <div className="workflow-optimization">
        <div className="optimization-header">
          <h2 className="optimization-title">⚡ Workflow Optimization</h2>
          <div className="optimization-subtitle">
            AI-powered CI/CD pipeline recommendations for {repoName}
          </div>
          <div className="confidence-badge">
            Confidence Score:{" "}
            {Array.isArray(optimizationData.optimized_workflow)
              ? optimizationData.optimized_workflow[0]?.confidence_score || "N/A"
              : optimizationData.optimized_workflow.confidence_score}%
          </div>
        </div>

        {/* AI Analysis Section */}
        <div className="optimization-section">
          <h3 className="section-title">
            <span className="section-icon">🤖</span>
            AI Analysis & Insights
          </h3>
          <div className="analysis-content">
            <div
              className="analysis-text"
              dangerouslySetInnerHTML={{
                __html: optimizationData.ai_insights.ai_analysis
                  .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
                  .replace(/### ([^\n]+)/g, "<h4>$1</h4>")
                  .replace(/\n\n/g, "<br><br>")
                  .replace(/\n/g, "<br>"),
              }}
            />
          </div>
        </div>

        {/* Optimized Workflow Section - Fixed Logic */}
        <div className="optimization-section">
          <h3 className="section-title">
            <span className="section-icon">📋</span>
            Optimized Workflow File{hasMultipleWorkflows ? "s" : ""}
            {/* Show meta for first workflow if present */}
            <div className="workflow-meta">
              <span className="workflow-type">
                {workflowsArray[0]?.optimization_type || "Standard"}
              </span>
              <span className="time-savings">
                {workflowsArray[0]?.estimated_time_savings || "N/A"}
              </span>
            </div>
          </h3>

          {/* Display workflows - Fixed conditional logic */}
          {hasMultipleWorkflows ? (
            <div className="workflow-comparison">
              <div className="comparison-grid">
                {workflowsArray.map((wf, idx) => (
                  <div
                    className={`comparison-panel ${
                      idx === 0 ? "old-workflow" : "new-workflow"
                    }`}
                    key={idx}
                  >
                    <div className="panel-header">
                      <div>
                        <h4>
                          {idx === 0
                            ? "Original Workflow"
                            : "Optimized Workflow"}
                        </h4>
                        <span className="workflow-name">{wf.workflow_name}</span>
                      </div>
                      <button
                        onClick={() =>
                          copyToClipboard(wf.workflow_content, `workflow${idx}`)
                        }
                        className="copy-button"
                      >
                        {copiedSection === `workflow${idx}`
                          ? "✅ Copied!"
                          : "📋 Copy"}
                      </button>
                    </div>
                    <pre
                      className={`workflow-code ${idx === 0 ? "old" : "new"}`}
                    >
                      <code>{wf.workflow_content}</code>
                    </pre>
                    {/* Improvements List for each workflow */}
                    {wf.improvements && wf.improvements.length > 0 && (
                      <div className="improvements-grid">
                        <h4 className="improvements-title">
                          ✨ Key Improvements
                        </h4>
                        <div className="improvements-list">
                          {wf.improvements.map(
                            (improvement: string, i: number) => (
                              <div key={i} className="improvement-item">
                                <span className="improvement-icon">🔧</span>
                                {improvement}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // Single workflow display
            <div className="workflow-file">
              <div className="file-header">
                <span className="file-name">
                  {workflowsArray[0]?.workflow_name || "workflow.yml"}
                </span>
                <button
                  onClick={() =>
                    copyToClipboard(
                      workflowsArray[0]?.workflow_content || "",
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
                  {workflowsArray[0]?.workflow_content || "No content available"}
                </code>
              </pre>
              {/* Improvements List */}
              {workflowsArray[0]?.improvements && workflowsArray[0].improvements.length > 0 && (
                <div className="improvements-grid">
                  <h4 className="improvements-title">✨ Key Improvements</h4>
                  <div className="improvements-list">
                    {workflowsArray[0].improvements.map(
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
        </div>

        {/* Implementation Recommendations */}
        <div className="optimization-section">
          <h3 className="section-title">
            <span className="section-icon">🎯</span>
            Implementation Guide
            <div className="difficulty-badge">
              {optimizationData.recommendations?.difficulty_level || "Medium"}
            </div>
          </h3>

          <div className="recommendations-grid">
            <div className="recommendation-card">
              <h4 className="card-title">📝 Implementation Steps</h4>
              <ol className="steps-list">
                {(optimizationData.recommendations?.implementation_steps || []).map(
                  (step, index) => (
                    <li key={index} className="step-item">
                      {step}
                    </li>
                  )
                )}
              </ol>
            </div>

            <div className="recommendation-card">
              <h4 className="card-title">✅ Testing Checklist</h4>
              <ul className="checklist">
                {(optimizationData.recommendations?.testing_checklist || []).map(
                  (item, index) => (
                    <li key={index} className="checklist-item">
                      <span className="checkbox">☐</span>
                      {item}
                    </li>
                  )
                )}
              </ul>
            </div>

            <div className="recommendation-card">
              <h4 className="card-title">📋 Prerequisites</h4>
              <ul className="prerequisites-list">
                {(optimizationData.recommendations?.prerequisites || []).map(
                  (prereq, index) => (
                    <li key={index} className="prereq-item">
                      <span className="prereq-icon">🔸</span>
                      {prereq}
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
                {optimizationData.recommendations?.estimated_setup_time || "N/A"}
              </span>
            </div>
            <div className="meta-item">
              <span className="meta-label">🤖 Model Used:</span>
              <span className="meta-value">
                {optimizationData.ai_insights?.model_used || "N/A"}
              </span>
            </div>
          </div>
        </div>

        {/* Accept/Reject Buttons or API Response */}
        {showActionButtons && (
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "1.5rem",
              marginTop: "2rem",
            }}
          >
            <button
              className="accept-btn"
              onClick={handleAccept}
              disabled={isLoading}
            >
              {isLoading ? "Processing..." : "✅ Accept"}
            </button>
            <button
              className="reject-btn"
              onClick={handleReject}
              disabled={isLoading}
            >
              {isLoading ? "Please wait..." : "❌ Reject"}
            </button>
          </div>
        )}

        {showCustomPrompt && (
          <div style={{ marginTop: "2rem", textAlign: "center" }}>
            <label
              htmlFor="customPrompt"
              style={{ color: "#e2e8f0", fontWeight: 600 }}
            >
              Please provide your custom requirements:
            </label>
            <textarea
              id="customPrompt"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              rows={4}
              style={{
                width: "100%",
                margin: "1rem 0",
                borderRadius: 8,
                padding: 8,
                color: "#e2e8f0",
                background: "#1e293b",
                border: "1px solid #334155",
              }}
              placeholder="Describe your requirements..."
            />
            <button
              className="accept-btn"
              onClick={handleCustomPromptSubmit}
              disabled={isLoading || !customPrompt.trim()}
            >
              {isLoading ? "Processing..." : "Submit"}
            </button>
          </div>
        )}

        {error && (
          <div
            style={{
              color: "#ef4444",
              marginTop: "1.5rem",
              textAlign: "center",
            }}
          >
            {error}
          </div>
        )}
      </div>
      <style>{`
        .accept-btn {
          background: linear-gradient(135deg, #22c55e, #15803d);
          color: white;
          padding: 0.35rem 1.1rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 0.95rem;
          cursor: pointer;
          margin-right: 0.5rem;
          transition: all 0.2s;
          box-shadow: 0 2px 8px rgba(34, 197, 94, 0.08);
        }
        .accept-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .accept-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #16a34a, #166534);
        }
        .reject-btn {
          background: linear-gradient(135deg, #ef4444, #b91c1c);
          color: white;
          padding: 0.35rem 1.1rem;
          border: none;
          border-radius: 8px;
          font-weight: 600;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.2s;
          box-shadow: 0 2px 8px rgba(239, 68, 68, 0.08);
        }
        .reject-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        .reject-btn:hover:not(:disabled) {
          background: linear-gradient(135deg, #dc2626, #991b1b);
        }
        .workflow-optimization {
          background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(0, 0, 0, 0.95));
          border-radius: 20px;
          padding: 2rem;
          border: 2px solid rgba(34, 197, 94, 0.3);
          margin: 1rem 0;
          box-shadow: 0 8px 32px rgba(34, 197, 94, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .optimization-header {
          text-align: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid rgba(34, 197, 94, 0.2);
        }
        
        .optimization-title {
          background: linear-gradient(135deg, #22c55e, #15803d);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-size: 2.2rem;
          font-weight: bold;
          margin-bottom: 0.5rem;
        }
        
        .optimization-subtitle {
          color: #94a3b8;
          font-size: 1.1rem;
          margin-bottom: 1rem;
        }
        
        .confidence-badge {
          display: inline-block;
          background: linear-gradient(135deg, #22c55e30, #15803d50);
          color: #22c55e;
          padding: 0.4rem 1rem;
          border-radius: 20px;
          font-weight: 600;
          border: 1px solid rgba(34, 197, 94, 0.3);
          font-size: 0.9rem;
        }
        
        .optimization-section {
          margin-bottom: 2.5rem;
          background: rgba(17, 24, 39, 0.6);
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .section-title {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          font-size: 1.5rem;
          color: #22c55e;
          margin-bottom: 1.5rem;
          font-weight: bold;
          border-bottom: 1px solid rgba(34, 197, 94, 0.3);
          padding-bottom: 0.75rem;
        }
        
        .section-icon {
          font-size: 1.25rem;
          filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.5));
        }
        
        .workflow-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.8rem;
        }
        
        .workflow-type {
          background: linear-gradient(135deg, #22c55e, #15803d);
          color: white;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: capitalize;
        }
        
        .confidence-score {
          background: linear-gradient(135deg, #22c55e, #15803d);
          color: white;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
          font-weight: 600;
          font-size: 0.85rem;
          box-shadow: 0 2px 8px rgba(34, 197, 94, 0.3);
        }
        
        .time-savings {
          background: linear-gradient(135deg, #fbbf2430, #92400e40);
          color: #fbbf24;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
          font-weight: 600;
          border: 1px solid rgba(251, 191, 36, 0.3);
        }
        
        .difficulty-badge {
          background: linear-gradient(135deg, #22c55e30, #15803d40);
          color: #22c55e;
          padding: 0.3rem 0.8rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 600;
          text-transform: capitalize;
          border: 1px solid rgba(34, 197, 94, 0.3);
        }
        
        .analysis-content {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          padding: 1.5rem;
          border-left: 4px solid #22c55e;
        }
        
        .analysis-text {
          color: #e2e8f0;
          line-height: 1.7;
        }
        
        .analysis-text h4 {
          color: #22c55e;
          font-size: 1.2rem;
          font-weight: 600;
          margin: 1rem 0 0.5rem 0;
        }
        
        .analysis-text strong {
          color: #a7f3d0;
          font-weight: 600;
        }
        
        .workflow-file {
          background: rgba(0, 0, 0, 0.4);
          border-radius: 12px;
          overflow: hidden;
          border: 1px solid rgba(34, 197, 94, 0.2);
          margin-bottom: 1.5rem;
        }
        
        .file-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: rgba(34, 197, 94, 0.1);
          padding: 0.75rem 1rem;
          border-bottom: 1px solid rgba(34, 197, 94, 0.2);
        }
        
        .file-name {
          color: #a7f3d0;
          font-size: 0.95rem;
          font-weight: 600;
        }
        
        .copy-button {
          background: linear-gradient(135deg, #22c55e40, #15803d50);
          color: #a7f3d0;
          border: 1px solid rgba(34, 197, 94, 0.3);
          padding: 0.3rem 0.8rem;
          border-radius: 4px;
          font-size: 0.8rem;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        
        .copy-button:hover {
          background: linear-gradient(135deg, #22c55e60, #15803d70);
        }
        
        .workflow-code {
          margin: 0;
          padding: 1rem;
          background: transparent;
          color: #e2e8f0;
          font-family: monospace;
          font-size: 0.9rem;
          overflow-x: auto;
          max-height: 400px;
          overflow-y: auto;
        }
        
        .improvements-grid {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          padding: 1.25rem;
        }
        
        .improvements-title {
          color: #22c55e;
          font-size: 1.2rem;
          margin-bottom: 1rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .improvements-list {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }
        
        .improvement-item {
          background: rgba(34, 197, 94, 0.05);
          padding: 0.8rem 1rem;
          border-radius: 8px;
          border-left: 3px solid #22c55e;
          color: #e2e8f0;
          display: flex;
          align-items: flex-start;
          gap: 0.5rem;
          line-height: 1.5;
        }
        
        .improvement-icon {
          flex-shrink: 0;
        }
        
        .recommendations-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
          margin-bottom: 1.5rem;
        }
        
        .recommendation-card {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          padding: 1.25rem;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .card-title {
          color: #22c55e;
          font-size: 1.1rem;
          margin-bottom: 1rem;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .steps-list {
          color: #e2e8f0;
          padding-left: 1rem;
        }
        
        .step-item {
          margin-bottom: 0.75rem;
          line-height: 1.5;
        }
        
        .checklist {
          list-style: none;
          padding: 0;
        }
        
        .checklist-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
          color: #e2e8f0;
          line-height: 1.5;
        }
        
        .checkbox {
          color: #10b981;
          font-size: 1.1rem;
        }
        
        .prerequisites-list {
          list-style: none;
          padding: 0;
        }
        
        .prereq-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
          color: #e2e8f0;
          line-height: 1.5;
        }
        
        .prereq-icon {
          color: #fbbf24;
        }
        
        .meta-info {
          display: flex;
          flex-wrap: wrap;
          gap: 2rem;
          margin-top: 1.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid rgba(59, 130, 246, 0.2);
        }
        
        .meta-item {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        
        .meta-label {
          color: #94a3b8;
          font-size: 0.9rem;
        }
        
        .meta-value {
          color: #60a5fa;
          font-weight: 600;
        }

        /* Workflow Comparison Styles */
        .workflow-comparison {
          margin: 1.5rem 0;
        }
        
        .comparison-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1.5rem;
          margin-bottom: 2rem;
        }
        
        .comparison-panel {
          background: rgba(0, 0, 0, 0.6);
          border-radius: 12px;
          overflow: hidden;
          border: 1px solid rgba(34, 197, 94, 0.2);
        }
        
        .old-workflow {
          border-color: rgba(239, 68, 68, 0.3);
        }
        
        .new-workflow {
          border-color: rgba(34, 197, 94, 0.3);
        }
        
        .panel-header {
          padding: 1rem;
          background: rgba(16, 185, 129, 0.1);
          border-bottom: 1px solid rgba(34, 197, 94, 0.2);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .old-workflow .panel-header {
          background: rgba(239, 68, 68, 0.1);
          border-bottom-color: rgba(239, 68, 68, 0.2);
        }
        
        .panel-header h4 {
          color: #10b981;
          margin: 0;
          font-size: 1.1rem;
          font-weight: 700;
        }
        
        .old-workflow .panel-header h4 {
          color: #ef4444;
        }
        
        .workflow-name {
          color: #94a3b8;
          font-size: 0.9rem;
          font-family: 'JetBrains Mono', monospace;
        }
        
        .workflow-code.old {
          background: rgba(239, 68, 68, 0.05);
          border-left: 4px solid #ef4444;
        }
        
        .workflow-code.new {
          background: rgba(34, 197, 94, 0.05);
          border-left: 4px solid #10b981;
        }
        
        /* Responsive design for comparison */
        @media (max-width: 768px) {
          .comparison-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
          }
          
          .workflow-code {
            font-size: 0.75rem;
            padding: 1rem;
          }
        }
      `}</style>
    </>
  );
};

export default WorkflowOptimizationView;