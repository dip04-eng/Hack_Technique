import os
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()


class GroqAIAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq AI analyzer"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None
            print(
                "Warning: Groq API key not found. AI-powered analysis will be disabled."
            )

    def is_available(self) -> bool:
        """Check if Groq AI is available"""
        return self.client is not None

    async def analyze_repository_structure(
        self, repo_info: Dict, structure_data: Dict
    ) -> Dict:
        """
        Use Groq AI to analyze repository structure and provide intelligent insights
        """
        if not self.is_available():
            return {"ai_analysis": "AI analysis not available - missing Groq API key"}

        try:
            # Prepare context for AI analysis
            context = {
                "repository": {
                    "name": repo_info.get("name"),
                    "language": repo_info.get("language"),
                    "description": repo_info.get("description"),
                    "size": repo_info.get("size"),
                    "stars": repo_info.get("stars"),
                    "topics": repo_info.get("topics", []),
                },
                "structure": {
                    "total_files": structure_data.get("total_files"),
                    "total_size_mb": structure_data.get("total_size_mb"),
                    "file_types": structure_data.get("file_types", {}),
                    "languages": structure_data.get("languages", {}),
                    "directory_count": structure_data.get("directory_count"),
                },
            }

            prompt = f"""
You are an expert software architect and code quality analyst. Analyze this GitHub repository and provide comprehensive insights.

Repository Context:
{json.dumps(context, indent=2)}

Please provide a detailed analysis covering:

1. **Architecture Assessment**: Evaluate the overall project architecture and structure
2. **Code Quality Insights**: Assess code organization and potential quality issues
3. **Best Practices**: Compare against industry standards for this technology stack
4. **Scalability Concerns**: Identify potential scalability and maintainability issues
5. **Security Considerations**: Highlight any security-related structural concerns
6. **Performance Optimization**: Suggest performance improvements based on structure
7. **Developer Experience**: Evaluate how developer-friendly the project structure is
8. **Technology Stack Analysis**: Assess the appropriateness of the technology choices

Provide actionable, specific recommendations with clear reasoning. Format your response as a structured analysis with clear sections.
"""

            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect with deep knowledge of software engineering best practices, code quality, and project structure optimization.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=2000,
            )

            return {
                "ai_analysis": response.choices[0].message.content,
                "model_used": "meta-llama/llama-4-scout-17b-16e-instruct",
                "analysis_type": "comprehensive_structure",
            }

        except Exception as e:
            return {"ai_analysis": f"AI analysis failed: {str(e)}"}

    async def generate_smart_recommendations(
        self, cleanup_suggestions: List, structure_suggestions: List, repo_context: Dict
    ) -> Dict:
        """
        Generate intelligent recommendations using AI based on analysis results
        """
        if not self.is_available():
            return {"smart_recommendations": "AI recommendations not available"}

        try:
            suggestions_summary = {
                "cleanup_count": len(cleanup_suggestions),
                "structure_count": len(structure_suggestions),
                "cleanup_examples": (
                    cleanup_suggestions[:5] if cleanup_suggestions else []
                ),
                "structure_examples": (
                    structure_suggestions[:3] if structure_suggestions else []
                ),
            }

            prompt = f"""
Based on the repository analysis results, provide intelligent, prioritized recommendations:

Repository: {repo_context.get('name')} ({repo_context.get('language')})
Description: {repo_context.get('description', 'No description')}

Analysis Results:
{json.dumps(suggestions_summary, indent=2)}

Please provide:

1. **Priority Action Items**: Top 3-5 most important actions to take immediately
2. **Quick Wins**: Easy improvements that provide immediate value
3. **Long-term Improvements**: Strategic changes for long-term project health
4. **Risk Assessment**: Potential risks if current issues are not addressed
5. **Implementation Strategy**: Step-by-step approach to implement changes
6. **Resource Estimation**: Rough effort estimates for major recommendations

Be specific, actionable, and consider the project's context and maturity level.
"""

            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior technical consultant specializing in software project optimization and developer productivity.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                max_tokens=1500,
            )

            return {
                "smart_recommendations": response.choices[0].message.content,
                "model_used": "meta-llama/llama-4-scout-17b-16e-instruct",
                "recommendation_type": "strategic_planning",
            }

        except Exception as e:
            return {"smart_recommendations": f"AI recommendations failed: {str(e)}"}

    async def analyze_code_patterns(
        self, file_structure: Dict, repo_info: Dict
    ) -> Dict:
        """
        Analyze code patterns and suggest improvements using AI
        """
        if not self.is_available():
            return {"pattern_analysis": "Pattern analysis not available"}

        try:
            # Extract relevant patterns from file structure
            patterns = {
                "file_types": file_structure.get("file_types", {}),
                "languages": file_structure.get("languages", {}),
                "total_files": file_structure.get("total_files", 0),
                "avg_file_size": file_structure.get("avg_file_size", 0),
            }

            prompt = f"""
Analyze the code patterns and file organization for this {repo_info.get('language', 'Unknown')} project:

Project: {repo_info.get('name')}
File Patterns: {json.dumps(patterns, indent=2)}

Provide insights on:

1. **Code Organization Patterns**: How well is the code organized?
2. **File Size Distribution**: Are files appropriately sized?
3. **Language Mix**: Is the language distribution appropriate?
4. **Architectural Patterns**: What architectural patterns are evident?
5. **Potential Code Smells**: Structural indicators of code quality issues
6. **Modularization**: How well is the code modularized?
7. **Testing Strategy**: Evidence of testing practices from file structure
8. **Documentation Coverage**: Assessment of documentation completeness

Provide specific, actionable insights for improving code organization and quality.
"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code quality expert with extensive experience in software architecture and design patterns.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1200,
            )

            return {
                "pattern_analysis": response.choices[0].message.content,
                "model_used": "llama-3.1-8b-instant",
                "analysis_focus": "code_patterns",
            }

        except Exception as e:
            return {"pattern_analysis": f"Pattern analysis failed: {str(e)}"}

    async def generate_project_health_score(self, all_metrics: Dict) -> Dict:
        """
        Generate an overall project health score with AI insights
        """
        if not self.is_available():
            return {"health_score": "Health scoring not available"}

        try:
            prompt = f"""
Based on the following repository metrics, provide a comprehensive project health assessment:

Metrics:
{json.dumps(all_metrics, indent=2)}

Please provide:

1. **Overall Health Score**: Rate from 1-100 with clear justification
2. **Strengths**: What this project does well
3. **Critical Issues**: Most important problems to address
4. **Health Trends**: Likely trajectory if current patterns continue
5. **Improvement Roadmap**: Specific steps to improve health score
6. **Comparison**: How this compares to similar projects
7. **Maintenance Burden**: Assessment of ongoing maintenance requirements

Be honest but constructive in your assessment.
"""

            response = self.client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical project assessor with expertise in software engineering metrics and project health evaluation.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1300,
            )

            return {
                "health_assessment": response.choices[0].message.content,
                "model_used": "meta-llama/llama-4-scout-17b-16e-instruct",
                "assessment_type": "comprehensive_health",
            }

        except Exception as e:
            return {"health_assessment": f"Health assessment failed: {str(e)}"}


# Global AI analyzer instance
ai_analyzer = GroqAIAnalyzer()
