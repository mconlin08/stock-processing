
# imports
from datetime import datetime
from asyncio import CancelledError, TimeoutError, create_task

from src.async_session_manager import AsyncSessionManager


class TimeSeriesDataController:
    base_url = 'https://api.stockanalysis.com/api/symbol/{asset_type}/{ticker}/history?type=chart'

    valid_asset_types = [
        's',  # stock
        'e',  # etf
    ]

    async def get_asset_ts_data(self, ticker: str, asset_type: str):
        '''
            Gets a list of time-series data with closing prices for an asset.

            Arguments:
                ticker (str) Ticker for asset
                asset_type (str) Type of asset (e.g., e ('ETF'), s ('Stock'))

            Returns:
                time_series_data (List)
        '''

        # validate arguments
        if not self.validate_ts_parameters(ticker=ticker, asset_type=asset_type):
            return None

        # build url
        url = self.build_url_from_ticker(
            ticker=ticker,
            asset_type=asset_type
        )

        # get data
        data = create_task(self.get_ts_data_from_url(url))
        if not await data:
            return {
                'data_type': 'time_series',
                'data': data
            }
        
        formatted_data = [self.convert_time_series_entry(entry) for entry in await data]
        
        # format data
        if data:
            return {
                'data_type': 'time_series',
                'data': formatted_data
            }
        else:
            raise BaseException(f'time series data is none')

    def build_url_from_ticker(self, ticker: str, asset_type: str):
        '''
            Builds URL for ticker data with argument values.

            Arguments:
                asset_type (str)

            Returns:
                data_url (str)
        '''

        # check args
        if not ticker or not asset_type:
            raise BaseException(f'Invalid arguments for {__name__}')

        # build url
        url = self.base_url
        url = url.replace('{ticker}', ticker)
        url = url.replace('{asset_type}', asset_type)

        return url

    def convert_time_series_entry(self, entry):
        '''
            Handles formatting timestamps and float values from time-series list items
            
            Arguments:
                entry (list) 
                
            Returns
                formatted_entry (dict)
        '''
        
        # Extract timestamp and closing price
        timestamp_ms, closing_price = entry

        # Convert milliseconds to seconds
        timestamp_s = round(timestamp_ms / 1000.0)
        
        # Convert to a date string
        # date = datetime.utcfromtimestamp(timestamp_s).strftime('%Y-%m-%d')
        
        date = datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d')

        # Return a dictionary with the date and closing price
        return {'date': date, 'closing_price': float(closing_price)}

    async def get_ts_data_from_url(self, url):
        '''
            Handles retrieval of time-series data from url.
            
            Arguments:
                url (str) URL for data
                
            Returns:
                formatted_data (list)
        '''
        
        # get async client for request
        response_json = await AsyncSessionManager.request_with_limit(url)        
        json_data = response_json.get('data', None)
        if not json_data:
            return json_data

        return json_data
         
    def validate_ts_parameters(self, ticker: str, asset_type: str):
        '''
            Validates arguments are defined in class. Returns True if valid, False if not.

            Arguments:
                asset_type (str)

            Returns:
                are_parameters_valid (bool)
        '''

        # check args
        if not ticker or not asset_type:
            raise BaseException(f'Invalid arguments for {__name__}')

        # validate parameters
        if asset_type not in self.valid_asset_types:
            raise BaseException(f'Asset type parameter value {asset_type} is not valid.')

        return True
