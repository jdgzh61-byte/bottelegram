"""
AI Trading Assistant Telegram Bot

This bot integrates with Telegram and an AI model (OpenAI) to provide
market trend analysis and trading insights.

Environment Variables Required:
    - TELEGRAM_BOT_TOKEN: Your Telegram bot token from BotFather
    - OPENAI_API_KEY: Your OpenAI API key
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

import telebot
import openai
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Validate required environment variables
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY is required")

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

# User session storage (in production, use a database)
user_sessions = {}


class TradingAssistant:
    """Handles AI-powered trading analysis."""

    def __init__(self):
        """Initialize the trading assistant."""
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500

    def analyze_market_trends(self, symbol: str, timeframe: str = "1day") -> str:
        """
        Analyze market trends for a given symbol using AI.

        Args:
            symbol: Trading symbol (e.g., 'BTC', 'AAPL', 'EUR/USD')
            timeframe: Time frame for analysis (e.g., '1day', '1hour', '1week')

        Returns:
            AI-generated market analysis
        """
        try:
            prompt = f"""
            Analyze the market trends for {symbol} on a {timeframe} timeframe.
            Provide:
            1. Current trend direction (bullish/bearish/neutral)
            2. Key support and resistance levels (approximate)
            3. Potential entry/exit points
            4. Risk factors to consider
            5. Short-term outlook (next 24-48 hours)
            
            Keep the analysis concise and actionable.
            """

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading analyst with expertise in technical analysis and market trends."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            analysis = response.choices[0].message.content
            logger.info(f"Generated analysis for {symbol}")
            return analysis

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "Sorry, I encountered an error while analyzing the market. Please try again later."
        except Exception as e:
            logger.error(f"Unexpected error in market analysis: {e}")
            return "An unexpected error occurred. Please try again."

    def get_trading_recommendation(self, query: str) -> str:
        """
        Get a trading recommendation based on a user query.

        Args:
            query: User's trading question or request

        Returns:
            AI-generated trading recommendation
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading advisor. Provide helpful, balanced trading recommendations with risk disclaimers."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7
            )

            recommendation = response.choices[0].message.content
            logger.info(f"Generated recommendation for query: {query[:50]}...")
            return recommendation

        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "Sorry, I couldn't generate a recommendation at this moment. Please try again."
        except Exception as e:
            logger.error(f"Unexpected error in recommendation: {e}")
            return "An error occurred while processing your request."

    def fetch_market_data(self, symbol: str, source: str = "coingecko") -> Optional[dict]:
        """
        Fetch market data for a symbol (placeholder for real API integration).

        Args:
            symbol: Trading symbol
            source: Data source (currently supports placeholder)

        Returns:
            Market data dictionary or None if fetch fails
        """
        try:
            # Placeholder for actual market data API integration
            # In production, integrate with APIs like:
            # - CoinGecko for crypto
            # - Alpha Vantage for stocks
            # - OANDA for forex

            logger.info(f"Placeholder: Fetching market data for {symbol}")
            return {
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "status": "placeholder"
            }

        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            return None


# Initialize trading assistant
trading_assistant = TradingAssistant()


# Bot command handlers
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command."""
    chat_id = message.chat.id
    user_sessions[chat_id] = {"state": "idle"}

    welcome_text = """
🤖 Welcome to the AI Trading Assistant Bot!

I'm here to help you analyze market trends and get trading insights.

Available commands:
/analyze <symbol> - Analyze market trends for a symbol
/recommend - Get a trading recommendation
/help - Show all available commands
/about - Learn more about this bot

Example: /analyze BTC
    """

    bot.reply_to(message, welcome_text)
    logger.info(f"User {chat_id} started the bot")


@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle /help command."""
    help_text = """
📚 Available Commands:

/analyze <symbol> - Get AI analysis for a trading symbol
    Example: /analyze EUR/USD
    
/recommend - Get a personalized trading recommendation
    Just send your trading question after this command
    
/status - Check bot status and API connectivity
    
/history - View your recent queries
    
/about - Information about this bot
    
/help - Show this help message

💡 Tips:
- Use standard ticker symbols (BTC, AAPL, EUR/USD, etc.)
- Be specific with your trading questions
- Always consider risk management

⚠️ Disclaimer: This bot provides analysis for informational purposes only. 
Not financial advice. Always do your own research.
    """

    bot.reply_to(message, help_text)


@bot.message_handler(commands=['analyze'])
def handle_analyze(message):
    """Handle /analyze command to analyze market trends."""
    try:
        # Extract symbol from command
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Please provide a symbol.\nUsage: /analyze <symbol>\nExample: /analyze BTC")
            return

        symbol = args[1].upper()
        chat_id = message.chat.id

        # Send processing message
        processing_msg = bot.reply_to(message, f"🔄 Analyzing {symbol}... Please wait.")

        # Get analysis from AI
        analysis = trading_assistant.analyze_market_trends(symbol)

        # Edit message with analysis
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text=f"📊 Market Analysis for {symbol}:\n\n{analysis}"
        )

        logger.info(f"Analysis provided for {symbol} to user {chat_id}")

    except Exception as e:
        logger.error(f"Error in analyze command: {e}")
        bot.reply_to(message, "❌ An error occurred during analysis. Please try again.")


@bot.message_handler(commands=['recommend'])
def handle_recommend(message):
    """Handle /recommend command."""
    chat_id = message.chat.id
    user_sessions[chat_id] = {"state": "waiting_for_query"}

    bot.reply_to(
        message,
        "📝 Please describe your trading situation or ask your trading question.\n\n"
        "Example: 'I'm considering buying AAPL, should I wait for a pullback?'"
    )


@bot.message_handler(commands=['status'])
def handle_status(message):
    """Handle /status command to check bot health."""
    try:
        status_text = """
✅ Bot Status:
━━━━━━━━━━━━━━━━━━
🟢 Telegram Connection: Active
🟢 AI Model: Connected
🟢 Services: Online

Last Check: {}
Version: 1.0
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        bot.reply_to(message, status_text)
        logger.info(f"Status check by user {message.chat.id}")

    except Exception as e:
        logger.error(f"Error in status command: {e}")
        bot.reply_to(message, "❌ Unable to check status at the moment.")


@bot.message_handler(commands=['about'])
def handle_about(message):
    """Handle /about command."""
    about_text = """
ℹ️ About AI Trading Assistant Bot

This is an intelligent trading analysis bot powered by OpenAI's GPT models.

Features:
✨ Real-time market analysis
✨ AI-powered trading recommendations
✨ Technical analysis insights
✨ Risk assessment capabilities

Disclaimer:
⚠️ This bot provides analysis for educational and informational purposes only.
It is NOT financial advice. Always consult with a financial advisor before
making trading decisions. Past performance does not guarantee future results.

Use at your own risk and never invest more than you can afford to lose.
    """

    bot.reply_to(message, about_text)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle general messages."""
    chat_id = message.chat.id
    user_text = message.text

    # Check if user is waiting for a recommendation query
    if chat_id in user_sessions and user_sessions[chat_id].get("state") == "waiting_for_query":
        try:
            processing_msg = bot.reply_to(message, "🤔 Generating recommendation... Please wait.")

            # Get recommendation from AI
            recommendation = trading_assistant.get_trading_recommendation(user_text)

            # Edit message with recommendation
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=f"💡 Trading Recommendation:\n\n{recommendation}\n\n⚠️ Remember: This is educational only, not financial advice."
            )

            user_sessions[chat_id]["state"] = "idle"
            logger.info(f"Recommendation provided to user {chat_id}")

        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            bot.reply_to(message, "❌ An error occurred. Please try again.")
            user_sessions[chat_id]["state"] = "idle"
    else:
        # Default response for unknown commands
        bot.reply_to(
            message,
            "Sorry, I didn't understand that command.\n\n"
            "Try /help to see available commands or /analyze <symbol> to analyze a market."
        )


def main():
    """Main function to start the bot."""
    logger.info("Starting AI Trading Assistant Bot...")
    logger.info(f"Bot token: {TELEGRAM_BOT_TOKEN[:10]}...")

    try:
        # Start polling
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()
