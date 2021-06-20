#shortcut preparing
# list installed conda environments
conda env list

# activate base environment
conda activate

# activate freqtrade-conda environment
conda activate freqtrade-conda

#deactivate any conda environments
conda deactivate

# Step 1 - Initialize user folder
freqtrade create-userdir --userdir user_data

# Step 2 - Create a new configuration file
freqtrade new-config --config config.json

#start the bot
freqtrade trade --config config.json --strategy SampleStrategy
freqtrade trade --config config.json --strategy Strategy001

#download data
freqtrade download-data --exchange bittrex --timeframe 1h --days 365

#plot
freqtrade plot-dataframe --strategy Strategy001 --export-filename user_data/backtest_results/backtest-result.json -p BTC/ETH --timerange=20180801-20180805
freqtrade plot-dataframe -p BTC/ETH --strategy Strategy001
freqtrade plot-dataframe --export-filename user_data/backtest_results/backtest-result.json

#backtest
freqtrade backtesting --strategy SampleStrategy --timeframe 5m --export trades --config config.json
freqtrade backtesting --strategy Strategy001 --timeframe 1m --export trades --config config.json
freqtrade backtesting --strategy Strategy001 --timeframe 1m --export trades --export-filename=user_data/backtest_results/backtest_results.json --config config.json

#plot try
freqtrade plot-dataframe -p BTC/ETH --strategy SampleStrategy

#backtest test and plot
freqtrade backtesting --strategy SampleStrategy --timeframe 1h --export trades --config config.json --export-filename user_data/backtest_results/backtest-result-special.json
freqtrade plot-dataframe --strategy SampleStrategy -p ETC/BTC --timeframe 1h --export=trades --export-filename user_data/backtest_results/backtest-result-special-2021-04-04_14-20-20.json
https://www.ctolib.com/article/releases/96218


freqtrade backtesting -s Strategy0010 -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100 --export-filename user_data/backtest_results/backtest-result-special.json

freqtrade plot-dataframe --strategy Strategy0010 --timeframe 1h --export=trades

================================================

freqtrade backtesting -s HansenSmaOffsetV1 -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100

freqtrade plot-dataframe --strategy HansenSmaOffsetV1 --timeframe 1h --export=trades

==============================================

freqtrade backtesting --strategy  Obelisk_Ichimoku_Slow_v1_3 -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100

freqtrade plot-dataframe --strategy Obelisk_Ichimoku_Slow_v1_3 --timeframe 1h --export=trades

==============================================

freqtrade backtesting --strategy hansencandlepatternV1 -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100

freqtrade plot-dataframe --strategy hansencandlepatternV1 --timeframe 1h --export=trades

==============================================

freqtrade backtesting --strategy CombinedBinHAndCluc -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100

freqtrade plot-dataframe --strategy CombinedBinHAndCluc --timeframe 1h --export=trades

==============================================

freqtrade backtesting -s BBRSIStrategy -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100 --export-filename user_data/backtest_results/backtest-result-special.json

freqtrade plot-dataframe --strategy BBRSIStrategy --timeframe 1h --export=trades

freqtrade new-hyperopt --hyperopt latest

freqtrade hyperopt --hyperopt BBRSIHyperopt --hyperopt-loss SharpeHyperOptLoss --strategy BBRSINaiveStrategy -i 1h

freqtrade backtesting -s BBRSITestedStrategy -i 1h --datadir user_data/data/bittrex --export trades --config config.json --stake-amount 100 --export-filename user_data/backtest_results/backtest-result-special.json
