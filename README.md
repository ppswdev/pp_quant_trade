# PP量化交易系统

这是一个简单易用的量化交易系统，可以帮助您：
- 自动获取股票数据
- 运行交易策略
- 进行回测分析
- 执行实盘交易

## 系统特点

1. 数据获取
   - 支持从Tushare、AkShare等平台获取股票数据
   - 自动更新实时行情
   - 支持历史数据查询

2. 交易策略
   - 内置多种常用策略（均线交叉、突破、均值回归等）
   - 支持自定义新策略
   - 策略参数可调

3. 回测功能
   - 支持历史数据回测
   - 提供详细的回测报告
   - 可视化分析结果

4. 实盘交易
   - 支持多个券商接口（XTP、东方财富、同花顺、通达信）
   - 实时风险控制
   - 交易记录追踪

## 快速开始

### 第一步：安装系统

1. 下载系统
```bash
git clone https://github.com/ppswdev/pp_quant_trade.git
cd pp_quant_trade
```

2. 安装Python环境
   - 访问 [Python官网](https://www.python.org/downloads/) 下载并安装Python 3.8或更高版本
   - 安装时请勾选"Add Python to PATH"选项

3. 安装系统依赖
```bash
# Windows系统：
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux系统：
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 第二步：配置系统

1. 配置数据源
   - 打开 `config/data_config.yaml`
   - 填入您的数据源账号信息（如Tushare的token）

2. 配置券商接口
   - 打开 `config/broker_config.yaml`
   - 填入您的券商账号信息

3. 选择交易策略
   - 打开 `config/strategy_config.yaml`
   - 选择您想使用的策略
   - 调整策略参数

### 第三步：运行系统

1. 运行回测（推荐先进行回测）
```bash
# 运行均线交叉策略的回测
python -m src.backtest.run_backtest --strategy ma_cross --start_date 2020-01-01 --end_date 2023-12-31
```

2. 查看回测结果
   - 系统会自动生成回测报告
   - 可以在 `results/` 目录下查看详细报告
   - 使用浏览器打开 `results/backtest_report.html` 查看可视化报告

3. 实盘交易（确认回测效果后再进行）
```bash
# 使用均线交叉策略进行实盘交易
python -m src.trading.run_trading --strategy ma_cross --broker xtp
```

## 常见问题

1. 安装问题
   - 如果安装依赖时出错，请确保网络连接正常
   - 如果提示权限错误，请使用管理员权限运行命令

2. 配置问题
   - 确保配置文件中的账号信息正确
   - 检查文件路径是否正确

3. 运行问题
   - 确保Python环境已激活（命令提示符前有(venv)）
   - 检查日志文件了解详细错误信息

## 获取帮助

- 查看详细文档：`docs/` 目录
- 提交问题：在GitHub上创建Issue
- 加入讨论：项目Discussions页面

## 安全提示

- 请妥善保管您的账号信息
- 实盘交易前请充分测试
- 建议先使用小资金测试

## 许可证

本项目使用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 更新日志

详见 [CHANGELOG.md](CHANGELOG.md)。

## 联系方式

- 提交Issue
- 发送邮件
- 加入讨论组
