
import asyncio
from asyncio import TimeoutError, CancelledError, create_task

from src.controllers.data.historical_data_controller import HistoricalDataController
from src.controllers.data.time_series_data_controller import TimeSeriesDataController


class ETFDataOrchestrator:
    def __init__(self, hdc=HistoricalDataController(), tsdc=TimeSeriesDataController()) -> None:
        self.hdc = hdc
        self.tsdc = tsdc

    async def compose_etf_data(self, ticker: str):
        '''
            Arguments:
                ticker: str
            Returns:
                dict: {
                    'ticker': str,
                    'asset_type': str,
                    'data': dict,
                }
        '''
        
        final = {
            'ticker': ticker,
            'asset_type': 'etf',
            'data': {}
        }

        # Get all data
        tasks = await asyncio.gather(*[
            self.hdc.get_asset_historical_data(ticker, 'e', '5Y', 'Daily'),
            self.tsdc.get_asset_ts_data(ticker, 'e')
        ])

        final['data'] = {task_data['data_type']: task_data['data'] for task_data in tasks}
            
        return final

    async def prepare_etf_data_tasks(self, ticker: str):
        '''
        Creates etf task list

        Arguments:
            ticker (str): The etf ticker symbol.

        Returns:
            dict: Composed data for the stock.
        '''
        # Concurrently create tasks for each data type with awaited individual tasks
        historical = self.hdc.get_asset_historical_data(ticker, 'e', '5Y', 'Daily')
        time_series = self.tsdc.get_asset_ts_data(ticker, 'e')

        # Return all gathered data as a dictionary
        return [historical, time_series]
