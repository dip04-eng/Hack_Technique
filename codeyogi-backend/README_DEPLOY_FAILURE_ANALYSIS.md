# Post-Deploy Failure Analysis Feature

## 🎯 Overview

The **Post-Deploy Failure Analysis** feature is an AI-powered SRE agent that performs root cause analysis on deployment failures. It correlates code changes (git diff) with runtime errors to identify exactly WHY a deployment failed, not just WHAT failed.

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
cd codeyogi-backend
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

### 2. Test the API

```bash
python test_deploy_failure_api.py
```

### 3. Use the Frontend UI

Navigate to CodeYogi UI → Click **"Deploy Failure Analysis"** in Quick Actions sidebar

## 📡 API Endpoint

### **POST** `/api/post-deploy-analysis`

Analyzes deployment failures using AI-powered SRE expertise.

#### Request Body

```json
{
  "git_diff": "diff --git a/api/users.py...",
  "runtime_logs": "[2026-01-05] ERROR: Request timeout...",
  "pipeline_logs": "[2026-01-05] Tests passed ✓...",  // Optional
  "deployment_env": "production"  // Default: "production"
}
```

#### Response

```json
{
  "success": true,
  "summary": "Deployment caused severe API slowdown",
  "root_cause": "A blocking loop was introduced with time.sleep()...",
  "affected_file": "api/users.py",
  "affected_line": "get_users()",
  "impact": "Users experienced 45s response times and timeouts",
  "confidence": 0.95,
  "suggested_fix": "Remove time.sleep() and restore cache-based fetching",
  "detected_patterns": {
    "blocking_operations": {
      "matches": ["Found in code changes: time.sleep"],
      "impact": "latency / timeout",
      "severity": "high"
    }
  },
  "deployment_env": "production",
  "timestamp": "2026-01-05T10:37:30.123456"
}
```

## 🧠 How It Works

1. **Pattern Detection**: Automatically scans for 7+ common failure patterns:
   - Blocking loops → latency/timeout
   - Database calls in loops → performance degradation
   - Missing environment variables → crashes
   - Memory-intensive operations → OOM
   - Async-to-sync conversions → request backlog
   - File I/O in request paths → slow API
   - Heavy computation → CPU spikes

2. **AI Analysis**: Sends data to Groq's Llama 3.3 70B model with a specialized SRE system prompt

3. **Root Cause Identification**: Correlates code changes with runtime failures to identify the MOST LIKELY root cause

4. **Actionable Output**: Returns confidence-scored analysis with concrete fix recommendations

## 📁 File Structure

```
codeyogi-backend/
├── agents/
│   └── deploy_failure_analyzer.py      # Core SRE analysis agent
├── examples/
│   └── deploy_failure_analysis_demo.py # Demo scenarios
├── models/
│   └── schemas.py                       # API schemas (PostDeployAnalysisRequest/Result)
├── main.py                              # FastAPI endpoint: /api/post-deploy-analysis
├── test_deploy_failure_api.py           # API test script
└── README_DEPLOY_FAILURE_ANALYSIS.md    # This file

CodeYogi_Frontend/
└── src/components/
    ├── DeployFailureAnalysis.tsx        # UI component
    └── Dashboard.tsx                     # Quick Action integration
```

## 🔧 Environment Variables

```bash
# Required
GROQ_API_KEY=gsk_your_api_key_here
```

Set in `.env` file in the `codeyogi-backend` directory.

## 🎨 Frontend Integration

The feature is accessible via:
- **Quick Actions** sidebar → "Deploy Failure Analysis" button
- Panel type: `failure-analysis`

UI Features:
- Input fields for git diff, runtime logs, pipeline logs
- Environment selector (production/staging/development)
- Real-time analysis with loading state
- Confidence-scored results with color coding (green/yellow/red)
- Pattern detection visualization
- Copy results to clipboard

## 🧪 Test Scenarios

The test script includes 4 realistic scenarios:

1. **Blocking Loop**: `time.sleep()` in loop → 45s API latency
2. **Missing Env Var**: `STRIPE_API_KEY` not set → startup crash
3. **Memory Leak**: Loading 10GB data into memory → OOM kill
4. **Validation**: Tests required field validation

## 📊 Common Failure Patterns Detected

| Pattern | Keywords Detected | Impact | Severity |
|---------|------------------|---------|----------|
| Blocking Operations | `sleep(`, `Thread.sleep` | Latency/timeout | High |
| DB in Loop | `for.*query`, `while.*select` | Performance degradation | Critical |
| New Dependency | `import`, `require(` | Startup failure | High |
| Missing Env Var | `os.getenv`, `process.env` | Crash on startup | Critical |
| Async to Sync | `async def`, `await` | Request backlog | Medium |
| Memory Intensive | `large array`, `cache`, `in-memory` | OOM crash | Critical |
| File I/O in Request | `open(`, `read()`, `write()` | Slow API | Medium |

## 💡 Example Use Cases

### Scenario 1: API Timeout After Deployment

**Problem**: Deployment passed all tests, but production API started timing out.

**Input**:
- Git diff shows `time.sleep(0.1)` added inside loop processing 1000 users
- Runtime logs show "Request timeout" and "45s response time"

**Output**:
- Root Cause: "Blocking loop with sleep causing requests to queue"
- Confidence: 95%
- Fix: "Remove time.sleep() from request path"

### Scenario 2: Container Crashes on Startup

**Problem**: Container repeatedly crashes with exit code 1.

**Input**:
- Git diff shows new `STRIPE_API_KEY` environment variable
- Runtime logs show "AttributeError: 'NoneType' object..."

**Output**:
- Root Cause: "Missing STRIPE_API_KEY environment variable"
- Confidence: 88%
- Fix: "Set STRIPE_API_KEY in production environment"

## 🛠️ Development

### Adding New Failure Patterns

Edit `agents/deploy_failure_analyzer.py`:

```python
FAILURE_PATTERNS = {
    "your_pattern_name": {
        "keywords": ["keyword1", "keyword2"],
        "impact": "what happens to users",
        "severity": "critical|high|medium|low"
    }
}
```

### Customizing the System Prompt

Edit `_get_system_prompt()` in `agents/deploy_failure_analyzer.py` to adjust the AI's analysis approach.

## 🔒 Security Notes

- The endpoint does NOT execute code or modify deployments
- It only performs read-only analysis on provided logs
- No production credentials are stored or transmitted
- Analysis results are not persisted (stateless operation)

## 📈 Performance

- Average response time: 5-15 seconds (depends on log size and AI API latency)
- Logs are smartly truncated to prevent context overflow
- Fallback to pattern-based analysis if AI fails
- Concurrent request support via async FastAPI

## 🎯 Success Metrics

- **Confidence Score**: 0.0 - 1.0 (higher = more confident)
  - 0.7+ = High confidence (green)
  - 0.5-0.7 = Medium confidence (yellow)
  - <0.5 = Low confidence (red)

- **Pattern Detection**: Number of known patterns identified
- **Response Time**: Time to complete analysis

## 🐛 Troubleshooting

### "AI service configuration error: GROQ_API_KEY not set"
- Set `GROQ_API_KEY` in your `.env` file
- Restart the backend server

### "git_diff is required and cannot be empty"
- Ensure you're providing actual git diff content
- Check that the request body is properly formatted

### "Analysis completed in fallback mode"
- AI call failed but pattern detection succeeded
- Check backend logs for AI error details
- Verify your GROQ_API_KEY is valid

## 📚 Resources

- **Groq API Docs**: https://console.groq.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Agent Code**: [agents/deploy_failure_analyzer.py](agents/deploy_failure_analyzer.py)
- **Demo Examples**: [examples/deploy_failure_analysis_demo.py](examples/deploy_failure_analysis_demo.py)

## 🤝 Contributing

To improve the feature:
1. Add new failure patterns to the detection system
2. Enhance the SRE system prompt for better analysis
3. Add more test scenarios
4. Improve UI/UX in the frontend component

## 📝 License

Part of the CodeYogi DevOps AI Platform.

---

**Built with ❤️ for DevOps Engineers and SREs**
