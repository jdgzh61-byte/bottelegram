"""
Multilingual Support Module

Provides translations for the bot in multiple languages.
Easily extensible for additional languages.
"""

TRANSLATIONS = {
    'en': {
        'welcome': '🤖 Welcome to the AI Trading Assistant Bot!\n\nI\'m here to help you analyze market trends and get trading insights.',
        'commands': 'Available commands:',
        'analyze': '📊 Analyze market trends for a symbol',
        'recommend': '💡 Get a trading recommendation',
        'portfolio': '💼 View your portfolio',
        'alerts': '🔔 Manage price alerts',
        'history': '📈 View trading history',
        'help': '📚 Show all available commands',
        'about': 'ℹ️ About this bot',
        
        'example': 'Example: /analyze BTC',
        'invalid_symbol': '❌ Please provide a valid symbol.\nUsage: /analyze <symbol>',
        'analyzing': '🔄 Analyzing {symbol}... Please wait.',
        'market_analysis': '📊 Market Analysis for {symbol}:',
        'error_analysis': '❌ An error occurred during analysis. Please try again.',
        
        'recommend_prompt': '📝 Please describe your trading situation or ask your trading question.',
        'recommendation': '💡 Trading Recommendation:',
        'disclaimer': '⚠️ Remember: This is educational only, not financial advice.',
        
        'portfolio_title': '💼 Your Portfolio:',
        'portfolio_empty': 'Your portfolio is empty. Add holdings with /portfolio add',
        'add_holding': 'Add a holding to your portfolio.',
        'remove_holding': 'Remove a holding from your portfolio.',
        
        'alerts_title': '🔔 Your Price Alerts:',
        'alerts_empty': 'You have no active alerts.',
        'alert_set': '✅ Price alert set for {symbol} at ${price}',
        'alert_triggered': '🚨 Alert! {symbol} reached ${price}',
        
        'history_title': '📈 Trading History:',
        'history_empty': 'No trading history found.',
        'trade_recorded': '✅ Trade recorded: {action} {quantity} {symbol} at ${price}',
        
        'status': '✅ Bot Status:',
        'bot_connection': '🟢 Telegram Connection: Active',
        'ai_connection': '🟢 AI Model: Connected',
        'services': '🟢 Services: Online',
        'last_check': 'Last Check: {time}',
        
        'about_title': 'ℹ️ About AI Trading Assistant Bot',
        'about_text': 'This is an intelligent trading analysis bot powered by OpenAI\'s GPT models.',
        'features': 'Features:',
        'feature_analysis': 'Real-time market analysis',
        'feature_recommend': 'AI-powered trading recommendations',
        'feature_alerts': 'Price alert notifications',
        'feature_portfolio': 'Portfolio tracking',
        
        'setting_language': '🌐 Language set to English',
        'setting_timezone': '🕐 Timezone set to {timezone}',
        
        'error_general': 'Sorry, I didn\'t understand that command.',
        'error_api': 'API error. Please try again later.',
        'error_db': 'Database error. Please try again.',
        
        'bull': '📈 Bullish',
        'bear': '📉 Bearish',
        'neutral': '➡️ Neutral',
    },
    
    'es': {
        'welcome': '🤖 ¡Bienvenido al Bot Asistente de Trading de IA!\n\nEstoy aquí para ayudarte a analizar tendencias de mercado y obtener información sobre trading.',
        'commands': 'Comandos disponibles:',
        'analyze': '📊 Analizar tendencias de mercado para un símbolo',
        'recommend': '💡 Obtener una recomendación de trading',
        'portfolio': '💼 Ver tu portafolio',
        'alerts': '🔔 Gestionar alertas de precio',
        'history': '📈 Ver historial de trading',
        'help': '📚 Mostrar todos los comandos disponibles',
        'about': 'ℹ️ Acerca de este bot',
        
        'example': 'Ejemplo: /analyze BTC',
        'invalid_symbol': '❌ Por favor proporciona un símbolo válido.\nUso: /analyze <símbolo>',
        'analyzing': '🔄 Analizando {symbol}... Por favor espera.',
        'market_analysis': '📊 Análisis de Mercado para {symbol}:',
        'error_analysis': '❌ Ocurrió un error durante el análisis. Por favor intenta de nuevo.',
        
        'recommend_prompt': '📝 Por favor describe tu situación de trading o haz tu pregunta.',
        'recommendation': '💡 Recomendación de Trading:',
        'disclaimer': '⚠️ Recuerda: Esto es solo educativo, no es asesoramiento financiero.',
        
        'portfolio_title': '💼 Tu Portafolio:',
        'portfolio_empty': 'Tu portafolio está vacío. Añade participaciones con /portfolio add',
        
        'alerts_title': '🔔 Tus Alertas de Precio:',
        'alerts_empty': 'No tienes alertas activas.',
        'alert_triggered': '🚨 ¡Alerta! {symbol} alcanzó ${price}',
        
        'status': '✅ Estado del Bot:',
        'bot_connection': '🟢 Conexión Telegram: Activa',
        'ai_connection': '🟢 Modelo IA: Conectado',
        'services': '🟢 Servicios: En línea',
        
        'setting_language': '🌐 Idioma establecido a Español',
        'error_general': 'Disculpa, no entendí ese comando.',
        'bull': '📈 Alcista',
        'bear': '📉 Bajista',
        'neutral': '➡️ Neutral',
    },
    
    'fr': {
        'welcome': '🤖 Bienvenue dans le Bot Assistant de Trading IA!\n\nJe suis ici pour vous aider à analyser les tendances du marché et obtenir des informations commerciales.',
        'commands': 'Commandes disponibles:',
        'analyze': '📊 Analyser les tendances du marché pour un symbole',
        'recommend': '💡 Obtenir une recommandation de trading',
        'portfolio': '💼 Voir votre portefeuille',
        'alerts': '🔔 Gérer les alertes de prix',
        'history': '📈 Afficher l\'historique de trading',
        'help': '📚 Afficher toutes les commandes disponibles',
        'about': 'ℹ️ À propos de ce bot',
        
        'invalid_symbol': '❌ Veuillez fournir un symbole valide.\nUtilisation: /analyze <symbole>',
        'analyzing': '🔄 Analyse de {symbol}... Veuillez patienter.',
        'market_analysis': '📊 Analyse du Marché pour {symbol}:',
        'error_analysis': '❌ Une erreur s\'est produite lors de l\'analyse. Veuillez réessayer.',
        
        'setting_language': '🌐 Langue définie sur Français',
        'error_general': 'Désolé, je n\'ai pas compris cette commande.',
    },
    
    'de': {
        'welcome': '🤖 Willkommen beim KI-Trading-Assistenten Bot!\n\nIch bin hier, um dir bei der Analyse von Markttrends und Handelsinformationen zu helfen.',
        'commands': 'Verfügbare Befehle:',
        'analyze': '📊 Markttrends für ein Symbol analysieren',
        'recommend': '💡 Eine Handelsempfehlung erhalten',
        'portfolio': '💼 Ihr Portfolio anzeigen',
        'alerts': '🔔 Preisalarme verwalten',
        'help': '📚 Alle verfügbaren Befehle anzeigen',
        
        'invalid_symbol': '❌ Bitte geben Sie ein gültiges Symbol an.\nVerwendung: /analyze <Symbol>',
        'analyzing': '🔄 {symbol} wird analysiert... Bitte warten.',
        'market_analysis': '📊 Marktanalyse für {symbol}:',
        
        'setting_language': '🌐 Sprache auf Deutsch eingestellt',
        'error_general': 'Entschuldigung, ich habe diesen Befehl nicht verstanden.',
    },
    
    'pt': {
        'welcome': '🤖 Bem-vindo ao Bot Assistente de Trading de IA!\n\nEstou aqui para ajudá-lo a analisar tendências de mercado e obter informações comerciais.',
        'commands': 'Comandos disponíveis:',
        'analyze': '📊 Analisar tendências de mercado para um símbolo',
        'recommend': '💡 Obter uma recomendação de negociação',
        'portfolio': '💼 Ver seu portfólio',
        'alerts': '🔔 Gerenciar alertas de preço',
        
        'invalid_symbol': '❌ Por favor, forneça um símbolo válido.\nUso: /analyze <símbolo>',
        'analyzing': '🔄 Analisando {symbol}... Por favor aguarde.',
        'market_analysis': '📊 Análise de Mercado para {symbol}:',
        
        'setting_language': '🌐 Idioma definido para Português',
        'error_general': 'Desculpe, não entendi esse comando.',
    },
    
    'ja': {
        'welcome': '🤖 AI取引アシスタントボットへようこそ！\n\n市場トレンドを分析し、取引情報を取得するお手伝いをします。',
        'commands': '利用可能なコマンド:',
        'analyze': '📊 シンボルの市場トレンドを分析する',
        'recommend': '💡 取引推奨を取得する',
        'portfolio': '💼 ポートフォリオを表示',
        'alerts': '🔔 価格アラートを管理',
        
        'invalid_symbol': '❌ 有効なシンボルを入力してください。\n使用方法: /analyze <シンボル>',
        'analyzing': '🔄 {symbol}を分析中... お待ちください。',
        'market_analysis': '{symbol}の📊市場分析:',
        
        'setting_language': '🌐 言語が日本語に設定されました',
        'error_general': '申し訳ありません。そのコマンドが理解できません。',
    },
    
    'zh': {
        'welcome': '🤖 欢迎使用AI交易助手机器人！\n\n我在这里帮助您分析市场趋势并获取交易信息。',
        'commands': '可用命令:',
        'analyze': '📊 分析符号的市场趋势',
        'recommend': '💡 获取交易建议',
        'portfolio': '💼 查看您的投资组合',
        'alerts': '🔔 管理价格警报',
        
        'invalid_symbol': '❌ 请提供有效的符号。\n用法: /analyze <符号>',
        'analyzing': '🔄 正在分析{symbol}...请稍候。',
        'market_analysis': '{symbol}的📊市场分析:',
        
        'setting_language': '🌐 语言已设置为中文',
        'error_general': '抱歉，我不明白这个命令。',
    }
}


class LanguageManager:
    """Manages multilingual support for the bot."""

    def __init__(self, default_language: str = 'en'):
        """
        Initialize language manager.
        
        Args:
            default_language: Default language code (default: 'en')
        """
        self.default_language = default_language
        self.supported_languages = list(TRANSLATIONS.keys())

    def get_text(self, key: str, language: str = None, **kwargs) -> str:
        """
        Get translated text.
        
        Args:
            key: Translation key
            language: Language code (uses default if None)
            **kwargs: Format arguments for string templating
        
        Returns:
            Translated text
        """
        if language is None:
            language = self.default_language
        
        if language not in TRANSLATIONS:
            language = self.default_language
        
        text = TRANSLATIONS[language].get(key, TRANSLATIONS[self.default_language].get(key, f'[{key}]'))
        
        # Format string with provided arguments
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger = __import__('logging').getLogger(__name__)
                logger.warning(f"Missing format argument {e} for key {key}")
        
        return text

    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return self.supported_languages

    def get_language_names(self) -> Dict[str, str]:
        """Get language names in their native language."""
        return {
            'en': 'English',
            'es': 'Español',
            'fr': 'Français',
            'de': 'Deutsch',
            'pt': 'Português',
            'ja': '日本語',
            'zh': '中文'
        }

    def set_language(self, language: str) -> bool:
        """
        Set user's language preference.
        
        Args:
            language: Language code
        
        Returns:
            True if language is supported, False otherwise
        """
        if language in TRANSLATIONS:
            self.default_language = language
            return True
        return False
