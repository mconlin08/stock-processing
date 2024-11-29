
import asyncio
from asyncio import create_task

from src.async_session_manager import AsyncSessionManager

from src.controllers.robinhood.rh_auth_controller import RHAuthController
from src.controllers.robinhood.rh_account_controller import RHAccountController

from src.controllers.data.historical_data_controller import HistoricalDataController

async def main(range: str = '1Y', period: str = 'Daily'):
    try:
        # login
        RHAuthController.login(
            username=RHAuthController.get_username(),
            password=RHAuthController.get_password(),
            totp=RHAuthController.get_mfa_totp()
        )
            
        # extract holdings and separate into stocks and etfs
        holdings = RHAccountController.get_holdings()    
        stocks_tickers = [item['ticker'] for item in holdings if 'stock' in item['type']]
        etf_tickers = [item['ticker'] for item in holdings if 'et' in item['type']]
       
        # create historical data controller
        hdc = HistoricalDataController()

        # get historical data for stocks
        stocks_historical_data = create_task(process_asset_tickers(hdc, stocks_tickers, 'stock', range, period))
        etfs_historical_data = create_task(process_asset_tickers(hdc, etf_tickers, 'etf', range, period))
        
        # return object with all data        
        return {
            'stocks_history': await stocks_historical_data,
            'etfs_history': await etfs_historical_data
        }
    except BaseException as e:
        raise e
    finally:
        await AsyncSessionManager.close_session()
        
        RHAuthController.logout()

async def process_asset_tickers(hdc: HistoricalDataController, tickers: list[str], asset_type: str, range: str, period: str):
    # intial values
    dataset = []
    count = 0
    asset = 'e' if asset_type == 'etf' else 's'
    
    # get historical data for stocks
    print(f"Fetching history for {len(tickers)} {asset_type}s...")
    for ticker in tickers:
        data = create_task(hdc.get_asset_historical_data(ticker, asset, range, period))
        
        # add data to dataset
        dataset.append({
            'asset': ticker,
            'asset_type': asset_type,
            'history': await data
        })
        
        await asyncio.sleep(0.25)
        count += 1
        print(f"[{count}/{len(tickers)}] done.", end="\r", flush=True)
    print("\n")
    
    return dataset