import requests
import json
from .credentials import iex_token

def get_quote(symbol):
    quote = requests.get(f'https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={iex_token}')
    parsed_quote = json.loads(quote.text)

    intraday = requests.get(f'https://cloud.iexapis.com/stable/stock/{symbol}/intraday-prices?chartLast=1&token={iex_token}')
    parsed_intraday = json.loads(intraday.text)

    quote_string = f'''
    <b>${parsed_quote["symbol"]} {parsed_quote["companyName"]}</b>
    <b>${parsed_quote["latestPrice"]:,.2f}</b>
    Previous close: ${parsed_quote["previousClose"]:,.2f}
    Change: ${parsed_quote["change"]:,.2f}      % Change: {parsed_quote["changePercent"]:.2%}
    Market cap: {int(parsed_quote["marketCap"]/10e6):,}M    P/E: {parsed_quote["peRatio"]}
    <a href="https://iexcloud.io">IEX Cloud</a>
    '''
    # with open('quote.json', 'w') as f:
    # f.write(json.dumps(parsed_quote, indent=4, sort_keys=True))

    # with open('intraday.json', 'w') as f:
    # f.write(json.dumps(parsed_intraday, indent=4, sort_keys=True))
    
    return quote_string
