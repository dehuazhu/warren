from price_scraper import get_price_history_yahoo
from oauth2client.service_account import ServiceAccountCredentials
import gspread
from pdb import set_trace
import argparse


def exportToGoogleSheet(url, days, ticker = 'PSTG'):
    worksheet = getGoogleWorksheet(url)
    price = get_price_history_yahoo(ticker,1000)
    insertData(worksheet, price)


def getGoogleWorksheet(url):
    credentials = ServiceAccountCredentials.from_json_keyfile_name('.credentials.json')
    client = gspread.authorize(credentials)
    workbook = client.open_by_url(url)
    worksheet = workbook.worksheet('stock_prices')
    return worksheet


def insertData(worksheet, price):
    dataframe = price[0]
    column_names = getColumnNames()
    datalist = cleanPriceListDataframe(dataframe)
    worksheet.clear()
    worksheet.update([column_names] + datalist)


def getColumnNames():
    column_names = [
            'Date',
            'Open',
            'High',
            'Low',
            'Close',
            'Adj Close',
            'Volumne'
            ]
    return column_names


def cleanPriceListDataframe(dataframe):
    datalist = dataframe.values.tolist()
    datalist.pop()
    return datalist

if __name__ == '__main__':
    url = 'https://docs.google.com/spreadsheets/d/1uXGMcfDjuWzLoIaSl4-aDrWAKFn-_NIE1LrW-DCH6Gs/edit#gid=0'
    # ticker = 'PSTG'
    days = 1000

    parser = argparse.ArgumentParser()
    parser.add_argument('-t', dest='ticker', help='specify the ticker for the stock you want to scrape')
    arguments = parser.parse_args()
    ticker = arguments.ticker

    exportToGoogleSheet(
            url = url,
            days = days,
            ticker = ticker,
            )
