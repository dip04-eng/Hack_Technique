import React from "react";
import { GithubStructureAnalysis } from "../../types/chat";

// GitHub Structure Analysis View Component
// GitHub Structure Analysis View Component
const GithubStructureAnalysisView: React.FC<{
  data: GithubStructureAnalysis;
  repoName: string;
}> = ({ data, repoName }) => {
  // Handle null data
  if (!data) {
    return (
      <div className="error-container">
        <h2 className="error-title">Error Loading Repository Structure</h2>
        <p className="error-message">
          The analysis data could not be loaded. Please try again.
        </p>
      </div>
    );
  }

  try {
    return (
      <>
        <div className="github-structure">
          <div className="structure-header">
            <h2 className="structure-title">📊 GitHub Structure Analysis</h2>
            <div className="structure-subtitle">
              Repository structure analysis for {repoName || "Repository"}
            </div>
            {data?.structure_metrics ? (
              <div className="score-badge">
                Organization Score:{" "}
                {data.structure_metrics.organization_score || "N/A"}/100
              </div>
            ) : (
              <div className="no-score-badge">
                Organization Score not available
              </div>
            )}
          </div>

          {/* Metrics Overview Section */}
          <div className="structure-section">
            <h3 className="section-title">
              <span className="section-icon">📈</span>
              Structure Metrics
            </h3>

            <div className="metrics-grid">
              <div className="metric-card">
                <div className="metric-label">Files</div>
                <div className="metric-value">
                  {data?.structure_metrics?.total_files || "N/A"}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Directories</div>
                <div className="metric-value">
                  {data?.structure_metrics?.total_directories || "N/A"}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Max Depth</div>
                <div className="metric-value">
                  {data?.structure_metrics?.max_depth ?? "N/A"}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Files per Directory</div>
                <div className="metric-value">
                  {data?.structure_metrics?.files_per_directory
                    ? data.structure_metrics.files_per_directory.toFixed(2)
                    : "N/A"}
                </div>
              </div>
            </div>
          </div>

          {/* File Distribution Section */}
          <div className="structure-section">
            <h3 className="section-title">
              <span className="section-icon">📁</span>
              File Distribution
            </h3>

            <div className="distribution-container">
              <div className="distribution-chart">
                <h4>File Types</h4>
                <div className="file-types-grid">
                  {data?.file_distribution?.type_distribution ? (
                    Object.entries(
                      data.file_distribution.type_distribution
                    ).map(([type, count]) => (
                      <div key={type} className="file-type-item">
                        <div className="file-type-icon">
                          {type === "javascript" && "📜"}
                          {type === "typescript" && "📘"}
                          {type === "html" && "🌐"}
                          {type === "css" && "🎨"}
                          {type === "configuration" && "⚙️"}
                          {type === "documentation" && "📚"}
                          {type === "other" && "📄"}
                        </div>
                        <div className="file-type-details">
                          <div className="file-type-name">{type}</div>
                          <div className="file-type-count">{count} files</div>
                        </div>
                        <div
                          className="file-type-bar"
                          style={{
                            width: `${Math.min(
                              100,
                              (count / data.structure_metrics.total_files) * 100
                            )}%`,
                            backgroundColor:
                              type === "javascript"
                                ? "#f7df1e"
                                : type === "typescript"
                                ? "#3178c6"
                                : type === "html"
                                ? "#e34c26"
                                : type === "css"
                                ? "#563d7c"
                                : type === "configuration"
                                ? "#89e051"
                                : type === "documentation"
                                ? "#fc4f4f"
                                : "#9ca3af",
                          }}
                        />
                      </div>
                    ))
                  ) : (
                    <div>No file type distribution available</div>
                  )}
                </div>
              </div>
            </div>

            {/* Mixed Types & Scattered Types */}
            <div className="distribution-details">
              {data?.file_distribution?.directories_with_mixed_types?.length >
                0 && (
                <div className="mixed-types">
                  <h4>Directories with Mixed File Types</h4>
                  <div className="mixed-types-list">
                    {data?.file_distribution?.directories_with_mixed_types?.map(
                      (dir, index) => (
                        <div key={index} className="mixed-type-item">
                          <div className="directory-name">{dir.directory}</div>
                          <div className="directory-types">
                            {dir.types.map((type) => (
                              <span key={type} className="directory-type-tag">
                                {type}
                              </span>
                            ))}
                          </div>
                          <div className="directory-count">
                            {dir.file_count} files
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}

              {data?.file_distribution?.scattered_types?.length > 0 && (
                <div className="scattered-types">
                  <h4>Scattered File Types</h4>
                  <div className="scattered-types-list">
                    {data?.file_distribution?.scattered_types?.map(
                      (scattered, index) => (
                        <div key={index} className="scattered-type-item">
                          <div className="scattered-type-name">
                            {scattered.type}
                          </div>
                          <div className="scattered-type-locations">
                            {scattered.locations.map((location) => (
                              <span key={location} className="location-tag">
                                {location}
                              </span>
                            ))}
                          </div>
                          <div className="location-count">
                            {scattered.location_count} locations
                          </div>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Suggestions Section */}
          <div className="structure-section">
            <h3 className="section-title">
              <span className="section-icon">💡</span>
              Improvement Suggestions
            </h3>

            <div className="suggestions-list">
              {data?.structure_suggestions?.map((suggestion, index) => (
                <div
                  key={index}
                  className={`suggestion-item ${
                    suggestion?.priority || "medium"
                  }`}
                >
                  <div className="suggestion-header">
                    <div className="suggestion-type">
                      {suggestion?.type === "separate_types" &&
                        "📂 Separate Files"}
                      {suggestion?.type === "consolidate_type" &&
                        "🔄 Consolidate Files"}
                      {suggestion?.type === "move_files" && "📦 Move Files"}
                      {suggestion?.type === "rename_folders" &&
                        "✏️ Rename Folders"}
                      {!suggestion?.type && "🔧 Suggestion"}
                    </div>
                    <div
                      className={`priority-badge ${
                        suggestion?.priority || "medium"
                      }`}
                    >
                      {suggestion?.priority
                        ? suggestion.priority.charAt(0).toUpperCase() +
                          suggestion.priority.slice(1)
                        : "Medium"}{" "}
                      Priority
                    </div>
                  </div>
                  <div className="suggestion-content">
                    <div className="suggestion-folder">
                      {suggestion?.folder || "N/A"}
                    </div>
                    <div className="suggestion-reason">
                      {suggestion?.reason || "No reason provided"}
                    </div>
                    {suggestion?.suggested_subfolders && (
                      <div className="suggested-folders">
                        <div className="suggested-label">
                          Suggested Folders:
                        </div>
                        <div className="folders-list">
                          {suggestion?.suggested_subfolders?.map(
                            (folder, idx) => (
                              <span key={idx} className="folder-tag">
                                {folder}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Structure Section */}
          <div className="structure-section">
            <h3 className="section-title">
              <span className="section-icon">🏆</span>
              Recommended Structure
            </h3>

            <div className="recommended-folders">
              {data?.recommended_folders ? (
                Object.entries(data.recommended_folders).map(
                  ([folder, description]) => (
                    <div key={folder} className="recommended-folder">
                      <div className="folder-name">{folder}</div>
                      <div className="folder-description">{description}</div>
                    </div>
                  )
                )
              ) : (
                <div className="no-folders">
                  No recommended folders available
                </div>
              )}
            </div>
          </div>
        </div>

        <style>{`
        .github-structure {
          background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(0, 0, 0, 0.95));
          border-radius: 20px;
          padding: 2rem;
          border: 2px solid rgba(34, 197, 94, 0.3);
          margin: 1rem 0;
          box-shadow: 0 8px 32px rgba(34, 197, 94, 0.1);
          backdrop-filter: blur(10px);
        }
        
        .structure-header {
          text-align: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid rgba(34, 197, 94, 0.2);
        }
        
        .structure-title {
          background: linear-gradient(135deg, #22c55e, #15803d);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          font-size: 2.2rem;
          font-weight: bold;
          margin-bottom: 0.5rem;
        }
        
        .structure-subtitle {
          color: #94a3b8;
          font-size: 1.1rem;
          margin-bottom: 1rem;
        }
        
        .score-badge {
          display: inline-block;
          background: linear-gradient(135deg, #22c55e30, #15803d50);
          color: #22c55e;
          padding: 0.4rem 1rem;
          border-radius: 20px;
          font-weight: 600;
          border: 1px solid rgba(34, 197, 94, 0.3);
          font-size: 0.9rem;
        }
        
        .no-score-badge {
          display: inline-block;
          background: linear-gradient(135deg, rgba(100, 116, 139, 0.2), rgba(100, 116, 139, 0.3));
          color: #94a3b8;
          padding: 0.4rem 1rem;
          border-radius: 20px;
          font-weight: 600;
          border: 1px solid rgba(100, 116, 139, 0.3);
          font-size: 0.9rem;
        }
        
        .structure-section {
          margin-bottom: 2.5rem;
          background: rgba(17, 24, 39, 0.6);
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .section-title {
          display: flex;
          align-items: center;
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
        }
        
        /* Metrics Grid */
        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1.25rem;
        }
        
        .metric-card {
          background: rgba(0, 0, 0, 0.3);
          padding: 1.25rem;
          border-radius: 12px;
          border: 1px solid rgba(34, 197, 94, 0.15);
          text-align: center;
          transition: all 0.3s ease;
        }
        
        .metric-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 5px 15px rgba(34, 197, 94, 0.15);
        }
        
        .metric-label {
          color: #94a3b8;
          font-size: 0.9rem;
          margin-bottom: 0.5rem;
        }
        
        .metric-value {
          color: #22c55e;
          font-size: 2rem;
          font-weight: bold;
        }
        
        /* File Distribution */
        .distribution-container {
          margin-bottom: 2rem;
        }
        
        .file-types-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 0.75rem;
        }
        
        .file-type-item {
          display: flex;
          align-items: center;
          padding: 0.75rem;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 8px;
          position: relative;
          overflow: hidden;
          border: 1px solid rgba(34, 197, 94, 0.1);
        }
        
        .file-type-icon {
          margin-right: 1rem;
          font-size: 1.5rem;
        }
        
        .file-type-details {
          z-index: 2;
        }
        
        .file-type-name {
          color: #e2e8f0;
          font-weight: 600;
          text-transform: capitalize;
        }
        
        .file-type-count {
          color: #94a3b8;
          font-size: 0.85rem;
        }
        
        .file-type-bar {
          position: absolute;
          height: 100%;
          left: 0;
          top: 0;
          opacity: 0.15;
          z-index: 1;
        }
        
        /* Mixed & Scattered Types */
        .distribution-details {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem;
        }
        
        .mixed-types, .scattered-types {
          background: rgba(0, 0, 0, 0.3);
          padding: 1.25rem;
          border-radius: 12px;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .mixed-types h4, .scattered-types h4 {
          color: #22c55e;
          margin-bottom: 1rem;
          font-size: 1.1rem;
          font-weight: 600;
          border-bottom: 1px solid rgba(34, 197, 94, 0.15);
          padding-bottom: 0.5rem;
        }
        
        .mixed-types-list, .scattered-types-list {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1rem;
        }
        
        .mixed-type-item, .scattered-type-item {
          padding: 0.75rem;
          background: rgba(17, 24, 39, 0.6);
          border-radius: 8px;
          border: 1px solid rgba(34, 197, 94, 0.1);
        }
        
        .directory-name, .scattered-type-name {
          color: #e2e8f0;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          margin-bottom: 0.5rem;
        }
        
        .directory-types, .scattered-type-locations {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }
        
        .directory-type-tag, .location-tag {
          background: rgba(34, 197, 94, 0.1);
          border: 1px solid rgba(34, 197, 94, 0.3);
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          color: #a7f3d0;
          font-size: 0.8rem;
        }
        
        .directory-count, .location-count {
          color: #94a3b8;
          font-size: 0.85rem;
        }
        
        /* Suggestions */
        .suggestions-list {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.25rem;
        }
        
        .suggestion-item {
          background: rgba(0, 0, 0, 0.3);
          border-radius: 12px;
          overflow: hidden;
        }
        
        .suggestion-item.high {
          border-left: 4px solid #ef4444;
        }
        
        .suggestion-item.medium {
          border-left: 4px solid #f59e0b;
        }
        
        .suggestion-item.low {
          border-left: 4px solid #3b82f6;
        }
        
        .suggestion-header {
          padding: 0.75rem 1rem;
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1px solid rgba(34, 197, 94, 0.1);
        }
        
        .suggestion-type {
          color: #e2e8f0;
          font-weight: 600;
        }
        
        .priority-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 600;
        }
        
        .priority-badge.high {
          background: rgba(239, 68, 68, 0.1);
          color: #ef4444;
          border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .priority-badge.medium {
          background: rgba(245, 158, 11, 0.1);
          color: #f59e0b;
          border: 1px solid rgba(245, 158, 11, 0.3);
        }
        
        .priority-badge.low {
          background: rgba(59, 130, 246, 0.1);
          color: #3b82f6;
          border: 1px solid rgba(59, 130, 246, 0.3);
        }
        
        .suggestion-content {
          padding: 1rem;
        }
        
        .suggestion-folder {
          color: #a7f3d0;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          margin-bottom: 0.5rem;
        }
        
        .suggestion-reason {
          color: #e2e8f0;
          margin-bottom: 1rem;
        }
        
        .suggested-folders {
          background: rgba(34, 197, 94, 0.05);
          padding: 0.75rem;
          border-radius: 8px;
          border: 1px dashed rgba(34, 197, 94, 0.3);
        }
        
        .suggested-label {
          color: #a7f3d0;
          font-size: 0.85rem;
          margin-bottom: 0.5rem;
        }
        
        .folders-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }
        
        .folder-tag {
          background: rgba(34, 197, 94, 0.1);
          border: 1px solid rgba(34, 197, 94, 0.3);
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          color: #a7f3d0;
          font-size: 0.8rem;
          font-family: 'JetBrains Mono', monospace;
        }
        
        /* Recommended Structure */
        .recommended-folders {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 1.25rem;
          margin-bottom: 2rem;
        }
        
        .recommended-folder {
          background: rgba(0, 0, 0, 0.3);
          padding: 1rem;
          border-radius: 12px;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .folder-name {
          color: #a7f3d0;
          font-weight: 600;
          font-family: 'JetBrains Mono', monospace;
          margin-bottom: 0.5rem;
        }
        
        .folder-description {
          color: #94a3b8;
          font-size: 0.9rem;
        }
        
        .summary-box {
          background: rgba(0, 0, 0, 0.3);
          padding: 1.25rem;
          border-radius: 12px;
          border: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .summary-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
          border-bottom: 1px solid rgba(34, 197, 94, 0.15);
          padding-bottom: 0.5rem;
        }
        
        .summary-header h4 {
          color: #22c55e;
          font-size: 1.1rem;
          font-weight: 600;
        }
        
        .organization-level {
          color: #22c55e;
          font-weight: 600;
        }
        
        .issues-list, .quick-wins-list {
          margin-bottom: 1rem;
        }
        
        .issues-list h5, .quick-wins-list h5 {
          color: #e2e8f0;
          margin-bottom: 0.5rem;
          font-size: 0.95rem;
          font-weight: 600;
        }
        
        .issues-list ul, .quick-wins-list ul {
          list-style-type: none;
          padding: 0;
          margin: 0;
        }
        
        .issues-list li {
          padding: 0.5rem 0;
          color: #f87171;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .issues-list li:before {
          content: "⚠️";
        }
        
        .quick-wins-list li {
          padding: 0.5rem 0;
          color: #a7f3d0;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .quick-wins-list li:before {
          content: "✅";
        }
        
        .improvement-time {
          color: #e2e8f0;
          padding-top: 0.75rem;
          border-top: 1px solid rgba(34, 197, 94, 0.15);
        }
        
        .improvement-time span {
          color: #94a3b8;
        }
        
        /* Responsive design */
        .error-container {
          background: rgba(239, 68, 68, 0.1);
          border: 1px solid rgba(239, 68, 68, 0.3);
          border-radius: 12px;
          padding: 2rem;
          text-align: center;
          margin: 2rem 0;
        }
        
        .error-title {
          color: #ef4444;
          font-size: 1.5rem;
          margin-bottom: 1rem;
        }
        
        .error-message {
          color: #fca5a5;
        }
        
        .no-folders {
          color: #94a3b8;
          text-align: center;
          padding: 1rem;
          font-style: italic;
        }
        
        @media (max-width: 768px) {
          .structure-section {
            padding: 1rem;
          }
          
          .metrics-grid {
            grid-template-columns: 1fr 1fr;
          }
          
          .recommended-folders {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
      </>
    );
  } catch (error) {
    console.error("Error rendering GitHub structure analysis:", error);
    return (
      <div className="error-container">
        <h2 className="error-title">Error Rendering Analysis</h2>
        <p className="error-message">
          There was an error rendering the repository structure analysis. Please
          try again or contact support.
        </p>
      </div>
    );
  }
};

export default GithubStructureAnalysisView;
