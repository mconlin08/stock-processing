
# imports
from asyncio import CancelledError, TimeoutError, create_task, Task

from src.async_session_manager import AsyncSessionManager


class QuoteDataController:
    '''Handles retrieving and formatting quote data'''
    base_url = 'https://api.stockanalysis.com/api/quotes/{asset_type}/{ticker}'

    valid_asset_types = [
        's',  # stock
        'e',  # etf
    ]
    
    stock_quote_data_keys_to_labels = {
        "c": "price_change",                            # Change in price from previous close
        "cdr": "change_direction",                      # Direction of change (e.g., -1 for decrease)
        "cl": "closing_price",                          # Current or last known closing price
        "cp": "percent_change",                         # Percentage change from previous close
        "days": "days_traded",                          # Days since start of trading session
        "e": "is_extended_hours",                       # Boolean indicating extended hours status
        "ec": "extended_hours_change",                  # Change in price during extended hours
        "ecp": "extended_hours_percent_change",         # Percentage change during extended hours
        "ep": "extended_hours_price",                   # Price during extended hours
        "epd": "extended_hours_previous_day_price",     # Previous day's extended hours price
        "es": "extended_hours_status",                  # Status of extended hours (e.g., "After-hours")
        "ets": "extended_hours_timestamp",              # Timestamp of the extended hours update
        "eu": "extended_hours_update_time",             # Last update time during extended hours
        "ex": "exchange",                               # Exchange where the asset is traded (e.g., NASDAQ)
        "exp": "extended_hours_price_expiration",       # Expiration time for the extended hours price
        "h": "high_price",                              # Daily high price
        "h52": "fifty_two_week_high",                   # 52-week high price
        "l": "low_price",                               # Daily low price
        "l52": "fifty_two_week_low",                    # 52-week low price
        "ms": "market_status",                          # Market status (e.g., "closed")
        "o": "open_price",                              # Opening price for the current trading day
        "p": "current_price",                           # Current price during normal trading hours
        "pd": "previous_close_price",                   # Previous day's closing price
        "symbol": "ticker_symbol",                      # Ticker symbol of the asset
        "td": "trading_date",                           # Date of the current trading session
        "ts": "timestamp",                              # Timestamp for the most recent price
        "u": "last_update_time",                        # Time of the last regular-hours price update
        "uid": "unique_id",                             # Unique identifier for the asset
        "v": "volume"                                   # Trading volume for the day
    }

    etf_quote_data_keys_to_labels = {
        "c": "price_change",                              # Change in price from previous close
        "cdr": "change_direction",                        # Direction of change (e.g., 1 for increase, -1 for decrease)
        "cl": "closing_price",                            # Closing price at the end of the regular trading session
        "cp": "percent_change",                           # Percentage change from previous close
        "days": "days_traded",                            # Days since start of trading session
        "e": "is_extended_hours",                         # Boolean indicating extended hours status
        "ec": "extended_hours_change",                    # Change in price during extended hours
        "ecp": "extended_hours_percent_change",           # Percentage change during extended hours
        "ep": "extended_hours_price",                     # Price during extended hours
        "epd": "extended_hours_previous_day_price",       # Previous day's extended hours price
        "es": "extended_hours_status",                    # Status of extended hours (e.g., "After-hours")
        "ets": "extended_hours_timestamp",                # Timestamp of the extended hours update
        "eu": "extended_hours_update_time",               # Last update time in extended hours
        "ex": "exchange",                                 # Exchange where the ETF is traded (e.g., NYSEARCA for ETFs)
        "exp": "extended_hours_price_expiration",         # Expiration time for extended hours price
        "h": "high_price",                                # Daily high price
        "h52": "fifty_two_week_high",                     # 52-week high price
        "l": "low_price",                                 # Daily low price
        "l52": "fifty_two_week_low",                      # 52-week low price
        "ms": "market_status",                            # Market status (e.g., "closed")
        "o": "open_price",                                # Opening price for the current trading day
        "p": "current_price",                             # Current price during regular trading hours
        "pd": "previous_close_price",                     # Previous day's closing price
        "symbol": "ticker_symbol",                        # ETF ticker symbol (e.g., "SCHD")
        "td": "trading_date",                             # Date of the current trading session
        "ts": "timestamp",                                # Timestamp for the most recent price
        "u": "last_update_time",                          # Time of the last price update in regular hours
        "uid": "unique_id",                               # Unique identifier for the ETF (e.g., "etfs/SCHD")
        "v": "volume"                                     # Trading volume for the ETF
    }


    async def get_asset_quote_data(self, ticker: str, asset_type: str):
        '''
            Gets quote for an asset.

            Arguments:
                ticker (str) Ticker for asset
                asset_type (str) Type of asset (e.g., e ('ETF'), s ('Stock'))

            Returns:
                quote_data (dict)
        '''

        # validate arguments
        if asset_type not in self.valid_asset_types:
            raise BaseException(f'Asset type: {asset_type} - is not valid.')

        # build url
        url = self.build_url_from_ticker(
            ticker=ticker,
            asset_type=asset_type,
        )

        # get data
        data = create_task(self.get_quote_data_from_url(url))
        if not await data:
            return {
                'data_type': 'quote',
                'data': data
            }

        # format data
        formatted_data = self.convert_keys_to_labels(await data, asset_type)

        if formatted_data is not None:
            # return data
            return {
                'data_type': 'quote',
                'data': formatted_data
            }
        else:
            raise f'Formatted_data is none'

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
            raise f'Invalid arguments for {__name__}'

        # build url
        url = self.base_url
        url = url.replace('{ticker}', ticker)
        url = url.replace('{asset_type}', asset_type)

        return url

    def convert_keys_to_labels(self, entry, asset_type: str):
        '''
        Relabels single character keys to a meaningful label depending on asset type

        Arguments:
            entry (dict) Dictionary item from historical data list

        Returns:
            converted_item (dict)
        '''

        if asset_type == 'e':
            return {self.etf_quote_data_keys_to_labels.get(key, key): value for key, value in entry.items()}
        
        if asset_type == 's':
            return {self.stock_quote_data_keys_to_labels.get(key, key): value for key, value in entry.items()}

    async def get_quote_data_from_url(self, url):
        '''
            Handles retrieval of quote data from url.

            Arguments:
                url (str) URL for data

            Returns:
                formatted_data (list)
        '''

        response_json = await AsyncSessionManager.request_with_limit(url)
        
        json_data = response_json.get('data', None)
        if not json_data:
            return json_data
            
        return json_data
