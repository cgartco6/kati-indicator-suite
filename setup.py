from setuptools import setup, find_packages

setup(
    name="kati-indicator-suite",
    version="1.0.0",
    author="Kati Tutorials",
    description="Professional trading bot and telegram signal system using multi-indicator confluence",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "yfinance>=0.2.0",
        "ta-lib>=0.4.25",
        "plotly>=5.14.0",
        "streamlit>=1.25.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "matplotlib>=3.7.0",
        "ccxt>=4.0.0",
        "python-telegram-bot>=20.0",
        "schedule>=1.2.0",
        "websocket-client>=1.5.0",
        "pandas-ta>=0.3.14b0",
    ],
    entry_points={
        "console_scripts": [
            "kati-bot=run_bot:main",
            "kati-signal=run_signal_bot:main",
            "kati-backtest=run_backtest:main",
            "kati-dashboard=src.visualization.dashboard:run_dashboard",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
