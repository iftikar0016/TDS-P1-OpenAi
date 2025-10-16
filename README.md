# 🚀 Web App Generator API

A FastAPI-based service that automatically generates web applications using Google's Gemini AI, deploys them to GitHub, and publishes them via GitHub Pages. Built for the TDS (Tools in Data Science) project.

## 📋 Overview

This API receives requests with application specifications, uses Gemini AI to generate complete single-file HTML applications, creates GitHub repositories, and deploys them live via GitHub Pages. It supports both initial builds and iterative revisions.

### Key Features

- 🤖 **AI-Powered Generation**: Uses Gemini 2.0 Flash to generate complete web applications
- 🔄 **Two-Round System**: Initial build (Round 1) and revision (Round 2) support
- 📦 **Automatic Deployment**: Creates repos, commits code, enables GitHub Pages
- 🔔 **Callback Notifications**: Notifies evaluation server with deployment details
- ⚡ **Background Processing**: Non-blocking async task execution
- 🔒 **Secret Authentication**: API key-based request validation

## 🛠️ Tech Stack

- **Framework**: FastAPI + Uvicorn
- **AI Model**: Google Gemini 2.0 Flash (via `google-generativeai`)
- **GitHub Integration**: PyGithub
- **HTTP Client**: httpx (for async callbacks)
- **Validation**: Pydantic v2

## 📦 Installation

### Prerequisites

- Python 3.12+
- GitHub Personal Access Token (with `repo` scope)
- Google Gemini API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd tds-p1-gemini
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   MY_SECRET=your-api-secret
   GITHUB_TOKEN=ghp_your_github_token
   GITHUB_USERNAME=your-github-username
   GEMINI_API_KEY=your-gemini-api-key
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### `POST /api-endpoint`

Main endpoint for processing web app generation requests.

#### Request Format

```json
{
  "email": "student@example.com",
  "secret": "your-api-secret",
  "task": "my-app-name",
  "round": 1,
  "nonce": "unique-correlation-id",
  "brief": "Create a calculator app with basic operations...",
  "checks": [
    "Repo has MIT license",
    "README.md is professional",
    "App is functional"
  ],
  "evaluation_url": "https://example.com/notify",
  "attachments": [
    {
      "name": "sample.png",
      "url": "data:image/png;base64,iVBORw..."
    }
  ]
}
```

#### Response

```json
{
  "status": "processing",
  "task": "my-app-name",
  "round": 1,
  "message": "Task 'my-app-name' (Round 1) accepted and processing in background"
}
```

#### Evaluation Callback

The API sends this payload to `evaluation_url`:

```json
{
  "email": "student@example.com",
  "task": "my-app-name",
  "round": 1,
  "nonce": "unique-correlation-id",
  "repo_url": "https://github.com/username/my-app-name",
  "commit_sha": "abc123...",
  "pages_url": "https://username.github.io/my-app-name/"
}
```

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
# Response: {"status": "healthy"}
```

### `GET /`

Serves the web UI (static files from `/static`).

## 🔄 Workflow

### Round 1: Initial Build

1. **Receive Request**: Validates secret and request format
2. **Generate HTML**: Calls Gemini API with brief and attachments
3. **Create Repository**: Creates public GitHub repo
4. **Commit Files**: 
   - `index.html` (generated app)
   - `LICENSE` (MIT License)
   - `README.md` (comprehensive documentation)
5. **Enable Pages**: Activates GitHub Pages on main branch
6. **Send Callback**: Notifies evaluation server with deployment details

### Round 2: Revision

1. **Receive Request**: Validates secret and request format
2. **Fetch Existing Code**: Retrieves current `index.html` from repo
3. **Generate Update**: Calls Gemini API with existing code + new requirements
4. **Update Files**:
   - `index.html` (updated app)
   - `README.md` (updated for Round 2)
5. **Send Callback**: Notifies evaluation server with new commit SHA

## 🧪 Testing

### Quick Test

```bash
# Start server
uvicorn main:app --reload

# In another terminal, run test script
./test_api.sh
```

### Manual Testing

**Round 1:**
```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d @test_round1.json
```

**Round 2:**
```bash
curl -X POST http://localhost:8000/api-endpoint \
  -H "Content-Type: application/json" \
  -d @test_round2.json
```

### Test Files Included

- `test_round1.json` - Example Round 1 request (Hello World app)
- `test_round2.json` - Example Round 2 request (adds features)
- `test_api.sh` - Automated test script

## 📚 Documentation

### Technical Docs

- **[NONCE_HANDLING.md](./NONCE_HANDLING.md)** - Detailed explanation of nonce/correlation ID handling

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ | Student/user email |
| `secret` | string | ✅ | API authentication secret |
| `task` | string | ✅ | Unique task/repo name |
| `round` | int | ✅ | Round number (1 or 2) |
| `nonce` | string | ✅ | Correlation ID for callbacks |
| `brief` | string | ✅ | Application requirements |
| `checks` | string[] | ✅ | Evaluation criteria |
| `evaluation_url` | string | ✅ | Callback URL for results |
| `attachments` | object[] | ❌ | Optional files (name + data URI) |

### Evaluation Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | User email (from request) |
| `task` | string | Task name (from request) |
| `round` | int | Round number (from request) |
| `nonce` | string | Correlation ID (from request) |
| `repo_url` | string | GitHub repository URL |
| `commit_sha` | string | Latest commit SHA |
| `pages_url` | string | Live GitHub Pages URL |

## 🔒 Security

### Authentication

- API uses secret-based authentication (`MY_SECRET` env variable)
- All requests must include matching `secret` field
- Returns `401 Unauthorized` for invalid secrets

### Environment Variables

Never commit `.env` file. Always use `.env.example` as template.

### Nonce Handling

- Nonce is a **pass-through correlation ID**
- No validation or deduplication by this API
- Evaluation server should implement nonce tracking
- See [NONCE_HANDLING.md](./NONCE_HANDLING.md) for details

## 🔧 Configuration

### Environment Variables

```env
# Required
MY_SECRET=your-api-secret                    # Request authentication
GITHUB_TOKEN=ghp_xxxxx                       # GitHub PAT with repo scope
GITHUB_USERNAME=your-username                # GitHub username
GEMINI_API_KEY=AIzaSyxxxx                   # Gemini API key

# Optional
WEBHOOK_SECRET=default_webhook_secret        # Future webhook validation
PORT=8000                                     # Server port (default: 8000)
```

### Gemini Model

Currently uses `gemini-2.0-flash-exp`. To change model, edit `main.py`:

```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Line 73
```

## �� Project Structure

```
.
├── main.py                 # FastAPI application & core logic
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── README.md             # This file
├── NONCE_HANDLING.md     # Nonce documentation
├── static/               # Web UI assets
│   ├── index.html
│   ├── script.js
│   └── style.css
├── test_round1.json      # Round 1 test request
├── test_round2.json      # Round 2 test request
└── test_api.sh           # Test automation script
```

## 🚨 Troubleshooting

### Common Issues

**401 Unauthorized**
- Check `MY_SECRET` in `.env` matches request `secret` field

**Gemini API Error**
- Verify `GEMINI_API_KEY` is valid
- Check API quota/limits

**GitHub API Error**
- Verify `GITHUB_TOKEN` has `repo` scope
- Check token hasn't expired

**Pages Not Enabled**
- GitHub Pages may take 1-2 minutes to activate
- Check repository settings manually

### Debug Mode

Run with verbose logging:
```bash
uvicorn main:app --reload --log-level debug
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ for TDS Project**
