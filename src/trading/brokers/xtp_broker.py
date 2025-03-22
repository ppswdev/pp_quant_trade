from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime
import logging
import xtquant.xttype as xttype
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader
from xtquant import xtconstant

from ..base_broker import BaseBroker

class XTPBroker(BaseBroker):
    """华泰证券XTP接口"""
    
    def __init__(self, config: Dict):
        """
        初始化XTP接口
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.trader = None
        self.connected = False
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        required_fields = ['account', 'password']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"缺少必需配置项: {field}")
    
    def connect(self) -> bool:
        """
        连接交易接口
        
        Returns:
            bool: 是否连接成功
        """
        try:
            self.trader = XtQuantTrader(
                host=self.config.get('host', '119.3.103.38'),
                port=self.config.get('port', 6001),
                username=self.config['account'],
                password=self.config['password']
            )
            
            # 连接
            self.trader.connect()
            
            # 等待连接成功
            if self.trader.wait_connected():
                self.connected = True
                self.logger.info("XTP接口连接成功")
                return True
            else:
                self.logger.error("XTP接口连接失败")
                return False
                
        except Exception as e:
            self.logger.error(f"XTP接口连接错误: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.trader and self.connected:
            self.trader.disconnect()
            self.connected = False
            self.logger.info("XTP接口已断开连接")
    
    def get_account_info(self) -> Dict:
        """
        获取账户信息
        
        Returns:
            Dict: 账户信息
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            account_info = self.trader.query_account()
            return {
                'account': account_info.account_id,
                'total_asset': account_info.total_asset,
                'available': account_info.cash,
                'frozen': account_info.frozen_cash,
                'market_value': account_info.market_value
            }
        except Exception as e:
            self.logger.error(f"获取账户信息失败: {str(e)}")
            raise
    
    def get_positions(self) -> List[Dict]:
        """
        获取持仓信息
        
        Returns:
            List[Dict]: 持仓列表
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            positions = self.trader.query_positions()
            return [{
                'symbol': pos.stock_code,
                'volume': pos.volume,
                'cost_price': pos.cost_price,
                'market_price': pos.market_price,
                'market_value': pos.market_value,
                'profit': pos.profit
            } for pos in positions]
        except Exception as e:
            self.logger.error(f"获取持仓信息失败: {str(e)}")
            raise
    
    def get_orders(self) -> List[Dict]:
        """
        获取订单信息
        
        Returns:
            List[Dict]: 订单列表
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            orders = self.trader.query_orders()
            return [{
                'order_id': order.order_id,
                'symbol': order.stock_code,
                'direction': 'buy' if order.order_type == xtconstant.SIDE_BUY else 'sell',
                'volume': order.order_volume,
                'price': order.price,
                'status': order.order_status,
                'create_time': order.create_time
            } for order in orders]
        except Exception as e:
            self.logger.error(f"获取订单信息失败: {str(e)}")
            raise
    
    def place_order(
        self,
        symbol: str,
        order_type: str,
        direction: str,
        volume: float,
        price: Optional[float] = None
    ) -> str:
        """
        下单
        
        Args:
            symbol: 交易品种
            order_type: 订单类型，如'limit'、'market'
            direction: 交易方向，如'buy'、'sell'
            volume: 交易数量
            price: 价格，市价单不需要
            
        Returns:
            str: 订单ID
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            # 验证参数
            self._validate_symbol(symbol)
            self._validate_order_type(order_type)
            self._validate_direction(direction)
            self._validate_volume(volume)
            if order_type == 'limit':
                self._validate_price(price)
            
            # 创建订单
            order = xttype.XtOrder()
            order.stock_code = symbol
            order.order_type = xtconstant.ORDER_TYPE_LIMIT if order_type == 'limit' else xtconstant.ORDER_TYPE_MARKET
            order.order_side = xtconstant.SIDE_BUY if direction == 'buy' else xtconstant.SIDE_SELL
            order.order_volume = int(volume)
            if price:
                order.price = price
            
            # 发送订单
            order_id = self.trader.order_stock(order)
            self.logger.info(f"下单成功: {order_id}")
            return order_id
            
        except Exception as e:
            self.logger.error(f"下单失败: {str(e)}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """
        撤单
        
        Args:
            order_id: 订单ID
            
        Returns:
            bool: 是否撤单成功
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            self._validate_order_id(order_id)
            result = self.trader.cancel_order(order_id)
            self.logger.info(f"撤单结果: {result}")
            return result
        except Exception as e:
            self.logger.error(f"撤单失败: {str(e)}")
            raise
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        获取订单状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            Dict: 订单状态信息
        """
        if not self.connected:
            raise RuntimeError("未连接到XTP接口")
        
        try:
            self._validate_order_id(order_id)
            order = self.trader.query_order(order_id)
            return {
                'order_id': order.order_id,
                'status': order.order_status,
                'volume': order.order_volume,
                'price': order.price,
                'filled_volume': order.traded_volume,
                'filled_price': order.traded_price,
                'create_time': order.create_time
            }
        except Exception as e:
            self.logger.error(f"获取订单状态失败: {str(e)}")
            raise
    
    def get_market_data(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        period: str = '1d'
    ) -> pd.DataFrame:
        """
        获取市场数据
        
        Args:
            symbol: 交易品种
            start_date: 开始日期
            end_date: 结束日期
            period: 周期，如'1d'、'1h'、'1m'
            
        Returns:
            DataFrame: 市场数据
        """
        try:
            self._validate_symbol(symbol)
            self._validate_date_range(start_date, end_date)
            self._validate_period(period)
            
            # 转换日期格式
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # 获取数据
            data = xtdata.get_market_data(
                stock_code=symbol,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                period=period
            )
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df.index = pd.to_datetime(df.index)
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取市场数据失败: {str(e)}")
            raise
    
    def get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            symbol: 交易品种
            
        Returns:
            DataFrame: 实时数据
        """
        try:
            self._validate_symbol(symbol)
            
            # 获取实时数据
            data = xtdata.get_full_tick([symbol])
            
            # 转换为DataFrame
            df = pd.DataFrame(data)
            df.index = pd.to_datetime(df.index)
            
            return df
            
        except Exception as e:
            self.logger.error(f"获取实时数据失败: {str(e)}")
            raise 