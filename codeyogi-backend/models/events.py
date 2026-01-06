from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class EventType(str, Enum):
    REPO_SELECTION = "repo_selection"
    CODE_PUSH = "code_push"
    WORKFLOW_OPTIMIZATION_REQUEST = "workflow_optimization_request"
    NEW_REPO_INITIALIZE = "new_repo_initialize"
    REPO_ANALYSIS_REQUEST = "repo_analysis_request"
    REPO_DESCRIPTION_REQUEST = "repo_description_request"
    DEPLOYMENT_REQUEST = "deployment_request"


class GitHubEventType(str, Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    REPOSITORY = "repository"
    CREATE = "create"
    DELETE = "delete"
    COMMIT_COMMENT = "commit_comment"


class EventPayload(BaseModel):
    event_type: EventType
    repo_url: str
    repo_owner: str
    repo_name: str
    github_token: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class GitHubWebhookPayload(BaseModel):
    action: Optional[str] = None
    repository: Dict[str, Any]
    commits: Optional[List[Dict[str, Any]]] = None
    ref: Optional[str] = None
    pusher: Optional[Dict[str, Any]] = None
    sender: Dict[str, Any]
    head_commit: Optional[Dict[str, Any]] = None


class RepositoryState(BaseModel):
    repo_url: str
    repo_owner: str
    repo_name: str
    last_commit_sha: Optional[str] = None
    last_push_time: Optional[datetime] = None
    monitoring_enabled: bool = True
    readme_initialized: bool = False
    seo_optimized: bool = False
    workflow_optimized: bool = False
    last_analysis_time: Optional[datetime] = None
    selected_by_user: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class AgentTrigger(BaseModel):
    agent_name: str
    event_types: List[EventType]
    conditions: Optional[Dict[str, Any]] = None
    priority: int = 1  # 1-5, where 5 is highest priority
    enabled: bool = True


class EventProcessingResult(BaseModel):
    event_id: str
    event_type: EventType
    agent_name: str
    status: str  # "success", "failed", "skipped"
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    processing_time_seconds: Optional[float] = None
    timestamp: datetime = datetime.now()
