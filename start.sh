#!/bin/bash

# Start virtual display
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Start the bot
python bot/telegram_bot.py
