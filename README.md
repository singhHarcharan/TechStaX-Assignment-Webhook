# How to Test the GitHub Webhook Integration

This guide provides step-by-step instructions to test all features of the GitHub Webhook integration, including push events, pull requests, and merge events.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Test Script](#test-script)
- [Running the Tests](#running-the-tests)
- [Verifying the Results](#verifying-the-results)
- [Troubleshooting](#troubleshooting)
- [Cleaning Up](#cleaning-up)
- [Viewing Events](#viewing-events)

## Prerequisites

1. **Clone the Action Repository**:
   ```bash
   git clone https://github.com/singhHarcharan/TechStaX-Assignment-ActionRepo.git
   cd TechStaX-Assignment-ActionRepo
   ```

2. **Ensure you have**:
   - Git installed on your system
   - Proper GitHub authentication set up
   - Access to the webhook receiver interface

## Test Script

Create a new file named `test_webhooks.sh` with the following content:

```bash
#!/bin/bash
set -e  # Exit on error

# Navigate to repository
cd "$(dirname "$0")"

# Function to print section headers
section() {
    echo -e "\n\033[1;34m=== $1 ===\033[0m"
}

# 1. Test Push Event
section "Testing Push Event"
git checkout main
git pull origin main
echo "Test push - $(date)" > push_test.txt
git add push_test.txt
git commit -m "Test push event - $(date)"
git push origin main
echo "✅ Push event triggered. Check your webhook receiver for the event."

# 2. Test Pull Request Event
section "Testing Pull Request"
git checkout -b test-pr 2>/dev/null || git checkout test-pr
echo "PR test - $(date)" > pr_test.txt
git add pr_test.txt
git commit -m "Test PR changes - $(date)"
git push -f -u origin test-pr
echo "✅ PR branch pushed. Please create a PR from 'test-pr' to 'main' on GitHub."

# 3. Test Merge Event
section "Testing Merge"
git checkout -b test-merge 2>/dev/null || git checkout test-merge
echo "Merge test - $(date)" > merge_test.txt
git add merge_test.txt
git commit -m "Test merge changes - $(date)"
git push -f -u origin test-merge
echo "✅ Merge branch pushed. Please create and merge a PR from 'test-merge' to 'main' on GitHub."

section "Testing Complete"
echo "All test events have been triggered. Check your webhook receiver for the events."

## Running the Tests

1. **Make the script executable**:
   ```bash
   chmod +x test_webhooks.sh
   ```

2. **Run the test script**:
   ```bash
   ./test_webhooks.sh
   ```

3. **Complete the manual steps**:
   - Go to your GitHub repository
   - Create a PR from `test-pr` to `main` (but don't merge it)
   - Create another PR from `test-merge` to `main` and merge it

## Verifying the Results

### Expected Outputs:

1. **Push Event**:
   - Should appear immediately after the first section runs
   - Format: `{user} pushed to {branch} on {timestamp}`

2. **Pull Request Event**:
   - Should appear when you create the PR from `test-pr` to `main`
   - Format: `{user} submitted a pull request from {from_branch} to {to_branch} on {timestamp}`

3. **Merge Event**:
   - Should appear when you merge the PR from `test-merge` to `main`
   - Format: `{user} merged branch {from_branch} to {to_branch} on {timestamp}`

## Troubleshooting

### Common Issues:

1. **Authentication Errors**:
   ```bash
   # Ensure you have proper Git credentials
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **Webhook Not Triggering**:
   - Verify the webhook is properly configured in your GitHub repository settings
   - Check the webhook URL is correct
   - Ensure the webhook secret matches your configuration

3. **Viewing Logs**:
   ```bash
   # If using Render
   render logs
   
   # If using Heroku
   heroku logs --tail
   ```

## Cleaning Up

After testing, clean up the test branches:

```bash
# Delete local branches
git checkout main
git branch -D test-pr test-merge 2>/dev/null || true

# Delete remote branches
git push origin --delete test-pr test-merge 2>/dev/null || true

# Remove test files
rm -f push_test.txt pr_test.txt merge_test.txt 2>/dev/null || true
```

## Viewing Events

All events are stored in MongoDB and can be viewed in the web interface at:
`https://techstax-assignment-webhook.onrender.com`

The interface automatically refreshes every 15 seconds to show new events.

---

For any additional help, please refer to the project documentation or open an issue in the repository.
### Next Steps:
 
1. Commit and push the new documentation:
   ```bash
   git add README.md
   git commit -m "Add comprehensive testing guide"
   git push origin main