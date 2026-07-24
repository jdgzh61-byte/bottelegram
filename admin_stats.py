"""
Bot Statistics and Admin Module

Tracks bot statistics and provides admin controls.
Monitors users, active sessions, blocked users, and profits/losses.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import sqlite3

logger = logging.getLogger(__name__)


class BotStatistics:
    """Manages bot statistics and analytics."""

    def __init__(self, db_manager):
        """
        Initialize bot statistics.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def get_total_users(self) -> int:
        """Get total number of registered users."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0

    def get_active_users(self, days: int = 7) -> int:
        """
        Get number of active users in last N days.
        
        Args:
            days: Number of days to check
        
        Returns:
            Number of active users
        """
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                date_threshold = datetime.now() - timedelta(days=days)
                cursor.execute('''
                    SELECT COUNT(DISTINCT user_id) FROM user_logs 
                    WHERE timestamp > ?
                ''', (date_threshold.isoformat(),))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return 0

    def get_blocked_users(self) -> int:
        """Get number of blocked users."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM users 
                    WHERE status = 'blocked'
                ''')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting blocked users: {e}")
            return 0

    def get_inactive_users(self, days: int = 30) -> int:
        """
        Get number of inactive users (not active in N days).
        
        Args:
            days: Inactivity threshold
        
        Returns:
            Number of inactive users
        """
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                date_threshold = datetime.now() - timedelta(days=days)
                cursor.execute('''
                    SELECT COUNT(*) FROM users u
                    WHERE u.updated_at < ? OR u.user_id NOT IN 
                    (SELECT DISTINCT user_id FROM user_logs WHERE timestamp > ?)
                ''', (date_threshold.isoformat(), date_threshold.isoformat()))
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting inactive users: {e}")
            return 0

    def get_user_status_breakdown(self) -> Dict[str, int]:
        """Get breakdown of user statuses."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT status, COUNT(*) FROM users 
                    GROUP BY status
                ''')
                results = cursor.fetchall()
                return {row[0]: row[1] for row in results} if results else {}
        except Exception as e:
            logger.error(f"Error getting user status breakdown: {e}")
            return {}

    def get_total_trades(self) -> int:
        """Get total number of trades executed."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM trading_history')
                result = cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting total trades: {e}")
            return 0

    def get_total_profit_loss(self) -> float:
        """Get total profit/loss across all users."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT SUM(total) FROM trading_history WHERE action = "BUY"')
                buys = cursor.fetchone()[0] or 0
                cursor.execute('SELECT SUM(total) FROM trading_history WHERE action = "SELL"')
                sells = cursor.fetchone()[0] or 0
                return sells - buys
        except Exception as e:
            logger.error(f"Error calculating profit/loss: {e}")
            return 0

    def get_user_profit_loss(self, user_id: int) -> float:
        """Get profit/loss for a specific user."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT SUM(total) FROM trading_history 
                    WHERE user_id = ? AND action = "BUY"
                ''', (user_id,))
                buys = cursor.fetchone()[0] or 0
                cursor.execute('''
                    SELECT SUM(total) FROM trading_history 
                    WHERE user_id = ? AND action = "SELL"
                ''', (user_id,))
                sells = cursor.fetchone()[0] or 0
                return sells - buys
        except Exception as e:
            logger.error(f"Error calculating user profit/loss: {e}")
            return 0

    def get_top_traders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top traders by profit."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        u.user_id, 
                        u.username,
                        SUM(CASE WHEN t.action = 'SELL' THEN t.total ELSE 0 END) - 
                        SUM(CASE WHEN t.action = 'BUY' THEN t.total ELSE 0 END) as profit
                    FROM users u
                    LEFT JOIN trading_history t ON u.user_id = t.user_id
                    GROUP BY u.user_id, u.username
                    ORDER BY profit DESC
                    LIMIT ?
                ''', (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting top traders: {e}")
            return []

    def get_trading_stats(self) -> Dict[str, Any]:
        """Get comprehensive trading statistics."""
        return {
            'total_trades': self.get_total_trades(),
            'total_profit_loss': round(self.get_total_profit_loss(), 2),
            'total_users': self.get_total_users(),
            'active_users': self.get_active_users(),
            'inactive_users': self.get_inactive_users(),
            'blocked_users': self.get_blocked_users(),
            'top_traders': self.get_top_traders(5)
        }

    def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get daily statistics for the last N days."""
        try:
            stats = []
            for i in range(days, -1, -1):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                
                with sqlite3.connect(self.db.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT COUNT(*) FROM trading_history 
                        WHERE DATE(created_at) = ?
                    ''', (date_str,))
                    trades = cursor.fetchone()[0] or 0
                    
                    cursor.execute('''
                        SELECT COUNT(DISTINCT user_id) FROM user_logs 
                        WHERE DATE(timestamp) = ?
                    ''', (date_str,))
                    active = cursor.fetchone()[0] or 0
                    
                    stats.append({
                        'date': date_str,
                        'trades': trades,
                        'active_users': active
                    })
            return stats
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return []


class AdminManager:
    """Manages admin operations and user management."""

    def __init__(self, db_manager, admin_ids: List[int] = None):
        """
        Initialize admin manager.
        
        Args:
            db_manager: Database manager instance
            admin_ids: List of admin user IDs
        """
        self.db = db_manager
        self.admin_ids = admin_ids or []
        self.stats = BotStatistics(db_manager)

    def is_admin(self, user_id: int) -> bool:
        """Check if user is an admin."""
        return user_id in self.admin_ids

    def block_user(self, user_id: int) -> bool:
        """Block a user."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET status = 'blocked' WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                logger.info(f"User {user_id} blocked")
                return True
        except Exception as e:
            logger.error(f"Error blocking user: {e}")
            return False

    def unblock_user(self, user_id: int) -> bool:
        """Unblock a user."""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET status = 'active' WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                logger.info(f"User {user_id} unblocked")
                return True
        except Exception as e:
            logger.error(f"Error unblocking user: {e}")
            return False

    def get_admin_panel_stats(self) -> Dict[str, Any]:
        """Get comprehensive admin panel statistics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'trading_stats': self.stats.get_trading_stats(),
            'daily_stats': self.stats.get_daily_stats(7),
            'user_status_breakdown': self.stats.get_user_status_breakdown()
        }

    def generate_admin_report(self) -> str:
        """Generate comprehensive admin report."""
        stats = self.stats.get_trading_stats()
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║          BOT STATISTICS & ADMIN REPORT                   ║
║          Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}              ║
╚══════════════════════════════════════════════════════════╝

📊 USER STATISTICS:
├─ Total Users: {stats['total_users']}
├─ Active Users (7 days): {stats['active_users']}
├─ Inactive Users (30 days): {stats['inactive_users']}
└─ Blocked Users: {stats['blocked_users']}

💱 TRADING STATISTICS:
├─ Total Trades: {stats['total_trades']}
└─ Total Profit/Loss: ${stats['total_profit_loss']:.2f}

🏆 TOP TRADERS:
"""
        for i, trader in enumerate(stats['top_traders'], 1):
            report += f"   {i}. @{trader['username']}: ${trader['profit']:.2f}\n"

        return report

    def get_user_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a user."""
        try:
            user = self.db.get_user(user_id)
            if not user:
                return None

            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM trading_history WHERE user_id = ?', (user_id,))
                trades = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM user_logs WHERE user_id = ?', (user_id,))
                actions = cursor.fetchone()[0]

            return {
                **user,
                'total_trades': trades,
                'total_actions': actions,
                'profit_loss': self.stats.get_user_profit_loss(user_id)
            }
        except Exception as e:
            logger.error(f"Error getting user details: {e}")
            return None
