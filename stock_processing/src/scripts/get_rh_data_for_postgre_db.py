import asyncio
import asyncpg
from asyncio import create_task

from src.async_session_manager import AsyncSessionManager
from src.controllers.robinhood.rh_auth_controller import RHAuthController
from src.controllers.robinhood.rh_account_controller import RHAccountController
from src.controllers.robinhood.rh_db_controller import RHDatabaseController
from src.controllers.data.historical_data_controller import HistoricalDataController

async def main(range: str = '1Y', period: str = 'Daily'):
    try:
        # Log in to Robinhood
        RHAuthController.login(
            username=RHAuthController.get_username(),
            password=RHAuthController.get_password(),
            totp=RHAuthController.get_mfa_totp()
        )
        
        dbc = RHDatabaseController(db_name="public")
        rhac = RHAccountController()

        # Set up PostgreSQL connection
        conn = dbc.get_connection()
        if not await conn:
            raise BaseException('No connection.')

        # Fetch account information
        account_data = rhac.get_user_profile()
        await insert_account(conn, account_data)

        # Fetch holdings and separate into stocks and ETFs
        holdings = rhac.get_holdings()
        stocks_tickers = [item['ticker'] for item in holdings if 'stock' in item['type']]
        etf_tickers = [item['ticker'] for item in holdings if 'et' in item['type']]

        # Insert holdings into the database
        await insert_holdings(conn, holdings)

        # Set up historical data controller
        hdc = HistoricalDataController()

        # Fetch and insert historical data for stocks and ETFs
        stocks_historical_data = create_task(process_asset_tickers(await conn, hdc, stocks_tickers, 'stock', range, period))
        etfs_historical_data = create_task(process_asset_tickers(await conn, hdc, etf_tickers, 'etf', range, period))

        # Wait for both tasks to complete
        await asyncio.gather(stocks_historical_data, etfs_historical_data)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await AsyncSessionManager.close_session()
        RHAuthController.logout()
        await conn.close()

async def insert_account(conn, account_data):
    try:
        await conn.execute('''
            INSERT INTO accounts (account_number, total_equity, extended_hours_equity, cash, dividend_total)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (account_number) DO UPDATE SET
                total_equity = EXCLUDED.total_equity,
                extended_hours_equity = EXCLUDED.extended_hours_equity,
                cash = EXCLUDED.cash,
                dividend_total = EXCLUDED.dividend_total
        ''', account_data['account_number'], account_data['total_equity'],
           account_data['extended_hours_equity'], account_data['cash'], account_data['dividend_total'])
    except Exception as e:
        print(f"Failed to insert account data: {e}")

async def insert_holdings(conn, holdings):
    for holding in holdings:
        try:
            # Insert stock data if it doesn't already exist
            await conn.execute('''
                INSERT INTO stocks (ticker, name, type, pe_ratio)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (ticker) DO NOTHING
            ''', holding['ticker'], holding['name'], holding['type'], holding.get('pe_ratio'))

            # Insert or update holdings data
            await conn.execute('''
                INSERT INTO holdings (account_id, stock_id, quantity, average_buy_price, equity, percent_change, equity_change, percentage_of_portfolio)
                VALUES (
                    (SELECT account_id FROM accounts WHERE account_number = $1),
                    (SELECT stock_id FROM stocks WHERE ticker = $2),
                    $3, $4, $5, $6, $7, $8
                )
                ON CONFLICT (account_id, stock_id) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    equity = EXCLUDED.equity,
                    percent_change = EXCLUDED.percent_change
            ''', holding['account_number'], holding['ticker'], holding['quantity'],
               holding['average_buy_price'], holding['equity'], holding['percent_change'],
               holding['equity_change'], holding['percentage_of_portfolio'])
        except Exception as e:
            print(f"Failed to insert holding for ticker {holding['ticker']}: {e}")

async def process_asset_tickers(conn, hdc, tickers: list[str], asset_type: str, range: str, period: str):
    print(f"Fetching history for {len(tickers)} {asset_type}s...")
    for ticker in tickers:
        try:
            # Fetch historical data
            historical_data = await hdc.get_asset_historical_data(ticker, asset_type, range, period)
            await insert_historical_data(conn, ticker, historical_data)
            print(f"Inserted historical data for {ticker}")
        except Exception as e:
            print(f"Failed to process historical data for ticker {ticker}: {e}")
        await asyncio.sleep(0.25)

async def insert_historical_data(conn, ticker, historical_data):
    try:
        stock_id = await conn.fetchval('SELECT stock_id FROM stocks WHERE ticker = $1', ticker)
        if not stock_id:
            print(f"Stock ID not found for ticker {ticker}. Skipping historical data insertion.")
            return

        for data_point in historical_data:
            await conn.execute('''
                INSERT INTO stock_historical_prices (stock_id, date, open_price, close_price, high_price, low_price, volume, adjusted_close)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (stock_id, date) DO NOTHING
            ''', stock_id, data_point['date'], data_point['open_price'], data_point['close_price'],
               data_point['high_price'], data_point['low_price'], data_point['volume'], data_point['adjusted_close'])
    except Exception as e:
        print(f"Failed to insert historical data for ticker {ticker}: {e}")

if __name__ == "__main__":
    asyncio.run(main())