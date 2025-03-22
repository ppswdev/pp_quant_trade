# PP量化交易系统

一个基于Python的量化交易系统，支持多数据源、多策略、多券商接口。

## 功能特点

- 多数据源支持：Tushare、AkShare、Baostock等
- 多策略支持：均线交叉、突破、均值回归等
- 多券商接口：XTP、东方财富、同花顺、通达信等
- 完整的回测系统
- 实盘交易支持
- 风险控制
- 性能分析
- 可视化展示
- 日志系统

## 安装

### 环境要求

- Python 3.8+
- pip 20.0+
- Git

### 安装步骤

1. 克隆项目

```bash
git clone https://github.com/yourusername/pp_quant_trade.git
cd pp_quant_trade
```

2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 配置

在 `config/` 目录下配置相关参数：

- `data_config.yaml`: 数据源配置
- `broker_config.yaml`: 券商接口配置
- `strategy_config.yaml`: 策略配置
- `risk_config.yaml`: 风险控制配置

### 2. 运行回测

```bash
python -m src.backtest.run_backtest --strategy ma_cross --start_date 2020-01-01 --end_date 2023-12-31
```

### 3. 实盘交易

```bash
python -m src.trading.run_trading --strategy ma_cross --broker xtp
```

## 文档

- [安装和配置指南](docs/installation.md)
- [使用指南](docs/usage.md)
- [API文档](docs/api.md)
- [示例文档](docs/examples.md)

## 开发

### 代码风格

- 使用Python 3.8+语法
- 使用PEP 8编码规范
- 使用类型注解
- 使用docstring文档字符串
- 使用pylint进行代码检查
- 使用black进行代码格式化

### 测试

```bash
pytest tests/
```

### 代码检查

```bash
pylint src/ tests/
black --check src/ tests/
```

## 贡献

欢迎提交Issue和Pull Request！

- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [安全策略](SECURITY.md)

## 许可证

本项目使用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)。

## 联系方式

- 提交Issue
- 发送邮件
- 加入讨论组
