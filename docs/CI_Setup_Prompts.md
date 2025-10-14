 Universal Setup Prompt (Copy & Paste)

  I want to set up automated code quality and security checks for this repository. Please:

  1. **Code Formatting:**
     - Set up automatic formatters (black/isort for Python, prettier for JS/TS, rustfmt for Rust, etc.)
     - Create configuration files so formatting is consistent
     - Add pre-commit hooks or CI checks to enforce formatting

  2. **Security Scanning:**
     - Set up secret detection (TruffleHog or similar)
     - Add dependency vulnerability scanning
     - Configure security linting appropriate for this language

  3. **CI/CD Pipeline:**
     - Create a GitHub Actions workflow that runs on every push/PR
     - Include: linting, formatting checks, security scans
     - Make it non-blocking for false positives but log warnings

  4. **Documentation:**
     - Update .gitignore to exclude secrets, build artifacts, etc.
     - Create/update README with instructions for running checks locally
     - Document what tools are being used and why

  Make sure configuration files are in the right locations and compatible with each other (like we did with black + isort using the black
  profile).

  Language-Specific Variations:

  For Python Projects:

  Set up Python code quality and security for this project:
  - black (formatter) with line-length 88
  - isort (import sorting) with black profile
  - flake8 (linting) for syntax errors
  - bandit (security) for common vulnerabilities
  - TruffleHog for secret detection

  Create pyproject.toml with compatible settings and a GitHub Actions workflow.
  Exclude test files from security scans where appropriate.

  For JavaScript/TypeScript:

  Set up JavaScript/TypeScript code quality and security:
  - prettier (formatter) with default settings
  - eslint (linting) with airbnb or standard config
  - npm audit or snyk for dependency vulnerabilities
  - TruffleHog for secret detection

  Create .prettierrc, .eslintrc, and GitHub Actions workflow.
  Configure to work with React/Vue/Angular if applicable.

  For Multi-Language Repos:

  This repo has [Python backend / JavaScript frontend / etc.]. Set up:
  1. Language-specific formatters for each part
  2. Unified CI/CD workflow that runs appropriate checks for each directory
  3. Security scanning across the entire repo
  4. Configuration that doesn't conflict between languages

  Quick Security-Only Prompt:

  I want to add security scanning to this repository without changing existing code:
  - Scan for accidentally committed secrets (API keys, passwords, tokens)
  - Check dependencies for known vulnerabilities
  - Flag hardcoded credentials in code
  - Make scans non-blocking but report issues as warnings
  - Add to GitHub Actions so it runs automatically

  Quick Formatting-Only Prompt:

  I want to standardize code formatting in this repository:
  - Set up auto-formatters for [language]
  - Create configuration files with sensible defaults
  - Format all existing code to match
  - Add CI check to enforce formatting on new code
  - Don't change any functionality, just formatting

  Detailed "Make It Professional" Prompt:

  I want this repository to look professional for portfolio/job applications. Please:

  **Code Quality:**
  - Set up industry-standard formatters and linters
  - Format all existing code to match best practices
  - Add type hints/annotations where appropriate
  - Fix any obvious code smells or anti-patterns

  **Security:**
  - Scan for secrets and remove any found
  - Add .gitignore for sensitive files
  - Set up automated security scanning
  - Document any security considerations in README

  **CI/CD:**
  - Create GitHub Actions workflow with all quality checks
  - Add status badges to README showing tests pass
  - Make sure workflow is efficient (caches dependencies, runs fast)

  **Documentation:**
  - Ensure README has clear setup instructions
  - Document what CI/CD checks run and why
  - Add contributing guidelines if applicable

  Make this look like a well-maintained professional project that shows I follow best practices.

  Incremental Improvement Prompt:

  This project already has some code but no quality checks. Please:
  1. Analyze what language(s) and frameworks are used
  2. Recommend appropriate formatters, linters, and security tools
  3. Show me what changes will be made before applying them
  4. Set up CI/CD to enforce standards going forward
  5. Let me review before committing changes

  Don't break existing functionality - only add tooling and fix formatting.

  Post-Setup Verification Prompt:

  We just set up code quality and security tools. Please verify:
  1. Run all checks locally and confirm they pass
  2. Show me the CI/CD workflow status
  3. Explain what each tool does and why it's included
  4. Tell me how to run checks locally before pushing
  5. Identify any remaining issues that need manual fixing

  Bonus: Pre-Commit Hook Setup:

  Set up pre-commit hooks so formatting/linting runs automatically before each commit:
  - Install pre-commit framework
  - Configure to run [black, isort, flake8, etc.]
  - Make it fast (only check changed files)
  - Add instructions to README for other contributors
  - Ensure it works cross-platform (Windows/Mac/Linux)

    What to Expect as Output:

  When you use these prompts, Claude should give you:
  - ✅ Configuration files (.bandit, pyproject.toml, .prettierrc, etc.)
  - ✅ CI/CD workflow file (.github/workflows/ci.yml)
  - ✅ Formatted code (if you asked for it)
  - ✅ Updated .gitignore
  - ✅ Documentation updates
  - ✅ Explanation of what each tool does

  Red Flags to Watch For:

  If the AI gives you:
  - ❌ Overly complex setup with too many tools
  - ❌ Configuration files in wrong locations
  - ❌ Tools that conflict with each other (like we had with black/isort)
  - ❌ No explanation of what tools do

  Push back and ask: "Simplify this - I want the minimum setup that covers security and formatting."