# CodeYogi Backend

AI-powered agentic repository monitoring and optimization system built with FastAPI.

## Features

- 🔍 **Repository Analysis**: Comprehensive analysis of GitHub repositories
- 🛠️ **Workflow Optimization**: Automated GitHub Actions workflow optimization
- 📊 **File Analysis**: Deep code structure and pattern analysis
- 🌐 **Multi-Language Support**: Supports Python, JavaScript, Java, C++, and more
- 🚀 **SEO Optimization**: Automated GitHub repository SEO improvements
- 📝 **README Generation**: AI-powered README generation
- 🔄 **Real-time Monitoring**: Monitor repository changes and trigger optimizations
- ⏪ **Rollback Intelligence**: AI-powered deployment rollback with numbered selection and safety analysis

## Prerequisites

- Python 3.8 or higher
- Git installed on your system
- GitHub Personal Access Token (with repo permissions)
- API Keys:
  - Groq API Key (for AI analysis)
  - Google Gemini API Key (for SEO optimization)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd codeyogi-backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your API keys:
   ```env
   GITHUB_TOKEN=your_github_personal_access_token
   GH_TOKEN=your_github_personal_access_token
   GROQ_API_KEY=your_groq_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

   **Getting API Keys:**
   - **GitHub Token**: Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens) and create a new token with `repo` permissions
   - **Groq API Key**: Sign up at [Groq](https://groq.com/) and get your API key
   - **Gemini API Key**: Get your key at [Google AI Studio](https://ai.google.dev/)

## Running the Server

### Method 1: Using Python directly
```bash
python main.py
```

### Method 2: Using uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Health Check
```
GET /health
```

### Repository Analysis
```
POST /analyze-repository/
```

### GitHub Structure Analysis
```
POST /analyze-github-structure/
```

### GitHub Code Analysis
```
POST /analyze-github-code/
```

### File Analysis
```
POST /analyze-file/
```

### Workflow Optimization
```
POST /optimize-workflow-deployment/
```

### SEO Optimization
```
POST /seo/optimize
```

### README Generation
```
POST /readme/generate
```

For detailed API documentation, visit `/docs` after starting the server.

## Project Structure

```
codeyogi-backend/
├── agents/              # AI agents for various tasks
│   ├── repo_analyzer.py
│   ├── workflow_optimizer.py
│   ├── file_analyzer.py
│   ├── seo_injector.py
│   └── readme_generator.py
├── core/               # Core event management
│   └── event_manager.py
├── models/             # Pydantic models and schemas
│   ├── schemas.py
│   └── events.py
├── services/           # Business logic services
│   └── github_structure_service.py
├── utils/              # Utility functions
│   ├── github_ops.py
│   ├── pr_creator.py
│   └── file_ops.py
├── examples/           # Example usage scripts
├── main.py            # FastAPI application
└── requirements.txt   # Python dependencies
```

## Usage Examples

### Analyze a Repository
```bash
curl -X POST "http://localhost:8000/analyze-repository/" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repo",
    "github_token": "your_token"
  }'
```

### Optimize Workflow
```bash
curl -X POST "http://localhost:8000/optimize-workflow-deployment/" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repo",
    "github_token": "your_token"
  }'
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated the virtual environment and installed all dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. **API Key Errors**: Verify your `.env` file has all required API keys

3. **GitHub API Rate Limiting**: Use a Personal Access Token to increase rate limits

4. **Port Already in Use**: Change the port in the uvicorn command:
   ```bash
   uvicorn main:app --reload --port 8001
   ```

## Development

To run in development mode with auto-reload:
```bash
python main.py
```

Or:
```bash
uvicorn main:app --reload
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
