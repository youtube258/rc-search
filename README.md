
# RC Info Telegram Bot — Railway 1‑Click Deploy

This repo is ready to deploy on Railway.

## Files
- `bot.py` — Your full bot code
- `requirements.txt` — Python dependencies
- `Procfile` — Tells Railway how to run the bot

## Deploy (GitHub → Railway)
1. Create a **new GitHub repo** and upload these three files.
2. Go to **Railway.app → New Project → Deploy from GitHub Repo** and select your repo.
3. No env vars are required because `BOT_TOKEN` is already inside `bot.py` (you can change it there if needed).
4. Click **Deploy**. Open **Logs** to confirm: `🤖 Bot is running...`
5. Go to Telegram and send **/start** to your bot.

> Recommended: In production, move the token to a Railway **Environment Variable** named `BOT_TOKEN` and read it in code. But for 1‑click, this repo works as‑is.
