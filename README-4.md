# 🎙️ Denji World TTS Bot

Text → Voice Note bot for Telegram with group membership verification.

## Features
- `/start` → Group join prompt with inline button
- ✅ Verify button checks membership in real-time
- 🎙️ Text to voice note using gTTS (Google)
- ⚠️ Auto re-verification if user leaves group

---

## Setup Guide

### Step 1 — BotFather
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. `/newbot` → give name & username
3. Copy your **BOT_TOKEN**

### Step 2 — Make bot admin of your group
1. Open `t.me/thats_me_denji`
2. Add your bot as **Admin** (needs at least "Read Messages" permission)
   - This is required so the bot can check membership!

### Step 3 — GitHub Upload
```
denji-tts-bot/
├── api/
│   └── webhook.py      ← Vercel serverless handler
├── bot.py              ← Local polling (for testing)
├── set_webhook.py      ← Run once after deploy
├── requirements.txt
├── vercel.json
└── README.md
```
Push all files to a new GitHub repo.

### Step 4 — Vercel Deploy
1. Go to [vercel.com](https://vercel.com) → New Project
2. Import your GitHub repo
3. Add Environment Variable:
   - Key: `BOT_TOKEN`
   - Value: your token from BotFather
4. Deploy!

### Step 5 — Set Webhook
After deploy, run once on your phone (Termux):
```bash
python set_webhook.py
```
Enter your BOT_TOKEN and Vercel URL when asked.

---

## Local Testing (Termux)
```bash
pip install python-telegram-bot gTTS
BOT_TOKEN=your_token python bot.py
```

---

## Flow
```
User /start
  ↓
Not in group? → Show "Join" + "Verify" buttons
  ↓
User joins → clicks Verify
  ↓
Bot checks membership via Telegram API
  ↓
✅ Verified → Welcome message
  ↓
User sends text → Bot replies with voice note 🎙️
  ↓
User leaves group → Next message shows verify prompt again
```
