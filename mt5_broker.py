"""
MetaTrader 5 Brokerage Integration

Integrates with MetaTrader 5 for real trading, deposits, withdrawals,
and account management connected to brokerage firms.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Note: Install MetaTrader5 with: pip install MetaTrader5

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 not installed. Install with: pip install MetaTrader5")


class MetaTrader5Manager:
    """Manages MetaTrader 5 account and trading operations."""

    def __init__(self, db_manager):
        """
        Initialize MT5 Manager.
        
        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager
        self.mt5_initialized = False
        self.initialize_mt5()

    def initialize_mt5(self) -> bool:
        """Initialize MetaTrader 5 connection."""
        if not MT5_AVAILABLE:
            logger.error("MetaTrader5 library not available")
            return False

        try:
            if mt5.initialize():
                self.mt5_initialized = True
                logger.info("MetaTrader5 initialized successfully")
                return True
            else:
                logger.error(f"MT5 initialization failed: {mt5.last_error()}")
                return False
        except Exception as e:
            logger.error(f"Error initializing MT5: {e}")
            return False

    def connect_account(self, user_id: int, account_number: int, password: str, server: str) -> bool:
        """
        Connect user MT5 account.
        
        Args:
            user_id: User ID
            account_number: MT5 account number
            password: MT5 password
            server: MT5 server name
        
        Returns:
            True if connection successful
        """
        if not self.mt5_initialized:
            return False

        try:
            if mt5.login(account_number, password, server):
                account_info = mt5.account_info()
                if account_info:
                    # Store account info in database
                    self.db.add_user_account(user_id, account_number, server, account_info)
                    logger.info(f"User {user_id} connected to MT5 account {account_number}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error connecting MT5 account: {e}")
            return False

    def get_account_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user's MT5 account information."""
        try:
            if not self.mt5_initialized:
                return None

            account_info = mt5.account_info()
            if account_info:
                return {
                    'login': account_info.login,
                    'balance': account_info.balance,
                    'equity': account_info.equity,
                    'margin': account_info.margin,
                    'free_margin': account_info.free_margin,
                    'margin_level': account_info.margin_level,
                    'server': account_info.server,
                    'currency': account_info.currency,
                    'profit': account_info.profit,
                    'leverage': account_info.leverage,
                    'credit': account_info.credit
                }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
        return None

    def get_positions(self, user_id: int) -> List[Dict[str, Any]]:
        """Get open positions for user's MT5 account."""
        try:
            if not self.mt5_initialized:
                return []

            positions = mt5.positions_get()
            if positions:
                return [
                    {
                        'ticket': pos.ticket,
                        'symbol': pos.symbol,
                        'type': 'BUY' if pos.type == 0 else 'SELL',
                        'volume': pos.volume,
                        'open_price': pos.price_open,
                        'current_price': pos.price_current,
                        'profit': pos.profit,
                        'open_time': datetime.fromtimestamp(pos.time).isoformat(),
                        'commission': pos.commission,
                        'swap': pos.swap
                    }
                    for pos in positions
                ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
        return []

    def open_trade(self, user_id: int, symbol: str, order_type: str, volume: float, price: Optional[float] = None) -> bool:
        """
        Open a trade on MT5.
        
        Args:
            user_id: User ID
            symbol: Trading symbol
            order_type: 'BUY' or 'SELL'
            volume: Trade volume
            price: Entry price (None for market order)
        
        Returns:
            True if trade opened successfully
        """
        if not self.mt5_initialized:
            return False

        try:
            # Get current symbol info
            symbol_info = mt5.symbol_info(symbol)
            if not symbol_info:
                logger.error(f"Symbol {symbol} not found")
                return False

            # Prepare order request
            if order_type.upper() == 'BUY':
                action = mt5.ORDER_TYPE_BUY
            else:
                action = mt5.ORDER_TYPE_SELL

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": action,
                "price": price or mt5.symbol_info_tick(symbol).ask if order_type.upper() == 'BUY' else mt5.symbol_info_tick(symbol).bid,
                "deviation": 20,
                "magic": 234000,
                "comment": f"AI Trading Bot - User {user_id}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Send order
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Trade failed: {result.comment}")
                return False

            # Log trade in database
            self.db.add_trade(user_id, symbol, order_type, volume, price or mt5.symbol_info_tick(symbol).ask)
            logger.info(f"Trade opened: {order_type} {volume} {symbol} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error opening trade: {e}")
            return False

    def close_trade(self, user_id: int, ticket: int) -> bool:
        """
        Close an open trade.
        
        Args:
            user_id: User ID
            ticket: Trade ticket number
        
        Returns:
            True if trade closed successfully
        """
        if not self.mt5_initialized:
            return False

        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"Position {ticket} not found")
                return False

            pos = position[0]
            symbol_info_tick = mt5.symbol_info_tick(pos.symbol)

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "price": symbol_info_tick.bid if pos.type == 0 else symbol_info_tick.ask,
                "deviation": 20,
                "magic": 234000,
                "comment": f"Close trade - User {user_id}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Close failed: {result.comment}")
                return False

            logger.info(f"Trade closed: {ticket} for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return False

    def deposit(self, user_id: int, amount: float) -> bool:
        """
        Process deposit to MT5 account (requires broker integration).
        
        Args:
            user_id: User ID
            amount: Deposit amount
        
        Returns:
            True if deposit initiated
        """
        try:
            # Store deposit request in database for manual processing
            # In production, integrate with payment gateway
            self.db.add_deposit_request(user_id, amount, 'pending')
            logger.info(f"Deposit request created: User {user_id}, Amount {amount}")
            return True
        except Exception as e:
            logger.error(f"Error processing deposit: {e}")
            return False

    def withdraw(self, user_id: int, amount: float) -> bool:
        """
        Process withdrawal from MT5 account.
        
        Args:
            user_id: User ID
            amount: Withdrawal amount
        
        Returns:
            True if withdrawal initiated
        """
        try:
            account_info = self.get_account_info(user_id)
            if not account_info or account_info['balance'] < amount:
                logger.error(f"Insufficient balance for withdrawal")
                return False

            # Store withdrawal request in database for manual processing
            self.db.add_withdrawal_request(user_id, amount, 'pending')
            logger.info(f"Withdrawal request created: User {user_id}, Amount {amount}")
            return True
        except Exception as e:
            logger.error(f"Error processing withdrawal: {e}")
            return False

    def get_trading_history(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trading history from MT5."""
        try:
            if not self.mt5_initialized:
                return []

            deals = mt5.history_deals_get(position=0)
            if deals:
                return [
                    {
                        'ticket': deal.ticket,
                        'symbol': deal.symbol,
                        'type': 'BUY' if deal.type == 0 else 'SELL',
                        'volume': deal.volume,
                        'price': deal.price,
                        'commission': deal.commission,
                        'profit': deal.profit,
                        'time': datetime.fromtimestamp(deal.time).isoformat()
                    }
                    for deal in deals[-limit:]
                ]
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
        return []

    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information from MT5."""
        try:
            if not self.mt5_initialized:
                return None

            info = mt5.symbol_info(symbol)
            if info:
                tick = mt5.symbol_info_tick(symbol)
                return {
                    'symbol': info.name,
                    'ask': tick.ask,
                    'bid': tick.bid,
                    'spread': tick.ask - tick.bid,
                    'contract_size': info.trade_contract_size,
                    'min_volume': info.volume_min,
                    'max_volume': info.volume_max,
                    'step': info.volume_step
                }
        except Exception as e:
            logger.error(f"Error getting symbol info: {e}")
        return None

    def shutdown(self):
        """Shutdown MT5 connection."""
        try:
            if self.mt5_initialized and MT5_AVAILABLE:
                mt5.shutdown()
                self.mt5_initialized = False
                logger.info("MetaTrader5 shutdown")
        except Exception as e:
            logger.error(f"Error shutting down MT5: {e}")
