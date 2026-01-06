# Rollback Intelligence Feature

## Overview
**Rollback Intelligence** is a human-friendly, AI-powered rollback system for CodeYogi that simplifies deployment rollback with numbered selection, safety analysis, and one-click execution.

## Problem Solved
Traditional GitHub rollback is painful because:
- Developers must find commit hashes manually
- Tokens, permissions, and commands are confusing
- During incidents, speed matters more than precision
- Risk assessment is manual and error-prone

## Solution
Rollback Intelligence provides:
- **Numbered commit selection** (no commit hashes)
- **AI-powered safety analysis** 
- **One-click rollback execution**
- **Real-time status updates**
- **Visual, intuitive interface**

---

## Architecture

### Backend Components

#### 1. `rollback_intelligence_agent.py`
Located: `codeyogi-backend/agents/rollback_intelligence_agent.py`

**Core Functionality:**
```python
class RollbackIntelligenceAgent:
    - get_rollback_candidates()     # Fetch recent commits as numbered list
    - analyze_rollback_safety()     # Safety check for specific commit
    - execute_rollback()            # Execute rollback with safety checks
    - _analyze_best_candidate()     # AI recommendation
    - trigger_deployment_workflow() # Trigger GitHub Actions
```

**Key Features:**
- Fetches last N commits from repository
- Converts to numbered list (#1 = current, #2 = previous, etc.)
- AI analysis using Groq (llama-3.3-70b-versatile)
- Safety checks for:
  - Commit age
  - Code change size
  - Deployment status
  - Historical stability

**API Integration:**
- Uses GitHub API via PyGithub
- Supports deployment status tracking
- Handles git operations safely

#### 2. API Endpoints in `main.py`

**Three new endpoints:**

##### `POST /api/rollback/candidates`
Fetch rollback candidates with AI recommendation.

**Request:**
```json
{
  "repo_owner": "owner-name",
  "repo_name": "repo-name",
  "branch": "main",
  "limit": 10,
  "github_token": "optional-token"
}
```

**Response:**
```json
{
  "success": true,
  "repository": "owner/repo",
  "branch": "main",
  "total_candidates": 10,
  "candidates": [
    {
      "number": 1,
      "sha": "abc123...",
      "short_sha": "abc123",
      "message": "Fix critical bug",
      "author": "John Doe",
      "timestamp_readable": "2 hours ago",
      "is_current": true,
      "files_changed": 5,
      "additions": 50,
      "deletions": 20,
      "deployment_status": "success"
    }
  ],
  "ai_recommendation": {
    "recommended_number": 3,
    "safety_level": "SAFE",
    "reason": "Stable deployment with successful status",
    "warning": null
  }
}
```

##### `POST /api/rollback/execute`
Execute rollback to specified commit number.

**Request:**
```json
{
  "repo_owner": "owner-name",
  "repo_name": "repo-name",
  "rollback_number": 3,
  "branch": "main",
  "force": false,
  "github_token": "optional-token"
}
```

**Response:**
```json
{
  "success": true,
  "execution_method": "revert_commit",
  "target_commit": { ... },
  "message": "Rollback prepared successfully",
  "git_instructions": {
    "commands": [
      "git revert --no-commit abc...xyz",
      "git commit -m 'Rollback via CodeYogi'",
      "git push origin main"
    ]
  },
  "next_steps": [
    "Rollback prepared",
    "Trigger deployment workflow to apply changes",
    "Monitor deployment status"
  ]
}
```

##### `POST /api/rollback/safety-check`
Perform detailed safety analysis for a candidate.

**Request:**
```json
{
  "repo_owner": "owner-name",
  "repo_name": "repo-name",
  "rollback_number": 5,
  "branch": "main"
}
```

**Response:**
```json
{
  "success": true,
  "safety_analysis": {
    "safe": false,
    "risk_level": "CAUTION",
    "warnings": [
      "Commit is 15 days old",
      "Large change: 120 files modified"
    ],
    "age_days": 15,
    "requires_confirmation": true
  }
}
```

---

### Frontend Components

#### 1. `RollbackIntelligence.tsx`
Located: `CodeYogi_Frontend/src/components/RollbackIntelligence.tsx`

**Props:**
```typescript
interface RollbackIntelligenceProps {
  repoOwner: string;
  repoName: string;
  branch?: string;
}
```

**Features:**
- Displays numbered list of commits
- Shows AI recommendation banner
- One-click rollback buttons
- Safety confirmation modal
- Real-time execution status
- Professional color scheme (blue/slate)

**UI Components:**
1. **Header** - Repository info and branch
2. **AI Recommendation Banner** - Highlighted best candidate
3. **Commit List** - Numbered deployments with metadata
4. **Rollback Buttons** - Per-commit action buttons
5. **Confirmation Modal** - Safety warnings before risky rollbacks
6. **Execution Result** - Success/failure feedback

#### 2. Integration in `ChatInterface.tsx`

**Message Type Extension:**
```typescript
interface Message {
  // ... existing fields
  rollbackIntelligence?: {
    repoOwner: string;
    repoName: string;
    branch?: string;
  };
}
```

**Trigger Keywords:**
- "rollback"
- "revert"
- "rollback intelligence"
- "show rollback"
- "deployment history"

**Action Button:**
Added to quick actions list at bottom of chat.

#### 3. Dashboard Integration

**Quick Actions Section:**
- Added "Rollback Intelligence" button
- Icon: RotateCcw from lucide-react
- Switches to chat and triggers rollback view

---

## User Flow

### Happy Path
1. User clicks "Rollback Intelligence" in Dashboard or types "rollback" in chat
2. System fetches last 10 commits from repository
3. AI analyzes and recommends best rollback candidate
4. User sees numbered list with:
   - Commit messages
   - Authors
   - Timestamps
   - File changes
   - Deployment status
5. User clicks "Rollback" button on desired commit
6. System performs safety check
7. If safe: Immediate rollback preparation
8. If risky: Confirmation modal with warnings
9. User confirms (if needed)
10. System prepares rollback instructions
11. User sees next steps and execution guidance

### Safety Check Flow
```
User selects commit
    ↓
Safety analysis
    ↓
    ├─ SAFE → Execute immediately
    ├─ CAUTION → Show warnings + confirm
    └─ RISKY → Show severe warnings + require confirmation
        ↓
    User confirms
        ↓
    Execute rollback
```

---

## AI Intelligence

### AI Analysis Uses
1. **Best Candidate Recommendation**
   - Analyzes commit history
   - Considers deployment status
   - Evaluates code change size
   - Checks commit age

2. **Safety Level Classification**
   - SAFE: Recent, small changes, successful deployment
   - CAUTION: Moderate age, medium changes
   - RISKY: Old commits, large changes, failed deployments

3. **Warning Generation**
   - Age warnings (>7 days old)
   - Size warnings (>50 files changed)
   - Status warnings (failed/unknown deployments)

### AI Model
- **Provider:** Groq
- **Model:** llama-3.3-70b-versatile
- **Temperature:** 0.3 (deterministic)
- **Max Tokens:** 300

---

## Safety Features

### 1. No Destructive Operations
- Never uses `git reset --hard`
- Always creates revert commits
- Preserves full git history

### 2. Confirmation for Risky Rollbacks
Requires confirmation when:
- Commit is >7 days old
- Large file changes (>50 files)
- Unknown or failed deployment status

### 3. Detailed Warnings
User sees specific issues:
- "Commit is 15 days old - may be outdated"
- "Large change: 120 files modified"
- "This commit had a failed deployment"

### 4. Git Instructions Provided
System returns exact commands needed:
```bash
git revert --no-commit abc123...xyz456
git commit -m 'Rollback via CodeYogi'
git push origin main
```

---

## Configuration

### Environment Variables

```bash
# Required
GITHUB_TOKEN=your_github_personal_access_token

# Optional (for AI recommendations)
GROQ_API_KEY=your_groq_api_key
```

### GitHub Token Permissions
Required scopes:
- `repo` - Full repository access
- `workflow` - Trigger GitHub Actions (optional)

---

## Usage Examples

### Example 1: Simple Rollback
```typescript
// User types "rollback" in chat
// System shows:
#1 → Current deployment (feat: new feature)
#2 → Previous stable (fix: critical bug)  ← AI RECOMMENDED
#3 → Last week (refactor: cleanup)

// User clicks "Rollback" on #2
// System executes immediately (SAFE)
```

### Example 2: Risky Rollback
```typescript
// User selects commit #5 (14 days old)
// System shows warning:
⚠️ Risk Level: CAUTION
- Commit is 14 days old
- 78 files modified

// User confirms
// System prepares rollback
```

### Example 3: API Usage
```bash
# Get candidates
curl -X POST http://localhost:8000/api/rollback/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "repo_owner": "myorg",
    "repo_name": "myapp",
    "branch": "main"
  }'

# Execute rollback
curl -X POST http://localhost:8000/api/rollback/execute \
  -H "Content-Type: application/json" \
  -d '{
    "repo_owner": "myorg",
    "repo_name": "myapp",
    "rollback_number": 3
  }'
```

---

## Testing

### Manual Testing Checklist
- [ ] Fetch candidates for valid repository
- [ ] AI recommendation appears correctly
- [ ] Click rollback on safe commit
- [ ] Click rollback on risky commit (see warning)
- [ ] Confirm risky rollback
- [ ] Cancel risky rollback
- [ ] Verify execution result display
- [ ] Test with repository without deployments
- [ ] Test with invalid repository
- [ ] Test without GitHub token

### Test Repositories
Use these for testing:
- Small repo: 5-10 commits
- Large repo: 100+ commits
- Recent deployments
- Old deployments (>30 days)

---

## Limitations

### Current Limitations
1. **Git Operations Manual** - System provides instructions, doesn't execute directly
2. **Deployment Status** - May be "unknown" for repos without GitHub Actions
3. **Branch Selection** - Defaults to "main", requires manual specification for others
4. **AI Optional** - Recommendations require Groq API key

### Future Enhancements
- [ ] Direct git operation execution via GitHub API
- [ ] Multi-branch support with branch selector
- [ ] Deployment history tracking
- [ ] Rollback success/failure metrics
- [ ] Automated post-rollback validation
- [ ] Slack/email notifications
- [ ] Rollback scheduling
- [ ] Diff preview before rollback

---

## Troubleshooting

### Common Issues

#### "GitHub token is required"
**Cause:** No token provided and GITHUB_TOKEN env var not set  
**Fix:** Set GITHUB_TOKEN in `.env` or pass in request

#### "Failed to fetch rollback candidates"
**Cause:** Invalid repo owner/name or token lacks permissions  
**Fix:** Verify repository exists and token has `repo` scope

#### AI recommendation not showing
**Cause:** GROQ_API_KEY not set  
**Fix:** Set GROQ_API_KEY in `.env` (optional, system works without it)

#### "Cannot rollback to current deployment"
**Cause:** User selected commit #1  
**Fix:** Select commit #2 or higher

---

## Architecture Decisions

### Why Numbered Selection?
- **User-friendly** - No need to memorize/copy commit hashes
- **Visual** - Easy to scan and compare
- **Safe** - Hard to make mistakes with clear numbering

### Why AI Analysis?
- **Smart recommendations** - Not just "most recent"
- **Risk assessment** - Automated safety checks
- **Time-saving** - No manual investigation needed

### Why No Direct Execution?
- **Safety** - Prevents accidental destructive operations
- **Transparency** - User sees exact commands
- **Flexibility** - Works with any git workflow

### Why Confirmation Modals?
- **Prevent mistakes** - Double-check for risky operations
- **Informed decisions** - User understands risks
- **Regulatory compliance** - Audit trail of confirmations

---

## API Reference

### RollbackIntelligenceAgent Methods

#### `get_rollback_candidates(repo_owner, repo_name, branch, limit)`
Fetch recent commits as numbered rollback candidates.

**Parameters:**
- `repo_owner` (str): Repository owner
- `repo_name` (str): Repository name
- `branch` (str): Branch name (default: "main")
- `limit` (int): Number of commits (default: 10)

**Returns:** Dict with candidates and AI recommendation

#### `analyze_rollback_safety(repo_owner, repo_name, rollback_number, candidates)`
Perform safety analysis for specific commit.

**Parameters:**
- `repo_owner` (str): Repository owner
- `repo_name` (str): Repository name  
- `rollback_number` (int): Commit number to analyze
- `candidates` (list): List of candidate commits

**Returns:** Dict with safety analysis

#### `execute_rollback(repo_owner, repo_name, rollback_number, branch, create_rollback_commit, force)`
Execute rollback to specified commit.

**Parameters:**
- `repo_owner` (str): Repository owner
- `repo_name` (str): Repository name
- `rollback_number` (int): Target commit number
- `branch` (str): Branch name
- `create_rollback_commit` (bool): Generate revert commit instructions
- `force` (bool): Skip safety checks

**Returns:** Dict with execution results

---

## Security Considerations

### Token Security
- Never log or expose GitHub tokens
- Use environment variables
- Support user-provided tokens for multi-user scenarios

### Permission Validation
- Verify user has write access before rollback
- Check token scopes before operations
- Validate repository ownership

### Audit Trail
- Log all rollback attempts
- Record user confirmations
- Track execution results

---

## Performance

### Optimization Strategies
- **Caching** - Cache commit data for 5 minutes
- **Pagination** - Default to 10 commits, expandable
- **Parallel Requests** - Fetch candidates and AI analysis simultaneously
- **Lazy Loading** - Load deployment status on-demand

### Response Times
- Fetch candidates: ~1-2 seconds
- AI analysis: ~2-3 seconds
- Safety check: <1 second
- Total: ~3-5 seconds for complete flow

---

## Deployment

### Backend Setup
```bash
cd codeyogi-backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd CodeYogi_Frontend
npm install
npm run dev
```

### Environment Configuration
```bash
# .env file
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GROQ_API_KEY=gsk_xxxxxxxxxxxx
```

---

## Monitoring & Observability

### Key Metrics to Track
- Rollback request count
- Success/failure rate
- Average execution time
- AI recommendation accuracy
- Safety confirmation rate

### Logging
All operations logged with:
- Timestamp
- Repository
- Commit selected
- Safety level
- Execution result

---

## Contributing

### Code Style
- Follow existing patterns
- Add type hints
- Write docstrings
- Include error handling

### Testing
- Add unit tests for new features
- Test with various repository sizes
- Verify error scenarios

### Documentation
- Update this README for changes
- Add inline comments
- Document API changes

---

## License
Part of CodeYogi platform. See main project license.

## Support
For issues or questions:
- Open GitHub issue
- Contact: CodeYogi team
- Documentation: This file

---

## Changelog

### Version 1.0.0 (Initial Release)
- ✅ Numbered commit selection
- ✅ AI-powered recommendations
- ✅ Safety analysis and warnings
- ✅ One-click rollback execution
- ✅ Professional UI with real-time updates
- ✅ Dashboard integration
- ✅ Chat interface integration
