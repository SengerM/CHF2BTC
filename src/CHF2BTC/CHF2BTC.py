import ccxt # https://docs.ccxt.com
from logging import getLogger
import pandas
from pathlib import Path
from datetime import datetime

logger = getLogger(__name__)

PATH_TO_DATA_FOLDER = Path(__file__).parent.parent.parent/'data'
PATH_TO_LOCAL_BTC2CHF_FILE = PATH_TO_DATA_FOLDER/'CHF2BTC.csv'

def find_exchanges_with_pair(
	# Find all the exchanges that have a specific pair available.
	target_pair:str,
		# The pair to search for, e.g. `'BTC/CHF'`.
	raise_error_if_cannot_fetch_data:bool=True,
		# If `False` then if cannot fetch data from some exchange, it will be skipped.
)->list:
	exchanges_with_pair = []
	for exchange_id in ccxt.exchanges:
		try:
			exchange_class = getattr(ccxt, exchange_id)
			exchange = exchange_class()
			markets = exchange.load_markets()
			if 'kraken' in str(exchange).lower():
				print(exchange, sorted(set(markets)))
			else:
				print(exchange)
			print('---------------------------------')
			if target_pair in markets:
				exchanges_with_pair.append(exchange_id)
		except Exception as e:
			if raise_error_if_cannot_fetch_data:
				raise e
			else:
				logger.debug(f'Skipping {exchange} because "{e}"')
				pass
	return exchanges_with_pair

def download_BTC2CHF_data(n_days:int, exchange=None)->pandas.DataFrame:
	if exchange is None:
		exchange = ccxt.kraken()
	logger.debug(f'Downloading CHF/BTC data from {exchange}...')
	ohlcv = exchange.fetch_ohlcv(
		'BTC/CHF',
		timeframe = '1d',
		limit = n_days,
		# ~ params = {"paginate": True, "paginationCalls": 5},
	)
	df = pandas.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
	df['datetime'] = pandas.to_datetime(df['timestamp'], unit='ms')
	df.rename(columns={col: f'{col} (CHF/BTC)' for col in ['open','high','low','close']}, inplace=True)
	df['source'] = str(exchange)
	df.set_index(['datetime'], inplace=True)
	df.sort_index(inplace=True)
	return df

def read_CHF2USD_downloaded_from_forexsb():
	data = pandas.read_csv(
		PATH_TO_DATA_FOLDER/'USDCHF1440.csv',
		comment = '#',
	)
	data['datetime'] = pandas.to_datetime(data['datetime'])
	data['source'] = 'forexsb'
	data.set_index('datetime', inplace=True)
	data.sort_index(inplace=True)
	data.rename(columns={col: f'{col} (CHF/USD)' for col in ['open','high','low','close']}, inplace=True)
	return data

def download_BTC2CHF_data_and_update_local_database():
	if not PATH_TO_LOCAL_BTC2CHF_FILE.is_file():
		data = download_BTC2CHF_data(n_days=99999) # Just download all we can.
		data.to_csv(PATH_TO_LOCAL_BTC2CHF_FILE)
	else:
		data = read_local_BTC2CHF_data()
		n_missing_days = (datetime.today() - data.reset_index()['datetime'].max()).days
		if n_missing_days > 0:
			new_data = download_BTC2CHF_data(n_days = n_missing_days)
			data = pandas.concat([data,new_data])
			data.to_csv(PATH_TO_LOCAL_BTC2CHF_FILE)

def read_local_BTC2CHF_data()->pandas.DataFrame:
	data = pandas.read_csv(PATH_TO_LOCAL_BTC2CHF_FILE)
	data['datetime'] = pandas.to_datetime(data['datetime'])
	data.set_index('datetime', inplace=True)
	return data

def read_USD2BTC_data_downloaded_from_coincodex()->pandas.DataFrame:
	data = pandas.read_csv(
		PATH_TO_DATA_FOLDER/'USD2BTC.csv',
		comment = '#',
	)
	for col in {'Start','End'}:
		data[col] = pandas.to_datetime(data[col])
	data['datetime'] = data['End']
	data['datetime'] = pandas.to_datetime(data['datetime'])
	data['source'] = 'coincodex'
	data.set_index('datetime', inplace=True)
	data.sort_index(inplace=True)
	data.rename(columns={col: f'{col.lower()} (USD/BTC)' for col in ['Open','High','Low','Close']}, inplace=True)
	return data

def get_data()->pandas.DataFrame:
	download_BTC2CHF_data_and_update_local_database()
	data = read_local_BTC2CHF_data()

	chf2usd = read_CHF2USD_downloaded_from_forexsb()
	usd2btc = read_USD2BTC_data_downloaded_from_coincodex()

	data_calculated = pandas.DataFrame(index=usd2btc.index)
	for col in ['open','high','low','close']:
		data_calculated[f'{col} (CHF/BTC)'] = usd2btc[f'{col} (USD/BTC)']*chf2usd[f'{col} (CHF/USD)']
	data_calculated['source'] = usd2btc['source'].map(str) + '*' + chf2usd['source']

	data = pandas.concat([data, data_calculated])

	return data.sort_index()

if __name__ == '__main__':
	import plotly.express as px

	data = get_data()

	fig = px.line(
		data_frame = data.sort_index().reset_index(drop=False),
		x = 'datetime',
		y = 'close (CHF/BTC)',
		color = 'source',
		log_y = True,
	)
	SAVE_PLOT_HERE = Path.home()/'deleteme.html'
	fig.write_html(SAVE_PLOT_HERE)

	print(f'Plot has been created in {SAVE_PLOT_HERE}')
