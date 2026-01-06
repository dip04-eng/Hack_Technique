import React from "react";
import { RepoAnalysis } from "../../types/chat";
import MermaidDiagram from "./MermaidDiagram";

const RepoAnalysisView: React.FC<{ data: RepoAnalysis; repoName: string }> = ({
  data,
  repoName,
}) => {
  return (
    <>
      <div className="repo-analysis">
        <h2 className="gradient-text">🚀 Repository Analysis: {repoName}</h2>

        <div className="analysis-section">
          <h3>📝 Description</h3>
          <p className="description">{data.description}</p>
        </div>

        <div className="analysis-section">
          <h3>💻 Tech Stack</h3>
          <div className="tech-stack">
            {Object.keys(data.tech_stack).map((key) => (
              <span key={key} className="tech-badge">
                {key}
              </span>
            ))}
          </div>
        </div>

        <div className="analysis-section">
          <h3>🏗️ Architecture Summary</h3>
          <div className="architecture">{data.architecture_summary}</div>
        </div>

        <div className="analysis-section">
          <h3>✨ Key Features</h3>
          <ul className="features-list">
            {data.key_features.map((feature, index) => (
              <li key={index} className="feature-item">
                ✓ {feature}
              </li>
            ))}
          </ul>
        </div>

        <div className="analysis-section">
          <h3>🎯 Project Type</h3>
          <div className="project-type">
            <span className="type-badge">{data.project_type}</span>
          </div>
        </div>

        <div className="analysis-section">
          <h3>📊 System Flow Diagram</h3>
          {/* Use the new animated Mermaid component here */}
          <MermaidDiagram chart={data.flowchart.mermaid_diagram} />
        </div>

        <div className="analysis-section">
          <h3>🔍 Complexity Analysis</h3>
          <div className="complexity-score">
            <div
              className="score-bar"
              style={
                {
                  "--score": `${data.flowchart.complexity_score}%`,
                } as React.CSSProperties
              }
            >
              <span className="score-label">
                Complexity Score: {data.flowchart.complexity_score}%
              </span>
            </div>
          </div>
        </div>
      </div>
      {/* NOTE: It's best practice to move this CSS to a dedicated .css file 
        and import it, but it's included here for simplicity.
      */}
      <style>{`
        .repo-analysis { background: linear-gradient(135deg, rgba(17, 24, 39, 0.8), rgba(0, 0, 0, 0.9)); border-radius: 16px; padding: 2rem; border: 1px solid rgba(34, 197, 94, 0.2); margin-top: 1rem; }
        .gradient-text { background: linear-gradient(135deg, #22c55e, #15803d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem; font-weight: bold; margin-bottom: 1.5rem; }
        .analysis-section { margin-bottom: 2rem; padding: 1rem; background: rgba(17, 24, 39, 0.5); border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.1); }
        .analysis-section:last-child { margin-bottom: 0; }
        .analysis-section h3 { color: #22c55e; font-size: 1.2rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem; }
        .tech-stack { display: flex; flex-wrap: wrap; gap: 0.5rem; }
        .tech-badge { background: linear-gradient(135deg, #22c55e20, #15803d40); color: #22c55e; padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.9rem; border: 1px solid rgba(34, 197, 94, 0.3); }
        .features-list { list-style: none; padding: 0; }
        .feature-item { margin-bottom: 0.5rem; color: #e2e8f0; display: flex; align-items: center; gap: 0.5rem; }
        .type-badge { background: linear-gradient(135deg, #22c55e, #15803d); color: white; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold; }
        .flow-diagram { background: rgba(0, 0, 0, 0.2); border-radius: 8px; padding: 1rem; margin-top: 1rem; display: flex; justify-content: center; align-items: center; }
        .flow-diagram svg { max-width: 100%; height: auto; }
        .complexity-score { margin-top: 1rem; }
        .score-bar { height: 2rem; background: rgba(34, 197, 94, 0.1); border-radius: 1rem; overflow: hidden; position: relative; }
        .score-bar::before { content: ''; position: absolute; top: 0; left: 0; height: 100%; width: var(--score); background: linear-gradient(90deg, #22c55e, #15803d); border-radius: 1rem; transition: width 1s ease-in-out; }
        .score-label { position: absolute; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 0 0 4px rgba(0, 0, 0, 0.5); }
      `}</style>
    </>
  );
};

export default RepoAnalysisView;
