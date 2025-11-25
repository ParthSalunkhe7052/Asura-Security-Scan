# 🔑 How to Get Your OpenRouter API Key

This guide will walk you through getting a **free** OpenRouter API key to enable AI-powered features in ASURA.

## 🤖 What is OpenRouter?

OpenRouter is a unified API platform that provides access to multiple AI models through a single API key. ASURA uses it to:
- Explain vulnerabilities in plain English
- Suggest secure code fixes
- Help you learn security concepts

**Cost**: FREE tier available (no credit card required!)

---

## 📝 Step-by-Step Guide

### Step 1: Visit OpenRouter

Go to [https://openrouter.ai](https://openrouter.ai)

### Step 2: Sign Up

1. Click **"Sign Up"** in the top-right corner
2. Choose sign-up method:
   - **Google** (recommended - fastest)
   - **GitHub**
   - **Email/Password**

3. Complete the sign-up process

**Screenshot reference:**
```
┌─────────────────────────────────┐
│   OpenRouter.ai                 │
│                                 │
│   [ Sign Up with Google ]      │
│   [ Sign Up with GitHub ]      │
│   [ Sign Up with Email  ]      │
└─────────────────────────────────┘
```

### Step 3: Navigate to API Keys

1. After signing in, click your **profile picture** (top-right)
2. Select **"Keys"** from the dropdown menu
3. Or go directly to: [https://openrouter.ai/keys](https://openrouter.ai/keys)

### Step 4: Create New API Key

1. Click the **"Create Key"** button
2. Give your key a name (e.g., "ASURA Security Scanner")
3. (Optional) Set a credit limit for safety
4. Click **"Create"**

### Step 5: Copy Your API Key

⚠️ **IMPORTANT**: Copy the key immediately - you won't see it again!

Your key will look like:
```
sk-or-v1-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567
```

**Key format:**
- Starts with: `sk-or-v1-`
- Long string of letters and numbers
- About 68 characters total

---

## 🔧 Configure ASURA

### Method 1: Using .env File (Recommended)

1. **Navigate to backend folder**
   ```bash
   cd c:\Users\parth\OneDrive\Desktop\Asura\backend
   ```

2. **Create .env file** (if it doesn't exist)
   ```bash
   # Windows
   copy .env.example .env
   
   # Linux/Mac
   cp .env.example .env
   ```

3. **Edit .env file**
   Open `backend/.env` in any text editor and add:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE
   ```

4. **Save the file**

5. **Restart ASURA**
   ```bash
   # Stop the backend (Ctrl+C)
   # Start it again
   cd ..
   start.bat
   ```

### Method 2: Manual Configuration

If you prefer to set it manually:

**Windows:**
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-YOUR-KEY-HERE"
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY="sk-or-v1-YOUR-KEY-HERE"
```

---

## ✅ Test the Integration

### Step 1: Run a Security Scan

1. Open ASURA: http://localhost:5173
2. Create/select a project
3. Click **"Start Security Scan"**
4. Wait for scan to complete

### Step 2: Test AI Features

1. Go to **Security Results** page
2. Find any vulnerability
3. Click **"Explain with AI"** button
4. You should see:
   - ✅ AI-generated explanation
   - ✅ Beginner-friendly language
   - ✅ Secure code suggestions

**Success looks like:**
```
┌─────────────────────────────────┐
│ 🤖 AI Explanation               │
│                                 │
│ This vulnerability allows...    │
│                                 │
│ 💡 Suggested Fix:               │
│ Replace this code with...       │
└─────────────────────────────────┘
```

---

## 🚨 Troubleshooting

### "API key is invalid"

**Causes:**
- Key was copied incorrectly
- Key has been revoked
- Trailing spaces in .env file

**Solutions:**
1. Check for typos in the key
2. Ensure no spaces before/after the key
3. Generate a new key on OpenRouter
4. Restart the backend after changes

### "Rate limit exceeded"

**Cause:** Too many requests to OpenRouter

**Solutions:**
- Wait a few minutes
- ASURA automatically tries backup models
- Free tier has limits (refresh daily)
- Upgrade to paid tier if needed

### "AI features not working"

**Check:**
```bash
# 1. Verify .env file exists
dir backend\.env  # Windows
ls backend/.env   # Linux/Mac

# 2. Check if key is set
# Open backend/.env and look for OPENROUTER_API_KEY

# 3. Check backend logs
# Look for API errors in terminal where backend is running
```

**Common fixes:**
1. Restart backend after adding key
2. Clear browser cache
3. Check OpenRouter dashboard for API status
4. Verify key hasn't been deleted

---

## 🆓 Free Tier Limits

OpenRouter's free tier includes:

| Feature | Limit |
|---------|-------|
| Models | 4 free models |
| Requests | Rate-limited (generous) |
| Cost | $0 |
| Credit Card | Not required |
| Expiration | Never (as of Nov 2025) |

**Models used by ASURA (in order):**
1. `meta-llama/llama-3.2-3b-instruct:free` (primary)
2. `qwen/qwen-2-7b-instruct:free` (backup 1)
3. `google/gemini-2.0-flash-exp:free` (backup 2)
4. `deepseek/deepseek-r1:free` (backup 3)

If one model is rate-limited, ASURA automatically tries the next one!

---

## 🔒 Security Best Practices

### ✅ DO:
- Store key in `.env` file
- Add `.env` to `.gitignore` (already done)
- Keep key private
- Rotate key periodically
- Revoke old keys

### ❌ DON'T:
- Commit key to Git
- Share key publicly
- Hardcode key in source code
- Share screenshots with key visible
- Use key in untrusted environments

---

## 💡 Optional: Without AI

ASURA works perfectly **without** AI features:

**✅ Still works:**
- Security scanning (Bandit, Safety, Semgrep)
- Code metrics (Radon, Coverage)
- Health scoring
- Report exports
- All core features

**❌ Won't work:**
- "Explain with AI" button (disabled)
- AI-generated fix suggestions

---

## 📚 Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Supported Models](https://openrouter.ai/models)
- [API Status](https://status.openrouter.ai/)
- [ASURA Documentation](README.md)

---

## 🎉 You're All Set!

Once configured, you can:
- 🤖 Get AI explanations for vulnerabilities
- 💡 Receive secure code fix suggestions
- 📚 Learn security concepts while scanning
- 🚀 Improve your code security knowledge

**Happy scanning!** 🔥

---

**Last Updated**: November 3, 2025  
**Version**: 0.3.0  
**Need Help?** Open an issue: https://github.com/ParthSalunkhe7052/Asura-Security-Scan/issues
