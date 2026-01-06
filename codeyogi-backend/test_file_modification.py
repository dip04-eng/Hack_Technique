"""
Test script for CodeYogi File Modification PR Creator
Shows red (deletions) and green (additions) in PRs
Asks user for permission before creating PR
"""

import os
import sys
from dotenv import load_dotenv
from utils.pr_creator import GitHubPRCreator
from rich.console import Console

load_dotenv()
console = Console()


def test_file_modification_pr():
    """
    Test creating a PR that modifies existing files
    This will show RED lines (deletions) and GREEN lines (additions)
    """
    
    console.print("\n[bold cyan]" + "="*80 + "[/bold cyan]")
    console.print("[bold cyan]🧪 CodeYogi File Modification PR Test[/bold cyan]")
    console.print("[bold cyan]" + "="*80 + "[/bold cyan]\n")

    # Initialize PR creator
    try:
        pr_creator = GitHubPRCreator()
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize: {str(e)}[/red]")
        return

    # Test repository
    repo_name = "Park-AI-Zen/Park-AI-Zen"  # Change to your repo
    
    # Files to modify (these should exist in your repo)
    files_to_modify = {
        # Example 1: Optimize GitHub Actions workflow
        ".github/workflows/ci.yml": """name: CI/CD Pipeline
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 1  # Shallow clone for faster checkout
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'  # Enable npm caching
      
      - name: Install dependencies
        run: npm ci  # Use ci instead of install for faster, reproducible builds
      
      - name: Run linter
        run: npm run lint
      
      - name: Run tests
        run: npm test -- --coverage
        env:
          NODE_ENV: test
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: success()
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false

  build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build project
        run: npm run build
      
      - name: Archive production artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build-artifacts
          path: dist/
          retention-days: 7
""",

        # Example 2: Optimize package.json (if it exists)
        "package.json": """{
  "name": "optimized-project",
  "version": "2.0.0",
  "description": "Optimized by CodeYogi AI",
  "main": "index.js",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest --coverage --maxWorkers=50%",
    "test:watch": "jest --watch",
    "lint": "eslint . --ext .js,.jsx,.ts,.tsx --cache",
    "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
    "build": "webpack --mode production",
    "clean": "rm -rf dist node_modules"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  },
  "dependencies": {
    "express": "^4.18.2",
    "dotenv": "^16.3.1"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "eslint": "^8.54.0",
    "nodemon": "^3.0.2",
    "webpack": "^5.89.0"
  }
}
""",

        # Example 3: Add optimized .env.example
        ".env.example": """# Application Configuration
NODE_ENV=production
PORT=3000

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=

# API Keys (fill in your actual keys)
API_KEY=
API_SECRET=

# Logging
LOG_LEVEL=info
LOG_FILE=./logs/app.log

# Feature Flags
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
""",
    }

    console.print(f"[bold]Target Repository:[/bold] {repo_name}")
    console.print(f"[bold]Files to modify:[/bold] {len(files_to_modify)}")
    for file_path in files_to_modify.keys():
        console.print(f"  - {file_path}")
    console.print()

    # Create the PR (will ask for permission)
    result = pr_creator.create_modification_pr(
        repo_name=repo_name,
        files_to_modify=files_to_modify,
        pr_title="🚀 CodeYogi: Optimize Project Configuration",
        pr_description="""This PR optimizes your project configuration for better performance:

- **Workflow optimization:** Added caching, parallel jobs, and shallow clones
- **Package.json:** Updated scripts for better performance and caching
- **Environment template:** Added comprehensive .env.example file

All changes were reviewed and approved.""",
        ask_permission=True  # Will show diffs and ask for approval
    )

    # Display result
    console.print("\n[bold cyan]" + "="*80 + "[/bold cyan]")
    console.print("[bold cyan]📊 Result Summary[/bold cyan]")
    console.print("[bold cyan]" + "="*80 + "[/bold cyan]\n")

    if result["success"]:
        console.print("[green]✅ PR Created Successfully![/green]\n")
        console.print(f"[bold]PR Number:[/bold] #{result['pr_number']}")
        console.print(f"[bold]PR URL:[/bold] {result['pr_url']}")
        console.print(f"[bold]Branch:[/bold] {result['branch_name']}")
        console.print(f"[bold]Files Modified:[/bold] {result['files_modified']}")
        
        if 'diff_summary' in result:
            console.print("\n[bold]Changes per file:[/bold]")
            for file_path, stats in result['diff_summary'].items():
                console.print(f"  {file_path}:")
                console.print(f"    [green]+{stats['additions']} additions[/green]")
                console.print(f"    [red]-{stats['deletions']} deletions[/red]")
        
        console.print(f"\n[bold green]🎉 Check your PR at:[/bold green]")
        console.print(f"[link]{result['pr_url']}[/link]")
        console.print("\n[yellow]You will see RED lines (deletions) and GREEN lines (additions)![/yellow]")
    else:
        console.print(f"[red]❌ Failed:[/red] {result.get('error', 'Unknown error')}")
        console.print(f"[yellow]Message:[/yellow] {result.get('message', 'N/A')}")


if __name__ == "__main__":
    console.print("\n[bold yellow]⚠️  IMPORTANT:[/bold yellow]")
    console.print("1. This will create a REAL PR in your repository")
    console.print("2. You will be asked to approve each file change")
    console.print("3. Only approved changes will be included in the PR")
    console.print("4. The PR will show RED (deletions) and GREEN (additions)\n")
    
    input("Press ENTER to continue or CTRL+C to cancel...")
    
    test_file_modification_pr()
