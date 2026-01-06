# 🎯 Quick Start: How to Use Rollback & Verify on GitHub

## What You'll See After Clicking Rollback

### ✅ **Success Case 1: Automatic PR Created**
When the rollback works automatically, you'll see:

```
┌─────────────────────────────────────────────────┐
│ ✓ Rollback Prepared                            │
│                                                  │
│ PR creation failed: 404 ...                     │
│ [but don't worry, there's a better solution!]   │
│                                                  │
│ ┌───────────────────────────────────────────┐  │
│ │  🔗 Create Pull Request on GitHub         │  │
│ │  [Click this big yellow/orange button]    │  │
│ └───────────────────────────────────────────┘  │
│                                                  │
│ Next Steps:                                     │
│ 1. Click the button above                      │
│ 2. Review and submit the PR on GitHub         │
│ 3. Merge when ready                            │
└─────────────────────────────────────────────────┘
```

## Step-by-Step: From Rollback Button to PR

### **Step 1:** Click "Rollback" Button
- Select any commit #2 or higher
- Click the red/orange "Rollback" button

### **Step 2:** Wait for Processing (10-30 seconds)
You'll see: "Executing rollback..." at the bottom right

### **Step 3:** Result Appears
You'll see a **big colored box** with one of these:

#### 🟦 Blue Box (Best Case) - Automatic PR
```
┌────────────────────────────────────┐
│ ✓ Pull Request Created!           │
│ PR #123                            │
│                                     │
│ [View Pull Request on GitHub] ←―― Click!
└────────────────────────────────────┘
```
**Action:** Click the blue button → Opens your PR on GitHub

#### 🟨 Yellow Box (Common) - Manual PR
```
┌────────────────────────────────────┐
│ ⚠ Manual PR Creation Required     │
│ Automatic creation failed          │
│                                     │
│ [Create Pull Request on GitHub] ←―― Click!
│ [View Changes Comparison]          │
└────────────────────────────────────┘
```
**Action:** Click the yellow button → GitHub opens with PR form pre-filled

### **Step 4:** On GitHub
After clicking either button, you're on GitHub:

#### If Blue Box (Automatic PR):
1. **You see the PR page immediately**
2. Click "Files changed" tab to review
3. Click "Merge pull request" 
4. Confirm → Done! ✅

#### If Yellow Box (Manual PR):
1. **GitHub PR creation page opens**
2. Title & description already filled in
3. Click **"Create pull request"** (green button)
4. Review the PR
5. Click **"Merge pull request"**
6. Confirm → Done! ✅

## Where to Find Your Rollback PR on GitHub

### Method 1: Direct Link (Easiest)
Click the button in CodeYogi (blue or yellow box)

### Method 2: GitHub Pull Requests Tab
1. Go to your repository:
   ```
   https://github.com/YOUR_USERNAME/Hack_Technique
   ```
2. Click **"Pull requests"** tab (near the top)
3. Look for PR title: **"🔄 Rollback to commit #X"**

### Method 3: GitHub Notifications
- Click the bell icon (top right on GitHub)
- You'll see a notification about the new PR

## What the PR Looks Like

```
Title: 🔄 Rollback to commit #3 (abc1234)

Body:
## Rollback Information
Target Commit: abc1234
Message: Your commit message here
Author: Your Name
Date: 2 hours ago

### Changes
- Files Changed: 5
- Additions: +10
- Deletions: -25

[Merge pull request] ← Click this when ready
```

## How to Verify Rollback Worked

### After Merging the PR:

1. **Check Latest Commit**
   - Go to your repo main page
   - Look at the latest commit
   - Should show: "Rollback to commit #X" or similar

2. **Check Your Code**
   - Browse your repository files
   - They should match the old commit you selected
   - Everything is reverted to that state

3. **Check Deployment** (if you have auto-deploy)
   - Wait for GitHub Actions to run
   - Your app will update to the rolled-back version
   - Usually takes 2-5 minutes

4. **Verify Locally** (optional)
   ```bash
   git pull origin main
   ```
   - Your local code now matches the rollback

## Common Questions

### Q: "I clicked rollback but don't see a PR on GitHub. What happened?"
**A:** Check these:
1. Did you click the yellow **"Create Pull Request"** button in CodeYogi?
2. If yes, did you click the green **"Create pull request"** button on GitHub?
3. Check spam/notifications - GitHub should email you
4. Go directly to: `https://github.com/YOUR_USERNAME/Hack_Technique/pulls`

### Q: "The yellow box says 'Create Pull Request' - does that mean it's not created yet?"
**A:** Correct! Yellow box means you need to click the button to create it. It opens GitHub with everything pre-filled, so you just click "Create pull request" there.

### Q: "After merging, how do I know the rollback is live?"
**A:** 
1. Check your latest commit on GitHub (should show rollback message)
2. If you have a deployed app, visit it in 2-5 minutes
3. Check GitHub Actions tab for deployment status

### Q: "Can I test the rollback before merging?"
**A:** Yes!
1. Click **"Files changed"** tab in the PR
2. Review all changes
3. See exactly what will be reverted
4. Only merge when you're confident

### Q: "What if I merge the PR and want to undo it?"
**A:** Easy!
1. Use the rollback feature again
2. Select a more recent commit (closer to #1)
3. This will undo the previous rollback

## Visual Flowchart

```
Click Rollback Button
        ↓
   (Wait 10-30s)
        ↓
    See Result Box
    ↙         ↘
Blue Box        Yellow Box
(PR Created)    (Manual)
    ↓              ↓
Click Blue      Click Yellow
Button          Button
    ↓              ↓
PR Opens on     GitHub Opens
GitHub          with Form
    ↓              ↓
                Fill & Submit
    ↓              ↓
    ↓──────────────↓
         ↓
    Review PR
    (Files Changed)
         ↓
    Merge PR
         ↓
    Rollback Complete!
         ↓
    (Wait for deployment)
         ↓
    Verify it worked ✓
```

## Need Help?

- **Backend not responding?** 
  - Check: `http://localhost:8000/docs`
  - Restart: `cd codeyogi-backend && python main.py`

- **Frontend issues?**
  - Check browser console (F12)
  - Restart: `cd CodeYogi_Frontend && npm run dev`

- **GitHub token issues?**
  - Check `.env` file has `GITHUB_TOKEN`
  - Token needs `repo` permission
  - Get new token: https://github.com/settings/tokens

---

**TL;DR:** Click rollback → Click the big button that appears → Review on GitHub → Merge → Done! 🎉
