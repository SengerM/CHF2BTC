# CHF2BTC

Bitcoin (BTC) price as measured in Swiss Francs (CHF), since the beginning of time.

Though packages such as [ccxt](https://docs.ccxt.com) provide easy and real-time access to the valuation of Bitcoin in Swiss Francs by fetching data from different exchanges, the data only goes as back as the exchange has been in operation. So far, the oldest data I found is from 2023. This can be limiting for data analysis. So I created this repository to easily get the price since the beginning of time, by computing an estimation through the USD/CHF price.

## Installation

1. Clone in `path/to/somewhere`.
2. Run `pip install path/to/somewhere`

## Usage

```
from CHF2BTC.CHF2BTC import get_data

data = get_data()
print(data)
```
That will print the following data frame:
```
               timestamp  open (CHF/BTC)  high (CHF/BTC)  low (CHF/BTC)  close (CHF/BTC)     volume             source
datetime
2010-07-18           NaN        0.052499        0.052505       0.052380         0.052443        NaN  coincodex*forexsb
2010-07-19           NaN        0.089991        0.090609       0.089631         0.090433        NaN  coincodex*forexsb
2010-07-20           NaN        0.085163        0.085224       0.084456         0.084876        NaN  coincodex*forexsb
2010-07-21           NaN        0.078469        0.078752       0.078315         0.078457        NaN  coincodex*forexsb
2010-07-22           NaN        0.083184        0.083235       0.082320         0.082526        NaN  coincodex*forexsb
...                  ...             ...             ...            ...              ...        ...                ...
2025-07-04  1.751587e+12    87121.200000    87122.200000   85290.000000     85956.000000  22.666134             Kraken
2025-07-04           NaN             NaN             NaN            NaN              NaN        NaN                NaN
2025-07-05           NaN             NaN             NaN            NaN              NaN        NaN                NaN
2025-07-05  1.751674e+12    85906.600000    86222.100000   85825.200000     86059.100000   3.461548             Kraken
2025-07-06  1.751760e+12    86093.800000    86711.600000   85793.600000     86679.200000   2.875901             Kraken

[6187 rows x 7 columns]
```
The function `get_data` will automatically try to fetch the latest data from Kraken and update the local database.
