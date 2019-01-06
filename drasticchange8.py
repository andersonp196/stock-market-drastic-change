import urllib.request
import json
import time
from random import shuffle
from decimal import Decimal

def stocks():
    with open('stocklist.txt', 'r') as f:
        stocklist = [line.strip() for line in f]
    f.close()
    print("Stock symbols gathered.")
    return stocklist

def stock_data(stock, apiKey):
    #stocklink = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=1min&apikey=apikey' % (stock)
    stocklink = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=%s&interval=1min&outputsize=compact&apikey=%s' % (stock, apiKey)
    print(stocklink)
    try:
        request = urllib.request.urlopen(stocklink).read()
        response = str(request, 'utf-8')
        data = json.loads(response)
        return data
    except:
        return None
    
def stock_prices(data, minutes):
    times = []
    prices = []
    volumes = []
    try:
        for item in data['Time Series (1min)']:
            times.append(item)
        times = sorted(times)
        times = times[-minutes:]
        day = times[-1]
        day = day[0:10]
        for x in times:
            prices.append(float(data['Time Series (1min)'][x]['4. close']))
            if (x[0:10] == day):
                volumes.append(float(data['Time Series (1min)'][times[-1]]['5. volume']))
        totalvolume = sum(volumes)
        if (totalvolume > 500):
            startavg = Decimal((prices[0]+prices[1]+prices[2])/3)
            startavg = round(startavg,5)
            endavg = Decimal((prices[-3]+prices[-2]+prices[-1])/3)
            endavg = round(endavg,5)
            changepercent = Decimal(((endavg-startavg)/startavg)*100)
            changepercent = round(changepercent,5)
            numbers = [startavg, endavg, changepercent, totalvolume]
            return numbers
        if (totalvolume < 1000):
            numbers = ['low volume']
            return numbers
    except:
        return None
  
def start():
    stocklist = stocks()
    order = input("Load stocks in random order [y/n]: ")
    minutes = int(input("How many minutes do you want to know the change for? (ex. 1-20): "))
    percent = float(input("Percent change in %s minutes stocks to show (ex. 2 or 2.5): " % minutes))
    apiKey = input("alphavantage api key: ")
    if (order == 'y'):
        shuffle(stocklist)
    print("Starting... \n")
    failed = []
    tried = 0

    for stock in stocklist:
        data = stock_data(stock, apiKey)
        if (data != None): #if data was gathered correctly
            numbers = stock_prices(data, minutes)
            try:
                if (len(numbers) > 2): #if the numbers were aquired
                    abschange = abs(numbers[2])
                    if (abschange > percent):
                        currenttime = time.strftime("%H:%M:%S")
                        print("*** %s has %s percent change at %s | Start: %s End: %s Total Volume Today: %s" % (stock, numbers[2], currenttime, numbers[0], numbers[1], numbers[3]))
            except:
                if (numbers != 'low volume'):
                    failed.append(stock)
        else:
            failed.append(stock)

        tried += 1
        time.sleep(2)
        
        if ((tried % 100) == 0):
            print("%s/100 new stocks failed." % (len(failed)))
            for stock in failed:
                try:
                    data = stock_data(stock)
                    if (data != None): #if data was gathered correctly
                        numbers = stock_prices(data, minutes)
                        if (len(numbers) > 1): #if the numbers were aquired
                            abschange = abs(numbers[2])
                            if (abschange > percent):
                                currenttime = time.strftime("%H:%M:%S")
                                print("*** %s has %s percent change at %s | Start: %s End: %s Total Volume Today: %s" % (stock, numbers[2], currenttime, numbers[0], numbers[1], numbers[3]))
                except:
                    didntwork = 1
                time.sleep(2)
            failed = []
            
start()


