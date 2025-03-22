from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union
import pandas as pd
from datetime import datetime, timedelta

class BaseDataFetcher(ABC):
    """数据采集基类"""
    
    def __init__(self, config: Dict):
        """
        初始化数据采集器
        
        Args:
            config: 配置信息
        """
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """验证配置信息"""
        pass
    
    @abstractmethod
    def get_stock_list(self, market: str = 'A') -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型，如'A'、'HK'、'US'
            
        Returns:
            DataFrame: 股票列表
        """
        pass
    
    @abstractmethod
    def get_daily_data(
        self,
        symbol: str,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        fields: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        获取日线数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            fields: 需要获取的字段列表
            
        Returns:
            DataFrame: 日线数据
        """
        pass
    
    @abstractmethod
    def get_minute_data(
        self,
        symbol: str,
        start_time: Union[str, datetime],
        end_time: Union[str, datetime],
        period: str = '1min'
    ) -> pd.DataFrame:
        """
        获取分钟线数据
        
        Args:
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            period: 周期，如'1min'、'5min'、'15min'、'30min'、'60min'
            
        Returns:
            DataFrame: 分钟线数据
        """
        pass
    
    @abstractmethod
    def get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame: 实时数据
        """
        pass
    
    @abstractmethod
    def get_fundamental_data(
        self,
        symbol: str,
        report_type: str = 'quarterly'
    ) -> pd.DataFrame:
        """
        获取基本面数据
        
        Args:
            symbol: 股票代码
            report_type: 报告类型，如'quarterly'、'yearly'
            
        Returns:
            DataFrame: 基本面数据
        """
        pass
    
    def _convert_date(self, date: Union[str, datetime]) -> datetime:
        """
        转换日期格式
        
        Args:
            date: 日期字符串或datetime对象
            
        Returns:
            datetime: 转换后的datetime对象
        """
        if isinstance(date, str):
            return datetime.strptime(date, '%Y-%m-%d')
        return date
    
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
        start = self._convert_date(start_date)
        end = self._convert_date(end_date)
        
        if start > end:
            raise ValueError("开始日期不能大于结束日期")
        
        if end > datetime.now():
            raise ValueError("结束日期不能大于当前日期")
    
    def _validate_symbol(self, symbol: str) -> None:
        """
        验证股票代码
        
        Args:
            symbol: 股票代码
        """
        if not symbol or not isinstance(symbol, str):
            raise ValueError("股票代码不能为空且必须为字符串") 