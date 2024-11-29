import asyncio
from asyncio import TimeoutError, CancelledError, create_task
from aiohttp import ClientResponseError

from typing import Dict, List, Any

from src.controllers.data.historical_data_controller import HistoricalDataController
from src.controllers.data.time_series_data_controller import TimeSeriesDataController

from src.controllers.data.stocks.financials.balance_sheet_data_controller import BalanceSheetDataController
from src.controllers.data.stocks.financials.cash_flow_data_controller import CashFlowDataController
from src.controllers.data.stocks.financials.income_data_controller import IncomeDataController
from src.controllers.data.stocks.financials.ratios_data_controller import RatiosDataController

from src.controllers.data.stocks.statistics.revenue_data_controller import RevenueDataController


class StockDataOrchestrator:
    def __init__(self,
                 bsdc=BalanceSheetDataController(),
                 cdc=CashFlowDataController(),
                 idc = IncomeDataController(),
                 hdc=HistoricalDataController(),
                 ratios_dc=RatiosDataController(),
                 revenue_dc=RevenueDataController(),
                 tsdc=TimeSeriesDataController(),
                 ) -> None:
        self.bsdc = bsdc
        self.cdc = cdc
        self.hdc = hdc
        self.ratios_dc = ratios_dc
        self.revenue_dc = revenue_dc
        self.tsdc = tsdc
        self.idc = idc

    async def compose_stock_data(self, ticker: str):
        '''
        Builds a dataset with a myriad of information about a stock from it's ticker.

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
            'asset_type': 'stock',
            'data': {}
        }

        # Get all data
        tasks = await asyncio.gather(*[
            self.hdc.get_asset_historical_data(ticker, 's', '5Y', 'Daily'),
            self.tsdc.get_asset_ts_data(ticker, 's'),
            self.bsdc.get_balance_sheet_data(ticker),
            self.cdc.get_cash_flow_data(ticker),
            self.idc.get_income_data(ticker, 'quarterly'),
            self.ratios_dc.get_ratios_data(ticker),
            self.revenue_dc.get_revenue_data(ticker)
        ])

        final['data'] = {task_data['data_type']: task_data['data'] for task_data in tasks}
            
        return final

    async def prepare_stock_data_tasks(self, ticker: str):
        '''
        Creates stock data tasks to be 'gathered' by asyncio.gather

        Arguments:
            ticker (str): The stock ticker symbol.

        Returns:
            dict: Composed data for the stock.
        '''
        # Concurrently create tasks for each data type with awaited individual tasks
        historical = self.hdc.get_asset_historical_data(
            ticker, 's', '5Y', 'Daily')
        time_series = self.tsdc.get_asset_ts_data(ticker, 's')
        balance_sheet = self.bsdc.get_balance_sheet_data(ticker)
        cash_flow = self.cdc.get_cash_flow_data(ticker)
        ratios = self.rdc.get_ratios_data(ticker)

        # Return all gathered data as a dictionary
        return [historical, time_series, balance_sheet, cash_flow, ratios]
