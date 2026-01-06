import os
import json
from groq import Groq
from dotenv import load_dotenv
import sys
import io
from typing import Dict, List, Any, Optional

# --- Configuration & Setup ---

# Load environment variables from a .env file in the same directory.
# Your .env file should now contain: GROQ_API_KEY="your_api_key_here"
load_dotenv()

# Configure the Groq client with the API key.
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in .env file.")
    groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"[ERROR] Failed to configure Groq client: {e}")
    print("[INFO] Please make sure your .env file contains a valid GROQ_API_KEY.")
    # Don't exit, just set a flag for fallback
    groq_api_key = None
    groq_client = None

# --- Prompt Engineering ---

# This prompt is engineered to force the LLM to return a JSON object with a list of steps.
# The curly braces in the example JSON are doubled ({{ and }}) to escape them,
# preventing the .format() method from misinterpreting them as placeholders.
PROMPT_TEMPLATE = """
You are an expert system that designs step-by-step process flowcharts for technical tasks.
Your goal is to break down a complex user query into a simple, sequential list of actions.

Analyze the following user query and convert it into a series of clear, actionable steps.

QUERY:
"{query}"

You MUST return your response as a single, valid JSON object.
The JSON object should have a single key named "steps", which contains a list of strings.
Each string in the list is a single step in the flowchart.

Example Response Format:
{{
  "steps": [
    "Step 1 description",
    "Step 2 description",
    "Step 3 description"
  ]
}}

Do NOT include any introductory text, explanations, or markdown formatting around the JSON.
Your entire output must be only the JSON object itself.
"""

# --- Core Functions ---


def get_steps_from_llm_as_list(
    query: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
) -> list:
    """
    Queries the Groq LLM to get a list of flowchart steps for a given query.

    Args:
        query: The user's request (e.g., "How to deploy a React project").
        model: The Groq model to use for generation

    Returns:
        A list of strings, where each string is a step in the flowchart.
        Returns an empty list if the API call fails or the response is invalid.
    """
    prompt = PROMPT_TEMPLATE.format(query=query)
    print(f"\n[INFO] Generating steps for query: '{query}' using model: {model}")

    try:
        if not groq_client:
            print("[ERROR] Groq client not initialized.")
            return []

        # Call the Groq API
        response = groq_client.chat.completions.create(
            model=model,  # Use the provided model
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
        )

        reply = response.choices[0].message.content
        print("[INFO] Successfully received response from LLM.")

        data = json.loads(reply)

        if "steps" in data and isinstance(data["steps"], list):
            print(f"[SUCCESS] Parsed {len(data['steps'])} steps from the response.")
            return data["steps"]
        else:
            print(
                "[ERROR] JSON response is missing the 'steps' key or it's not a list."
            )
            return []

    except json.JSONDecodeError:
        print(f"[ERROR] Failed to decode JSON from LLM response: {reply}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during the API call: {e}")
        return []


def process_query_and_print_json(query: str):
    """
    Main processing pipeline: takes a query, gets steps from the LLM,
    formats them into the desired JSON structure, and prints the result.
    """
    steps_list = get_steps_from_llm_as_list(query)

    if not steps_list:
        print(f"[FAILURE] Could not generate steps for the query: '{query}'")
        # Print an empty JSON object on failure
        print(json.dumps({}))
        return

    # Format the list into the desired dictionary format: {"step1": ..., "step2": ...}
    formatted_steps_dict = {f"step{i+1}": step for i, step in enumerate(steps_list)}

    # Convert the dictionary to a pretty-printed JSON string
    final_json_output = json.dumps(formatted_steps_dict, indent=4)

    # Print the final JSON output
    print("\n--- Flowchart Steps (JSON Output) ---")
    print(final_json_output)
    print("-------------------------------------")


# --- Main Execution Block ---

if __name__ == "__main__":
    # List of test cases to run
    test_queries = [
        "How can I deploy my Spring Boot project?",
        "What are the steps to deploy a React project to Vercel?",
        "Outline the process for setting up a CI/CD pipeline for a Python Flask app on GitHub Actions.",
        "How do I publish a package to NPM?",
    ]

    # Run the process for each test query
    for q in test_queries:
        process_query_and_print_json(q)
        print("=" * 50)

    # Example of handling a custom query from command line (optional)
    # if len(sys.argv) > 1:
    #     custom_query = " ".join(sys.argv[1:])


# --- Deployment Flowchart Generation ---


def generate_deployment_flowchart(repo_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a deployment flowchart based on repository information

    Args:
        repo_info: Repository information including language, framework, etc.

    Returns:
        Dictionary containing deployment flowchart and metadata
    """
    language_value = repo_info.get("language")
    language = language_value.lower() if language_value else ""
    repo_name = repo_info.get("name", "project")

    # Language-specific deployment strategies
    deployment_strategies = {
        "python": {
            "steps": [
                "Setup Python environment",
                "Install dependencies from requirements.txt",
                "Run tests with pytest",
                "Build application package",
                "Deploy to staging environment",
                "Run integration tests",
                "Deploy to production",
                "Monitor application health",
            ],
            "platforms": ["Heroku", "AWS Lambda", "Docker", "Kubernetes"],
            "tools": ["pytest", "gunicorn", "nginx"],
        },
        "javascript": {
            "steps": [
                "Setup Node.js environment",
                "Install dependencies with npm/yarn",
                "Run unit tests",
                "Build production bundle",
                "Deploy to staging",
                "Run end-to-end tests",
                "Deploy to production",
                "Monitor application metrics",
            ],
            "platforms": ["Vercel", "Netlify", "AWS", "Azure"],
            "tools": ["jest", "webpack", "pm2"],
        },
        "java": {
            "steps": [
                "Setup JDK environment",
                "Build with Maven/Gradle",
                "Run unit tests",
                "Create JAR/WAR package",
                "Deploy to staging server",
                "Run integration tests",
                "Deploy to production",
                "Monitor JVM metrics",
            ],
            "platforms": ["AWS Elastic Beanstalk", "Kubernetes", "Tomcat"],
            "tools": ["Maven", "Gradle", "JUnit"],
        },
    }

    # Get deployment strategy or use generic one
    strategy = deployment_strategies.get(
        language,
        {
            "steps": [
                "Prepare deployment environment",
                "Build application",
                "Run automated tests",
                "Deploy to staging",
                "Validate deployment",
                "Deploy to production",
                "Monitor and verify",
            ],
            "platforms": ["Docker", "Kubernetes", "Cloud Platforms"],
            "tools": ["CI/CD Pipeline", "Monitoring Tools"],
        },
    )

    # Generate detailed flowchart
    flowchart = {
        "name": f"{repo_name} Deployment Pipeline",
        "description": f"Automated deployment pipeline for {repo_name}",
        "language": language,
        "steps": strategy["steps"],
        "deployment_options": {
            "platforms": strategy.get("platforms", []),
            "tools": strategy.get("tools", []),
            "estimated_time": "15-30 minutes",
        },
        "prerequisites": [
            "Repository access",
            "CI/CD platform account",
            "Production environment setup",
            "Monitoring tools configured",
        ],
        "success_criteria": [
            "All tests pass",
            "Zero downtime deployment",
            "Health checks successful",
            "Performance metrics within bounds",
        ],
    }

    return {
        "flowchart": flowchart,
        "mermaid_diagram": generate_mermaid_diagram(strategy["steps"]),
        "deployment_ready": True,
        "recommendations": [
            "Implement blue-green deployment for zero downtime",
            "Add automated rollback capabilities",
            "Setup monitoring and alerting",
            "Use infrastructure as code",
        ],
    }


def generate_mermaid_diagram(steps: List[str]) -> str:
    """
    Generate a Mermaid diagram representation of the deployment steps

    Args:
        steps: List of deployment steps

    Returns:
        Mermaid diagram syntax as string
    """
    diagram = "graph TD\n"

    for i, step in enumerate(steps):
        step_id = f"S{i+1}"
        diagram += f'    {step_id}["{step}"]\n'

        if i > 0:
            prev_step = f"S{i}"
            diagram += f"    {prev_step} --> {step_id}\n"

    # Add decision points for testing
    if len(steps) > 3:
        test_step = len(steps) // 2
        diagram += f"    S{test_step} --> D1{{Tests Pass?}}\n"
        diagram += f"    D1 -->|Yes| S{test_step + 1}\n"
        diagram += f"    D1 -->|No| E1[Fix Issues]\n"
        diagram += f"    E1 --> S1\n"

    return diagram


async def generate_deployment_plan(repo_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate a comprehensive deployment plan

    Args:
        repo_info: Repository information

    Returns:
        Complete deployment plan with flowchart and recommendations
    """
    try:
        # Generate the flowchart
        deployment_plan = generate_deployment_flowchart(repo_info)

        # Add AI-generated insights if available
        if groq_client:
            try:
                query = f"Generate deployment best practices for a {repo_info.get('language', '')} project named {repo_info.get('name', '')}"
                # Use the existing function from the file
                ai_insights = get_steps_from_llm_as_list(query)
                deployment_plan["ai_insights"] = {"steps": ai_insights}
            except Exception as e:
                print(f"[WARNING] Could not generate AI insights: {e}")

        return deployment_plan

    except Exception as e:
        return {"flowchart": None, "error": str(e), "deployment_ready": False}
    #     process_query_and_print_json(custom_query)
