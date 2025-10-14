# Development Guide

## Code Quality & Security

This project enforces code quality and security best practices through automated tooling.

### Tools Used

| Tool | Purpose | Status |
|------|---------|--------|
| **black** | Code formatting (line length: 88) | ✓ Configured |
| **isort** | Import sorting (black profile) | ✓ Configured |
| **flake8** | Linting and syntax checking | ✓ Configured |
| **bandit** | Security vulnerability scanning | ✓ Configured |
| **GitHub Actions** | Automated CI/CD pipeline | ✓ Configured |

### Running Checks Locally

Before pushing code, run these commands to ensure your code passes CI:

```bash
# Install tools (one-time setup)
pip install black==24.1.1 isort==5.13.2 flake8==7.0.0 bandit==1.7.6

# Format code
black scraper-service/ scripts/
isort scraper-service/ scripts/

# Check linting
flake8 scraper-service/ scripts/

# Run security scan
bandit -r scraper-service/ scripts/
```

### Auto-Fix Formatting

To automatically fix all formatting issues:

```bash
# Fix formatting and imports in one command
black scraper-service/ scripts/ && isort scraper-service/ scripts/
```

### Configuration Files

All tool configurations are in:
- **pyproject.toml** - Black and isort settings
- **.flake8** - Flake8 linting rules
- **.github/workflows/ci.yml** - GitHub Actions workflow

### CI/CD Pipeline

Every push and pull request triggers automated checks:

1. **Formatting Check** (black, isort)
   - Fails if code isn't formatted correctly
   - Fix locally: `black scraper-service/ scripts/`

2. **Linting Check** (flake8)
   - Fails on syntax errors and code quality issues
   - Review output and fix issues

3. **Security Scan** (bandit, TruffleHog)
   - Warns on security vulnerabilities
   - Non-blocking (won't fail build)
   - Review warnings and address if needed

4. **Dependency Check** (Safety)
   - Checks for vulnerable dependencies
   - Non-blocking warning system

### What Gets Checked

**Included:**
- `scraper-service/` - All Python scraper code
- `scripts/` - Automation scripts

**Excluded:**
- `ignition-project/gateway-scripts/` - Jython 2.7 (different syntax)
- `venv/`, `.venv/` - Virtual environments
- `tests/` - Test files (excluded from bandit)

### Common Issues

#### "Black would reformat"
**Problem:** Code doesn't match formatting standard

**Fix:**
```bash
black scraper-service/ scripts/
```

#### "Import sorting issues found"
**Problem:** Imports aren't sorted correctly

**Fix:**
```bash
isort scraper-service/ scripts/
```

#### "Unused imports"
**Problem:** Imported modules not used in code

**Fix:** Remove the unused import or use it

#### "Function too complex (C901)"
**Problem:** Function has high cyclomatic complexity

**Note:** This is a warning, not an error. Consider refactoring complex functions, but it won't fail CI.

### Security Best Practices

1. **Never commit secrets**
   - Use `.env` files (gitignored)
   - Use environment variables
   - Check `.gitignore` before committing

2. **Dependency management**
   - Keep `requirements.txt` up to date
   - Review security warnings from Safety
   - Update vulnerable packages promptly

3. **Code review**
   - Review bandit security warnings
   - Don't ignore security issues
   - Use specific exceptions instead of bare `except:`

### Pre-Commit Hooks (Optional)

For automatic formatting before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks (future enhancement)
# pre-commit install
```

### VS Code Integration

Add to `.vscode/settings.json`:

```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.banditEnabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm Integration

1. Go to **Settings** > **Tools** > **Black**
2. Enable "Run Black on save"
3. Set line length to 88

For flake8:
1. Go to **Settings** > **Tools** > **External Tools**
2. Add flake8 with appropriate settings

### Repository Cleanup & Organization

**IMPORTANT:** Always keep the repository clean and organized!

#### Cleanup Checklist

Before committing code, always run this cleanup:

```bash
# 1. Remove Windows metadata files (Zone.Identifier)
find . -name "*Zone.Identifier*" -type f -delete

# 2. Remove other OS junk files
find . -name ".DS_Store" -type f -delete
find . -name "Thumbs.db" -type f -delete
find . -name "desktop.ini" -type f -delete

# 3. Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# 4. Clean up temporary files
find . -name "*.tmp" -delete
find . -name "*~" -delete
```

#### File Organization Rules

**Root directory** - Only essential files:
- `README.md` - Main project readme
- `QUICK_START.md` - Quick start guide
- `DEVELOPMENT.md` - This file (developer guide)
- `CLAUDE.md` - Claude Code instructions
- Configuration files (`.gitignore`, `pyproject.toml`, `.flake8`)

**Documentation** - Goes in `docs/`:
- Technical documentation
- Deployment guides
- Architecture decisions
- Project status updates
- Testing guides
- Setup instructions

**Code** - Organized by purpose:
- `scraper-service/` - Main scraper code
- `scripts/` - Automation and utility scripts
- `ignition-project/` - Ignition-specific files
- `sql/` - Database schemas
- `docker/` - Docker configurations
- `tests/` - Test files

#### .gitignore Coverage

The `.gitignore` file automatically excludes:
- Python cache files (`__pycache__`, `*.pyc`)
- Virtual environments (`venv/`, `.venv/`)
- OS metadata (`*.Zone.Identifier`, `.DS_Store`, `Thumbs.db`)
- IDE settings (`.vscode/`, `.idea/`)
- Secrets and credentials (`*.env`, `*.key`, `*.pem`)
- Build artifacts (`dist/`, `build/`, `*.egg-info`)
- Log files (`*.log`, `logs/`)

#### Best Practices

1. **Before every commit:**
   - Run cleanup commands above
   - Format code with black and isort
   - Check for uncommitted files: `git status`

2. **When adding new documentation:**
   - Place in `docs/` folder
   - Use clear, descriptive filenames
   - Update main README.md if needed

3. **When creating new files:**
   - Put them in appropriate directories
   - Don't leave files in root unless they're essential
   - Add to `.gitignore` if they're generated files

4. **Windows users (WSL/native):**
   - Always remove `Zone.Identifier` files before committing
   - These are Windows security metadata files
   - Already excluded in `.gitignore`

### Questions?

- **CI failing?** Check the workflow run logs in GitHub Actions
- **Tool issues?** Verify versions match those in this guide
- **Need help?** Review tool documentation:
  - [Black](https://black.readthedocs.io/)
  - [isort](https://pycqa.github.io/isort/)
  - [flake8](https://flake8.pycqa.org/)
  - [bandit](https://bandit.readthedocs.io/)
