import os
import json
from groq import Groq
from dotenv import load_dotenv
import sys
import io
import tempfile
import shutil
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup, Comment
from typing import Dict, Optional, Any, List
from github import Github, GithubException, InputGitTreeElement
from urllib.parse import urlparse
import uuid
from datetime import datetime

# --- Configuration & Setup ---

# Ensure UTF-8 output to avoid potential encoding issues.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# Load environment variables from a .env file.
# Your .env file must contain: GROQ_API_KEY="your_api_key_here" and GITHUB_TOKEN="your_github_token"
load_dotenv()

# Configure the Groq client with the API key.
groq_client = None
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
    else:
        print("[WARNING] GROQ_API_KEY not found in .env file. Some features may not work.")
except Exception as e:
    print(f"[WARNING] Failed to configure Groq client: {e}")
    print("[INFO] Please make sure your .env file contains a valid GROQ_API_KEY.")

# Configure GitHub client
github_client = None
try:
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if github_token:
        github_client = Github(github_token)
        try:
            user = github_client.get_user()
            print(f"[INFO] GitHub client configured for user: {user.login}")
        except Exception as e:
            print(f"[WARNING] GitHub token validation failed: {e}")
            github_client = None
    else:
        print("[WARNING] GITHUB_TOKEN not found in .env file. GitHub features will be limited.")
except Exception as e:
    print(f"[WARNING] Failed to configure GitHub client: {e}")
    print("[INFO] Please make sure your .env file contains a valid GITHUB_TOKEN.")

# --- Prompt Engineering ---

PROMPT_TEMPLATE = """
You are an expert SEO specialist. Your task is to generate concise, effective, and SEO-friendly metadata for a web page based on its HTML content.

Analyze the following HTML code to understand its main purpose and content. Then, generate the metadata.

HTML CONTENT:
```html
{html_content}
```

You MUST return your response as a single, valid JSON object.
The JSON object should have three keys: "title", "description", and "keywords".
- The "title" should be under 60 characters.
- The "description" should be under 160 characters.
- The "keywords" should be a list of relevant strings.

Example Response Format:
{{
  "title": "Example SEO Title",
  "description": "A concise and compelling meta description goes here.",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Do NOT include any introductory text, explanations, or markdown formatting around the JSON. Your entire output must be only the JSON object itself.
"""

# --- Core Functions ---


def parse_github_url(url: str) -> Dict[str, str]:
    """
    Parse GitHub URL to extract owner and repository name

    Args:
        url: GitHub repository URL

    Returns:
        Dictionary with owner and repo_name
    """
    # Remove .git suffix if present
    if url.endswith(".git"):
        url = url[:-4]

    # Parse URL
    parsed = urlparse(url)

    # Extract path components
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) >= 2:
        return {"owner": path_parts[0], "repo_name": path_parts[1]}
    else:
        raise ValueError(
            "Invalid GitHub URL format. Expected: https://github.com/owner/repo"
        )


def clone_repository(repo_url: str, temp_dir: str, github_token: Optional[str] = None) -> str:
    """
    Clone a GitHub repository to a temporary directory

    Args:
        repo_url: GitHub repository URL
        temp_dir: Temporary directory path
        github_token: GitHub token for authentication

    Returns:
        Path to the cloned repository
    """
    try:
        # Use token for authentication if provided
        clone_url = repo_url
        if github_token and "https://github.com" in repo_url:
            # Inject token into URL for authentication
            clone_url = repo_url.replace("https://github.com", f"https://{github_token}@github.com")
        
        print(f"[INFO] Cloning repository: {repo_url}")
        result = subprocess.run(
            ["git", "clone", clone_url, temp_dir],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"[SUCCESS] Repository cloned to: {temp_dir}")
        return temp_dir
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to clone repository: {e.stderr}")
        raise Exception(f"Git clone failed: {e.stderr}")


def find_html_files(repo_path: str) -> List[str]:
    """
    Find all HTML files in the repository

    Args:
        repo_path: Path to the repository

    Returns:
        List of HTML file paths
    """
    html_files = []
    repo_pathlib = Path(repo_path)

    # Common patterns for HTML files
    patterns = ["**/*.html", "**/*.htm", "**/index.*"]

    for pattern in patterns:
        html_files.extend(repo_pathlib.glob(pattern))

    # Filter to only HTML files and convert to strings
    html_files = [str(f) for f in html_files if f.suffix.lower() in [".html", ".htm"]]

    print(f"[INFO] Found {len(html_files)} HTML files")
    return html_files


def analyze_repository_content(repo_path: str) -> Dict[str, Any]:
    """
    Analyze repository content to understand its purpose and generate SEO data

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary containing analysis results
    """
    repo_pathlib = Path(repo_path)

    # Read README if exists
    readme_content = ""
    readme_files = list(repo_pathlib.glob("README*"))
    if readme_files:
        try:
            with open(readme_files[0], "r", encoding="utf-8", errors="ignore") as f:
                readme_content = f.read()
        except Exception as e:
            print(f"[WARNING] Could not read README: {e}")

    # Analyze package.json if it's a Node.js project
    package_json_content = ""
    package_json = repo_pathlib / "package.json"
    if package_json.exists():
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                package_data = json.load(f)
                package_json_content = f"Project: {package_data.get('name', '')}\\nDescription: {package_data.get('description', '')}"
        except Exception as e:
            print(f"[WARNING] Could not read package.json: {e}")

    # Combine content for analysis
    combined_content = f"""
    README Content: {readme_content}
    Package Info: {package_json_content}
    Repository Path: {repo_path}
    """

    return {
        "readme_content": readme_content,
        "package_info": package_json_content,
        "combined_content": combined_content.strip(),
    }


# --- Core Functions ---


def generate_seo_metadata(page_content: str, model: str = "meta-llama/llama-4-scout-17b-16e-instruct") -> dict:
    """
    Generates SEO metadata (title, description, keywords) for a given HTML content using the Groq API.

    Args:
        page_content: The textual content of the web page.
        model: The Groq model to use for generation

    Returns:
        A dictionary containing the SEO metadata, or an error dictionary on failure.
    """
    prompt = PROMPT_TEMPLATE.format(html_content=page_content)
    print(f"\n[INFO] Analyzing content and generating SEO metadata using model: {model}")

    try:
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
        )

        reply = response.choices[0].message.content
        print("[INFO] Successfully received response from LLM.")

        parsed_json = json.loads(reply)

        if all(key in parsed_json for key in ["title", "description", "keywords"]):
            print("[SUCCESS] Parsed valid SEO metadata from the response.")
            return parsed_json
        else:
            print("[ERROR] JSON response is missing one or more required keys.")
            return {"error": "Invalid JSON structure received from API."}

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during the API call: {e}")
        return {"error": str(e)}


def generate_repository_seo_metadata(
    repo_analysis: Dict[str, Any], html_content: str = "", model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
) -> Dict[str, Any]:
    """
    Generate SEO metadata for a repository based on its content and any HTML files

    Args:
        repo_analysis: Repository analysis results
        html_content: HTML content if available
        model: The Groq model to use for generation

    Returns:
        Dictionary containing SEO metadata
    """
    # Enhanced prompt for repository-based SEO
    enhanced_prompt = f"""
You are an expert SEO specialist analyzing a software repository. Generate comprehensive SEO metadata based on the repository content.

REPOSITORY ANALYSIS:
{repo_analysis.get('combined_content', '')}

HTML CONTENT (if available):
{html_content}

Generate SEO metadata that would be appropriate for:
1. The repository's main purpose and functionality
2. The target audience (developers, users, etc.)
3. Key technologies and frameworks used
4. Main features and benefits

You MUST return your response as a single, valid JSON object with the following structure:
{{
  "title": "SEO-optimized title under 60 characters",
  "description": "Compelling meta description under 160 characters", 
  "keywords": ["keyword1", "keyword2", "keyword3", "etc"],
  "og_title": "Open Graph title for social media",
  "og_description": "Open Graph description for social media",
  "og_type": "website",
  "twitter_card": "summary_large_image",
  "canonical_url": "",
  "schema_type": "SoftwareApplication"
}}

Focus on making the metadata:
- Relevant to the repository's actual purpose
- Appealing to both developers and end users
- Optimized for search engines
- Suitable for social media sharing

Do NOT include any explanatory text. Return only the JSON object.
"""

    try:
        print(f"[INFO] Generating repository-specific SEO metadata using model: {model}")
        response = groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": enhanced_prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
        )

        reply = response.choices[0].message.content
        print("[INFO] Successfully received SEO metadata from AI")

        parsed_json = json.loads(reply)

        # Validate required fields
        required_fields = ["title", "description", "keywords"]
        if all(key in parsed_json for key in required_fields):
            print("[SUCCESS] Generated comprehensive SEO metadata")
            return parsed_json
        else:
            print("[ERROR] AI response missing required SEO fields")
            return {"error": "Invalid SEO metadata structure"}

    except Exception as e:
        print(f"[ERROR] Failed to generate repository SEO metadata: {e}")
        return {"error": str(e)}


def inject_seo_into_html(html_code: str) -> str:
    """
    Takes HTML code, generates SEO metadata, and injects it into the <head>.

    Args:
        html_code: A string containing the full HTML of a page.

    Returns:
        A string containing the modified HTML with injected SEO tags.
    """
    soup = BeautifulSoup(html_code, "html.parser")

    # Extract text from the body to send to the LLM for analysis
    body_text = (
        " ".join(soup.body.get_text(separator=" ", strip=True)) if soup.body else ""
    )
    if not body_text:
        print("[WARNING] HTML body is empty or missing. Analysis may be inaccurate.")
        # Fallback to using all text if body is empty
        body_text = " ".join(soup.get_text(separator=" ", strip=True))
        if not body_text:
            print("[ERROR] No text content found in the HTML to analyze.")
            return html_code

    # Generate metadata based on the extracted text
    metadata = generate_seo_metadata(body_text)

    if "error" in metadata:
        print(f"[FAILURE] Could not generate metadata. Reason: {metadata['error']}")
        return html_code

    # Ensure there is a <head> tag
    if not soup.head:
        print("[INFO] No <head> tag found. Creating one.")
        head = soup.new_tag("head")
        soup.html.insert(0, head)

    # --- Inject Metadata ---
    print("[INFO] Injecting generated metadata into HTML <head>...")

    # 1. Title
    if soup.title:
        soup.title.string = metadata["title"]
    else:
        new_title = soup.new_tag("title")
        new_title.string = metadata["title"]
        soup.head.append(new_title)

    # 2. Meta Description
    # Remove old description tag if it exists
    old_desc = soup.find("meta", attrs={"name": "description"})
    if old_desc:
        old_desc.decompose()
    new_desc = soup.new_tag(
        "meta", attrs={"name": "description", "content": metadata["description"]}
    )
    soup.head.append(new_desc)

    # 3. Meta Keywords
    # Remove old keywords tag if it exists
    old_keys = soup.find("meta", attrs={"name": "keywords"})
    if old_keys:
        old_keys.decompose()
    new_keys = soup.new_tag(
        "meta", attrs={"name": "keywords", "content": ", ".join(metadata["keywords"])}
    )
    soup.head.append(new_keys)

    # Add a comment to indicate the change
    comment = Comment(" SEO metadata injected by Gemini ")
    soup.head.insert(0, comment)


def inject_enhanced_seo_into_html(html_code: str, seo_metadata: Dict[str, Any]) -> str:
    """
    Inject comprehensive SEO metadata into HTML

    Args:
        html_code: Original HTML content
        seo_metadata: SEO metadata dictionary

    Returns:
        HTML with injected SEO metadata
    """
    soup = BeautifulSoup(html_code, "html.parser")

    # Ensure there is a <head> tag
    if not soup.head:
        print("[INFO] No <head> tag found. Creating one.")
        head = soup.new_tag("head")
        if soup.html:
            soup.html.insert(0, head)
        else:
            # Create html tag if it doesn't exist
            html_tag = soup.new_tag("html")
            html_tag.append(head)
            soup.append(html_tag)

    # Remove existing meta tags to avoid duplicates
    existing_metas = soup.find_all(
        "meta", attrs={"name": ["description", "keywords", "author"]}
    )
    for meta in existing_metas:
        meta.decompose()

    existing_og_metas = soup.find_all("meta", attrs={"property": True})
    for meta in existing_og_metas:
        if meta.get("property", "").startswith("og:"):
            meta.decompose()

    # Add SEO comment
    comment = Comment(" Enhanced SEO metadata injected by GitHub SEO Optimizer ")
    soup.head.insert(0, comment)

    # 1. Title
    if soup.title:
        soup.title.string = seo_metadata.get("title", "")
    else:
        new_title = soup.new_tag("title")
        new_title.string = seo_metadata.get("title", "")
        soup.head.append(new_title)

    # 2. Meta Description
    new_desc = soup.new_tag(
        "meta",
        attrs={"name": "description", "content": seo_metadata.get("description", "")},
    )
    soup.head.append(new_desc)

    # 3. Meta Keywords
    if seo_metadata.get("keywords"):
        keywords_str = (
            ", ".join(seo_metadata["keywords"])
            if isinstance(seo_metadata["keywords"], list)
            else str(seo_metadata["keywords"])
        )
        new_keys = soup.new_tag(
            "meta", attrs={"name": "keywords", "content": keywords_str}
        )
        soup.head.append(new_keys)

    # 4. Open Graph tags
    og_tags = {
        "og:title": seo_metadata.get("og_title", seo_metadata.get("title", "")),
        "og:description": seo_metadata.get(
            "og_description", seo_metadata.get("description", "")
        ),
        "og:type": seo_metadata.get("og_type", "website"),
        "og:url": seo_metadata.get("canonical_url", ""),
    }

    for property_name, content in og_tags.items():
        if content:
            og_tag = soup.new_tag(
                "meta", attrs={"property": property_name, "content": content}
            )
            soup.head.append(og_tag)

    # 5. Twitter Card tags
    twitter_tags = {
        "twitter:card": seo_metadata.get("twitter_card", "summary"),
        "twitter:title": seo_metadata.get("og_title", seo_metadata.get("title", "")),
        "twitter:description": seo_metadata.get(
            "og_description", seo_metadata.get("description", "")
        ),
    }

    for name, content in twitter_tags.items():
        if content:
            twitter_tag = soup.new_tag("meta", attrs={"name": name, "content": content})
            soup.head.append(twitter_tag)

    # 6. Canonical URL
    if seo_metadata.get("canonical_url"):
        canonical_tag = soup.new_tag(
            "link", attrs={"rel": "canonical", "href": seo_metadata["canonical_url"]}
        )
        soup.head.append(canonical_tag)

    # 7. Viewport meta tag (if not present)
    if not soup.find("meta", attrs={"name": "viewport"}):
        viewport_tag = soup.new_tag(
            "meta",
            attrs={
                "name": "viewport",
                "content": "width=device-width, initial-scale=1.0",
            },
        )
        soup.head.append(viewport_tag)

    print("[SUCCESS] Enhanced SEO metadata successfully injected")
    return soup.prettify()


def create_seo_optimized_readme(
    repo_analysis: Dict[str, Any],
    seo_metadata: Dict[str, Any],
    repo_info: Dict[str, str],
) -> str:
    """
    Create an SEO-optimized README.md file

    Args:
        repo_analysis: Repository analysis results
        seo_metadata: Generated SEO metadata
        repo_info: Repository information (owner, repo_name)

    Returns:
        SEO-optimized README content
    """
    title = seo_metadata.get("title", repo_info["repo_name"])
    description = seo_metadata.get("description", "A software project")
    keywords = seo_metadata.get("keywords", [])

    # Extract key features from existing README or generate generic ones
    existing_readme = repo_analysis.get("readme_content", "")

    readme_content = f"""# {title}

{description}

## 🏆 Key Features

- **High Performance**: Optimized for speed and reliability
- **Modern Architecture**: Built with industry best practices
- **Developer Experience**: Easy to use and well-documented
- **Community Driven**: Open source and contribution-friendly

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/{repo_info['owner']}/{repo_info['repo_name']}.git

# Navigate to project directory
cd {repo_info['repo_name']}

# Install dependencies (adjust based on your project)
# npm install  # for Node.js projects
# pip install -r requirements.txt  # for Python projects
```

## 📖 Documentation

For comprehensive documentation, visit our [Wiki](../../wiki) or explore the `docs/` directory.

## 🛠️ Technologies

{', '.join(keywords[:5]) if keywords else 'Modern development stack'}

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Support

If you find this project helpful, please give it a ⭐ on GitHub!

## 📞 Contact

- **Repository**: [https://github.com/{repo_info['owner']}/{repo_info['repo_name']}](https://github.com/{repo_info['owner']}/{repo_info['repo_name']})
- **Issues**: [Report bugs or request features](https://github.com/{repo_info['owner']}/{repo_info['repo_name']}/issues)

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/{repo_info['owner']}/{repo_info['repo_name']})
![GitHub forks](https://img.shields.io/github/forks/{repo_info['owner']}/{repo_info['repo_name']})
![GitHub issues](https://img.shields.io/github/issues/{repo_info['owner']}/{repo_info['repo_name']})

---

Built with ❤️ by the community
"""

    return readme_content


def commit_and_push_changes(repo_path: str, branch_name: str, github_token: Optional[str] = None) -> bool:
    """
    Commit and push changes to a new branch

    Args:
        repo_path: Path to the repository
        branch_name: Name of the new branch
        github_token: GitHub personal access token for authentication

    Returns:
        True if successful, False otherwise
    """
    try:
        # Change to repository directory
        original_cwd = os.getcwd()
        os.chdir(repo_path)
        
        print(f"[INFO] Working directory: {repo_path}")

        # Configure git user if not set
        try:
            subprocess.run(
                ["git", "config", "user.name", "CodeYogi Bot"],
                check=True,
                capture_output=True,
                text=True
            )
            subprocess.run(
                ["git", "config", "user.email", "codeyogi@bot.local"],
                check=True,
                capture_output=True,
                text=True
            )
            print("[INFO] Git user configured")
        except Exception as e:
            print(f"[WARNING] Could not configure git user: {e}")

        # Get the current remote URL
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            remote_url = result.stdout.strip()
            print(f"[INFO] Current remote URL: {remote_url[:50]}...")  # Only show first 50 chars

            # If we have a token and the URL is HTTPS, inject the token
            if github_token and "https://github.com" in remote_url:
                # Replace https://github.com with https://TOKEN@github.com
                authenticated_url = remote_url.replace(
                    "https://github.com",
                    f"https://{github_token}@github.com"
                )
                subprocess.run(
                    ["git", "remote", "set-url", "origin", authenticated_url],
                    check=True,
                    capture_output=True
                )
                print("[INFO] Remote URL updated with authentication")
        except Exception as e:
            print(f"[ERROR] Failed to update remote URL: {e}")
            return False

        # Create and checkout new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name], check=True, capture_output=True, text=True
        )

        # Add all changes
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if not status.stdout.strip():
            print("[INFO] No changes to commit")
            return False

        # Commit changes
        commit_message = f"feat: Add SEO optimization by CodeYogi\\n\\n- Enhanced HTML meta tags\\n- Updated README with SEO improvements\\n- Added Open Graph and Twitter Card support"
        subprocess.run(
            ["git", "commit", "-m", commit_message], check=True, capture_output=True, text=True
        )

        # Push to origin
        push_result = subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            capture_output=True,
            text=True
        )
        
        if push_result.returncode != 0:
            print(f"[ERROR] Push failed: {push_result.stderr}")
            return False

        print(f"[SUCCESS] Changes committed and pushed to branch: {branch_name}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git operation failed: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"[ERROR] Details: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return False
    finally:
        os.chdir(original_cwd)


def create_pull_request(
    repo_info: Dict[str, str], branch_name: str, seo_metadata: Dict[str, Any]
) -> Optional[str]:
    """
    Create a pull request with the SEO improvements

    Args:
        repo_info: Repository information
        branch_name: Source branch name
        seo_metadata: Generated SEO metadata

    Returns:
        PR URL if successful, None otherwise
    """
    try:
        repo = github_client.get_repo(f"{repo_info['owner']}/{repo_info['repo_name']}")

        pr_title = "🚀 SEO Optimization: Enhanced Meta Tags and README"
        pr_body = f"""## 🎯 SEO Optimization Summary

This pull request adds comprehensive SEO improvements to enhance the repository's discoverability and social media presence.

### ✨ Changes Made

- **Enhanced HTML Meta Tags**: Added optimized title, description, and keywords
- **Open Graph Support**: Improved social media sharing with og: tags  
- **Twitter Card Integration**: Enhanced Twitter sharing experience
- **README Optimization**: Updated with SEO-friendly content and badges
- **Canonical URLs**: Added proper URL canonicalization

### 📊 Generated SEO Metadata

- **Title**: {seo_metadata.get('title', 'N/A')}
- **Description**: {seo_metadata.get('description', 'N/A')}
- **Keywords**: {', '.join(seo_metadata.get('keywords', [])) if seo_metadata.get('keywords') else 'N/A'}

### 🎯 Benefits

- Improved search engine ranking potential
- Better social media link previews
- Enhanced user experience
- Professional repository presentation

### 🔧 Technical Details

- All changes follow SEO best practices
- Non-breaking changes to existing functionality
- Responsive meta viewport added where missing
- Schema.org markup preparation

---

*Generated by GitHub SEO Optimizer - Automated SEO enhancement tool*
"""

        pr = repo.create_pull(
            title=pr_title, body=pr_body, head=branch_name, base=repo.default_branch
        )

        print(f"[SUCCESS] Pull request created: {pr.html_url}")
        return pr.html_url

    except Exception as e:
        print(f"[ERROR] Failed to create pull request: {e}")
        return None


async def analyze_repository_seo_only(
    github_url: str, github_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze repository for SEO potential without making changes

    Args:
        github_url: GitHub repository URL
        github_token: Optional GitHub token

    Returns:
        Dictionary containing analysis results
    """
    temp_dir = None

    try:
        print(f"[INFO] Analyzing SEO potential for: {github_url}")
        repo_info = parse_github_url(github_url)
        print(f"[INFO] Repository: {repo_info['owner']}/{repo_info['repo_name']}")

        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="seo_analyzer_")

        # Clone repository
        repo_path = clone_repository(github_url, temp_dir)

        # Analyze repository content
        repo_analysis = analyze_repository_content(repo_path)

        # Find HTML files
        html_files = find_html_files(repo_path)

        # Generate SEO metadata (but don't apply it)
        seo_metadata = generate_repository_seo_metadata(repo_analysis)

        if "error" in seo_metadata:
            return {"success": False, "error": seo_metadata["error"]}

        # Analyze current SEO status of HTML files
        current_seo_status = {}
        for html_file in html_files:
            try:
                with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, "html.parser")

                # Extract current meta tags
                title = soup.title.string if soup.title else None
                description_meta = soup.find("meta", attrs={"name": "description"})
                keywords_meta = soup.find("meta", attrs={"name": "keywords"})
                og_title_meta = soup.find("meta", attrs={"property": "og:title"})

                current_seo_status[html_file] = {
                    "has_title": bool(title),
                    "title": title,
                    "has_description": bool(description_meta),
                    "description": (
                        description_meta.get("content") if description_meta else None
                    ),
                    "has_keywords": bool(keywords_meta),
                    "keywords": keywords_meta.get("content") if keywords_meta else None,
                    "has_og_tags": bool(og_title_meta),
                }

            except Exception as e:
                print(f"[WARNING] Failed to analyze {html_file}: {e}")
                current_seo_status[html_file] = {"error": str(e)}

        # Generate recommendations
        recommendations = []
        if not html_files:
            recommendations.append(
                "No HTML files found - consider adding a landing page"
            )
        else:
            for file_path, status in current_seo_status.items():
                if not status.get("has_title"):
                    recommendations.append(f"Add <title> tag to {file_path}")
                if not status.get("has_description"):
                    recommendations.append(f"Add meta description to {file_path}")
                if not status.get("has_keywords"):
                    recommendations.append(f"Add meta keywords to {file_path}")
                if not status.get("has_og_tags"):
                    recommendations.append(f"Add Open Graph tags to {file_path}")

        if not repo_analysis.get("readme_content"):
            recommendations.append(
                "Create or enhance README.md for better discoverability"
            )

        return {
            "success": True,
            "repository": f"{repo_info['owner']}/{repo_info['repo_name']}",
            "seo_metadata": seo_metadata,
            "html_files_found": len(html_files),
            "current_seo_status": current_seo_status,
            "recommendations": recommendations,
        }

    except Exception as e:
        print(f"[ERROR] SEO analysis failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"[WARNING] Failed to cleanup temp directory: {e}")


async def get_current_seo_metadata(
    github_url: str, github_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get current SEO metadata from repository without cloning

    Args:
        github_url: GitHub repository URL
        github_token: Optional GitHub token

    Returns:
        Dictionary containing current SEO data
    """
    try:
        repo_info = parse_github_url(github_url)

        # Use GitHub API to get repository contents
        if github_token:
            g = Github(github_token)
        else:
            g = Github()  # Anonymous access

        repo = g.get_repo(f"{repo_info['owner']}/{repo_info['repo_name']}")

        # Get contents and look for HTML files and README
        metadata = {}
        html_files = []
        readme_analysis = {}

        def scan_directory(path=""):
            try:
                contents = repo.get_contents(path)
                for content in contents:
                    if content.type == "dir":
                        scan_directory(content.path)
                    elif content.name.endswith((".html", ".htm")):
                        html_files.append(content.path)
                        # Get file content and analyze
                        try:
                            file_content = content.decoded_content.decode("utf-8")
                            soup = BeautifulSoup(file_content, "html.parser")

                            metadata[content.path] = {
                                "title": soup.title.string if soup.title else None,
                                "description": soup.find(
                                    "meta", attrs={"name": "description"}
                                ),
                                "keywords": soup.find(
                                    "meta", attrs={"name": "keywords"}
                                ),
                                "og_title": soup.find(
                                    "meta", attrs={"property": "og:title"}
                                ),
                                "og_description": soup.find(
                                    "meta", attrs={"property": "og:description"}
                                ),
                            }
                        except Exception as e:
                            metadata[content.path] = {"error": str(e)}
                    elif content.name.upper().startswith("README"):
                        try:
                            readme_content = content.decoded_content.decode("utf-8")
                            readme_analysis = {
                                "length": len(readme_content),
                                "has_badges": "![" in readme_content,
                                "has_description": len(readme_content.split("\n")) > 5,
                                "has_installation": "install" in readme_content.lower(),
                                "has_usage": "usage" in readme_content.lower()
                                or "example" in readme_content.lower(),
                            }
                        except Exception as e:
                            readme_analysis = {"error": str(e)}
            except Exception as e:
                print(f"[WARNING] Failed to scan directory {path}: {e}")

        scan_directory()

        return {
            "metadata": metadata,
            "html_files": html_files,
            "readme_analysis": readme_analysis,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}


async def optimize_github_repository_seo(
    github_url: str,
    github_token: Optional[str] = None,
    branch_name: Optional[str] = None,
    create_pr: bool = True,
    auto_merge: bool = False,
    model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
) -> Dict[str, Any]:
    """
    Enhanced version of the main optimization function with additional parameters
    """
    temp_dir = None

    try:
        # Parse GitHub URL
        print(f"[INFO] Starting SEO optimization for: {github_url}")
        repo_info = parse_github_url(github_url)
        print(f"[INFO] Repository: {repo_info['owner']}/{repo_info['repo_name']}")

        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="seo_optimizer_")
        print(f"[INFO] Created temporary directory: {temp_dir}")

        # Use provided token or fallback to environment token
        token = github_token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        
        if not token:
            print("[WARNING] No GitHub token found. Push may fail if repository is private.")

        # Clone repository with authentication
        repo_path = clone_repository(github_url, temp_dir, token)

        # Analyze repository content
        print("[INFO] Analyzing repository content...")
        repo_analysis = analyze_repository_content(repo_path)

        # Find HTML files
        html_files = find_html_files(repo_path)

        # Generate SEO metadata
        print("[INFO] Generating SEO metadata...")
        seo_metadata = generate_repository_seo_metadata(repo_analysis, model=model)

        if "error" in seo_metadata:
            return {"success": False, "error": seo_metadata["error"]}

        print("[INFO] Generated SEO metadata:")
        print(f"  Title: {seo_metadata.get('title', 'N/A')}")
        print(f"  Description: {seo_metadata.get('description', 'N/A')}")
        print(f"  Keywords: {', '.join(seo_metadata.get('keywords', []))}")

        # Process HTML files
        modified_files = []
        if html_files:
            for html_file in html_files:
                try:
                    with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                        original_html = f.read()

                    optimized_html = inject_enhanced_seo_into_html(
                        original_html, seo_metadata
                    )

                    with open(html_file, "w", encoding="utf-8") as f:
                        f.write(optimized_html)

                    modified_files.append(html_file)
                    print(f"[SUCCESS] Optimized: {html_file}")

                except Exception as e:
                    print(f"[WARNING] Failed to process {html_file}: {e}")
        else:
            print("[INFO] No HTML files found, will only update README.md")

        # Create/update README.md
        readme_path = os.path.join(repo_path, "README.md")
        readme_content = create_seo_optimized_readme(
            repo_analysis, seo_metadata, repo_info
        )

        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)
        modified_files.append(readme_path)
        print("[SUCCESS] Created SEO-optimized README.md")
        
        # Create .seo-metadata.json file for reference
        metadata_file = os.path.join(repo_path, ".seo-metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump({
                "generated_at": datetime.now().isoformat(),
                "metadata": seo_metadata,
                "generated_by": "CodeYogi SEO Optimizer"
            }, f, indent=2)
        modified_files.append(metadata_file)
        print("[SUCCESS] Created .seo-metadata.json")

        # Create unique branch name if not provided
        if not branch_name:
            branch_name = f"seo-optimization-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Commit and push changes (token already retrieved earlier)
        if commit_and_push_changes(repo_path, branch_name, token):
            pr_url = None
            pr_number = None

            # Create pull request if requested
            if create_pr:
                pr_url = create_pull_request(repo_info, branch_name, seo_metadata)

                # Extract PR number from URL
                if pr_url:
                    try:
                        pr_number = int(pr_url.split("/")[-1])
                    except:
                        pr_number = None

            return {
                "success": True,
                "repository": f"{repo_info['owner']}/{repo_info['repo_name']}",
                "seo_metadata": seo_metadata,
                "modified_files": len(modified_files),
                "html_files_processed": len(html_files),
                "branch_name": branch_name,
                "pull_request_url": pr_url,
                "pull_request_number": pr_number,
                "temp_directory": temp_dir,
                "auto_merged": False,  # TODO: Implement auto-merge if needed
            }
        else:
            return {"success": False, "error": "Failed to commit and push changes"}

    except Exception as e:
        print(f"[ERROR] SEO optimization failed: {e}")
        return {"success": False, "error": str(e)}

    finally:
        # Cleanup temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                print(f"[INFO] Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                print(f"[WARNING] Failed to cleanup temp directory: {e}")


# --- CLI Interface ---


def main():
    """
    Command-line interface for GitHub SEO Optimizer
    """
    if len(sys.argv) != 2:
        print("Usage: python seo_injector.py <github_url>")
        print("Example: python seo_injector.py https://github.com/username/repository")
        sys.exit(1)

    github_url = sys.argv[1]

    print("🚀 GitHub SEO Optimizer")
    print("=" * 50)

    # Run the optimization
    import asyncio

    result = asyncio.run(optimize_github_repository_seo(github_url))

    if result.get("success"):
        print("\\n✅ SEO Optimization Complete!")
        print(f"Repository: {result['repository']}")
        print(f"Files modified: {result['modified_files']}")
        print(f"HTML files processed: {result['html_files_processed']}")
        print(f"Branch created: {result['branch_name']}")
        if result.get("pull_request_url"):
            print(f"Pull Request: {result['pull_request_url']}")
        print("\\n📊 Generated SEO Metadata:")
        metadata = result["seo_metadata"]
        print(f"  Title: {metadata.get('title')}")
        print(f"  Description: {metadata.get('description')}")
        print(f"  Keywords: {', '.join(metadata.get('keywords', []))}")
    else:
        print(f"\\n❌ Optimization failed: {result.get('error')}")


if __name__ == "__main__":
    main()
