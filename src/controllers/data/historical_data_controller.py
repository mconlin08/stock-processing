
# imports
from asyncio import CancelledError, TimeoutError, create_task, Task

from  src.async_session_manager import AsyncSessionManager


class HistoricalDataController:
    '''Handles retrieving and formatting historical data'''
    base_url = 'https://api.stockanalysis.com/api/symbol/{asset_type}/{ticker}/history?range={range}&period={period}'

    valid_asset_types = [
        's',  # stock
        'e',  # etf
    ]

    valid_periods = [
        'Daily',
        'Weekly',
        'Monthly',
        'Quarterly',
        'Annual'
    ]

    valid_ranges = [
        '3M',
        '6M',
        'YTD',
        '1Y',
        '5Y',
        '10Y',
        'Max'
    ]

    json_to_label_map = {
        "t": "date",
        "o": "opening_price",
        "h": "high_price",
        "l": "low_price",
        "c": "closing_price",
        "v": "volume",
        "a": "adjusted_closing_price",
        "ch": "price_change"
    }

    async def get_asset_historical_data(self, ticker: str, asset_type: str, range: str, period: str):
        '''
            Gets a list of historical data for an asset.

            Arguments:
                ticker (str) Ticker for asset
                asset_type (str) Type of asset (e.g., e ('ETF'), s ('Stock'))
                range (str) Length of time to go back
                period (str) Interval of time for row data  (e.g., Daily, Weekly, Monthly)

            Returns:
                historical_data (List)
        '''

        # validate arguments
        if not self.validate_historical_parameters(ticker=ticker, asset_type=asset_type, range=range, period=period):
            raise BaseException('Invalid historical parameters for asset data.')

        # build url
        url = self.build_url_from_ticker(
            ticker=ticker,
            asset_type=asset_type,
            range=range,
            period=period
        )

        # get data
        data = create_task(self.get_historical_data_from_url(url))
        if not await data:
            return {
                'data_type': 'historical',
                'data': data
            }

        # format data
        formatted_data = [self.convert_keys_to_labels(entry) for entry in await data if data != None]

        if formatted_data is not None:
            # return data
            return {
                'data_type': 'historical',
                'data': formatted_data
            }
        else:
            raise f'Formatted_data is none'

    def build_url_from_ticker(self, ticker: str, asset_type: str, range: str, period: str):
        '''
            Builds URL for ticker data with argument values.

            Arguments:
                asset_type (str)
                range (str)
                period (str)

            Returns:
                data_url (str)
        '''

        # check args
        if not ticker or not asset_type or not range or not period:
            raise f'Invalid arguments for {__name__}'

        # build url
        url = self.base_url
        url = url.replace('{ticker}', ticker)
        url = url.replace('{asset_type}', asset_type)
        url = url.replace('{range}', range)
        url = url.replace('{period}', period)

        return url

    def convert_keys_to_labels(self, entry):
        '''
        Relabels single character keys to a meaningful label shown in 'self.json_to_label_map'

        Arguments:
            entry (dict) Dictionary item from historical data list

        Returns:
            converted_item (dict)
        '''

        return {self.json_to_label_map.get(key, key): value for key, value in entry.items()}

    async def get_historical_data_from_url(self, url):
        '''
            Handles retrieval of historical data from url.

            Arguments:
                url (str) URL for data

            Returns:
                formatted_data (list)
        '''

        response_json = await AsyncSessionManager.request_with_limit(url)
        
        json_data = response_json.get('data', None)
        if not json_data:
            return json_data
            
        # Could get 'news' or  'data'
        return json_data.get('data')

    def validate_historical_parameters(self, ticker: str, asset_type: str, range: str, period: str):
        '''
            Validates arguments are defined in class. Returns True if valid, False if not.

            Arguments:
                asset_type (str)
                range (str)
                period (str) 

            Returns:
                are_parameters_valid (bool)
        '''

        # check args
        if not ticker or not asset_type or not range or not period:
            raise BaseException(f'Invalid arguments for {__name__}')

        # validate parameters
        if asset_type not in self.valid_asset_types:
            raise BaseException(
                f'Asset type parameter value {asset_type} is not valid.')
        if range not in self.valid_ranges:
            raise BaseException(f'Range parameter value {range} is not valid.')
        if period not in self.valid_periods:
            raise BaseException(
                f'Period parameter value {period} is not valid.')

        return True
