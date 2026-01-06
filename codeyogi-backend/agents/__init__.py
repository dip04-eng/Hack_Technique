# Agents package

# Import all available agents with error handling
available_agents = []

try:
    from . import repo_analyzer

    available_agents.append("repo_analyzer")
except ImportError as e:
    print(f"Warning: repo_analyzer not available: {e}")

try:
    from . import workflow_optimizer

    available_agents.append("workflow_optimizer")
except ImportError as e:
    print(f"Warning: workflow_optimizer not available: {e}")

try:
    from . import multi_language_optimizer

    available_agents.append("multi_language_optimizer")
except ImportError as e:
    print(f"Warning: multi_language_optimizer not available: {e}")

try:
    from . import seo_injector

    available_agents.append("seo_injector")
except ImportError as e:
    print(f"Warning: seo_injector not available: {e}")

try:
    from . import flowchart_generator

    available_agents.append("flowchart_generator")
except ImportError as e:
    print(f"Warning: flowchart_generator not available: {e}")

try:
    from . import deploy_agent

    available_agents.append("deploy_agent")
except ImportError as e:
    print(f"Warning: deploy_agent not available: {e}")

try:
    from . import ai_analyzer

    available_agents.append("ai_analyzer")
except ImportError as e:
    print(f"Warning: ai_analyzer not available: {e}")

try:
    from . import pattern_optimizer

    available_agents.append("pattern_optimizer")
except ImportError as e:
    print(f"Warning: pattern_optimizer not available: {e}")

try:
    from . import repo_description_agent

    available_agents.append("repo_description_agent")
except ImportError as e:
    print(f"Warning: repo_description_agent not available: {e}")

try:
    from . import file_analyzer

    available_agents.append("file_analyzer")
except ImportError as e:
    print(f"Warning: file_analyzer not available: {e}")

__all__ = available_agents
print(f"Available agents: {available_agents}")
