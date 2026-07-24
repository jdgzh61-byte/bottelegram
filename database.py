"""
Database models and management for the Trading Bot.

Handles user data, trading history, alerts, and portfolio information.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database for bot data persistence."""

    def __init__(self, db_path: str = "trading_bot.db"):
        """Initialize database manager."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        language TEXT DEFAULT 'en',
                        timezone TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # User logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        symbol TEXT,
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')

                # Portfolio table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS portfolio (
                        portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        symbol TEXT,
                        quantity REAL,
                        entry_price REAL,
                        current_price REAL,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                        UNIQUE(user_id, symbol)
                    )
                ''')

                # Price alerts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS price_alerts (
                        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        symbol TEXT,
                        alert_type TEXT,
                        target_price REAL,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        triggered_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')

                # Trading history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trading_history (
                        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        symbol TEXT,
                        action TEXT,
                        quantity REAL,
                        price REAL,
                        total REAL,
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                ''')

                # Technical indicators cache table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS technical_indicators (
                        indicator_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT,
                        rsi REAL,
                        macd REAL,
                        bollinger_upper REAL,
                        bollinger_middle REAL,
                        bollinger_lower REAL,
                        moving_avg_20 REAL,
                        moving_avg_50 REAL,
                        moving_avg_200 REAL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(symbol)
                    )
                ''')

                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")

    def add_user(self, user_id: int, username: str, language: str = 'en', timezone: str = 'UTC') -> bool:
        """Add or update user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, language, timezone, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, language, timezone))
                conn.commit()
                logger.info(f"User {user_id} added/updated")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding user: {e}")
            return False

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user details."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting user: {e}")
            return None

    def log_user_action(self, user_id: int, action: str, symbol: str = None, details: str = None) -> bool:
        """Log user action."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_logs (user_id, action, symbol, details)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, action, symbol, details))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error logging action: {e}")
            return False

    def get_user_logs(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user activity logs."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM user_logs 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting logs: {e}")
            return []

    def add_portfolio_item(self, user_id: int, symbol: str, quantity: float, entry_price: float) -> bool:
        """Add or update portfolio item."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO portfolio (user_id, symbol, quantity, entry_price, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, symbol, quantity, entry_price))
                conn.commit()
                logger.info(f"Portfolio item added: {symbol} for user {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding portfolio item: {e}")
            return False

    def get_portfolio(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user portfolio."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM portfolio WHERE user_id = ?', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting portfolio: {e}")
            return []

    def add_price_alert(self, user_id: int, symbol: str, alert_type: str, target_price: float) -> bool:
        """Add price alert."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO price_alerts (user_id, symbol, alert_type, target_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, symbol, alert_type, target_price))
                conn.commit()
                logger.info(f"Alert added: {symbol} at {target_price}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error adding alert: {e}")
            return False

    def get_active_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        """Get active price alerts for user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM price_alerts 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC
                ''', (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting alerts: {e}")
            return []

    def trigger_alert(self, alert_id: int) -> bool:
        """Mark alert as triggered."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE price_alerts 
                    SET is_active = 0, triggered_at = CURRENT_TIMESTAMP 
                    WHERE alert_id = ?
                ''', (alert_id,))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error triggering alert: {e}")
            return False

    def add_trade(self, user_id: int, symbol: str, action: str, quantity: float, price: float, notes: str = None) -> bool:
        """Record trading transaction."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                total = quantity * price
                cursor.execute('''
                    INSERT INTO trading_history (user_id, symbol, action, quantity, price, total, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, symbol, action, quantity, price, total, notes))
                conn.commit()
                logger.info(f"Trade recorded: {action} {quantity} {symbol} at {price}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Error recording trade: {e}")
            return False

    def get_trading_history(self, user_id: int, symbol: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trading history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if symbol:
                    cursor.execute('''
                        SELECT * FROM trading_history 
                        WHERE user_id = ? AND symbol = ?
                        ORDER BY created_at DESC 
                        LIMIT ?
                    ''', (user_id, symbol, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM trading_history 
                        WHERE user_id = ?
                        ORDER BY created_at DESC 
                        LIMIT ?
                    ''', (user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error getting trading history: {e}")
            return []

    def cache_technical_indicators(self, symbol: str, indicators: Dict[str, float]) -> bool:
        """Cache technical indicators."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO technical_indicators 
                    (symbol, rsi, macd, bollinger_upper, bollinger_middle, bollinger_lower, 
                     moving_avg_20, moving_avg_50, moving_avg_200)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    indicators.get('rsi'),
                    indicators.get('macd'),
                    indicators.get('bollinger_upper'),
                    indicators.get('bollinger_middle'),
                    indicators.get('bollinger_lower'),
                    indicators.get('moving_avg_20'),
                    indicators.get('moving_avg_50'),
                    indicators.get('moving_avg_200')
                ))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logger.error(f"Error caching indicators: {e}")
            return False

    def get_technical_indicators(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached technical indicators."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM technical_indicators WHERE symbol = ?', (symbol,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Error getting indicators: {e}")
            return None
