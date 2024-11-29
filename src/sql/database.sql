-- Create the accounts table to store general account information
CREATE TABLE
    accounts (
        account_id SERIAL PRIMARY KEY,
        account_number VARCHAR(50) UNIQUE NOT NULL,
        total_equity DECIMAL(20, 2),
        extended_hours_equity DECIMAL(20, 2),
        cash_balance DECIMAL(20, 2),
        dividend_total DECIMAL(20, 2),
        created_at TIMESTAMP DEFAULT NOW (),
        updated_at TIMESTAMP DEFAULT NOW ()
    );

-- Create the stocks table to store static stock data
CREATE TABLE
    stocks (
        stock_id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) UNIQUE NOT NULL,
        name VARCHAR(100),
        type VARCHAR(50),
        sector VARCHAR(50),
        pe_ratio DECIMAL(10, 2),
        dividend_yield DECIMAL(5, 2),
        created_at TIMESTAMP DEFAULT NOW (),
        updated_at TIMESTAMP DEFAULT NOW ()
    );

-- Create the holdings table to store user holdings, linking to accounts and stocks
CREATE TABLE
    holdings (
        holding_id SERIAL PRIMARY KEY,
        account_id INT REFERENCES accounts (account_id) ON DELETE CASCADE,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        quantity DECIMAL(20, 6) NOT NULL,
        average_buy_price DECIMAL(20, 2),
        equity DECIMAL(20, 2),
        percent_change DECIMAL(10, 2),
        equity_change DECIMAL(20, 2),
        percentage_of_portfolio DECIMAL(5, 2),
        created_at TIMESTAMP DEFAULT NOW (),
        updated_at TIMESTAMP DEFAULT NOW ()
    );

-- Create the stock_historical_prices table to store historical price data for each stock
CREATE TABLE
    stock_historical_prices (
        price_id SERIAL PRIMARY KEY,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        date DATE NOT NULL,
        open_price DECIMAL(10, 2),
        close_price DECIMAL(10, 2),
        high_price DECIMAL(10, 2),
        low_price DECIMAL(10, 2),
        volume BIGINT,
        adjusted_close DECIMAL(10, 2),
        UNIQUE (stock_id, date)
    );

-- Create the positions table to store details about each position ever traded by the account
CREATE TABLE
    positions (
        position_id SERIAL PRIMARY KEY,
        account_id INT REFERENCES accounts (account_id) ON DELETE CASCADE,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        average_buy_price DECIMAL(20, 2),
        pending_average_buy_price DECIMAL(20, 2),
        quantity DECIMAL(20, 6) NOT NULL,
        intraday_average_buy_price DECIMAL(20, 2),
        intraday_quantity DECIMAL(20, 6),
        shares_held_for_buys DECIMAL(20, 6),
        shares_held_for_sells DECIMAL(20, 6),
        shares_held_for_stock_grants DECIMAL(20, 6),
        shares_held_for_options_collateral DECIMAL(20, 6),
        shares_held_for_options_events DECIMAL(20, 6),
        shares_pending_from_options_events DECIMAL(20, 6),
        updated_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT NOW ()
    );

-- Create the watchlists table to store user-created watchlists
CREATE TABLE
    watchlists (
        watchlist_id SERIAL PRIMARY KEY,
        account_id INT REFERENCES accounts (account_id) ON DELETE CASCADE,
        name VARCHAR(50) NOT NULL,
        created_at TIMESTAMP DEFAULT NOW (),
        updated_at TIMESTAMP DEFAULT NOW ()
    );

-- Create the watchlist_items table to associate stocks with each watchlist
CREATE TABLE
    watchlist_items (
        watchlist_item_id SERIAL PRIMARY KEY,
        watchlist_id INT REFERENCES watchlists (watchlist_id) ON DELETE CASCADE,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        UNIQUE (watchlist_id, stock_id)
    );

-- Create the dividends table to track dividend events for stocks in the portfolio
CREATE TABLE
    dividends (
        dividend_id SERIAL PRIMARY KEY,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        account_id INT REFERENCES accounts (account_id) ON DELETE CASCADE,
        date DATE NOT NULL,
        amount DECIMAL(10, 2) NOT NULL,
        UNIQUE (stock_id, account_id, date)
    );

-- Create the transactions table to log buy/sell transactions for each account
CREATE TABLE
    transactions (
        transaction_id SERIAL PRIMARY KEY,
        account_id INT REFERENCES accounts (account_id) ON DELETE CASCADE,
        stock_id INT REFERENCES stocks (stock_id) ON DELETE CASCADE,
        transaction_type VARCHAR(10) CHECK (transaction_type IN ('buy', 'sell')),
        date DATE NOT NULL,
        quantity DECIMAL(20, 6) NOT NULL,
        price_per_share DECIMAL(10, 2) NOT NULL,
        total_cost DECIMAL(20, 2) GENERATED ALWAYS AS (quantity * price_per_share) STORED,
        created_at TIMESTAMP DEFAULT NOW ()
    );

-- Create an index on stock ticker for quick lookup
CREATE INDEX idx_stocks_ticker ON stocks (ticker);

-- Create an index on account number for faster access to account details
CREATE INDEX idx_accounts_account_number ON accounts (account_number);

-- Create an index on transaction type to quickly access buy/sell transactions
CREATE INDEX idx_transactions_type ON transactions (transaction_type);

-- Create an index on historical prices date for quick date-based retrieval
CREATE INDEX idx_historical_prices_date ON stock_historical_prices (date);