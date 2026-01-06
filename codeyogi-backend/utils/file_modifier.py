"""
File Modifier for CodeYogi - Modifies existing files instead of creating new ones
Shows red (deletions) and green (additions) in PRs
"""

import os
from typing import Dict, List, Optional, Tuple
from github import Github, GithubException
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from difflib import unified_diff
from dotenv import load_dotenv

load_dotenv()
console = Console()


class FileModifier:
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize File Modifier

        Args:
            github_token: GitHub token for authentication
        """
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GitHub token is required")

        self.github = Github(self.github_token)

    def fetch_existing_file(self, repo_name: str, file_path: str) -> Optional[str]:
        """
        Fetch existing file content from repository

        Args:
            repo_name: Repository name (owner/repo)
            file_path: Path to file in repository

        Returns:
            File content as string, or None if file doesn't exist
        """
        try:
            repo = self.github.get_repo(repo_name)
            file_content = repo.get_contents(file_path)
            
            if isinstance(file_content, list):
                console.print(f"[yellow]⚠️  {file_path} is a directory, not a file[/yellow]")
                return None
            
            return file_content.decoded_content.decode('utf-8')
        
        except GithubException as e:
            if e.status == 404:
                console.print(f"[yellow]⚠️  File not found: {file_path}[/yellow]")
                return None
            else:
                console.print(f"[red]❌ Error fetching file: {str(e)}[/red]")
                return None

    def show_diff(self, original: str, modified: str, file_path: str) -> List[str]:
        """
        Show colored diff between original and modified content

        Args:
            original: Original file content
            modified: Modified file content
            file_path: File path for display

        Returns:
            List of diff lines
        """
        # Generate unified diff
        original_lines = original.splitlines(keepends=True)
        modified_lines = modified.splitlines(keepends=True)
        
        diff = list(unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm=''
        ))

        if not diff:
            console.print(f"[yellow]⚠️  No changes detected in {file_path}[/yellow]")
            return []

        # Display diff with syntax highlighting
        console.print(Panel(f"[bold blue]Changes in {file_path}[/bold blue]"))
        
        additions = 0
        deletions = 0
        
        for line in diff[2:]:  # Skip the file headers
            if line.startswith('+') and not line.startswith('+++'):
                console.print(f"[green]{line}[/green]", end='')
                additions += 1
            elif line.startswith('-') and not line.startswith('---'):
                console.print(f"[red]{line}[/red]", end='')
                deletions += 1
            elif line.startswith('@@'):
                console.print(f"[cyan]{line}[/cyan]")
            else:
                console.print(line, end='')
        
        console.print()
        console.print(f"[green]+{additions} additions[/green] [red]-{deletions} deletions[/red]\n")
        
        return diff

    def ask_user_permission(
        self, 
        changes: Dict[str, Tuple[str, str]], 
        repo_name: str
    ) -> Dict[str, bool]:
        """
        Ask user for permission to apply changes

        Args:
            changes: Dictionary of file_path -> (original_content, modified_content)
            repo_name: Repository name

        Returns:
            Dictionary of file_path -> approved (True/False)
        """
        console.print(Panel.fit(
            f"[bold cyan]🔍 CodeYogi wants to modify {len(changes)} file(s) in {repo_name}[/bold cyan]",
            border_style="cyan"
        ))

        approved_changes = {}

        for file_path, (original, modified) in changes.items():
            console.print(f"\n[bold yellow]{'='*80}[/bold yellow]")
            
            # Show diff
            diff = self.show_diff(original, modified, file_path)
            
            if not diff:
                approved_changes[file_path] = False
                continue

            # Ask for permission
            approve = Confirm.ask(
                f"[bold]Apply these changes to {file_path}?[/bold]",
                default=True
            )
            
            approved_changes[file_path] = approve
            
            if approve:
                console.print(f"[green]✅ Approved changes for {file_path}[/green]")
            else:
                console.print(f"[red]❌ Rejected changes for {file_path}[/red]")

        # Summary
        approved_count = sum(1 for v in approved_changes.values() if v)
        console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        console.print(f"[bold]Summary:[/bold]")
        console.print(f"  ✅ Approved: {approved_count}")
        console.print(f"  ❌ Rejected: {len(approved_changes) - approved_count}")
        console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

        return approved_changes

    def prepare_modifications(
        self, 
        repo_name: str, 
        optimized_files: Dict[str, str],
        ask_permission: bool = True
    ) -> Dict[str, str]:
        """
        Prepare file modifications by fetching existing files and asking permission

        Args:
            repo_name: Repository name (owner/repo)
            optimized_files: Dictionary of file_path -> optimized_content
            ask_permission: Whether to ask user for permission

        Returns:
            Dictionary of approved file_path -> modified_content
        """
        console.print(f"\n[bold blue]🔍 Fetching existing files from {repo_name}...[/bold blue]\n")
        
        changes = {}
        files_not_found = []
        
        # Fetch existing files
        for file_path, optimized_content in optimized_files.items():
            original_content = self.fetch_existing_file(repo_name, file_path)
            
            if original_content is None:
                files_not_found.append(file_path)
                console.print(f"[yellow]⚠️  {file_path} doesn't exist - will create as new file[/yellow]")
                # For new files, we'll create them without showing diff
                changes[file_path] = (None, optimized_content)
            else:
                changes[file_path] = (original_content, optimized_content)

        # Separate existing vs new files
        existing_file_changes = {
            path: (orig, mod) for path, (orig, mod) in changes.items() if orig is not None
        }
        new_file_changes = {
            path: mod for path, (orig, mod) in changes.items() if orig is None
        }

        # Ask permission for existing file modifications
        if existing_file_changes and ask_permission:
            approved = self.ask_user_permission(existing_file_changes, repo_name)
            
            # Filter approved changes
            approved_modifications = {
                path: optimized_content 
                for path, (_, optimized_content) in existing_file_changes.items()
                if approved.get(path, False)
            }
        else:
            # If not asking permission, approve all
            approved_modifications = {
                path: mod for path, (_, mod) in existing_file_changes.items()
            }

        # Add new files (always approved)
        approved_modifications.update(new_file_changes)

        if not approved_modifications:
            console.print("[yellow]⚠️  No changes approved. PR will not be created.[/yellow]")
        else:
            console.print(f"[green]✅ {len(approved_modifications)} file(s) ready for PR[/green]")

        return approved_modifications

    def create_diff_summary(
        self, 
        original_files: Dict[str, str], 
        modified_files: Dict[str, str]
    ) -> Dict[str, Dict[str, int]]:
        """
        Create a summary of changes (additions/deletions) for each file

        Args:
            original_files: Dictionary of file_path -> original_content
            modified_files: Dictionary of file_path -> modified_content

        Returns:
            Dictionary of file_path -> {additions, deletions}
        """
        summary = {}

        for file_path, modified_content in modified_files.items():
            original_content = original_files.get(file_path, "")
            
            original_lines = original_content.splitlines() if original_content else []
            modified_lines = modified_content.splitlines()
            
            # Simple line-based diff count
            diff = list(unified_diff(
                original_lines,
                modified_lines,
                lineterm=''
            ))
            
            additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            
            summary[file_path] = {
                'additions': additions,
                'deletions': deletions,
                'net_change': additions - deletions
            }

        return summary


def test_file_modifier():
    """Test the file modifier with a sample repository"""
    console.print("[bold cyan]🧪 Testing File Modifier[/bold cyan]\n")
    
    # Example usage
    modifier = FileModifier()
    
    # Test with a sample file
    repo_name = "Park-AI-Zen/Park-AI-Zen"
    test_files = {
        ".github/workflows/ci.yml": """name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test
"""
    }
    
    # Prepare modifications
    approved_files = modifier.prepare_modifications(
        repo_name=repo_name,
        optimized_files=test_files,
        ask_permission=True
    )
    
    console.print(f"\n[green]✅ {len(approved_files)} file(s) approved for modification[/green]")
    return approved_files


if __name__ == "__main__":
    test_file_modifier()
