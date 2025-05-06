from client_api.bybit_api import BybitClient
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
from io import BytesIO



# Подготовка данных для графика
def prepare_dataframe(raw_data):
    df = pd.DataFrame(raw_data, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "turnover"
    ])
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    return df

# Функция для генерации графика
def generate_chart(df):
    # Рассчитываем SMA50

    # Настройка стиля
    style = dict(style_name    = 'tradingview',
                 base_mpl_style= 'fast',
                 marketcolors  = {'candle'   : {'up': 'white', 'down': 'black'},
                                  'edge'     : {'up': '#26a69a', 'down': '#ef5350'},
                                  'wick'     : {'up': '#26a69a', 'down': '#ef5350'},
                                  'ohlc'     : {'up': '#26a69a', 'down': '#ef5350'},
                                  'volume'   : {'up': '#26a69a', 'down': '#ef5350'},
                                  'vcedge'   : {'up': 'white'  , 'down': 'white'  },
                                  'vcdopcod' : False,
                                  'alpha'    : 1.0,
                                  'volume_alpha': 0.65,
                                 },
                 mavcolors     = ['#2962ff','#2962ff',],
                 y_on_right    = True,
                 gridcolor     = None,
                 gridstyle     = '--',
                 facecolor     =  None,
                 rc            = [ ('axes.grid','True'),
                                   ('axes.edgecolor'  , 'grey' ),
                                   ('axes.titlecolor','red'),
                                   ('figure.titlesize', 'x-large' ),
                                   ('figure.titleweight','semibold'),
                                   ('figure.facecolor', 'white' ),
                                 ],
                 base_mpf_style = 'tradingview'
                )

    mpf.plot(
        df,
        type='candle',
        style=style,
        returnfig=True,
        volume=True,
        ylabel='Price',
    
    )
    
    
    # Сохраняем график в байтовый поток
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf