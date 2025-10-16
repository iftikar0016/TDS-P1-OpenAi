import os
import time
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from github import Github, GithubException
# import google.generativeai as genai
import httpx
from models import TaskRequest, EvaluationPayload
import openai

# Load environment variables
load_dotenv()

# Configuration
class Settings(BaseSettings):
    MY_SECRET: str
    GITHUB_TOKEN: str
    GITHUB_USERNAME: str
    AIPIPE_TOKEN: str
    OPENAI_BASE_URL: str = "https://aipipe.org/openrouter/v1"
    WEBHOOK_SECRET: str = "default_webhook_secret"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Initialize FastAPI app
app = FastAPI(title="Web App Generator API")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure OpenAI client to use AI Pipe proxy
client = openai.OpenAI(api_key=settings.AIPIPE_TOKEN, base_url=settings.OPENAI_BASE_URL)

# Initialize GitHub client
github_client = Github(settings.GITHUB_TOKEN)


def generate_html_with_gemini(brief: str, attachments: list = None, existing_code: str = None) -> str:
    """Generate or revise HTML application using Gemini API."""
    
    if existing_code:
        # Round 2: Revision prompt
        prompt = f"""Given the current code below, update the application to satisfy this new requirement: {brief}

Current code:
{existing_code}

Please provide the complete updated HTML file with all HTML, CSS, and JavaScript in a single file. The application should be fully functional and self-contained."""
    else:
        # Round 1: Initial generation prompt
        prompt = f"""Create a fully functional single-file HTML web application based on the following brief:

{brief}

Requirements:
- Create a complete, self-contained HTML file (index.html)
- Include all HTML, CSS (in <style> tags), and JavaScript (in <script> tags) in one file
- The application should be fully functional and ready to deploy
- Use modern web standards and best practices
- Make it visually appealing and user-friendly
"""
        
        if attachments:
            attachment_info = "\n".join([f"- {att.name}: {att.url}" for att in attachments])
            prompt += f"\n\nAdditional context/attachments:\n{attachment_info}"
    
    try:
        # Send prompt via AI Pipe proxy using new OpenAI client
        resp = client.responses.create(
            model="openai/gpt-5-nano",
            input=prompt
        )
        # Extract the text content from the Response object
        html_content = resp.output_text
        
        # Clean up markdown code blocks if present
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()
        
        return html_content
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


def create_readme_content(task: str, brief: str, round_num: int = 1) -> str:
    """Generate comprehensive README content."""
    
    readme = f"""# {task}

## Summary
This web application was generated to fulfill the following requirement:

{brief}

## Setup
This is a static web application that requires no installation. Simply open `index.html` in a web browser.

## Usage
1. Clone this repository
2. Open `index.html` in your web browser
3. The application is ready to use

## Code Explanation
This application is built as a single-file HTML application containing:
- **HTML Structure**: The core markup and content
- **CSS Styling**: Embedded styles for visual presentation
- **JavaScript Logic**: Client-side functionality and interactivity

All components are contained within the `index.html` file for easy deployment and portability.

## Deployment
This application is deployed via GitHub Pages and is accessible at the Pages URL provided in the repository settings.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Generated on {datetime.now().strftime('%Y-%m-%d')} - Round {round_num}*
"""
    
    return readme


def create_mit_license(github_username: str) -> str:
    """Generate MIT License content."""
    
    year = datetime.now().year
    
    license_text = f"""MIT License

Copyright (c) {year} {github_username}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    
    return license_text


async def send_evaluation_with_retry(evaluation_url: str, payload: dict, timeout_minutes: int = 10):
    """Send evaluation payload with exponential backoff retry mechanism."""
    
    deadline = datetime.now() + timedelta(minutes=timeout_minutes)
    retry_delay = 1  # Start with 1 second
    max_retry_delay = 60  # Cap at 60 seconds
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while datetime.now() < deadline:
            try:
                response = await client.post(
                    evaluation_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print(f"✓ Successfully notified evaluation server: {response.status_code}")
                    return True
                else:
                    print(f"✗ Evaluation server returned {response.status_code}: {response.text}")
                    
            except Exception as e:
                print(f"✗ Error sending evaluation: {str(e)}")
            
            # Calculate time remaining
            time_remaining = (deadline - datetime.now()).total_seconds()
            
            if time_remaining <= 0:
                print("✗ Timeout reached, stopping retries")
                break
            
            # Wait before retry (exponential backoff)
            wait_time = min(retry_delay, time_remaining)
            print(f"⟳ Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            
            # Exponential backoff
            retry_delay = min(retry_delay * 2, max_retry_delay)
    
    print("✗ Failed to notify evaluation server within timeout period")
    return False


async def process_task_round_1(request: TaskRequest):
    """Process Round 1: Initial Build & Deployment."""
    
    print(f"\n{'='*60}")
    print(f"ROUND 1: Initial Build & Deployment")
    print(f"Task: {request.task}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Generate HTML with Gemini
        print("→ Generating HTML application with Gemini API...")
        html_content = generate_html_with_gemini(request.brief, request.attachments)
        print(f"✓ Generated {len(html_content)} characters of HTML")
        
        # Step 2: Create GitHub repository
        print(f"\n→ Creating GitHub repository: {request.task}")
        user = github_client.get_user()
        
        try:
            repo = user.create_repo(
                name=request.task,
                description=f"Web application: {request.brief[:100]}...",
                private=False,
                auto_init=False
            )
            print(f"✓ Repository created: {repo.html_url}")
        except GithubException as e:
            if e.status == 422:  # Repository already exists
                print(f"! Repository already exists, fetching existing repo...")
                repo = user.get_repo(request.task)
            else:
                raise
        
        # Step 3: Create and commit files
        print("\n→ Committing files to repository...")
        
        # Commit index.html
        try:
            index_file = repo.get_contents("index.html", ref="main")
            repo.update_file(
                path="index.html",
                message="Update index.html",
                content=html_content,
                sha=index_file.sha,
                branch="main"
            )
            print("✓ Updated index.html")
        except:
            repo.create_file(
                path="index.html",
                message="Initial commit: Add index.html",
                content=html_content,
                branch="main"
            )
            print("✓ Committed index.html")
        
        # Commit LICENSE
        license_content = create_mit_license(settings.GITHUB_USERNAME)
        try:
            license_file = repo.get_contents("LICENSE", ref="main")
            repo.update_file(
                path="LICENSE",
                message="Update LICENSE",
                content=license_content,
                sha=license_file.sha,
                branch="main"
            )
            print("✓ Updated LICENSE")
        except:
            repo.create_file(
                path="LICENSE",
                message="Add MIT License",
                content=license_content,
                branch="main"
            )
            print("✓ Committed LICENSE")
        
        # Commit README.md
        readme_content = create_readme_content(request.task, request.brief, round_num=1)
        try:
            readme_file = repo.get_contents("README.md", ref="main")
            readme_commit = repo.update_file(
                path="README.md",
                message="Update README",
                content=readme_content,
                sha=readme_file.sha,
                branch="main"
            )
            commit_sha = readme_commit['commit'].sha
            print(f"✓ Updated README.md (SHA: {commit_sha[:7]})")
        except:
            readme_commit = repo.create_file(
                path="README.md",
                message="Add comprehensive README",
                content=readme_content,
                branch="main"
            )
            commit_sha = readme_commit['commit'].sha
            print(f"✓ Committed README.md (SHA: {commit_sha[:7]})")
        
        # Step 4: Enable GitHub Pages
        print("\n→ Enabling GitHub Pages...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.github.com/repos/{settings.GITHUB_USERNAME}/{request.task}/pages",
                    headers={
                        "Authorization": f"token {settings.GITHUB_TOKEN}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={"source": {"branch": "main", "path": "/"}}
                )
                if response.status_code == 201:
                    print("✓ GitHub Pages enabled")
                elif response.status_code == 409:
                    print("! GitHub Pages already enabled")
                else:
                    print(f"✗ Warning: Could not enable Pages (status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"✗ Warning: Could not enable Pages: {e}")
        
        # Calculate Pages URL
        pages_url = f"https://{settings.GITHUB_USERNAME}.github.io/{request.task}/"
        print(f"✓ Pages URL: {pages_url}")
        
        # Step 5: Send evaluation payload
        print("\n→ Sending evaluation to server...")
        evaluation_payload = EvaluationPayload(
            email=request.email,
            task=request.task,
            round=1,
            nonce=request.nonce,
            repo_url=repo.html_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        await send_evaluation_with_retry(
            request.evaluation_url,
            evaluation_payload.model_dump()
        )
        
        print(f"\n{'='*60}")
        print(f"ROUND 1 COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ ERROR in Round 1: {str(e)}")
        raise


async def process_task_round_2(request: TaskRequest):
    """Process Round 2: Revision & Update."""
    
    print(f"\n{'='*60}")
    print(f"ROUND 2: Revision & Update")
    print(f"Task: {request.task}")
    print(f"{'='*60}\n")
    
    try:
        # Step 1: Retrieve existing repository and code
        print(f"→ Fetching repository: {request.task}")
        user = github_client.get_user()
        repo = user.get_repo(request.task)
        print(f"✓ Repository found: {repo.html_url}")
        
        # Get current index.html
        print("\n→ Retrieving current index.html...")
        index_file = repo.get_contents("index.html", ref="main")
        existing_html = index_file.decoded_content.decode('utf-8')
        print(f"✓ Retrieved {len(existing_html)} characters")
        
        # Step 2: Generate updated HTML with Gemini
        print("\n→ Generating updated HTML with Gemini API...")
        updated_html = generate_html_with_gemini(
            request.brief,
            request.attachments,
            existing_code=existing_html
        )
        print(f"✓ Generated {len(updated_html)} characters of updated HTML")
        
        # Step 3: Update files in repository
        print("\n→ Updating files in repository...")
        
        # Update index.html
        repo.update_file(
            path="index.html",
            message=f"Round 2: Update application - {request.brief[:50]}...",
            content=updated_html,
            sha=index_file.sha,
            branch="main"
        )
        print("✓ Updated index.html")
        
        # Update README.md
        readme_content = create_readme_content(request.task, request.brief, round_num=2)
        readme_file = repo.get_contents("README.md", ref="main")
        readme_commit = repo.update_file(
            path="README.md",
            message="Update README for Round 2",
            content=readme_content,
            sha=readme_file.sha,
            branch="main"
        )
        commit_sha = readme_commit['commit'].sha
        print(f"✓ Updated README.md (SHA: {commit_sha[:7]})")
        
        # Calculate Pages URL
        pages_url = f"https://{settings.GITHUB_USERNAME}.github.io/{request.task}/"
        
        # Step 4: Send evaluation payload
        print("\n→ Sending evaluation to server...")
        evaluation_payload = EvaluationPayload(
            email=request.email,
            task=request.task,
            round=2,
            nonce=request.nonce,
            repo_url=repo.html_url,
            commit_sha=commit_sha,
            pages_url=pages_url
        )
        
        await send_evaluation_with_retry(
            request.evaluation_url,
            evaluation_payload.model_dump()
        )
        
        print(f"\n{'='*60}")
        print(f"ROUND 2 COMPLETED SUCCESSFULLY")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ ERROR in Round 2: {str(e)}")
        raise


async def process_task(request: TaskRequest):
    """Main task processing function that routes to Round 1 or Round 2."""
    
    try:
        if request.round == 1:
            await process_task_round_1(request)
        elif request.round == 2:
            await process_task_round_2(request)
        else:
            print(f"✗ Invalid round number: {request.round}")
            
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


@app.post("/api-endpoint")
async def api_endpoint(request: TaskRequest, background_tasks: BackgroundTasks):
    """Main API endpoint for receiving evaluation requests."""
    
    # Authentication check
    if request.secret != settings.MY_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Add background task
    background_tasks.add_task(process_task, request)
    
    # Return immediate response
    return {
        "status": "processing",
        "task": request.task,
        "round": request.round,
        "message": f"Task '{request.task}' (Round {request.round}) accepted and processing in background"
    }


@app.get("/")
async def root():
    """Serve the web UI."""
    return FileResponse("static/index.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
