# 🔄 CodeYogi Rollback Intelligence - User Guide

## How Rollback Works

The Rollback Intelligence feature allows you to safely revert your application to a previous commit by creating a **Pull Request** on GitHub. This is the safest method because:

1. ✅ **No history is destroyed** - All commits are preserved
2. 👀 **You can review changes** before applying them
3. 🔒 **Requires approval** - You control when the rollback happens
4. 📝 **Fully documented** - Clear record of why the rollback was done

## Step-by-Step: How to Rollback

### Step 1: Access Rollback Intelligence
1. Open your CodeYogi dashboard
2. Navigate to the repository you want to rollback
3. Click on the **"Rollback Intelligence"** section

### Step 2: View Rollback Candidates
- You'll see a numbered list of recent commits (1-10)
- **Commit #1** = Current deployment (you're here now)
- **Commit #2+** = Previous versions you can rollback to

Each candidate shows:
- 📅 **Timestamp** - When it was committed
- 👤 **Author** - Who made the commit
- 📝 **Message** - What changed
- 📊 **Files changed** - How many files were modified
- ✅ **Status** - Whether deployment succeeded/failed

### Step 3: Select Rollback Target
1. **Review the AI recommendation** (shown at the top)
   - The AI analyzes all commits and suggests the best rollback target
   - It considers stability, age, and deployment status

2. **Choose a commit** to rollback to
   - Click the **"Rollback"** button on any commit
   - **WARNING**: You cannot rollback to Commit #1 (current version)

### Step 4: Safety Check
The system will automatically check:
- ⏰ **Age** - Is the commit too old?
- 📊 **Changes** - Are there many file changes?
- ✅ **Status** - Did it deploy successfully?

If there are risks, you'll see a confirmation dialog with warnings.

### Step 5: Execute Rollback
Click **"Confirm Rollback"** and the system will:

1. ✨ **Create a new branch** (e.g., `rollback/to-commit-2-20260106_143022`)
2. 📝 **Create a Pull Request** on GitHub
3. 🔗 **Show you the PR link**

## How to Verify the Rollback on GitHub

### Method 1: Through the UI (Easiest)
After clicking rollback, you'll see a blue box with:
```
✅ Pull Request Created!
PR #123

[View Pull Request on GitHub] ← Click this button
```

### Method 2: Check GitHub Directly

1. **Go to your repository on GitHub**
   ```
   https://github.com/YOUR_USERNAME/YOUR_REPO
   ```

2. **Click on "Pull requests" tab**

3. **Look for the rollback PR**
   - Title: `🔄 Rollback to commit #X (abc1234)`
   - It will be the most recent PR
   - Status: Open

4. **Review the PR**
   - Click on the PR to see details
   - Check the **"Files changed"** tab to see what will be reverted
   - Read the description for rollback information

5. **Merge the PR when ready**
   - Review the changes carefully
   - Click **"Merge pull request"**
   - Confirm the merge
   - Your application will rollback to that commit!

### Method 3: Via GitHub Notifications
- Check your GitHub notifications (bell icon)
- You'll see a notification about the new PR

### Method 4: Via Email
- GitHub will email you about the new PR
- Click the link in the email

## What Happens After You Merge the PR?

1. 🔄 **Code is reverted** to the selected commit
2. 🚀 **Deployment triggers** (if you have GitHub Actions)
3. ✅ **Application updates** to the rolled-back version
4. 📝 **History is preserved** - The rollback is a new commit

## Troubleshooting

### "Request timeout - the operation took too long"
**Problem**: The rollback took more than 60 seconds  
**Solution**:
- Check your GitHub repository anyway - the PR might have been created
- Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/pulls`
- If no PR exists, try again with a smaller rollback (closer commit)

### "PR creation failed"
**Problem**: GitHub API couldn't create the PR  
**Solution**:
1. The system will show git commands instead
2. Follow the manual instructions displayed
3. Make sure your GitHub token has `repo` permissions

### "Cannot rollback to current deployment"
**Problem**: You selected Commit #1 (current version)  
**Solution**: Select Commit #2 or higher

### Rollback button not responding
**Problem**: Backend might not be running or timeout  
**Solution**:
1. Check if backend is running: `http://localhost:8000/docs`
2. Look at browser console (F12) for errors
3. Wait 30-60 seconds for the operation to complete

## Best Practices

### ✅ DO:
- Review the AI recommendation before selecting
- Read the safety warnings carefully
- Check the "Files changed" in the PR before merging
- Test the rolled-back version after merging
- Document why you're rolling back in the PR comments

### ❌ DON'T:
- Rollback to very old commits (>7 days) without careful review
- Merge the PR without reviewing changes
- Rollback during active development (coordinate with team)
- Force rollback if safety level is "RISKY"

## GitHub Token Permissions

For rollback to work, your GitHub token needs:
- ✅ `repo` - Full repository access
- ✅ `workflow` - Update GitHub Actions workflows

To check/update permissions:
1. Go to https://github.com/settings/tokens
2. Click on your token
3. Ensure "repo" scope is checked
4. Update token in your `.env` file

## Example Rollback Workflow

```
1. Issue detected in production ❌
2. Open CodeYogi Rollback Intelligence
3. See Commit #3 was last stable version (green checkmark)
4. Click "Rollback" on Commit #3
5. Review safety analysis: "SAFE - Recent commit (2 hours ago)"
6. Click "Confirm Rollback"
7. PR created: https://github.com/user/repo/pull/42
8. Review changes on GitHub
9. Merge PR
10. Deployment triggers automatically
11. Application rolled back ✅
12. Issue resolved! 🎉
```

## Questions?

**Q: Will I lose my code?**  
A: No! Rollback creates a new commit that reverts changes. All history is preserved.

**Q: Can I undo a rollback?**  
A: Yes! Just rollback to a more recent commit or close the PR without merging.

**Q: How do I know if the rollback worked?**  
A: Check your deployment status after merging the PR. The application should be at the target commit.

**Q: What if I need to rollback urgently?**  
A: Merge the PR immediately after creation. If auto-deploy is enabled, changes apply in minutes.

---

**Need help?** Check the browser console (F12) or backend logs for detailed error messages.
