#!/usr/bin/env python3
import argparse
import yaml
from src.data.data_loader import DataLoader
from src.strategy.combined_strategy import CombinedStrategy
from src.backtest.backtest_engine import BacktestEngine

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--symbol', default='AAPL')
    parser.add_argument('--interval', default='15m')
    parser.add_argument('--period', default='3mo')
    args = parser.parse_args()
    
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    loader = DataLoader(config)
    data = loader.fetch_historical_data(args.symbol, args.interval, args.period)
    data = loader.add_all_indicators(data, config)
    
    strategy = CombinedStrategy(config)
    engine = BacktestEngine(
        initial_capital=config['backtest']['initial_capital'],
        commission=config['backtest']['commission'],
        slippage=config['backtest']['slippage']
    )
    results = engine.run(data, strategy)
    
    print(f"Total Return: {results['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Win Rate: {results['win_rate_pct']:.2f}%")

if __name__ == "__main__":
    main()
