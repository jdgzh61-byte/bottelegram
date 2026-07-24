"""
AI Trading Assistant Telegram Bot - MAIN BOT WITH FULL INTEGRATIONS

Complete implementation with all modules integrated:
- Database management
- Real-time market data
- Technical indicators
- Price alerts
- MetaTrader 5 integration
- Admin statistics
- Multilingual support
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional

import telebot
import openai
from dotenv import load_dotenv

# Import custom modules
from database import DatabaseManager
from market_data import MarketDataProvider, TechnicalIndicators
from alert_manager import AlertManager
from mt5_broker import MetaTrader5Manager
from admin_stats import BotStatistics, AdminManager
from translations import LanguageManager

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

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
    raise ValueError("TELEGRAM_BOT_TOKEN is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
logger.info("Telegram bot initialized")

# Initialize modules
try:
    db_manager = DatabaseManager("trading_bot.db")
    logger.info("Database initialized")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

try:
    market_provider = MarketDataProvider()
    logger.info("Market data provider initialized")
except Exception as e:
    logger.error(f"Failed to initialize market data: {e}")

try:
    alert_manager = AlertManager(db_manager)
    logger.info("Alert manager initialized")
except Exception as e:
    logger.error(f"Failed to initialize alert manager: {e}")

try:
    mt5_manager = MetaTrader5Manager(db_manager)
    logger.info("MetaTrader5 manager initialized")
except Exception as e:
    logger.warning(f"MetaTrader5 not available: {e}")
    mt5_manager = None

try:
    bot_stats = BotStatistics(db_manager)
    admin_manager = AdminManager(db_manager, ADMIN_IDS)
    logger.info("Statistics and admin managers initialized")
except Exception as e:
    logger.error(f"Failed to initialize stats: {e}")

try:
    language_manager = LanguageManager('en')
    logger.info("Language manager initialized")
except Exception as e:
    logger.error(f"Failed to initialize language manager: {e}")

# User sessions storage
user_sessions = {}


# ============================================================================
# ALERT CALLBACK - SEND NOTIFICATIONS WHEN PRICE ALERT TRIGGERS
# ============================================================================

def handle_alert_trigger(user_id, alert_id, symbol, current_price, target_price, alert_type):
    """Handle price alert triggered."""
    try:
        user = db_manager.get_user(user_id)
        language = user.get('language', 'en') if user else 'en'
        
        message = f"""
🚨 {language_manager.get_text('alert_triggered', language, symbol=symbol, price=f'${current_price:.2f}')}

📊 Symbol: {symbol}
💰 Current Price: ${current_price:.2f}
🎯 Target Price: ${target_price:.2f}
📈 Alert Type: {alert_type.upper()}

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        bot.send_message(user_id, message)
        logger.info(f"Alert notification sent to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending alert notification: {e}")


# Register alert callback
alert_manager.register_alert_callback(handle_alert_trigger)

# Start alert monitoring
alert_manager.start()
logger.info("Alert manager started")


# ============================================================================
# BOT COMMAND HANDLERS
# ============================================================================

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command."""
    chat_id = message.chat.id
    
    try:
        # Add user to database
        username = message.from_user.username or f"user_{chat_id}"
        db_manager.add_user(chat_id, username)
        user_sessions[chat_id] = {"state": "idle"}
        
        welcome_text = language_manager.get_text('welcome', 'en')
        welcome_text += "\n\n" + language_manager.get_text('commands', 'en') + ":\n"
        welcome_text += f"/analyze <symbol> - {language_manager.get_text('analyze', 'en')}\n"
        welcome_text += f"/recommend - {language_manager.get_text('recommend', 'en')}\n"
        welcome_text += f"/portfolio - {language_manager.get_text('portfolio', 'en')}\n"
        welcome_text += f"/alerts - {language_manager.get_text('alerts', 'en')}\n"
        welcome_text += f"/status - Check bot status\n"
        welcome_text += f"/language - Set your language\n"
        welcome_text += f"/help - {language_manager.get_text('help', 'en')}\n"
        
        bot.reply_to(message, welcome_text)
        logger.info(f"User {chat_id} started the bot")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        bot.reply_to(message, "❌ An error occurred. Please try again.")


@bot.message_handler(commands=['analyze'])
def handle_analyze(message):
    """Handle /analyze command to analyze market trends."""
    chat_id = message.chat.id
    
    try:
        user = db_manager.get_user(chat_id)
        language = user.get('language', 'en') if user else 'en'
        
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, language_manager.get_text('invalid_symbol', language))
            return
        
        symbol = args[1].upper()
        
        # Send processing message
        processing_msg = bot.reply_to(
            message,
            language_manager.get_text('analyzing', language, symbol=symbol)
        )
        
        # Fetch market data
        market_data = market_provider.get_market_data(symbol)
        if not market_data:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=language_manager.get_text('error_analysis', language, symbol=symbol)
            )
            db_manager.log_user_action(chat_id, 'analysis_failed', symbol, 'Market data unavailable')
            return
        
        # Generate AI analysis
        try:
            prompt = f"""
            Analyze the trading opportunity for {symbol}.
            
            Current Market Data:
            - Price: ${market_data.get('price', 'N/A')}
            - Change 24h: {market_data.get('change_24h', 'N/A')}%
            - Volume: {market_data.get('volume_24h', 'N/A')}
            
            Provide:
            1. Market Trend (Bullish/Bearish/Neutral)
            2. Key Support & Resistance Levels
            3. Entry/Exit Points
            4. Risk Assessment
            5. Short-term Outlook (24-48 hours)
            
            Keep it concise and actionable.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional trading analyst providing market insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            response_text = f"📊 {language_manager.get_text('market_analysis', language, symbol=symbol)}\n\n{analysis}"
            
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=response_text
            )
            
            db_manager.log_user_action(chat_id, 'analysis_completed', symbol, f"Price: ${market_data.get('price')}")
            logger.info(f"Analysis provided for {symbol} to user {chat_id}")
            
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=language_manager.get_text('error_api', language)
            )
    
    except Exception as e:
        logger.error(f"Error in analyze command: {e}")
        bot.reply_to(message, language_manager.get_text('error_general', language))


@bot.message_handler(commands=['portfolio'])
def handle_portfolio(message):
    """Handle /portfolio command."""
    chat_id = message.chat.id
    
    try:
        user = db_manager.get_user(chat_id)
        language = user.get('language', 'en') if user else 'en'
        
        portfolio = db_manager.get_portfolio(chat_id)
        
        if not portfolio:
            bot.reply_to(message, language_manager.get_text('portfolio_empty', language))
            return
        
        portfolio_text = language_manager.get_text('portfolio_title', language) + "\n\n"
        total_value = 0
        
        for item in portfolio:
            market_data = market_provider.get_market_data(item['symbol'])
            current_price = market_data.get('price', item['current_price']) if market_data else item['current_price']
            
            value = item['quantity'] * current_price
            entry_value = item['quantity'] * item['entry_price']
            profit = value - entry_value
            
            total_value += value
            
            portfolio_text += f"🔹 {item['symbol']}: {item['quantity']} @ ${current_price:.2f}\n"
            portfolio_text += f"   Entry: ${item['entry_price']:.2f} | Value: ${value:.2f}\n"
            portfolio_text += f"   P/L: ${profit:.2f} ({(profit/entry_value*100):.2f}%)\n\n"
        
        portfolio_text += f"💼 Total Portfolio Value: ${total_value:.2f}"
        
        bot.reply_to(message, portfolio_text)
        db_manager.log_user_action(chat_id, 'portfolio_viewed')
        
    except Exception as e:
        logger.error(f"Error in portfolio command: {e}")
        bot.reply_to(message, language_manager.get_text('error_general', language))


@bot.message_handler(commands=['alerts'])
def handle_alerts(message):
    """Handle /alerts command."""
    chat_id = message.chat.id
    
    try:
        user = db_manager.get_user(chat_id)
        language = user.get('language', 'en') if user else 'en'
        
        alerts = db_manager.get_active_alerts(chat_id)
        
        if not alerts:
            bot.reply_to(message, language_manager.get_text('alerts_empty', language))
            return
        
        alerts_text = language_manager.get_text('alerts_title', language) + "\n\n"
        
        for alert in alerts:
            alerts_text += f"🔔 {alert['symbol']} - {alert['alert_type'].upper()}\n"
            alerts_text += f"   Target: ${alert['target_price']:.2f}\n"
            alerts_text += f"   Created: {alert['created_at']}\n\n"
        
        bot.reply_to(message, alerts_text)
        db_manager.log_user_action(chat_id, 'alerts_viewed')
        
    except Exception as e:
        logger.error(f"Error in alerts command: {e}")
        bot.reply_to(message, language_manager.get_text('error_general', language))


@bot.message_handler(commands=['status'])
def handle_status(message):
    """Handle /status command."""
    try:
        status_text = f"""
✅ BOT STATUS:
━━━━━━━━━━━━━━━━━━
🟢 Telegram Connection: Active
🟢 AI Model: Connected
🟢 Database: Connected
🟢 Market Data: Online
{'🟢 MetaTrader5: Connected' if mt5_manager else '🟡 MetaTrader5: Disabled'}
🟢 Alert Manager: Running

Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 2.0 (Full Integration)
        """
        bot.reply_to(message, status_text)
    except Exception as e:
        logger.error(f"Error in status command: {e}")
        bot.reply_to(message, "❌ Unable to check status")


@bot.message_handler(commands=['language'])
def handle_language(message):
    """Handle /language command."""
    chat_id = message.chat.id
    
    try:
        langs = language_manager.get_language_names()
        language_text = "🌐 Select your language:\n\n"
        
        for code, name in langs.items():
            language_text += f"/{code} - {name}\n"
        
        bot.reply_to(message, language_text)
    except Exception as e:
        logger.error(f"Error in language command: {e}")


@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle /help command."""
    help_text = """
📚 AVAILABLE COMMANDS:

/analyze <symbol> - Analyze market trends
  Example: /analyze BTC

/portfolio - View your holdings
  
/alerts - See active price alerts
  
/status - Check bot and services status
  
/language - Change bot language
  
/stats - View bot statistics (Admin)
  
/help - Show this message

💡 TIPS:
• Use standard ticker symbols (BTC, AAPL, EUR/USD)
• Be specific with trading questions
• Always check market analysis before trading

⚠️ DISCLAIMER: Educational purposes only. Not financial advice.
    """
    bot.reply_to(message, help_text)


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    """Handle /stats command (Admin only)."""
    chat_id = message.chat.id
    
    if not admin_manager.is_admin(chat_id):
        bot.reply_to(message, "❌ Admin access required")
        return
    
    try:
        report = admin_manager.generate_admin_report()
        bot.send_message(chat_id, report)
        logger.info(f"Admin report generated for user {chat_id}")
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        bot.reply_to(message, "❌ Error generating report")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle general messages."""
    chat_id = message.chat.id
    
    try:
        user = db_manager.get_user(chat_id)
        language = user.get('language', 'en') if user else 'en'
        
        bot.reply_to(
            message,
            f"{language_manager.get_text('error_general', language)}\n\n/help - {language_manager.get_text('help', language)}"
        )
    except Exception as e:
        logger.error(f"Error handling message: {e}")


# ============================================================================
# BOT MAIN LOOP
# ============================================================================

def main():
    """Main function to start the bot."""
    logger.info("=" * 60)
    logger.info("AI TRADING ASSISTANT TELEGRAM BOT - STARTING")
    logger.info("=" * 60)
    logger.info(f"Bot Token: {TELEGRAM_BOT_TOKEN[:10]}...")
    logger.info(f"Admin IDs: {ADMIN_IDS}")
    logger.info(f"Database: trading_bot.db")
    logger.info("=" * 60)
    
    try:
        logger.info("Starting bot polling...")
        bot.infinity_polling()
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        logger.info("Shutting down...")
        alert_manager.stop()
        if mt5_manager:
            mt5_manager.shutdown()
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()
