from typing import Dict, List, Optional, Any, Tuple, Callable
import logging
from datetime import datetime
import pytdx
from .base_broker import BaseBroker
from ..models.order import Order, OrderStatus
from ..models.position import Position
from ..models.account import Account
from ..models.trade import Trade
from ..models.market_data import MarketData
import time

class TDXBroker(BaseBroker):
    """通达信接口实现"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化通达信接口
        
        Args:
            config: 配置信息，包含以下字段：
                - server: 服务器地址
                - port: 端口号
                - account: 账号
                - password: 密码
                - exe_path: 通达信客户端路径
        """
        super().__init__("TDX", config)
        self.client = None
        self.connected = False
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        连接到通达信交易接口
        
        Returns:
            bool: 是否连接成功
        """
        try:
            # 创建通达信接口实例
            self.client = pytdx.TdxHq_API()
            
            # 连接到服务器
            server = self.config.get('server', '119.147.212.81')
            port = self.config.get('port', 7709)
            
            if not self.client.connect(server, port):
                self.logger.error(f"连接通达信服务器失败: {server}:{port}")
                return False
                
            self.connected = True
            self.logger.info("成功连接到通达信服务器")
            return True
            
        except Exception as e:
            self.logger.error(f"连接通达信服务器异常: {str(e)}")
            return False
            
    def disconnect(self) -> bool:
        """
        断开与通达信交易接口的连接
        
        Returns:
            bool: 是否断开成功
        """
        try:
            if self.client:
                self.client.disconnect()
                self.connected = False
                self.logger.info("已断开通达信服务器连接")
                return True
            return True
        except Exception as e:
            self.logger.error(f"断开通达信服务器连接异常: {str(e)}")
            return False
            
    def get_account_info(self) -> Optional[Account]:
        """
        获取账户信息
        
        Returns:
            Optional[Account]: 账户信息，如果获取失败则返回None
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return None
                
            # 获取账户信息
            account_info = self.client.get_account_info()
            if not account_info:
                self.logger.error("获取账户信息失败")
                return None
                
            # 转换为Account对象
            account = Account(
                account_id=account_info.get('account'),
                total_asset=account_info.get('total_asset', 0.0),
                available_cash=account_info.get('available_cash', 0.0),
                frozen_cash=account_info.get('frozen_cash', 0.0),
                market_value=account_info.get('market_value', 0.0),
                update_time=datetime.now()
            )
            
            return account
            
        except Exception as e:
            self.logger.error(f"获取账户信息异常: {str(e)}")
            return None 

    def place_order(self, order: Order) -> bool:
        """
        下单
        
        Args:
            order: 订单对象
            
        Returns:
            bool: 是否下单成功
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return False
                
            # 构建下单参数
            order_params = {
                'price': order.price,
                'volume': order.volume,
                'direction': 'buy' if order.direction == 'BUY' else 'sell',
                'order_type': 'limit' if order.order_type == 'LIMIT' else 'market',
                'symbol': order.symbol,
                'exchange': order.exchange
            }
            
            # 发送订单
            order_id = self.client.send_order(**order_params)
            if not order_id:
                self.logger.error("下单失败")
                return False
                
            # 更新订单ID
            order.order_id = order_id
            order.status = OrderStatus.SUBMITTED
            order.create_time = datetime.now()
            
            self.logger.info(f"下单成功: {order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"下单异常: {str(e)}")
            return False
            
    def cancel_order(self, order: Order) -> bool:
        """
        撤单
        
        Args:
            order: 订单对象
            
        Returns:
            bool: 是否撤单成功
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return False
                
            # 撤单
            result = self.client.cancel_order(order.order_id)
            if not result:
                self.logger.error(f"撤单失败: {order.order_id}")
                return False
                
            order.status = OrderStatus.CANCELLED
            order.update_time = datetime.now()
            
            self.logger.info(f"撤单成功: {order.order_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"撤单异常: {str(e)}")
            return False
            
    def get_order_status(self, order: Order) -> bool:
        """
        查询订单状态
        
        Args:
            order: 订单对象
            
        Returns:
            bool: 是否查询成功
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return False
                
            # 查询订单状态
            order_info = self.client.get_order_info(order.order_id)
            if not order_info:
                self.logger.error(f"查询订单状态失败: {order.order_id}")
                return False
                
            # 更新订单状态
            status_map = {
                'submitted': OrderStatus.SUBMITTED,
                'accepted': OrderStatus.ACCEPTED,
                'rejected': OrderStatus.REJECTED,
                'cancelled': OrderStatus.CANCELLED,
                'filled': OrderStatus.FILLED,
                'partial_filled': OrderStatus.PARTIALLY_FILLED
            }
            
            order.status = status_map.get(order_info.get('status'), OrderStatus.UNKNOWN)
            order.filled_volume = order_info.get('filled_volume', 0)
            order.filled_price = order_info.get('filled_price', 0.0)
            order.update_time = datetime.now()
            
            return True
            
        except Exception as e:
            self.logger.error(f"查询订单状态异常: {str(e)}")
            return False 

    def get_positions(self) -> List[Position]:
        """
        获取持仓信息
        
        Returns:
            List[Position]: 持仓列表
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return []
                
            # 获取持仓信息
            positions = self.client.get_positions()
            if not positions:
                return []
                
            # 转换为Position对象列表
            position_list = []
            for pos in positions:
                position = Position(
                    symbol=pos.get('symbol'),
                    exchange=pos.get('exchange'),
                    volume=pos.get('volume', 0),
                    available_volume=pos.get('available_volume', 0),
                    cost_price=pos.get('cost_price', 0.0),
                    market_price=pos.get('market_price', 0.0),
                    market_value=pos.get('market_value', 0.0),
                    profit_loss=pos.get('profit_loss', 0.0),
                    profit_loss_ratio=pos.get('profit_loss_ratio', 0.0),
                    update_time=datetime.now()
                )
                position_list.append(position)
                
            return position_list
            
        except Exception as e:
            self.logger.error(f"获取持仓信息异常: {str(e)}")
            return []
            
    def get_market_data(self, symbol: str, exchange: str) -> Optional[MarketData]:
        """
        获取市场数据
        
        Args:
            symbol: 股票代码
            exchange: 交易所代码
            
        Returns:
            Optional[MarketData]: 市场数据，如果获取失败则返回None
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return None
                
            # 获取市场数据
            market_data = self.client.get_security_quotes([(exchange, symbol)])
            if not market_data:
                self.logger.error(f"获取市场数据失败: {symbol}")
                return None
                
            data = market_data[0]
            
            # 转换为MarketData对象
            market_data_obj = MarketData(
                symbol=symbol,
                exchange=exchange,
                open_price=data.get('open', 0.0),
                high_price=data.get('high', 0.0),
                low_price=data.get('low', 0.0),
                close_price=data.get('close', 0.0),
                volume=data.get('volume', 0),
                amount=data.get('amount', 0.0),
                bid_price=data.get('bid_price', 0.0),
                bid_volume=data.get('bid_volume', 0),
                ask_price=data.get('ask_price', 0.0),
                ask_volume=data.get('ask_volume', 0),
                update_time=datetime.now()
            )
            
            return market_data_obj
            
        except Exception as e:
            self.logger.error(f"获取市场数据异常: {str(e)}")
            return None
            
    def get_trades(self, start_time: datetime, end_time: datetime) -> List[Trade]:
        """
        获取成交记录
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            List[Trade]: 成交记录列表
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return []
                
            # 获取成交记录
            trades = self.client.get_trade_history(start_time, end_time)
            if not trades:
                return []
                
            # 转换为Trade对象列表
            trade_list = []
            for trade in trades:
                trade_obj = Trade(
                    trade_id=trade.get('trade_id'),
                    order_id=trade.get('order_id'),
                    symbol=trade.get('symbol'),
                    exchange=trade.get('exchange'),
                    direction=trade.get('direction'),
                    price=trade.get('price', 0.0),
                    volume=trade.get('volume', 0),
                    amount=trade.get('amount', 0.0),
                    trade_time=datetime.fromtimestamp(trade.get('trade_time', 0)),
                    commission=trade.get('commission', 0.0),
                    tax=trade.get('tax', 0.0)
                )
                trade_list.append(trade_obj)
                
            return trade_list
            
        except Exception as e:
            self.logger.error(f"获取成交记录异常: {str(e)}")
            return []
            
    def get_historical_data(self, symbol: str, exchange: str, 
                          start_date: datetime, end_date: datetime,
                          period: str = '1d') -> List[MarketData]:
        """
        获取历史K线数据
        
        Args:
            symbol: 股票代码
            exchange: 交易所代码
            start_date: 开始日期
            end_date: 结束日期
            period: K线周期，可选值：1m, 5m, 15m, 30m, 1h, 1d, 1w, 1M
            
        Returns:
            List[MarketData]: K线数据列表
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return []
                
            # 转换周期格式
            period_map = {
                '1m': 1, '5m': 5, '15m': 15, '30m': 30,
                '1h': 60, '1d': 101, '1w': 102, '1M': 103
            }
            period_value = period_map.get(period, 101)
            
            # 获取历史数据
            klines = self.client.get_security_bars(
                period_value,
                exchange,
                symbol,
                start_date,
                end_date
            )
            
            if not klines:
                return []
                
            # 转换为MarketData对象列表
            market_data_list = []
            for kline in klines:
                market_data = MarketData(
                    symbol=symbol,
                    exchange=exchange,
                    open_price=kline.get('open', 0.0),
                    high_price=kline.get('high', 0.0),
                    low_price=kline.get('low', 0.0),
                    close_price=kline.get('close', 0.0),
                    volume=kline.get('volume', 0),
                    amount=kline.get('amount', 0.0),
                    update_time=datetime.fromtimestamp(kline.get('time', 0))
                )
                market_data_list.append(market_data)
                
            return market_data_list
            
        except Exception as e:
            self.logger.error(f"获取历史数据异常: {str(e)}")
            return []
            
    def subscribe_market_data(self, symbols: List[Tuple[str, str]], 
                            callback: Callable[[MarketData], None]) -> bool:
        """
        订阅实时行情
        
        Args:
            symbols: 股票代码和交易所列表，如 [('000001', 'SZ'), ('600000', 'SH')]
            callback: 行情回调函数
            
        Returns:
            bool: 是否订阅成功
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return False
                
            # 订阅行情
            self.client.subscribe_quotes(symbols, callback)
            self.logger.info(f"订阅行情成功: {symbols}")
            return True
            
        except Exception as e:
            self.logger.error(f"订阅行情异常: {str(e)}")
            return False
            
    def unsubscribe_market_data(self, symbols: List[Tuple[str, str]]) -> bool:
        """
        取消订阅实时行情
        
        Args:
            symbols: 股票代码和交易所列表
            
        Returns:
            bool: 是否取消订阅成功
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return False
                
            # 取消订阅
            self.client.unsubscribe_quotes(symbols)
            self.logger.info(f"取消订阅行情成功: {symbols}")
            return True
            
        except Exception as e:
            self.logger.error(f"取消订阅行情异常: {str(e)}")
            return False
            
    def is_trading_time(self) -> bool:
        """
        判断当前是否为交易时间
        
        Returns:
            bool: 是否为交易时间
        """
        try:
            now = datetime.now()
            current_time = now.time()
            
            # 判断是否为工作日
            if now.weekday() >= 5:
                return False
                
            # 判断是否在交易时间内
            morning_start = datetime.strptime('09:30:00', '%H:%M:%S').time()
            morning_end = datetime.strptime('11:30:00', '%H:%M:%S').time()
            afternoon_start = datetime.strptime('13:00:00', '%H:%M:%S').time()
            afternoon_end = datetime.strptime('15:00:00', '%H:%M:%S').time()
            
            return (morning_start <= current_time <= morning_end) or \
                   (afternoon_start <= current_time <= afternoon_end)
                   
        except Exception as e:
            self.logger.error(f"判断交易时间异常: {str(e)}")
            return False
            
    def auto_reconnect(self, max_retries: int = 3, retry_interval: int = 5) -> bool:
        """
        自动重连机制
        
        Args:
            max_retries: 最大重试次数
            retry_interval: 重试间隔（秒）
            
        Returns:
            bool: 是否重连成功
        """
        try:
            retries = 0
            while retries < max_retries:
                if self.connect():
                    self.logger.info("自动重连成功")
                    return True
                    
                retries += 1
                if retries < max_retries:
                    self.logger.warning(f"第{retries}次重连失败，{retry_interval}秒后重试")
                    time.sleep(retry_interval)
                    
            self.logger.error(f"自动重连失败，已重试{max_retries}次")
            return False
            
        except Exception as e:
            self.logger.error(f"自动重连异常: {str(e)}")
            return False
            
    def get_trading_calendar(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """
        获取交易日历
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[datetime]: 交易日列表
        """
        try:
            if not self.connected:
                self.logger.error("未连接到通达信服务器")
                return []
                
            # 获取交易日历
            trading_days = self.client.get_trading_days(start_date, end_date)
            if not trading_days:
                return []
                
            # 转换为datetime对象列表
            return [datetime.fromtimestamp(day) for day in trading_days]
            
        except Exception as e:
            self.logger.error(f"获取交易日历异常: {str(e)}")
            return [] 