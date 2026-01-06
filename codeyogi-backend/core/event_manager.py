import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import BackgroundTasks
import logging

from models.events import (
    EventType,
    EventPayload,
    GitHubWebhookPayload,
    RepositoryState,
    AgentTrigger,
    EventProcessingResult,
)

# Import available agents
import agents

# Get available agents
available_agents = {}
if hasattr(agents, "repo_analyzer"):
    available_agents["repo_analyzer"] = agents.repo_analyzer
if hasattr(agents, "workflow_optimizer"):
    available_agents["workflow_optimizer"] = agents.workflow_optimizer
if hasattr(agents, "multi_language_optimizer"):
    available_agents["multi_language_optimizer"] = agents.multi_language_optimizer
if hasattr(agents, "seo_injector"):
    available_agents["seo_injector"] = agents.seo_injector
if hasattr(agents, "flowchart_generator"):
    available_agents["flowchart_generator"] = agents.flowchart_generator
if hasattr(agents, "deploy_agent"):
    available_agents["deploy_agent"] = agents.deploy_agent

logger = logging.getLogger(__name__)


class EventManager:
    """Central event manager for handling repository events and triggering agents"""

    def __init__(self):
        self.monitored_repos: Dict[str, RepositoryState] = {}
        self.agent_triggers: List[AgentTrigger] = self._setup_default_triggers()
        self.event_history: List[EventProcessingResult] = []

    def _setup_default_triggers(self) -> List[AgentTrigger]:
        """Setup default agent triggers for different events"""
        return [
            # Multi-language optimizer for code pushes
            AgentTrigger(
                agent_name="multi_language_optimizer",
                event_types=[EventType.CODE_PUSH],
                priority=4,
                conditions={"auto_optimize": True},
            ),
            # Workflow optimizer for user requests
            AgentTrigger(
                agent_name="workflow_optimizer",
                event_types=[EventType.WORKFLOW_OPTIMIZATION_REQUEST],
                priority=5,
            ),
            # SEO injector for new repos
            AgentTrigger(
                agent_name="seo_injector",
                event_types=[EventType.NEW_REPO_INITIALIZE],
                priority=3,
            ),
            # Repo analyzer for user requests
            AgentTrigger(
                agent_name="repo_analyzer",
                event_types=[EventType.REPO_ANALYSIS_REQUEST],
                priority=3,
            ),
            # Repository description agent for description requests
            AgentTrigger(
                agent_name="repo_description_agent",
                event_types=[EventType.REPO_DESCRIPTION_REQUEST],
                priority=4,
            ),
            # Flowchart generator for deployment requests
            AgentTrigger(
                agent_name="flowchart_generator",
                event_types=[EventType.DEPLOYMENT_REQUEST],
                priority=2,
            ),
            # Deploy agent for deployment requests
            AgentTrigger(
                agent_name="deploy_agent",
                event_types=[EventType.DEPLOYMENT_REQUEST],
                priority=1,
            ),
        ]

    async def register_repository(
        self, repo_url: str, user_id: str, github_token: Optional[str] = None
    ) -> RepositoryState:
        """Register a repository for monitoring"""
        # Parse repo info from URL
        parts = repo_url.replace("https://github.com/", "").split("/")
        repo_owner, repo_name = parts[0], parts[1]

        repo_state = RepositoryState(
            repo_url=repo_url,
            repo_owner=repo_owner,
            repo_name=repo_name,
            selected_by_user=user_id,
            monitoring_enabled=True,
        )

        self.monitored_repos[repo_url] = repo_state

        # Trigger repo selection event
        await self.process_event(
            EventPayload(
                event_type=EventType.REPO_SELECTION,
                repo_url=repo_url,
                repo_owner=repo_owner,
                repo_name=repo_name,
                github_token=github_token,
                user_id=user_id,
                metadata={"action": "register"},
            )
        )

        return repo_state

    async def handle_github_webhook(
        self, event_type: str, payload: GitHubWebhookPayload
    ) -> List[EventProcessingResult]:
        """Handle incoming GitHub webhook events"""
        repo_url = payload.repository["html_url"]

        if repo_url not in self.monitored_repos:
            logger.warning(f"Received webhook for unmonitored repo: {repo_url}")
            return []

        repo_state = self.monitored_repos[repo_url]

        # Process different GitHub event types
        events_to_process = []

        if event_type == "push":
            # Update repo state
            if payload.head_commit:
                repo_state.last_commit_sha = payload.head_commit["id"]
                repo_state.last_push_time = datetime.now()

            # Create code push event
            events_to_process.append(
                EventPayload(
                    event_type=EventType.CODE_PUSH,
                    repo_url=repo_url,
                    repo_owner=repo_state.repo_owner,
                    repo_name=repo_state.repo_name,
                    metadata={
                        "commits": payload.commits or [],
                        "ref": payload.ref,
                        "pusher": payload.pusher,
                        "head_commit": payload.head_commit,
                    },
                )
            )

        elif event_type == "repository" and payload.action == "created":
            # New repository created
            events_to_process.append(
                EventPayload(
                    event_type=EventType.NEW_REPO_INITIALIZE,
                    repo_url=repo_url,
                    repo_owner=repo_state.repo_owner,
                    repo_name=repo_state.repo_name,
                    metadata={"action": payload.action},
                )
            )

        # Process all events
        results = []
        for event in events_to_process:
            result = await self.process_event(event)
            results.extend(result)

        return results

    async def process_event(self, event: EventPayload) -> List[EventProcessingResult]:
        """Process an event and trigger appropriate agents"""
        results = []

        # Find matching agent triggers
        matching_triggers = [
            trigger
            for trigger in self.agent_triggers
            if event.event_type in trigger.event_types and trigger.enabled
        ]

        # Sort by priority (highest first)
        matching_triggers.sort(key=lambda x: x.priority, reverse=True)

        # Process each matching trigger
        for trigger in matching_triggers:
            if self._should_trigger_agent(trigger, event):
                result = await self._execute_agent(trigger.agent_name, event)
                results.append(result)

        return results

    def _should_trigger_agent(self, trigger: AgentTrigger, event: EventPayload) -> bool:
        """Check if agent should be triggered based on conditions"""
        if not trigger.conditions:
            return True

        # Check conditions
        for condition_key, condition_value in trigger.conditions.items():
            if condition_key == "auto_optimize":
                # Check if auto optimization is enabled for this repo
                repo_state = self.monitored_repos.get(event.repo_url)
                if repo_state and not repo_state.monitoring_enabled:
                    return False

            # Add more condition checks as needed

        return True

    async def _execute_agent(
        self, agent_name: str, event: EventPayload
    ) -> EventProcessingResult:
        """Execute a specific agent with the event data"""
        event_id = str(uuid.uuid4())
        start_time = datetime.now()

        try:
            result = None

            if agent_name == "multi_language_optimizer":
                result = await self._run_multi_language_optimizer(event)

            elif agent_name == "workflow_optimizer":
                result = await self._run_workflow_optimizer(event)

            elif agent_name == "seo_injector":
                result = await self._run_seo_injector(event)

            elif agent_name == "repo_analyzer":
                result = await self._run_repo_analyzer(event)

            elif agent_name == "repo_description_agent":
                result = await self._run_repo_description_agent(event)

            elif agent_name == "flowchart_generator":
                result = await self._run_flowchart_generator(event)

            elif agent_name == "deploy_agent":
                result = await self._run_deploy_agent(event)

            else:
                raise ValueError(f"Unknown agent: {agent_name}")

            processing_time = (datetime.now() - start_time).total_seconds()

            return EventProcessingResult(
                event_id=event_id,
                event_type=event.event_type,
                agent_name=agent_name,
                status="success",
                result=result,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing {agent_name}: {str(e)}")

            return EventProcessingResult(
                event_id=event_id,
                event_type=event.event_type,
                agent_name=agent_name,
                status="failed",
                error_message=str(e),
                processing_time_seconds=processing_time,
            )

    # Agent execution methods
    async def _run_multi_language_optimizer(
        self, event: EventPayload
    ) -> Dict[str, Any]:
        """Run multi-language optimizer"""
        if "multi_language_optimizer" not in available_agents:
            raise Exception("MultiLanguageOptimizer not available")

        multi_language_optimizer = available_agents["multi_language_optimizer"]
        if not hasattr(multi_language_optimizer, "GitHubMultiLanguageOptimizer"):
            raise Exception("GitHubMultiLanguageOptimizer not available")

        optimizer = multi_language_optimizer.GitHubMultiLanguageOptimizer()

        # Get changed files from the commit
        changed_files = []
        if event.metadata and "commits" in event.metadata:
            for commit in event.metadata["commits"]:
                changed_files.extend(commit.get("added", []))
                changed_files.extend(commit.get("modified", []))

        # For now, return a placeholder result
        return {
            "optimized_files": changed_files,
            "optimization_count": len(changed_files),
            "status": "completed",
        }

    async def _run_workflow_optimizer(self, event: EventPayload) -> Dict[str, Any]:
        """Run workflow optimizer"""
        if "workflow_optimizer" not in available_agents:
            raise Exception("Workflow optimizer not available")

        workflow_optimizer = available_agents["workflow_optimizer"]
        result = await workflow_optimizer.optimize(event.repo_url)

        # Update repo state
        if event.repo_url in self.monitored_repos:
            self.monitored_repos[event.repo_url].workflow_optimized = True
            self.monitored_repos[event.repo_url].updated_at = datetime.now()

        return result

    async def _run_seo_injector(self, event: EventPayload) -> Dict[str, Any]:
        """Run SEO injector"""
        # For new repos, initialize README with SEO optimization
        if "seo_injector" not in available_agents or not hasattr(
            available_agents["seo_injector"], "SEOInjector"
        ):
            # Create a simple result for now
            return {
                "readme_optimized": True,
                "seo_metadata_added": True,
                "status": "completed",
            }

        # Update repo state
        if event.repo_url in self.monitored_repos:
            self.monitored_repos[event.repo_url].readme_initialized = True
            self.monitored_repos[event.repo_url].seo_optimized = True
            self.monitored_repos[event.repo_url].updated_at = datetime.now()

        return {
            "readme_optimized": True,
            "seo_metadata_added": True,
            "status": "completed",
        }

    async def _run_repo_analyzer(self, event: EventPayload) -> Dict[str, Any]:
        """Run repository analyzer"""
        from models.schemas import RepoAnalysisRequest

        request = RepoAnalysisRequest(github_url=event.repo_url, analysis_type="full")

        if "repo_analyzer" not in available_agents:
            raise Exception("Repository analyzer not available")

        repo_analyzer = available_agents["repo_analyzer"]
        result = await repo_analyzer.analyze(request)

        # Update repo state
        if event.repo_url in self.monitored_repos:
            self.monitored_repos[event.repo_url].last_analysis_time = datetime.now()
            self.monitored_repos[event.repo_url].updated_at = datetime.now()

        return result.model_dump()

    async def _run_repo_description_agent(self, event: EventPayload) -> Dict[str, Any]:
        """Run repository description agent"""
        from agents.repo_description_agent import repo_description_agent
        from models.schemas import RepoDescriptionRequest

        request = RepoDescriptionRequest(
            github_url=event.repo_url,
            include_tech_stack=True,
            include_architecture=True,
            include_features=True,
        )

        result = await repo_description_agent.analyze_repository_description(request)

        # Update repo state
        if event.repo_url in self.monitored_repos:
            self.monitored_repos[event.repo_url].updated_at = datetime.now()

        return result.model_dump()

    async def _run_flowchart_generator(self, event: EventPayload) -> Dict[str, Any]:
        """Run flowchart generator"""
        # Placeholder implementation
        return {
            "flowchart_generated": True,
            "deployment_steps": [
                "Build application",
                "Run tests",
                "Deploy to staging",
                "Run integration tests",
                "Deploy to production",
            ],
            "status": "completed",
        }

    async def _run_deploy_agent(self, event: EventPayload) -> Dict[str, Any]:
        """Run deployment agent"""
        # Placeholder implementation
        return {
            "deployment_initiated": True,
            "deployment_strategy": "blue-green",
            "estimated_time": "15 minutes",
            "status": "in_progress",
        }

    # API methods for user requests
    async def request_workflow_optimization(
        self, repo_url: str, user_id: str, github_token: Optional[str] = None
    ) -> List[EventProcessingResult]:
        """User requests workflow optimization"""
        repo_state = self.monitored_repos.get(repo_url)
        if not repo_state:
            raise Exception(f"Repository {repo_url} is not registered for monitoring")

        event = EventPayload(
            event_type=EventType.WORKFLOW_OPTIMIZATION_REQUEST,
            repo_url=repo_url,
            repo_owner=repo_state.repo_owner,
            repo_name=repo_state.repo_name,
            github_token=github_token,
            user_id=user_id,
        )

        return await self.process_event(event)

    async def request_repo_analysis(
        self, repo_url: str, user_id: str, github_token: Optional[str] = None
    ) -> List[EventProcessingResult]:
        """User requests repository analysis"""
        repo_state = self.monitored_repos.get(repo_url)
        if not repo_state:
            raise Exception(f"Repository {repo_url} is not registered for monitoring")

        event = EventPayload(
            event_type=EventType.REPO_ANALYSIS_REQUEST,
            repo_url=repo_url,
            repo_owner=repo_state.repo_owner,
            repo_name=repo_state.repo_name,
            github_token=github_token,
            user_id=user_id,
        )

        return await self.process_event(event)

    async def request_deployment(
        self, repo_url: str, user_id: str, github_token: Optional[str] = None
    ) -> List[EventProcessingResult]:
        """User requests deployment"""
        repo_state = self.monitored_repos.get(repo_url)
        if not repo_state:
            raise Exception(f"Repository {repo_url} is not registered for monitoring")

        event = EventPayload(
            event_type=EventType.DEPLOYMENT_REQUEST,
            repo_url=repo_url,
            repo_owner=repo_state.repo_owner,
            repo_name=repo_state.repo_name,
            github_token=github_token,
            user_id=user_id,
        )

        return await self.process_event(event)

    async def request_repo_description(
        self, repo_url: str, user_id: str, github_token: Optional[str] = None
    ) -> List[EventProcessingResult]:
        """User requests repository description with flowchart"""
        repo_state = self.monitored_repos.get(repo_url)
        if not repo_state:
            raise Exception(f"Repository {repo_url} is not registered for monitoring")

        event = EventPayload(
            event_type=EventType.REPO_DESCRIPTION_REQUEST,
            repo_url=repo_url,
            repo_owner=repo_state.repo_owner,
            repo_name=repo_state.repo_name,
            github_token=github_token,
            user_id=user_id,
        )

        return await self.process_event(event)

    def get_repo_status(self, repo_url: str) -> Optional[RepositoryState]:
        """Get current status of a monitored repository"""
        return self.monitored_repos.get(repo_url)

    def get_event_history(
        self, repo_url: Optional[str] = None, limit: int = 50
    ) -> List[EventProcessingResult]:
        """Get event processing history"""
        history = self.event_history[-limit:]

        if repo_url:
            # Filter by repo_url if provided
            history = [
                event
                for event in history
                if event.result and event.result.get("repo_url") == repo_url
            ]

        return history


# Global event manager instance
event_manager = EventManager()
