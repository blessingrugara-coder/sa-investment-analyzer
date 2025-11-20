# SA Investment Analyzer 🇿🇦📊

**Institutional-grade investment analytics for South African retail investors**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

Track, analyze, and optimize portfolios containing ANY retail investment product available in South Africa:
- JSE Equities (7,000+ stocks)
- ETFs (Satrix, CoreShares, Sygnia)
- Unit Trusts (Allan Gray, Coronation, etc.)
- Money Market Funds
- Bank Products
- Offshore Holdings

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yourusername/sa-investment-analyzer.git
cd sa-investment-analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize
python scripts/init_system.py

# Run dashboard
streamlit run app.py
```

## ✨ Features

- ✅ Automated data collection (OpenBB, yfinance, web scraping)
- ✅ Portfolio optimization (Markowitz, Black-Litterman, Risk Parity)
- ✅ Performance analytics (Sharpe, Sortino, max drawdown)
- ✅ Risk analysis (VaR, CVaR, stress testing)
- ✅ Factor analysis
- ✅ Interactive Streamlit dashboard
- ✅ 100% Free & Open Source

## 📚 Documentation

See [docs/](docs/) folder for detailed guides.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - see [LICENSE](LICENSE)

## ⚠️ Disclaimer

Educational purposes only. Not financial advice. Consult a qualified advisor.
