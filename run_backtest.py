#!/usr/bin/env python3
"""Run backtest on historical data"""
import argparse
import yaml
from src.data.data_loader import DataLoader
from src.strategy.combined_strategy import CombinedStrategy
from src.backtest.backtest_engine import BacktestEngine

def main():
    parser = argparse.ArgumentParser(description='Run backtest on a symbol')
    parser.add_argument('--symbol', type=str, default='AAPL', help='Trading symbol')
    parser.add_argument('--interval', type=str, default='15m', help='Timeframe (1m,5m,15m,1h,4h,1d)')
    parser.add_argument('--period', type=str, default='3mo', help='Period (1mo,3mo,6mo,1y)')
    args = parser.parse_args()
    
    with open('config/settings.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Override config with CLI args
    config['trading']['symbol'] = args.symbol
    config['trading']['timeframe'] = args.interval
    
    # Fetch data
    loader = DataLoader(config)
    data = loader.fetch_historical_data(args.symbol, args.interval, args.period)
    data = loader.add_all_indicators(data, config)
    
    # Run backtest
    strategy = CombinedStrategy(config)
    engine = BacktestEngine(
        initial_capital=config['backtest']['initial_capital'],
        commission=config['backtest']['commission'],
        slippage=config['backtest']['slippage']
    )
    results = engine.run(data, strategy)
    
    # Print results
    print("\n" + "="*50)
    print("BACKTEST RESULTS")
    print("="*50)
    print(f"Symbol:        {args.symbol}")
    print(f"Period:        {args.period} ({args.interval})")
    print(f"Final Value:   ${results['final_value']:.2f}")
    print(f"Total Return:  {results['total_return_pct']:.2f}%")
    print(f"Sharpe Ratio:  {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown:  {results['max_drawdown_pct']:.2f}%")
    print(f"Win Rate:      {results['win_rate_pct']:.2f}%")
    print(f"Total Trades:  {results['num_trades']}")
    print("="*50)

if __name__ == "__main__":
    main()
