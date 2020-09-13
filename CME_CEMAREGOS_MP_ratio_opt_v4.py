
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import sys
import argparse
import datetime
import pandas as pd

# The above could be sent to an independent module
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import statistics


class Ratio_deviation (bt.Indicator):
    lines = ('ratio','StdDevRatio','LargeStdDev',  'deviation' , 'trigger', 'lagger',)
    params = (('period', 10),('Correlation_param',1.2))

    def __init__(self):
        self.lines.ratio = self.data0 / self.data1
        self.lines.StdDevRatio = btind.StdDev(self.data0 / self.data1, period =self.params.period) # Std Dev looking back period days
        self.sma0=  btind.SMA(self.data0, period =self.params.period)
        self.sma1 =  btind.SMA(self.data1, period =self.params.period)
    def next(self):
        slice =self.lines.StdDevRatio.get(ago=-1,size=self.params.period) # Std Dev of last period days excluding today
        if len(slice) > 0 :
            self.lines.LargeStdDev[0] =  max(slice) # Max Std Dev of last period days excluding today
            self.lines.deviation[0] =self.lines.StdDevRatio[0] > \
                                     self.params.Correlation_param *  self.lines.LargeStdDev[0]  # True if current Std Dev is Correlation_param  largest than last 10
            self.lines.trigger[0] =self.lines.deviation[0]  \
                                     and  self.data0[0] > self.sma0[0] and self.data1[0] > self.sma1[0] # True if also both stocks are in buy territory
        if (self.data0[0] / self.sma0[0] ) < (self.data1[0] / self.sma1[0] ) : self.lines.lagger[0] = 0
        # decide what stock to buy. Buy the onw for which the ratio to sma is larger (more upside potential)
        # In other words, choose the stock that is flat while the matching pair started rallying
        else: self.lines.lagger[0] = 1




class PairTradingStrategy(bt.Strategy):
    params = dict(
        period=10,
        period_market=25,
        Corr_Parm=1.2,
        stake=10,
        qty1=0,
        qty2=0,
        printout=True,
        upper=2.1,
        lower=-2.1,
        up_medium=0.5,
        low_medium=-0.5,
        status=0,
        portfolio_value=10000,
        Norders=0,
    )

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))


    def notify_order(self, order):
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return  # Await further notifications

        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
                self.Norders += 1
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)

        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass  # Simply log

        # Allow new orders
        self.orderid = None


    def __init__(self):
        # To control operation entries
        self.orderid = None
        self.qty1 = self.p.qty1
        self.qty2 = self.p.qty2
        self.upper_limit = self.p.upper
        self.lower_limit = self.p.lower
        self.up_medium = self.p.up_medium
        self.low_medium = self.p.low_medium
        self.status = self.p.status
        self.portfolio_value = self.p.portfolio_value
        self.Norders = self.p.Norders

        # Signals performed with PD.OLS :
   #     self.AccDesOsc = btind.AccDeOsc(self.data0/self.data1, period=self.p.period)
    #    self.AccDesOsc.csv = True

# Two different periods, period  and period_market
#period is used to calculate the correlation between the two stocks, if the correlation is broken and both stocks are
        #in buy territory (according to period_market) sma we should buy
# period_market is the characteristic period of the market, we are using it to decide if there is the stocks
        # are in buy or sell terriotory
        # I expect period_market to be longer than period, period is determinated buy large buy/sell orders we are trying to
        # take advantage off, while period_market should be moved mainly by fundamental reasons
        self.Ratio  = Ratio_deviation(self.data0, self.data1, period=self.params.period,
                                      Correlation_param = self.params.Corr_Parm )
        self.Ratio.csv = True
        self.sma0 = btind.SMA(self.data0, period=self.params.period_market)
        self.sma0.csv = True
        self.sma1 = btind.SMA(self.data1, period=self.params.period_market)
        self.sma1.csv = True

    def next(self):

        if self.orderid:
            return  # if an order is active, no new orders are allowed

        if self.p.printout:
            print('Self  len:', len(self))
            print('Data0 len:', len(self.data0))
            print('Data1 len:', len(self.data1))
       #     print('Data0 len == Data1 len:',  len(self.data0) == len(self.data1))

            print('Data0 dt:', self.data0.datetime.datetime())
            print('Data1 dt:', self.data1.datetime.datetime())
        #    print('position ' ,self.getposition(data1))
        # Step 2: Check conditions for SHORT & place the order
        # Check if the trigger from the indicator is up and also that we do not have previous open positions on any stock
        if self.Ratio.trigger == 1 and self.getposition(self.data1).size==0 and self.getposition(self.data0).size ==0 :

            if self.Ratio.lagger ==0 :
               self.buy(data=self.data0)
            elif self.Ratio.lagger ==1:
                self.buy(data=self.data1)
        # Selling if any of the stocks crosses into bearish territory according to sma
        if  (self.data1 < self.sma1 or self.data0 < self.sma0 ):
            if  self.getposition(self.data0): # if the matching stock changes momentum close the position on the traded stock
                self.log('CLOSE LONG %s, price = %.2f' % ("PEP", self.data0.close[0]))
                self.close(self.data0)
            elif self.getposition(self.data1):   # if the matching stock changes momentum close the position on the traded stock
                self.log('CLOSE LONG %s, price = %.2f' % ("PEP", self.data1.close[0]))
                self.close(self.data1)


    def stop(self):
        pnl = round(self.broker.getvalue() - self.broker.startingcash, 2)
        print('{},  {},   {},  {},  {}, {},   {},   {}'.format(self.params.period, self.params.period_market,\
        self.params.Corr_Parm , self.broker.startingcash, round(self.broker.getvalue(),2), \
                 pnl, self.Norders,  round(pnl/self.Norders, 2) if self.Norders > 0 else 0))
#    print('period   period_market   Corr_Parm  startingcash    endcash     profit      Norders')

def runstrat(args=None):
    args = parse_args(args)

    df = pd.read_csv('Updated.csv', index_col='Date', parse_dates=True)  # Read csv file
    # df = df[ (df.PrecioCierre > 0) & (df.PrecioMayor > 0) & (df.PrecioMedio > 0) & (df.PrecioMenor > 0)] #Delete all zero entries for stock prices

    # I divided all pesos by 1000 otherwise volatility ~1E11 and crashes the library with nans
    df.Volumen = df.Volumen / 1000
    df.Precio = df.Precio / 1000

    # Create column PrecioAbertura, which is the PrecioCierre of the previous daay
    # df["PrecioAbertura"] = df.PrecioCierre.shift(periods=1, fill_value=df.PrecioCierre[1])
    #    print(df.head().to_string())

    kwargs = dict(  ## args to describe the pandas input file
        fromdate=datetime.datetime(2015, 12, 28),
        open=3,
        close=3,
        volume=0,
        openinterest=-1
    )
    if 'cerebro' in locals() : del cerebro;
    cerebro = bt.Cerebro(writer=True)
    cerebro = bt.Cerebro();
    data0 = bt.feeds.PandasData( dataname=df[(df.Nemotecnico == "CLH")], **kwargs )
    cerebro.adddata(data0, "CLH")  # loaded data and name

    #print(dataname.head().to_string())
    data1 = bt.feeds.PandasData(dataname=df[(df.Nemotecnico == "CEMARGOS")], **kwargs)
    cerebro.adddata(data1, "CEMARGOS")  # loaded data and name

    # Add the strategy
    # cerebro.addstrategy(PairTradingStrategy,
    #                     period=10,
    #                     period_market=60)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcash(10000)

    # Add the commission - only stocks like a for each operation
    cerebro.broker.setcommission(commission=0.003) # 0.3% commision on transaction
    cerebro.addsizer(bt.sizers.SizerFix, stake=100)
 #   cerebro.addwriter(bt.WriterFile, rounding=4, csv = True, out="trial.csv" )


    cerebro.optstrategy(
        PairTradingStrategy,
        #period=10,
        period=range(2, 15),
        #period_market=17,
        period_market=range(2, 40),
        Corr_Parm= [x/10 for x  in range(11,20)] ,
        printout=False
    )


   # [x/10 for x  in range(11,14)]
    # And run it
    print('period,   period_market,   Corr_Parm ,  startingcash,    endcash,     profit,      Norders,      PPT')
    cerebro.run()

#    cerebro.run(maxcpus=1)
#11*11*10

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Sample Skeleton'
        )
    )

    parser.add_argument('--data0', default='../../datas/2005-2006-day-001.txt',
                        required=False, help='Data to read in')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--plot', required=False, default='',
                        nargs='?', const='{}',
                        metavar='kwargs', help='kwargs in key=value format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()



################# DO NOT DELETE #####################################################
##---------- The buy and sell columns on the output of the writter are not the actual price numbers (They are close)
##----------- The price of the buy is given by the open, however the last columns "CLH2 and CEMARGOS2" are useful for the profit per trade
## This can be changed by creating proper observers
# BuySell 2	len 9	buy 2	sell 2	DataTrades
# BuySell	333			             DataTrades
# BuySell	334			            DataTrades
# BuySell	335			            DataTrades
# BuySell	336	    11.82		    DataTrades
# BuySell	337			            DataTrades
# BuySell	348			            DataTrades
# BuySell	349		        12.3221	DataTrades
# BuySell	350			            DataTrades
