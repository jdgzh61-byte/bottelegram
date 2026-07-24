# AI Trading Assistant Telegram Bot

A smart Telegram bot powered by OpenAI's GPT models to provide real-time market analysis and trading recommendations.

## Features

✨ **Market Analysis** - Analyze trends for any trading symbol (crypto, stocks, forex)
✨ **AI Recommendations** - Get intelligent trading recommendations based on your questions
✨ **Real-time Insights** - Quick technical analysis and market insights
✨ **Easy to Use** - Simple commands and intuitive interface

## Prerequisites

- Python 3.8+
- Telegram Bot Token (from [BotFather](https://t.me/botfather))
- OpenAI API Key (from [OpenAI Platform](https://platform.openai.com/api-keys))

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jdgzh61-byte/bottelegram.git
   cd bottelegram
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your:
   - `TELEGRAM_BOT_TOKEN`: Get from BotFather on Telegram
   - `OPENAI_API_KEY`: Get from OpenAI platform

5. **Run the bot**
   ```bash
   python main.py
   ```

## Usage

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot and see welcome message | `/start` |
| `/analyze <symbol>` | Analyze market trends for a symbol | `/analyze BTC` |
| `/recommend` | Get AI trading recommendation | `/recommend` |
| `/status` | Check bot and API connectivity | `/status` |
| `/help` | Show all available commands | `/help` |
| `/about` | About the bot and disclaimer | `/about` |

### Examples

```
/analyze BTC          # Analyze Bitcoin trends
/analyze AAPL         # Analyze Apple stock
/analyze EUR/USD      # Analyze Euro/Dollar forex pair
/recommend            # Get personalized trading advice
```

## Project Structure

```
bottelegram/
├── main.py                 # Main bot script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .env                   # Local environment variables (create from .env.example)
├── bot.log               # Bot logs (auto-generated)
└── README.md             # This file
```

## Key Features Explained

### TradingAssistant Class

The core AI engine that handles:
- **Market analysis** using GPT-3.5-turbo
- **Trading recommendations** based on user queries
- **Market data fetching** (placeholder for API integration)

### Bot Commands

- **Message Handlers**: Process user commands and text
- **Session Management**: Track user states and conversations
- **Error Handling**: Comprehensive error logging and user feedback

## Configuration

### OpenAI Model Settings

In `main.py`, you can customize:
```python
self.model = "gpt-3.5-turbo"      # Model to use
self.max_tokens = 500              # Response length
temperature = 0.7                  # Creativity level (0-1)
```

## Logging

All bot activities are logged to `bot.log`. Check this file for:
- Command usage
- AI API calls
- Error messages
- User interactions

## Important Disclaimer

⚠️ **This bot is for educational purposes only. It does NOT provide financial advice.**

- Always consult with a financial advisor before trading
- Past performance does not guarantee future results
- Use at your own risk and never invest more than you can afford to lose
- Do your own research (DYOR) before making any trading decisions

## Troubleshooting

### Bot doesn't start
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Ensure internet connection is active
- Check `bot.log` for error details

### AI analysis not working
- Verify `OPENAI_API_KEY` is valid
- Check OpenAI API credits/usage limits
- Ensure you have internet connectivity

### Commands not responding
- Restart the bot
- Check for error messages in `bot.log`
- Verify Telegram bot token permissions

## Future Enhancements

- 📊 Integration with real market data APIs
- 💾 Database storage for user history
- 📈 Advanced technical indicators
- 🔔 Price alert notifications
- 📱 Portfolio tracking
- 🤖 Multi-language support

## Dependencies

- **pytelegrambotapi**: Telegram bot API wrapper
- **openai**: OpenAI API client
- **pandas**: Data analysis library
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management

## License

MIT License - feel free to use and modify

## Support

For issues and questions:
- Check the [GitHub Issues](https://github.com/jdgzh61-byte/bottelegram/issues)
- Review the bot logs for error messages
- Ensure all API keys are valid and have sufficient credits

---

**Happy Trading! 🚀**

*Remember: This bot is a tool for analysis, not a substitute for professional financial advice.*
