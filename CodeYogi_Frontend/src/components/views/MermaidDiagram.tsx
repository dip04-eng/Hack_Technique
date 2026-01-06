import React, { useEffect, useState } from "react";
import mermaid from "mermaid";
import { motion } from "framer-motion";

const MermaidDiagram: React.FC<{ chart: string }> = ({ chart }) => {
  const [svg, setSvg] = useState("");

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: "dark",
      themeVariables: {
        primaryColor: "#22c55e",
        primaryTextColor: "#fff",
        primaryBorderColor: "#15803d",
        lineColor: "#22c55e",
        secondaryColor: "#475569",
        tertiaryColor: "#1f2937",
      },
    });

    const renderMermaid = async () => {
      try {
        const { svg } = await mermaid.render(
          `mermaid-graph-${Math.random().toString(36).substring(2, 9)}`,
          chart
        );
        setSvg(svg);
      } catch (error) {
        console.error("Failed to render Mermaid diagram:", error);
        // Fallback to displaying the code on error
        setSvg(`<pre><code>${chart}</code></pre>`);
      }
    };

    renderMermaid();
  }, [chart]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2, ease: "easeOut" }}
      className="flow-diagram"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );
};

export default MermaidDiagram;
