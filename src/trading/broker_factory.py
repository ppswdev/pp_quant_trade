from typing import Dict
from .base_broker import BaseBroker
from .brokers.xtp_broker import XTPBroker
from .brokers.eastmoney_broker import EastMoneyBroker
from .brokers.ths_broker import THSBroker
from .brokers.tdx_broker import TDXBroker

class BrokerFactory:
    """券商接口工厂类"""
    
    @staticmethod
    def create_broker(config: Dict) -> BaseBroker:
        """
        创建券商接口实例
        
        Args:
            config: 配置信息
            
        Returns:
            BaseBroker: 券商接口实例
        """
        broker_type = config.get('type', '').lower()
        
        if broker_type == 'xtp':
            return XTPBroker(config)
        elif broker_type == 'eastmoney':
            return EastMoneyBroker(config)
        elif broker_type == 'ths':
            return THSBroker(config)
        elif broker_type == 'tdx':
            return TDXBroker(config)
        else:
            raise ValueError(f"不支持的券商类型: {broker_type}") 