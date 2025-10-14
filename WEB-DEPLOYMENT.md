# Web Deployment Workflow

This guide covers the complete web deployment workflow for the Around the Grounds project.

## Overview

The system deploys a complete static website to a separate target repository, which is then automatically deployed by platforms like Vercel.

### Two-Repository Architecture

- **Source repo** (this one): Contains scraping code, runs workers, web templates
- **Target repo** (e.g., `ballard-food-trucks`): Receives complete website, served as static site

## Quick Start

```bash
# Deploy with defaults
uv run around-the-grounds --deploy

# Deploy to custom repository
uv run around-the-grounds --deploy --git-repo https://github.com/username/custom-repo.git

# Deploy with verbose logging
uv run around-the-grounds --deploy --verbose
```

## Development & Testing

### Local Preview

Before deploying, generate and test web files locally:

```bash
# Generate web files locally for testing (~60s to scrape all sites)
uv run around-the-grounds --preview

# Serve locally and view in browser
cd public && python -m http.server 8000
# Visit: http://localhost:8000
```

**What `--preview` does:**
- Scrapes fresh data from all brewery websites
- Copies templates from `public_template/` to `public/`
- Generates `data.json` with current food truck data
- Creates complete website in `public/` directory (git-ignored)

This allows you to test web interface changes, verify data accuracy, and debug issues before deploying to production.

### Testing Web Interface Changes

1. **Edit templates**: Make changes to files in `public_template/`
2. **Generate preview**: Run `uv run around-the-grounds --preview`
3. **Test locally**: Serve with `cd public && python -m http.server 8000`
4. **Verify changes**: Check http://localhost:8000 in browser
5. **Deploy when ready**: Run `uv run around-the-grounds --deploy`

### Testing Data Generation

```bash
# Test data.json endpoint
cd public && timeout 10s python -m http.server 8000 > /dev/null 2>&1 & sleep 1 && curl -s http://localhost:8000/data.json | head -20 && pkill -f "python -m http.server" || true

# Test for specific event data
cd public && timeout 10s python -m http.server 8000 > /dev/null 2>&1 & sleep 1 && curl -s http://localhost:8000/data.json | grep "2025-07-06" && pkill -f "python -m http.server" || true

# Test full homepage (basic connectivity)
cd public && timeout 10s python -m http.server 8000 > /dev/null 2>&1 & sleep 1 && curl -s http://localhost:8000/ > /dev/null && echo "✅ Homepage loads" && pkill -f "python -m http.server" || echo "❌ Homepage failed"
```

## Deployment Process

### Manual Deployment

```bash
# Full deployment workflow
uv run around-the-grounds --deploy

# This command will:
# 1. Scrape all brewery websites for fresh data
# 2. Copy web templates from public_template/ to target repository
# 3. Generate web-friendly JSON data in target repository
# 4. Authenticate using GitHub App credentials
# 5. Commit and push complete website to target repository
# 6. Trigger automatic deployment (Vercel/Netlify/etc.)
# 7. Website updates live within minutes
```

### Deployment Configuration

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

## Scheduled Updates (Temporal)

For automated regular updates, use Temporal workflows:

### Manual Execution via Temporal

```bash
# Execute workflow with deployment
uv run python -m around_the_grounds.temporal.starter --deploy --verbose

# Execute workflow with custom configuration
uv run python -m around_the_grounds.temporal.starter --config /path/to/config.json --deploy
```

### Scheduled Execution

Create a schedule that runs automatically:

```bash
# Create a schedule that runs every 30 minutes
uv run python -m around_the_grounds.temporal.schedule_manager create --schedule-id daily-scrape --interval 30

# The schedule will automatically:
# 1. Trigger workflow every 30 minutes
# 2. Scrape all brewery websites
# 3. Deploy updated data to target repository
# 4. Trigger Vercel deployment
```

See [SCHEDULES.md](./SCHEDULES.md) for complete schedule management documentation.

## Verifying Deployments

### Check Target Repository

```bash
# Clone target repository
git clone https://github.com/username/ballard-food-trucks.git

# Check latest commit
cd ballard-food-trucks
git log -1

# Verify files are present
ls -la  # Should see: index.html, data.json, vercel.json
```

### Check Live Website

1. **Visit website**: Go to your Vercel deployment URL
2. **Verify data**: Check that latest food truck events are showing
3. **Test mobile**: Verify responsive design on mobile viewport
4. **Check console**: Open browser dev tools, verify no JavaScript errors

### Monitor Vercel Deployment

1. **Vercel Dashboard**: Visit https://vercel.com/dashboard
2. **Find your project**: Navigate to `ballard-food-trucks` project
3. **Check deployments**: View recent deployment history
4. **View logs**: Check deployment logs for any errors

## Troubleshooting

### No changes deployed

**Possible causes**:
- Data hasn't actually changed since last deployment
- Templates haven't been modified
- Git thinks there are no changes to commit

**Solutions**:
```bash
# Force deployment by updating timestamp
uv run around-the-grounds --deploy --verbose

# Check if data is actually different
diff public/data.json ~/path/to/ballard-food-trucks/data.json
```

### Website not updating

**Possible causes**:
- Git push to target repository failed
- Vercel deployment failed or is delayed
- Browser cache showing old version

**Solutions**:
```bash
# Check target repository for latest commit
cd ~/path/to/ballard-food-trucks
git pull origin main
git log -1

# Force refresh browser (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

# Check Vercel deployment logs
# Visit Vercel dashboard and check deployment status
```

### Mobile display issues

**Possible causes**:
- Missing viewport meta tag
- CSS not loading properly
- JavaScript errors on mobile

**Solutions**:
```html
<!-- Ensure viewport meta tag in public_template/index.html -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- Test responsive design locally -->
# Open browser dev tools (F12)
# Toggle device toolbar (Cmd+Shift+M)
# Test different viewport sizes
```

### Data fetching errors

**Possible causes**:
- `data.json` not generated correctly
- CORS issues (shouldn't happen with static hosting)
- JavaScript errors preventing fetch

**Solutions**:
```bash
# Verify data.json is valid JSON
cd public
cat data.json | python -m json.tool

# Check for syntax errors
jq . data.json  # If jq is installed

# Test data.json endpoint
curl -s http://localhost:8000/data.json | head -20
```

### Authentication errors

**Possible causes**:
- GitHub App credentials not configured
- Private key expired or invalid
- Repository permissions insufficient

**Solutions**:
```bash
# Verify environment variables are set
echo $GITHUB_APP_ID
echo $GITHUB_APP_PRIVATE_KEY_B64

# Check GitHub App installation
# Visit https://github.com/settings/installations
# Verify app is installed on target repository

# Test authentication
uv run around-the-grounds --deploy --verbose
# Check logs for authentication errors
```

See [DEPLOYMENT.MD](./DEPLOYMENT.MD) for GitHub App configuration details.

## Web Template Structure

### public_template/

This directory contains the web interface templates that get copied to the target repository:

- **index.html**: Mobile-responsive web interface
- **vercel.json**: Vercel deployment configuration

### Customizing the Web Interface

1. **Edit templates**: Modify files in `public_template/`
2. **Test locally**: Run `--preview` and serve locally
3. **Verify changes**: Check http://localhost:8000
4. **Deploy**: Run `--deploy` to push changes to target repo

### Generated Files

During deployment, the system generates:

- **data.json**: Food truck event data in web-friendly format
- **Complete website**: All templates + generated data copied to target repo

## Best Practices

1. **Test locally first**: Always run `--preview` before `--deploy`
2. **Check data.json**: Verify generated JSON is valid and contains expected data
3. **Monitor deployments**: Watch Vercel dashboard for deployment status
4. **Use version control**: Keep track of template changes in source repository
5. **Set up schedules**: Use Temporal schedules for automated regular updates
6. **Handle errors gracefully**: System continues even if some breweries fail
7. **Log verbosely**: Use `--verbose` flag for troubleshooting
8. **Test responsive design**: Check mobile viewport before deploying

## Deployment Checklist

Before deploying:

- [ ] Templates in `public_template/` are up to date
- [ ] GitHub App credentials are configured
- [ ] Target repository exists and is accessible
- [ ] Vercel project is configured for target repository
- [ ] Local preview tested and working
- [ ] Data.json contains expected events
- [ ] Mobile responsive design verified

After deploying:

- [ ] Target repository received latest commit
- [ ] Vercel deployment completed successfully
- [ ] Live website shows updated data
- [ ] No JavaScript errors in browser console
- [ ] Mobile view works correctly
- [ ] All brewery data is present
