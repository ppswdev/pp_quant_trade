import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """日志系统"""
    
    def __init__(self, 
                 log_dir: str = 'logs',
                 log_level: int = logging.INFO,
                 log_format: Optional[str] = None):
        """
        初始化日志系统
        
        Args:
            log_dir: 日志目录
            log_level: 日志级别
            log_format: 日志格式
        """
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志格式
        if log_format is None:
            log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            
        # 创建日志文件名
        log_file = os.path.join(log_dir, f'trading_{datetime.now().strftime("%Y%m%d")}.log')
        
        # 配置根日志记录器
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # 创建日志记录器
        self.logger = logging.getLogger('trading_system')
        
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器
        """
        return logging.getLogger(name)
        
    def set_level(self, level: int) -> None:
        """
        设置日志级别
        
        Args:
            level: 日志级别
        """
        self.logger.setLevel(level)
        
    def debug(self, message: str) -> None:
        """
        记录调试信息
        
        Args:
            message: 日志信息
        """
        self.logger.debug(message)
        
    def info(self, message: str) -> None:
        """
        记录一般信息
        
        Args:
            message: 日志信息
        """
        self.logger.info(message)
        
    def warning(self, message: str) -> None:
        """
        记录警告信息
        
        Args:
            message: 日志信息
        """
        self.logger.warning(message)
        
    def error(self, message: str) -> None:
        """
        记录错误信息
        
        Args:
            message: 日志信息
        """
        self.logger.error(message)
        
    def critical(self, message: str) -> None:
        """
        记录严重错误信息
        
        Args:
            message: 日志信息
        """
        self.logger.critical(message)
        
    def exception(self, message: str) -> None:
        """
        记录异常信息
        
        Args:
            message: 日志信息
        """
        self.logger.exception(message)
        
    def log_trade(self, trade: dict) -> None:
        """
        记录交易信息
        
        Args:
            trade: 交易信息
        """
        message = (
            f"交易执行 - 品种: {trade['symbol']}, "
            f"方向: {trade['action']}, "
            f"价格: {trade['price']}, "
            f"数量: {trade['volume']}, "
            f"时间: {trade['date']}"
        )
        self.info(message)
        
    def log_position(self, position: dict) -> None:
        """
        记录持仓信息
        
        Args:
            position: 持仓信息
        """
        message = (
            f"持仓更新 - 品种: {position['symbol']}, "
            f"数量: {position['volume']}, "
            f"市值: {position['value']}"
        )
        self.info(message)
        
    def log_risk(self, risk_metrics: dict) -> None:
        """
        记录风险指标
        
        Args:
            risk_metrics: 风险指标
        """
        message = (
            f"风险指标 - 回撤: {risk_metrics['drawdown']:.2%}, "
            f"波动率: {risk_metrics['volatility']:.2%}, "
            f"夏普比率: {risk_metrics['sharpe_ratio']:.2f}"
        )
        self.info(message)
        
    def log_strategy(self, strategy_name: str, signal: dict) -> None:
        """
        记录策略信号
        
        Args:
            strategy_name: 策略名称
            signal: 交易信号
        """
        message = (
            f"策略信号 - 策略: {strategy_name}, "
            f"品种: {signal['symbol']}, "
            f"方向: {signal['action']}, "
            f"价格: {signal['price']}, "
            f"数量: {signal['volume']}"
        )
        self.info(message)
        
    def log_performance(self, performance: dict) -> None:
        """
        记录性能指标
        
        Args:
            performance: 性能指标
        """
        message = (
            f"性能指标 - 总收益: {performance['total_return']:.2%}, "
            f"年化收益: {performance['annual_return']:.2%}, "
            f"最大回撤: {performance['max_drawdown']:.2%}, "
            f"夏普比率: {performance['sharpe_ratio']:.2f}"
        )
        self.info(message)
        
    def log_error(self, error: Exception, context: str = '') -> None:
        """
        记录错误信息
        
        Args:
            error: 异常对象
            context: 错误上下文
        """
        message = f"错误信息 - 上下文: {context}, 错误: {str(error)}"
        self.error(message)
        self.exception(message) 