#!/usr/bin/env python3
"""
Run this ONCE after Vercel deployment to register webhook.
Usage: python set_webhook.py
"""
import urllib.request
import json
import os

BOT_TOKEN = input("Enter your BOT_TOKEN: ").strip()
VERCEL_URL = input("Enter your Vercel URL (e.g. https://denji-tts-bot.vercel.app): ").strip()

webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
data = json.dumps({"url": f"{VERCEL_URL}/api/webhook"}).encode()

req = urllib.request.Request(
    webhook_url,
    data=data,
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(req) as res:
    print(res.read().decode())
