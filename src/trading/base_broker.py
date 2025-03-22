from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime
import logging

class BaseBroker(ABC):
    """券商接口基类"""
    
    def __init__(self, config: Dict):
        """
        初始化券商接口
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置信息"""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接交易接口
        
        Returns:
            bool: 是否连接成功
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """
        获取账户信息
        
        Returns:
            Dict: 账户信息
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """
        获取持仓信息
        
        Returns:
            List[Dict]: 持仓列表
        """
        pass
    
    @abstractmethod
    def get_orders(self) -> List[Dict]:
        """
        获取订单信息
        
        Returns:
            List[Dict]: 订单列表
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        撤单
        
        Args:
            order_id: 订单ID
            
        Returns:
            bool: 是否撤单成功
        """
        pass
    
    @abstractmethod
    def get_order_status(self, order_id: str) -> Dict:
        """
        获取订单状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            Dict: 订单状态信息
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            symbol: 交易品种
            
        Returns:
            DataFrame: 实时数据
        """
        pass
    
    def _validate_symbol(self, symbol: str) -> None:
        """
        验证交易品种
        
        Args:
            symbol: 交易品种
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("交易品种不能为空且必须为字符串")
    
    def _validate_order_type(self, order_type: str) -> None:
        """
        验证订单类型
        
        Args:
            order_type: 订单类型
        """
        valid_types = ['limit', 'market']
        if order_type not in valid_types:
            raise ValueError(f"不支持的订单类型: {order_type}")
    
    def _validate_direction(self, direction: str) -> None:
        """
        验证交易方向
        
        Args:
            direction: 交易方向
        """
        valid_directions = ['buy', 'sell']
        if direction not in valid_directions:
            raise ValueError(f"不支持的交易方向: {direction}")
    
    def _validate_volume(self, volume: float) -> None:
        """
        验证交易数量
        
        Args:
            volume: 交易数量
        """
        if volume <= 0:
            raise ValueError("交易数量必须大于0")
    
    def _validate_price(self, price: Optional[float]) -> None:
        """
        验证价格
        
        Args:
            price: 价格
        """
        if price is not None and price <= 0:
            raise ValueError("价格必须大于0")
    
    def _validate_order_id(self, order_id: str) -> None:
        """
        验证订单ID
        
        Args:
            order_id: 订单ID
        """
        if not order_id or not isinstance(order_id, str):
            raise ValueError("订单ID不能为空且必须为字符串")
    
    def _validate_date_range(
        self,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime]
    ) -> None:
        """
        验证日期范围
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_date > end_date:
            raise ValueError("开始日期不能大于结束日期")
        
        if end_date > datetime.now():
            raise ValueError("结束日期不能大于当前日期")
    
    def _validate_period(self, period: str) -> None:
        """
        验证周期
        
        Args:
            period: 周期
        """
        valid_periods = ['1d', '1h', '1m']
        if period not in valid_periods:
            raise ValueError(f"不支持的周期: {period}") 