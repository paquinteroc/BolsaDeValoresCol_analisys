import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import pandas as pd

# I divided all pesos by 1000 otherwise volatility ~1E11 and crashes the library with nans

class firstStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=21)

    def next(self):
        if not self.position:
            if self.rsi < 50:
                self.buy(size=100)
        else:
            if self.rsi > 50:
               self.sell(size=100)



df = pd.read_csv('All_Stocks_historical_ver2.csv',index_col='fecha' ,parse_dates= True)
df.Nemotecnico = df.Nemotecnico.str.replace(' ', '') #  remove white space in the names of stocks

print(df.head().to_string() )
df.columns

df.drop(  'Unnamed: 0', axis=1, inplace=True)


dfBCOL = df[ (df.Nemotecnico == "BCOLOMBIA" )    ]
dfBCOL = dfBCOL[ dfBCOL.index >  datetime.datetime(2018, 12, 28)  ]

# I divided all pesos by 1000 otherwise volatility ~1E11 and crashes the library with nans
dfBCOL.Volumen = dfBCOL.Volumen/1000
dfBCOL.PrecioCierre = dfBCOL.PrecioCierre/1000
dfBCOL.PrecioMayor = dfBCOL.PrecioMayor/1000
dfBCOL.PrecioMedio = dfBCOL.PrecioMedio/1000
dfBCOL.PrecioMenor = dfBCOL.PrecioMenor/1000


# Create column PrecioAbertura, which is the PrecioCierre of the previous daay
dfBCOL["PrecioAbertura"] = dfBCOL.PrecioCierre.shift(periods=1, fill_value= dfBCOL.PrecioCierre[1])



print(dfBCOL.head().to_string() )

data = bt.feeds.PandasData( dataname =dfBCOL  ,
                        fromdate=datetime.datetime(2018, 12, 28),
                            open=9, # open is preciomedio for now
                           high=4,
                           low=6,
                           close=3,
                           volume=1,
                            openinterest =-1
                           )



data.getwriterinfo()
print( data.getwritervalues() )
data.open.plot()
del cerebro
\
#Variable for our starting cash
startcash = 10000
#Create an instance of cerebro
cerebro = bt.Cerebro()

#Add our strategy
cerebro.addstrategy(firstStrategy)

#Add the data to Cerebro
cerebro.adddata(data)

# Set our desired cash start
cerebro.broker.setcash(startcash)

# Run over everything
cerebro.run()
print(cerebro.broker.getvalue())
#Get final portfolio Value
portvalue = cerebro.broker.getvalue()
pnl = portvalue - startcash

#Print out the final result
print('Final Portfolio Value: ${}'.format(portvalue))
print('P/L: ${}'.format(pnl))

#Finally plot the end results
cerebro.plot(style='candlestick')

print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.plot()

