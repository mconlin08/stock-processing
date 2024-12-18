
import asyncio
from fastapi import FastAPI, Depends
from pydantic import BaseModel

from src.orchestrators.stock_data_orchestrator import StockDataOrchestrator
from src.orchestrators.etf_data_orchestrator import ETFDataOrchestrator

from src.controllers.data.historical_data_controller import HistoricalDataController
from src.controllers.data.quote_data_controller import QuoteDataController
from src.controllers.data.time_series_data_controller import TimeSeriesDataController

from src.controllers.data.stocks.financials.balance_sheet_data_controller import BalanceSheetDataController
from src.controllers.data.stocks.financials.cash_flow_data_controller import CashFlowDataController
from src.controllers.data.stocks.financials.income_data_controller import IncomeDataController
from src.controllers.data.stocks.financials.ratios_data_controller import RatiosDataController

from src.controllers.data.stocks.statistics.revenue_data_controller import RevenueDataController

from src.async_session_manager import AsyncSessionManager

# start API and define shutdown process
app = FastAPI()
async def close_session():
    await AsyncSessionManager.close_session()

app.add_event_handler("shutdown", close_session)

#  -- Stocks routes --
@app.get("/stocks/{ticker}/data")
async def stock_data(ticker: str, sdo: StockDataOrchestrator = Depends(StockDataOrchestrator)):
    return await sdo.compose_stock_data(ticker)

@app.get("/stocks/{ticker}/financials/balance_sheet")
async def stock_over_time(ticker: str, bsdc: BalanceSheetDataController = Depends(BalanceSheetDataController)):
    return await bsdc.get_balance_sheet_data(ticker)

@app.get("/stocks/{ticker}/financials/cash_flow")
async def stock_over_time(ticker: str, cfdc: CashFlowDataController = Depends(CashFlowDataController)):
    return await cfdc.get_cash_flow_data(ticker)

@app.get("/stocks/{ticker}/financials/income")
async def stock_over_time(ticker: str, period: str = 'quarterly', idc: IncomeDataController = Depends(IncomeDataController)):
    return await idc.get_income_data(ticker, period)

@app.get("/stocks/{ticker}/financials/ratios")
async def stock_over_time(ticker: str, rdc: RatiosDataController = Depends(RatiosDataController)):
    return await rdc.get_ratios_data(ticker)

@app.get("/stocks/{ticker}/history")
async def stock_history(ticker: str, range: str = '1Y', period: str = 'Daily', hdc: HistoricalDataController = Depends(HistoricalDataController)):
    return await hdc.get_asset_historical_data(ticker, 's', range, period)

@app.get("/stocks/{ticker}/over_time")
async def stock_over_time(ticker: str, tsdc: TimeSeriesDataController = Depends(TimeSeriesDataController)):
    return await tsdc.get_asset_ts_data(ticker, 's')

@app.get("/stocks/{ticker}/quote")
async def etf_over_time(ticker: str, qdc: QuoteDataController = Depends(QuoteDataController)):
    return await qdc.get_asset_quote_data(ticker, 's')

@app.get("/stocks/{ticker}/statistics/revenue")
async def stock_over_time(ticker: str, rdc: RevenueDataController = Depends(RevenueDataController)):
    return await rdc.get_revenue_data(ticker)


# -- ETFs routes ---
@app.get("/etfs/{ticker}/data")
async def etf_data(ticker: str, edo: ETFDataOrchestrator = Depends(ETFDataOrchestrator)):
    return await edo.compose_etf_data(ticker)

@app.get("/etfs/{ticker}/history")
async def etf_history(ticker: str, range: str = '1Y', period: str = 'Daily', hdc: HistoricalDataController = Depends(HistoricalDataController)):
    return await hdc.get_asset_historical_data(ticker, 'e', range, period)

@app.get("/etfs/{ticker}/over_time")
async def etf_over_time(ticker: str, tsdc: TimeSeriesDataController = Depends(TimeSeriesDataController)):
    return await tsdc.get_asset_ts_data(ticker, 'e')

@app.get("/etfs/{ticker}/quote")
async def etf_over_time(ticker: str, qdc: QuoteDataController = Depends(QuoteDataController)):
    return await qdc.get_asset_quote_data(ticker, 'e')
