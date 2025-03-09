# 市场追踪器 (Market Tracker)

一个实时追踪股票和加密货币市场的 Web 应用程序。

## 功能特点

- 实时追踪多个股票市场数据
- 实时追踪多个加密货币市场数据
- 支持盘前盘后交易数据显示
- 价格变动视觉反馈
- 深色模式界面
- 响应式设计，支持移动端
- 自动刷新数据（每5秒）

## 技术栈

- 后端：Python Flask
- 前端：HTML5, JavaScript, Bootstrap 5
- 数据源：
  - 股票数据：Yahoo Finance API
  - 加密货币数据：Binance API

## 在线演示

你可以通过以下方式快速部署并查看演示：

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/akige/market-tracker)

## 本地安装

1. 克隆仓库：
```bash
git clone https://github.com/akige/market-tracker.git
cd market-tracker
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行应用：
```bash
python api/index.py
```

4. 访问应用：
打开浏览器访问 `http://localhost:8000`

## Vercel 部署步骤

1. Fork 这个仓库到你的 GitHub 账号

2. 访问 [Vercel](https://vercel.com) 并使用 GitHub 账号登录

3. 点击 "New Project"

4. 从你的 GitHub 仓库列表中选择 `market-tracker`

5. 配置部署选项：
   - Framework Preset: 选择 "Other"
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: `pip install -r requirements.txt`

6. 点击 "Deploy" 开始部署

部署完成后，Vercel 会提供一个域名供你访问应用。

## 监控的市场

### 股票
- MSTR (MicroStrategy)
- ^IXIC (纳斯达克综合指数)
- NVDA (英伟达)
- TSLA (特斯拉)

### 加密货币
- BTC/USDT (比特币)
- ETH/USDT (以太坊)
- SOL/USDT (索拉纳)
- DOGE/USDT (狗狗币)
- XRP/USDT (瑞波币)
- BNB/USDT (币安币)
- ADA/USDT (卡尔达诺)
- XLM/USDT (恒星币)

## 特色功能详解

- **实时数据更新**：每5秒自动更新一次市场数据
- **价格变动提示**：价格上涨显示绿色闪烁，下跌显示红色闪烁
- **盘前盘后数据**：支持显示美股盘前盘后交易数据
- **市场状态显示**：清晰显示市场当前状态（交易中/盘前/盘后/已收盘）
- **响应式设计**：完美支持各种设备尺寸

## 使用说明

- 页面会自动更新数据，无需手动刷新
- 价格变动会有颜色指示：
  - 绿色：价格上涨
  - 红色：价格下跌
- 盘前盘后数据会在股票卡片上显示，格式为 <+/-X.XX%>

## 注意事项

- 数据来源于 Yahoo Finance 和 Binance API，可能存在延迟
- 建议在使用时遵守相关 API 的使用条款
- 本应用仅供参考，不构成任何投资建议

## 贡献指南

1. Fork 本仓库
2. 创建新的功能分支
3. 提交你的修改
4. 创建 Pull Request

## 开源协议

MIT License 