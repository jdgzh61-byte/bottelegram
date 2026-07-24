"""
Alert Manager Module

Handles automated price alerts and notifications.
Monitors prices and triggers alerts when thresholds are reached.
"""

import logging
import threading
import time
from typing import Optional, Dict, List, Callable
from datetime import datetime, timedelta
from market_data import MarketDataProvider

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages price alerts and automated notifications."""

    def __init__(self, db_manager, check_interval: int = 300):
        """
        Initialize alert manager.
        
        Args:
            db_manager: Database manager instance
            check_interval: Check interval in seconds (default 300 = 5 minutes)
        """
        self.db = db_manager
        self.market_data = MarketDataProvider()
        self.check_interval = check_interval
        self.is_running = False
        self.thread = None
        self.alert_callbacks: List[Callable] = []

    def register_alert_callback(self, callback: Callable):
        """
        Register a callback function to be called when alert is triggered.
        
        Args:
            callback: Function to call with (user_id, alert_id, symbol, price, target_price)
        """
        self.alert_callbacks.append(callback)

    def start(self):
        """Start the alert monitoring thread."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._monitor_alerts, daemon=True)
            self.thread.start()
            logger.info("Alert manager started")

    def stop(self):
        """Stop the alert monitoring thread."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Alert manager stopped")

    def _monitor_alerts(self):
        """Monitor alerts in a background thread."""
        while self.is_running:
            try:
                self._check_all_alerts()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")

    def _check_all_alerts(self):
        """Check all active alerts against current market prices."""
        try:
            # Query all active alerts
            with __import__('sqlite3').connect(self.db.db_path) as conn:
                conn.row_factory = __import__('sqlite3').Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT alert_id, user_id, symbol, alert_type, target_price 
                    FROM price_alerts 
                    WHERE is_active = 1
                ''')
                alerts = cursor.fetchall()

            for alert in alerts:
                self._check_alert(dict(alert))

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

    def _check_alert(self, alert: Dict):
        """
        Check if an alert should be triggered.
        
        Args:
            alert: Alert data dictionary
        """
        try:
            # Fetch current price
            market_data = self.market_data.get_market_data(alert['symbol'])
            if not market_data:
                return

            current_price = market_data.get('price', 0)
            target_price = alert['target_price']
            alert_type = alert['alert_type']

            should_trigger = False

            # Check alert conditions
            if alert_type == 'above' and current_price >= target_price:
                should_trigger = True
            elif alert_type == 'below' and current_price <= target_price:
                should_trigger = True
            elif alert_type == 'change' and abs(current_price - target_price) > (target_price * 0.05):
                should_trigger = True

            if should_trigger:
                self._trigger_alert(alert, current_price)

        except Exception as e:
            logger.error(f"Error checking alert {alert.get('alert_id')}: {e}")

    def _trigger_alert(self, alert: Dict, current_price: float):
        """
        Trigger an alert and call registered callbacks.
        
        Args:
            alert: Alert data
            current_price: Current market price
        """
        try:
            # Mark alert as triggered
            self.db.trigger_alert(alert['alert_id'])

            # Call registered callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(
                        user_id=alert['user_id'],
                        alert_id=alert['alert_id'],
                        symbol=alert['symbol'],
                        current_price=current_price,
                        target_price=alert['target_price'],
                        alert_type=alert['alert_type']
                    )
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")

            logger.info(f"Alert triggered for {alert['symbol']} at ${current_price}")

        except Exception as e:
            logger.error(f"Error triggering alert: {e}")

    def create_alert(self, user_id: int, symbol: str, alert_type: str, target_price: float) -> bool:
        """
        Create a new price alert.
        
        Args:
            user_id: User ID
            symbol: Trading symbol
            alert_type: 'above', 'below', or 'change'
            target_price: Target price threshold
        
        Returns:
            True if alert created successfully
        """
        return self.db.add_price_alert(user_id, symbol, alert_type, target_price)

    def get_user_alerts(self, user_id: int) -> List[Dict]:
        """Get all active alerts for a user."""
        return self.db.get_active_alerts(user_id)

    def remove_alert(self, alert_id: int) -> bool:
        """Remove an alert."""
        try:
            with __import__('sqlite3').connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE price_alerts SET is_active = 0 WHERE alert_id = ?', (alert_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error removing alert: {e}")
            return False
