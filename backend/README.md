# User Story Generator & GitHub QC Integration

AI-powered user story generator component for the project management system with automated GitHub quality control integration.

## Features

- **AI-Powered Generation**: Uses Google Gemini API for intelligent user story creation
- **User Persona Generation**: Automatically creates user personas based on requirements
- **INVEST Compliance**: Ensures stories are Independent, Negotiable, Valuable, Estimable, Small, and Testable
- **Structured Output**: Returns well-formatted user stories with acceptance criteria and story points
- **Data Validation**: Uses Pydantic models for robust data validation
- **Error Handling**: Comprehensive error handling for API failures and data issues
- **GitHub Integration**: Automated QC analysis of pull requests via webhooks

## GitHub QC Integration

The system includes automated quality control analysis for code submissions via GitHub webhooks.

### Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Environment Variables** (add to `.env`):
```bash
# Existing variables
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# GitHub Integration
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret_from_github
```

## GitHub Integration Setup

### Option 1: Individual Repository Webhooks (Current - Simple)
For each repository, go to:
- **Settings** → **Webhooks** → **Add webhook**
- **Payload URL**: `https://your-domain.com/api/github-webhook`
- **Content type**: `application/json`
- **Secret**: Your `GITHUB_WEBHOOK_SECRET`
- **Events**: Select "Pull requests"

**Pros**: Simple, works immediately
**Cons**: Manual setup for each repository

### Option 2: GitHub App (Recommended for Scale)
Create a GitHub App for automatic installation across repositories.

#### GitHub App Setup:
1. Go to **GitHub Settings** → **Developer settings** → **GitHub Apps**
2. **New GitHub App**:
   - **Name**: "Jod QC Agent"
   - **Homepage URL**: Your app URL
   - **Webhook URL**: `https://your-domain.com/api/github-webhook`
   - **Webhook secret**: Your secret
3. **Permissions**:
   - **Repository permissions** → **Pull requests**: Read & Write
   - **Repository permissions** → **Contents**: Read
4. **Subscribe to events**: Pull requests
5. **Install** the app on your repositories

#### Benefits:
- ✅ **One-time setup** for multiple repositories
- ✅ **Automatic installation** on new repos
- ✅ **Better permission control**
- ✅ **Organization-wide deployment**

### Environment Variables:
```bash
# For GitHub App (recommended)
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# OR for Personal Access Token (simpler)
GITHUB_TOKEN=your_personal_access_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### How It Works

1. **PR Submission**: When a PR is opened/updated, the webhook triggers
2. **Task ID Extraction**: Parses PR title/branch for task IDs (T001, TASK-001, etc.)
3. **Code Analysis**: Fetches the diff and compares against task requirements
4. **AI QC Review**: Uses Gemini to analyze code quality, security, and acceptance criteria compliance
5. **Database Storage**: Saves review results to Supabase
6. **PR Comments**: Posts detailed feedback as a comment on the PR

### PR Title Formats

The system extracts task IDs from PR titles using these patterns:
- `Implement user login T001`
- `TASK-002: Add payment processing`
- `Fix dashboard bug (003)`

### QC Analysis Output

The AI provides:
- **Acceptance Criteria Check**: Verifies each criterion is met
- **Code Quality Review**: Comments on readability, best practices, bugs
- **Security Analysis**: Checks for vulnerabilities
- **QC Score**: Overall score from 0-100
- **Approval Status**: "Approved" or "Changes Requested"

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys and tokens
```

## Usage

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
```

## Usage

### Basic Usage

```python
from user_story_generator import UserStoryGenerator
from models import Requirement, UserStoryGenerationRequest

# Initialize generator
generator = UserStoryGenerator()

# Create requirements
requirements = [
    Requirement(
        id="req_001",
        description="Users need to create project boards with customizable columns",
        priority=9
    )
]

# Generate user stories
request = UserStoryGenerationRequest(
    requirements=requirements,
    include_personas=True
)

response = generator.generate_complete_stories(request)

print(f"Generated {len(response.user_stories)} user stories")
```

### Running the Example

```bash
python example_usage.py
```

## Data Models

### Requirement
- `id`: Unique identifier
- `description`: Detailed requirement description
- `priority`: Priority level (1-10)

### UserStory
- `id`: Unique identifier
- `title`: Concise story title
- `description`: Full user story in "As a... I want... So that..." format
- `acceptance_criteria`: List of testable criteria
- `story_points`: Estimation (1, 2, 3, 5, 8, 13)
- `priority`: Priority level (1-10)
- `requirement_ids`: Associated requirement IDs

### UserPersona
- `id`: Unique identifier
- `name`: Persona name
- `role`: Job title or role
- `description`: Detailed persona description
- `goals`: Primary goals and motivations
- `pain_points`: Main challenges

## Configuration

Environment variables in `.env`:
- `GOOGLE_API_KEY`: Google Gemini API key (required)
- `GEMINI_MODEL`: Model name (default: gemini-pro)
- `GEMINI_TEMPERATURE`: Temperature for generation (default: 0.7)
- `GEMINI_MAX_OUTPUT_TOKENS`: Max tokens (default: 2048)

## Testing

Run the test suite:
```bash
pytest test_user_story_generator.py -v
```

## API Integration

The component is designed to be integrated into larger systems:

```python
# Integration example
def process_requirements(requirements_data):
    generator = UserStoryGenerator()
    
    requirements = [Requirement(**req) for req in requirements_data]
    request = UserStoryGenerationRequest(requirements=requirements)
    
    response = generator.generate_complete_stories(request)
    
    return {
        'personas': [p.dict() for p in response.personas],
        'user_stories': [s.dict() for s in response.user_stories],
        'metadata': response.generation_metadata
    }
```

## Quality Assurance

The component ensures:
- All stories follow proper user story format
- Story points use Fibonacci sequence (1, 2, 3, 5, 8, 13)
- Each story has comprehensive acceptance criteria
- Stories are mapped back to original requirements
- INVEST criteria compliance validation

## Error Handling

- API connection failures
- Invalid JSON responses
- Data validation errors
- Missing or invalid configuration

## Output Example

```json
{
  "personas": [
    {
      "id": "persona_1",
      "name": "Project Manager",
      "role": "Project Manager",
      "description": "Manages multiple projects and coordinates team activities",
      "goals": ["Track project progress", "Coordinate team activities"],
      "pain_points": ["Manual reporting", "Lack of real-time updates"]
    }
  ],
  "user_stories": [
    {
      "id": "story_1",
      "title": "Create Project Board",
      "description": "As a Project Manager, I want to create project boards with customizable columns so that I can organize my team's work effectively",
      "persona_id": "persona_1",
      "acceptance_criteria": [
        {
          "id": "ac_1",
          "description": "User can create a new board with a custom name",
          "priority": "Must have"
        }
      ],
      "story_points": 5,
      "priority": 9,
      "requirement_ids": ["req_001"],
      "tags": ["board", "creation"]
    }
  ]
}
```
