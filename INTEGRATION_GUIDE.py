"""
COMPLETE INTEGRATION GUIDE
AI Trading Assistant Telegram Bot with MetaTrader 5

This guide explains how to integrate all modules together.
"""

# ============================================================================
# STEP 1: INSTALLATION & SETUP
# ============================================================================

"""
1. Install all dependencies:
   pip install -r requirements.txt

2. Install MetaTrader 5 (optional, for live trading):
   pip install MetaTrader5

3. Set up environment variables:
   - Copy .env.example to .env
   - Add your API keys:
     * TELEGRAM_BOT_TOKEN
     * OPENAI_API_KEY
     * ALPHA_VANTAGE_API_KEY (optional, for stocks)
     * OANDA_API_KEY (optional, for forex)

4. Database:
   - SQLite database is created automatically on first run
   - Location: trading_bot.db
"""

# ============================================================================
# STEP 2: MODULE OVERVIEW
# ============================================================================

"""
📁 PROJECT STRUCTURE:

├── main.py                 # Main bot entry point (UPDATED with all integrations)
├── database.py             # SQLite database management
├── market_data.py          # Real-time market data APIs & indicators
├── alert_manager.py        # Automated price alert system
├── mt5_broker.py           # MetaTrader 5 integration
├── admin_stats.py          # Statistics & admin panel
├── translations.py         # Multilingual support (7 languages)
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
├── .env                    # Your local secrets (DO NOT COMMIT)
├── trading_bot.db          # SQLite database (auto-created)
├── bot.log                 # Bot activity logs
└── README.md               # Documentation
"""

# ============================================================================
# STEP 3: MODULE DEPENDENCIES & IMPORTS
# ============================================================================

"""
In main.py, import all modules in this order:

    import os
    import logging
    from datetime import datetime
    import telebot
    import openai
    from dotenv import load_dotenv
    
    # Import custom modules
    from database import DatabaseManager
    from market_data import MarketDataProvider, TechnicalIndicators
    from alert_manager import AlertManager
    from mt5_broker import MetaTrader5Manager
    from admin_stats import BotStatistics, AdminManager
    from translations import LanguageManager, TRANSLATIONS
"""

# ============================================================================
# STEP 4: INITIALIZATION SEQUENCE
# ============================================================================

"""
Initialize in this order:

    1. Load environment variables:
       load_dotenv()
       bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
       api_key = os.getenv("OPENAI_API_KEY")

    2. Initialize database:
       db_manager = DatabaseManager("trading_bot.db")

    3. Initialize market data:
       market_provider = MarketDataProvider()

    4. Initialize technical indicators:
       indicators = TechnicalIndicators()

    5. Initialize alert manager:
       alert_manager = AlertManager(db_manager)
       alert_manager.start()

    6. Initialize MetaTrader 5 (optional):
       mt5_manager = MetaTrader5Manager(db_manager)

    7. Initialize statistics:
       bot_stats = BotStatistics(db_manager)

    8. Initialize admin manager:
       admin_manager = AdminManager(db_manager, admin_ids=[YOUR_ID])

    9. Initialize language manager:
       language_manager = LanguageManager()

    10. Initialize Telegram bot:
        bot = telebot.TeleBot(bot_token)
"""

# ============================================================================
# STEP 5: COMMAND HANDLERS WITH INTEGRATIONS
# ============================================================================

"""
KEY COMMAND INTEGRATIONS:

@bot.message_handler(commands=['analyze'])
├─ Extract symbol from /analyze <symbol>
├─ Fetch market data (market_provider.get_market_data)
├─ Calculate indicators (TechnicalIndicators.calculate_*)
├─ Generate AI analysis (openai.ChatCompletion)
├─ Log action (db_manager.log_user_action)
└─ Send response to user

@bot.message_handler(commands=['portfolio'])
├─ Get user portfolio (db_manager.get_portfolio)
├─ Fetch current prices for all holdings
├─ Calculate profits/losses
├─ Display portfolio summary

@bot.message_handler(commands=['alerts'])
├─ Show active alerts (db_manager.get_active_alerts)
├─ Allow user to create/remove alerts
├─ Alert manager monitors prices automatically

@bot.message_handler(commands=['trade'])
├─ Connect to MT5 (mt5_manager.open_trade)
├─ Execute trades on brokerage
├─ Track trades in database
└─ Log transaction

@bot.message_handler(commands=['deposit'])
├─ Process deposit request
├─ Store in database with 'pending' status
└─ Notify admin for manual processing

@bot.message_handler(commands=['stats'])  # Admin only
├─ Get statistics (bot_stats.get_trading_stats)
├─ Show user count, active users, blocked users
├─ Display profit/loss summary
└─ Show top traders

@bot.message_handler(commands=['language'])
├─ Show language options
└─ Set user language preference in database
"""

# ============================================================================
# STEP 6: ALERT CALLBACK INTEGRATION
# ============================================================================

"""
Register alert callback to send Telegram notifications:

    def alert_callback(user_id, alert_id, symbol, current_price, target_price, alert_type):
        message = f"🚨 Alert: {symbol} reached ${current_price}"
        bot.send_message(user_id, message)
        db_manager.log_user_action(user_id, 'alert_triggered', symbol)
    
    alert_manager.register_alert_callback(alert_callback)
"""

# ============================================================================
# STEP 7: MULTILINGUAL SUPPORT INTEGRATION
# ============================================================================

"""
Use language manager in all responses:

    # Get user's language from database
    user = db_manager.get_user(user_id)
    language = user.get('language', 'en')
    
    # Get translated text
    welcome_msg = language_manager.get_text('welcome', language)
    error_msg = language_manager.get_text('error_analysis', language, symbol='BTC')
    
    # Allow users to change language
    @bot.message_handler(commands=['language'])
    def set_language(message):
        langs = language_manager.get_language_names()
        markup = telebot.types.InlineKeyboardMarkup()
        for code, name in langs.items():
            markup.add(telebot.types.InlineKeyboardButton(name, callback_data=f'lang_{code}'))
        bot.send_message(message.chat.id, 'Select language:', markup_markup=markup)
"""

# ============================================================================
# STEP 8: METATRADER 5 INTEGRATION
# ============================================================================

"""
Connect user to MT5 and enable trading:

    @bot.message_handler(commands=['connect_account'])
    def connect_mt5(message):
        user_id = message.chat.id
        chat_msg = bot.send_message(user_id, "Enter MT5 account number:")
        bot.register_next_step_handler(chat_msg, process_account_number)
    
    def process_account_number(message):
        account_number = message.text
        chat_msg = bot.send_message(message.chat.id, "Enter password:")
        bot.register_next_step_handler(chat_msg, lambda m: process_password(m, account_number))
    
    def process_password(message, account_number):
        password = message.text
        server = "MetaQuotes-Demo"  # or your broker's server
        
        if mt5_manager.connect_account(message.chat.id, int(account_number), password, server):
            bot.send_message(message.chat.id, "✅ Account connected!")
        else:
            bot.send_message(message.chat.id, "❌ Connection failed")
"""

# ============================================================================
# STEP 9: DATA FLOW EXAMPLE - MARKET ANALYSIS
# ============================================================================

"""
COMPLETE DATA FLOW WHEN USER USES /analyze BTC:

1. User sends: /analyze BTC
2. Bot receives command
3. Extract symbol: BTC
4. Log action: db_manager.log_user_action(user_id, 'analysis_request', 'BTC')
5. Fetch market data: market_data = market_provider.get_crypto_data('BTC')
6. Calculate indicators:
   - RSI = TechnicalIndicators.calculate_rsi(prices)
   - MACD = TechnicalIndicators.calculate_macd(prices)
   - BB = TechnicalIndicators.calculate_bollinger_bands(prices)
   - MA = TechnicalIndicators.calculate_moving_averages(prices)
7. Cache indicators: db_manager.cache_technical_indicators('BTC', indicators)
8. Generate AI analysis using OpenAI with indicators + market data
9. Format response with user's language preference
10. Send response to user in Telegram
11. Log completion: db_manager.log_user_action(user_id, 'analysis_completed', 'BTC')
"""

# ============================================================================
# STEP 10: RUNNING THE BOT
# ============================================================================

"""
Start the bot:

    python main.py

The bot will:
1. Initialize all modules
2. Connect to Telegram
3. Start alert monitoring thread
4. Begin polling for user messages
5. Handle commands and requests
6. Log all activities to bot.log
"""

# ============================================================================
# STEP 11: DEPLOYMENT OPTIONS
# ============================================================================

"""
LOCAL DEPLOYMENT:
- Simply run: python main.py
- Press Ctrl+C to stop

CLOUD DEPLOYMENT (Heroku):
1. Create Procfile:
   web: python main.py

2. Deploy with Git:
   git push heroku main

DOCKER DEPLOYMENT:
1. Create Dockerfile (see below)
2. Build: docker build -t trading-bot .
3. Run: docker run -d trading-bot

CLOUD VPS (AWS, DigitalOcean, etc):
1. SSH into server
2. Clone repository
3. Install Python 3.8+
4. Create .env file
5. Run: nohup python main.py &
"""

# ============================================================================
# STEP 12: ADMIN COMMANDS
# ============================================================================

"""
Admin-only commands (add to main.py):

@bot.message_handler(commands=['stats'])
def admin_stats(message):
    if not admin_manager.is_admin(message.chat.id):
        return
    
    report = admin_manager.generate_admin_report()
    bot.send_message(message.chat.id, report)

@bot.message_handler(commands=['block_user'])
def block_user(message):
    if not admin_manager.is_admin(message.chat.id):
        return
    
    user_id = int(message.text.split()[1])
    admin_manager.block_user(user_id)
    bot.send_message(message.chat.id, f"User {user_id} blocked")

@bot.message_handler(commands=['user_info'])
def user_info(message):
    if not admin_manager.is_admin(message.chat.id):
        return
    
    user_id = int(message.text.split()[1])
    info = admin_manager.get_user_details(user_id)
    bot.send_message(message.chat.id, str(info))
"""

# ============================================================================
# STEP 13: ERROR HANDLING
# ============================================================================

"""
All modules include try-except blocks:

- Database errors are logged and handled gracefully
- Market data API failures fall back to cached data
- MT5 connection errors prevent trades but don't crash bot
- Alert failures are logged but don't stop monitoring
- Telegram sending errors are retried

Check bot.log for detailed error information:
    tail -f bot.log  # Linux/Mac
    type bot.log     # Windows
"""

# ============================================================================
# STEP 14: CONFIGURATION CHECKLIST
# ============================================================================

"""
Before deploying, ensure:

☑ Telegram Bot Token obtained from BotFather
☑ OpenAI API key obtained and has credits
☑ Alpha Vantage API key (optional, for stocks)
☑ OANDA API key (optional, for forex)
☑ .env file created with all secrets
☑ requirements.txt all dependencies installed
☑ MetaTrader 5 installed (if using live trading)
☑ Admin user IDs configured
☑ Database initialized and tested
☑ Alert manager tested with test alerts
☑ Logs are being created successfully
☑ Bot can connect to Telegram
☑ Market data APIs are reachable
"""

# ============================================================================
# STEP 15: TROUBLESHOOTING
# ============================================================================

"""
Common Issues & Solutions:

ISSUE: Bot doesn't respond to commands
FIX: Check TELEGRAM_BOT_TOKEN in .env, restart bot

ISSUE: Market data returns None
FIX: Check API keys, verify internet connection, check rate limits

ISSUE: Alerts not triggering
FIX: Ensure alert_manager.start() called, check bot.log for errors

ISSUE: MT5 connection fails
FIX: Verify account credentials, check MT5 terminal is running, verify server name

ISSUE: Database locked error
FIX: Close all connections, ensure only one bot instance running

ISSUE: Memory leak
FIX: Check for infinite loops, ensure threads are properly closed

For more help, check bot.log file for detailed error messages.
"""

print(__doc__)
