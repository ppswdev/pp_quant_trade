import os
import tushare as ts
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union

from .base import BaseDataFetcher

class TushareDataFetcher(BaseDataFetcher):
    """Tushare数据采集器"""
    
    def __init__(self, config: Dict):
        """
        初始化Tushare数据采集器
        
        Args:
            config: 配置信息
        """
        super().__init__(config)
        self.api = ts.pro_api(self.config['token'])
    
    def _validate_config(self) -> None:
        """验证配置信息"""
        if 'token' not in self.config:
            raise ValueError("Tushare token未配置")
    
    def get_stock_list(self, market: str = 'A') -> pd.DataFrame:
        """
        获取股票列表
        
        Args:
            market: 市场类型，如'A'、'HK'、'US'
            
        Returns:
            DataFrame: 股票列表
        """
        if market == 'A':
            return self.api.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
        else:
            raise ValueError(f"暂不支持{market}市场")
    
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
        self._validate_symbol(symbol)
        self._validate_date_range(start_date, end_date)
        
        start = self._convert_date(start_date).strftime('%Y%m%d')
        end = self._convert_date(end_date).strftime('%Y%m%d')
        
        default_fields = [
            'ts_code', 'trade_date', 'open', 'high', 'low', 'close',
            'vol', 'amount', 'change', 'pct_chg'
        ]
        
        if fields is None:
            fields = default_fields
        
        return self.api.daily(
            ts_code=symbol,
            start_date=start,
            end_date=end,
            fields=','.join(fields)
        )
    
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
        self._validate_symbol(symbol)
        self._validate_date_range(start_time, end_time)
        
        start = self._convert_date(start_time).strftime('%Y%m%d %H:%M:%S')
        end = self._convert_date(end_time).strftime('%Y%m%d %H:%M:%S')
        
        period_map = {
            '1min': '1',
            '5min': '5',
            '15min': '15',
            '30min': '30',
            '60min': '60'
        }
        
        if period not in period_map:
            raise ValueError(f"不支持的周期类型: {period}")
        
        return self.api.stk_mins(
            ts_code=symbol,
            start_date=start,
            end_date=end,
            freq=period_map[period],
            fields='ts_code,trade_time,open,high,low,close,vol,amount'
        )
    
    def get_realtime_data(self, symbol: str) -> pd.DataFrame:
        """
        获取实时数据
        
        Args:
            symbol: 股票代码
            
        Returns:
            DataFrame: 实时数据
        """
        self._validate_symbol(symbol)
        return self.api.daily(
            ts_code=symbol,
            trade_date=datetime.now().strftime('%Y%m%d')
        )
    
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
        self._validate_symbol(symbol)
        
        if report_type == 'quarterly':
            return self.api.financial_indicator(
                ts_code=symbol,
                period=datetime.now().strftime('%Y%m%d'),
                fields='ts_code,ann_date,eps,roe,roa,debt_to_assets'
            )
        elif report_type == 'yearly':
            return self.api.financial_indicator(
                ts_code=symbol,
                period=datetime.now().strftime('%Y') + '1231',
                fields='ts_code,ann_date,eps,roe,roa,debt_to_assets'
            )
        else:
            raise ValueError(f"不支持的报告类型: {report_type}") 