import React from "react";

const AIStrategicAnalysisView: React.FC<{ content: string }> = ({
  content,
}) => {
  return (
    <div className="ai-strategic-analysis">
      <div className="analysis-header">
        <h2>
          <span role="img" aria-label="ai">
            🧠
          </span>{" "}
          AI Strategic Analysis
        </h2>
      </div>
      <div className="analysis-content">
        {(() => {
          const lines = content.split("\n");
          const elements = [];
          let currentOl: string[] = [];
          let olStartIdx = 0;
          for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            // Horizontal rule
            if (/^[-]{3,}$/.test(line.trim())) {
              // Flush any open ol
              if (currentOl.length > 0) {
                elements.push(
                  <ol className="analysis-ol" key={"ol-" + olStartIdx}>
                    {currentOl.map((item, idx) => (
                      <li
                        key={idx}
                        className="analysis-ol-item"
                        dangerouslySetInnerHTML={{ __html: item }}
                      />
                    ))}
                  </ol>
                );
                currentOl = [];
              }
              elements.push(<hr className="analysis-hr" key={"hr-" + i} />);
              continue;
            }
            // Numbered list
            const olMatch = line.match(/^\d+\. (.+)$/);
            if (olMatch) {
              if (currentOl.length === 0) olStartIdx = i;
              // Support bold in list items
              currentOl.push(
                olMatch[1].replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
              );
              continue;
            } else if (currentOl.length > 0) {
              // Flush ol if ended
              elements.push(
                <ol className="analysis-ol" key={"ol-" + olStartIdx}>
                  {currentOl.map((item, idx) => (
                    <li
                      key={idx}
                      className="analysis-ol-item"
                      dangerouslySetInnerHTML={{ __html: item }}
                    />
                  ))}
                </ol>
              );
              currentOl = [];
            }
            // Section headers
            if (line.startsWith("# ")) {
              elements.push(
                <h2 key={i} className="analysis-section-title">
                  {line.replace("# ", "")}
                </h2>
              );
            } else if (line.startsWith("## ")) {
              elements.push(
                <h3 key={i} className="analysis-subsection-title">
                  {line.replace("## ", "")}
                </h3>
              );
            } else if (line.startsWith("- ")) {
              // Unordered list item
              elements.push(
                <div
                  key={i}
                  className="analysis-list-item"
                  dangerouslySetInnerHTML={{
                    __html: line
                      .replace("- ", "")
                      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>"),
                  }}
                />
              );
            } else if (line.trim() === "") {
              elements.push(<div key={i} className="spacer"></div>);
            } else {
              // Regular paragraph, support bold
              elements.push(
                <p
                  key={i}
                  className="analysis-paragraph"
                  dangerouslySetInnerHTML={{
                    __html: line.replace(
                      /\*\*([^*]+)\*\*/g,
                      "<strong>$1</strong>"
                    ),
                  }}
                />
              );
            }
          }
          // Flush any remaining ol
          if (currentOl.length > 0) {
            elements.push(
              <ol className="analysis-ol" key={"ol-" + olStartIdx}>
                {currentOl.map((item, idx) => (
                  <li
                    key={idx}
                    className="analysis-ol-item"
                    dangerouslySetInnerHTML={{ __html: item }}
                  />
                ))}
              </ol>
            );
          }
          return elements;
        })()}
      </div>

      <style>{`
        .analysis-hr {
          border: none;
          border-top: 2px solid #334155;
          margin: 1.5rem 0 1.5rem 0;
        }
        .analysis-ol {
          margin: 0 0 1.2rem 1.5rem;
          padding-left: 1.2rem;
          color: #e2e8f0;
        }
        .analysis-ol-item {
          margin-bottom: 0.5rem;
          line-height: 1.7;
        }
          
        .ai-strategic-analysis {
          background: linear-gradient(135deg, rgba(17, 24, 39, 0.9), rgba(0, 0, 0, 0.9));
          border-radius: 16px;
          padding: 1.5rem;
          border: 1px solid rgba(34, 197, 94, 0.3);
          margin: 1rem 0;
        }
        
        .analysis-header {
          margin-bottom: 1.5rem;
          text-align: center;
        }
        
        .analysis-header h2 {
          color: #22c55e;
          font-size: 1.8rem;
          font-weight: 600;
        }
        
        .analysis-content {
          color: #e2e8f0;
          line-height: 1.7;
        }
        
        .analysis-section-title {
          color: #22c55e;
          font-size: 1.5rem;
          font-weight: 600;
          margin-top: 2rem;
          margin-bottom: 1rem;
          border-bottom: 1px solid rgba(34, 197, 94, 0.3);
          padding-bottom: 0.5rem;
        }
        
        .analysis-subsection-title {
          color: #a7f3d0;
          font-size: 1.3rem;
          font-weight: 600;
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
        }
        
        .analysis-paragraph {
          margin-bottom: 1rem;
        }
        
        .analysis-list-item {
          padding-left: 1.5rem;
          position: relative;
          margin-bottom: 0.5rem;
        }
        
        .analysis-list-item:before {
          content: "•";
          color: #22c55e;
          position: absolute;
          left: 0.5rem;
        }
        
        .spacer {
          height: 1rem;
        }
      `}</style>
    </div>
  );
};

export default AIStrategicAnalysisView;
