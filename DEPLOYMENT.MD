### GitHub App Configuration

Web deployment uses GitHub App authentication for secure repository access:

#### 1. Create GitHub App
1. Go to https://github.com/settings/apps
2. Click "New GitHub App"
3. Configure:
   - **App name**: "Around the Grounds Deployer" (or similar)
   - **Homepage URL**: Your repository URL
   - **Repository permissions**:
     - Contents: Read & Write
     - Metadata: Read
   - **Where can this GitHub App be installed?**: Only on this account
4. **Generate private key** and download the `.pem` file
5. Note the **App ID** from the app settings page

#### 2. Install App on Repository
1. Go to your GitHub App settings
2. Click "Install App" 
3. Select your target repository (e.g., `ballard-food-trucks`)
4. The installation ID will be automatically retrieved by the system

#### 3. Configure Environment Variables
```bash
# Copy template
cp .env.example .env

# Add GitHub App credentials to .env:
GITHUB_APP_ID=123456
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_APP_PRIVATE_KEY_B64=$(base64 -i path/to/your-app.private-key.pem)
GIT_REPOSITORY_URL=https://github.com/username/ballard-food-trucks.git

# Optional: AI vision analysis
ANTHROPIC_API_KEY=your-anthropic-api-key
```

**Note:** The system includes working defaults for `GITHUB_APP_ID` and `GITHUB_CLIENT_ID`. You only need to override these if you're using a different GitHub App. The installation ID is automatically retrieved via the GitHub API - you don't need to configure it manually.

#### 4. Target Repository Setup

The system pushes a complete static website to a **separate target repository** which is then deployed by platforms like Vercel:

**Two-Repository Architecture**:
- **Source repo** (this one): Contains scraping code, runs workers, web templates
- **Target repo** (e.g., `ballard-food-trucks`): Receives complete website, served as static site

**Configuration Options**:

**Default Repository**: `steveandroulakis/ballard-food-trucks`
```bash
# Uses default repository from settings
uv run around-the-grounds --deploy
```

**Custom Repository via CLI**:
```bash
uv run around-the-grounds --deploy --git-repo https://github.com/username/custom-repo.git
```

**Custom Repository via Environment**:
```bash
export GIT_REPOSITORY_URL="https://github.com/username/custom-repo.git"
uv run around-the-grounds --deploy
```

**Configuration Precedence**:
1. CLI argument (`--git-repo`)
2. Environment variable (`GIT_REPOSITORY_URL`)
3. Default (`steveandroulakis/ballard-food-trucks`)

#### 5. Deployment Workflow

When you run `--deploy`, the system:
1. **Scrapes** all brewery websites for fresh data
2. **Copies** web templates from `public_template/` to target repository
3. **Generates** web-friendly JSON data in target repository
4. **Authenticates** using GitHub App credentials
5. **Commits** and pushes complete website to target repository
6. **Triggers** automatic deployment (Vercel/Netlify/etc.)
7. **Website** updates live within minutes

### Temporal Workflow Execution

The system supports multiple Temporal deployment scenarios through environment-based configuration:

#### Local Development (Default)
```bash
# No configuration needed - connects to localhost:7233

# Method 1: Run worker in background (for testing)
# Start Temporal worker (run in separate terminal - runs continuously, not good for agents)
uv run python -m around_the_grounds.temporal.worker

# Method 2: Test with timeout (recommended for development and agents)
# Start workflow first, then run worker with timeout to process it
uv run python -m around_the_grounds.temporal.starter --deploy --verbose &
timeout 60s uv run python -m around_the_grounds.temporal.worker

# Execute workflow manually
uv run python -m around_the_grounds.temporal.starter --deploy --verbose

# Execute workflow with custom configuration
uv run python -m around_the_grounds.temporal.starter --config /path/to/config.json --deploy

# Execute workflow with custom ID for tracking
uv run python -m around_the_grounds.temporal.starter --workflow-id daily-update-2025 --deploy
```

**Note:** The Temporal worker runs as a foreground service and will not exit until manually stopped (Ctrl+C). For testing purposes, use `timeout 60s` to limit worker execution time, allowing enough time for the full scraping and deployment workflow (~90-60s).

#### Temporal Cloud Deployment
```bash
# Set environment variables for Temporal Cloud
export TEMPORAL_ADDRESS="your-namespace.acct.tmprl.cloud:7233"
export TEMPORAL_NAMESPACE="your-namespace"
export TEMPORAL_API_KEY="your-api-key"

# Start worker - automatically connects to Temporal Cloud (runs continuously)
uv run python -m around_the_grounds.temporal.worker

# Execute workflows - uses cloud configuration
uv run python -m around_the_grounds.temporal.starter --deploy --verbose
```

### Production Deployment via CI/CD

For automated production updates using Docker and Watchtower:

```bash
# 1. GitHub Actions builds and pushes to Docker Hub (takes ~4 minutes)
# 2. Watchtower runs every 5 minutes to pull latest image
# 3. Monitor worker container:
ssh admin@192.168.0.20
docker ps -a -f "ancestor=steveandroulakis/around-the-grounds-worker:latest"
docker logs -f around-the-grounds-worker

# 4. Trigger schedule via Temporal UI and watch execution
```

**CI/CD Workflow:**
1. **Code changes** → GitHub Actions → Docker Hub (4 minutes)
2. **Watchtower** detects new image → pulls and restarts worker (every 5 minutes)
3. **Temporal schedules** trigger workflows → worker executes deployment
4. **Data deploys** automatically to target repository → live website updates

**Production Monitoring:**
- Monitor Docker containers on production server
- Check worker logs for execution status
- Trigger immediate updates via Temporal UI
- Verify deployment success on live website

#### Custom Server with mTLS
```bash
# Set environment variables for custom server with certificate authentication
export TEMPORAL_ADDRESS="your-server.example.com:7233"
export TEMPORAL_NAMESPACE="production"
export TEMPORAL_TLS_CERT="/path/to/cert.pem"
export TEMPORAL_TLS_KEY="/path/to/key.pem"

# Start worker and execute workflows
uv run python -m around_the_grounds.temporal.worker
uv run python -m around_the_grounds.temporal.starter --deploy
```

#### Environment Configuration
Create a `.env` file (based on `.env.example`) for persistent configuration:
```bash
# Copy the template
cp .env.example .env

# Edit with your Temporal configuration
# TEMPORAL_ADDRESS=your-namespace.acct.tmprl.cloud:7233
# TEMPORAL_API_KEY=your-api-key
# etc.
```

#### Legacy CLI Arguments (Deprecated)
```bash
# CLI arguments still work but show deprecation warnings
uv run python -m around_the_grounds.temporal.starter --temporal-address production:7233 --deploy
# Warning: --temporal-address is deprecated, use TEMPORAL_ADDRESS environment variable
```