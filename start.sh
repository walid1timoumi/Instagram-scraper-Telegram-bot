#!/bin/bash

echo "🧹 Cleaning previous Xvfb lock (if exists)..."
rm -f /tmp/.X99-lock

echo "🚀 Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

echo "▶️ Launching bot..."
python bot/telegram_bot.py
