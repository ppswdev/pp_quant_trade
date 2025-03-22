from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime
import logging
import requests
import json
import time

from ..base_broker import BaseBroker

class THSBroker(BaseBroker):
    """同花顺接口"""
    
    def __init__(self, config: Dict):
        """
        初始化同花顺接口
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.session = requests.Session()
        self.connected = False
        self.base_url = "https://tradeapi.10jqka.com.cn"
    
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
            # 登录
            login_data = {
                'account': self.config['account'],
                'password': self.config['password']
            }
            
            response = self.session.post(
                f"{self.base_url}/login",
                json=login_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.connected = True
                    self.logger.info("同花顺接口连接成功")
                    return True
            
            self.logger.error("同花顺接口连接失败")
            return False
            
        except Exception as e:
            self.logger.error(f"同花顺接口连接错误: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """断开连接"""
        if self.connected:
            try:
                self.session.post(f"{self.base_url}/logout")
                self.connected = False
                self.logger.info("同花顺接口已断开连接")
            except Exception as e:
                self.logger.error(f"断开连接错误: {str(e)}")
    
    def get_account_info(self) -> Dict:
        """
        获取账户信息
        
        Returns:
            Dict: 账户信息
        """
        if not self.connected:
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            response = self.session.get(f"{self.base_url}/account")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    raise RuntimeError(result.get('message', '获取账户信息失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
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
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            response = self.session.get(f"{self.base_url}/positions")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    raise RuntimeError(result.get('message', '获取持仓信息失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
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
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            response = self.session.get(f"{self.base_url}/orders")
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    raise RuntimeError(result.get('message', '获取订单信息失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
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
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            # 验证参数
            self._validate_symbol(symbol)
            self._validate_order_type(order_type)
            self._validate_direction(direction)
            self._validate_volume(volume)
            if order_type == 'limit':
                self._validate_price(price)
            
            # 构建订单数据
            order_data = {
                'symbol': symbol,
                'order_type': order_type,
                'direction': direction,
                'volume': volume,
                'price': price
            }
            
            # 发送订单
            response = self.session.post(
                f"{self.base_url}/order",
                json=order_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    order_id = result['data']['order_id']
                    self.logger.info(f"下单成功: {order_id}")
                    return order_id
                else:
                    raise RuntimeError(result.get('message', '下单失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
            
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
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            self._validate_order_id(order_id)
            
            response = self.session.post(
                f"{self.base_url}/cancel_order",
                json={'order_id': order_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.logger.info(f"撤单成功: {order_id}")
                    return True
                else:
                    raise RuntimeError(result.get('message', '撤单失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
            
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
            raise RuntimeError("未连接到同花顺接口")
        
        try:
            self._validate_order_id(order_id)
            
            response = self.session.get(
                f"{self.base_url}/order_status",
                params={'order_id': order_id}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result['data']
                else:
                    raise RuntimeError(result.get('message', '获取订单状态失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
            
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
            
            # 构建请求参数
            params = {
                'symbol': symbol,
                'start_date': start_date.strftime('%Y%m%d'),
                'end_date': end_date.strftime('%Y%m%d'),
                'period': period
            }
            
            # 获取数据
            response = self.session.get(
                f"{self.base_url}/market_data",
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # 转换为DataFrame
                    df = pd.DataFrame(result['data'])
                    df.index = pd.to_datetime(df.index)
                    return df
                else:
                    raise RuntimeError(result.get('message', '获取市场数据失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
            
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
            
            response = self.session.get(
                f"{self.base_url}/realtime_data",
                params={'symbol': symbol}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    # 转换为DataFrame
                    df = pd.DataFrame(result['data'])
                    df.index = pd.to_datetime(df.index)
                    return df
                else:
                    raise RuntimeError(result.get('message', '获取实时数据失败'))
            else:
                raise RuntimeError(f"请求失败: {response.status_code}")
            
        except Exception as e:
            self.logger.error(f"获取实时数据失败: {str(e)}")
            raise 