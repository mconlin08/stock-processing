# imports
from asyncio import CancelledError, TimeoutError, create_task
from typing import Dict, List, Optional, Any

from src.async_session_manager import AsyncSessionManager


class RatiosDataController:
    '''Handles retrieving and formatting ratios financial data'''

    financial_ratio_base_url = 'https://stockanalysis.com/stocks/{ticker}/financials/ratios/__data.json?x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001'

    financial_ratios_keys_to_labels = {
        "datekey": "date_of_financial_data",
        "fiscalYear": "fiscal_year",
        "fiscalQuarter": "fiscal_quarter",
        "marketcap": "market_cap",
        "marketCapGrowth": "market_cap_growth",
        "ev": "enterprise_value",
        "lastCloseRatios": "last_close_ratios",
        "pe": "price_to_earnings_ratio",
        "ps": "price_to_sales_ratio",
        "pb": "price_to_book_ratio",
        "pfcf": "price_to_free_cash_flow_ratio",
        "pocf": "price_to_operating_cash_flow_ratio",
        "evrevenue": "enterprise_value_to_revenue",
        "evebitda": "enterprise_value_to_ebitda",
        "evebit": "enterprise_value_to_ebit",
        "evfcf": "enterprise_value_to_free_cash_flow",
        "debtequity": "debt_to_equity_ratio",
        "debtebitda": "debt_to_ebitda_ratio",
        "debtfcf": "debt_to_free_cash_flow_ratio",
        "assetturnover": "asset_turnover_ratio",
        "inventoryTurnover": "inventory_turnover_ratio",
        "quickRatio": "quick_ratio",
        "currentratio": "current_ratio",
        "roe": "return_on_equity",
        "roa": "return_on_assets",
        "roic": "return_on_invested_capital",
        "earningsyield": "earnings_yield",
        "fcfyield": "free_cash_flow_yield",
        "dividendyield": "dividend_yield",
        "payoutratio": "payout_ratio",
        "buybackyield": "buyback_yield",
        "totalreturn": "total_return"
    }

    async def get_ratios_data(self, stock_ticker: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Gets ratios data for a stock.

        Arguments:
            stock_ticker (str): Stock ticker.

        Returns:
            Optional[List[Dict[str, Any]]]: Cash flow data or None if not found.
        '''
        if not stock_ticker:
            print('No stock ticker provided for cash flow data.')
            return None

        url = self.build_ratios_url(stock_ticker)
        
        data = create_task(self.fetch_ratios_data(url))
        
        if data:
            return {
                'data_type': 'ratios',
                'data': await data
            }
        else:
            raise BaseException('Ratios data is none.')

    def build_ratios_url(self, ticker: str) -> str:
        '''
        Builds URL for ratios data using the given ticker.

        Arguments:
            ticker (str): Stock ticker.

        Returns:
            str: Constructed URL.
        '''
        return self.financial_ratio_base_url.replace('{ticker}', ticker)

    def convert_keys_to_labels(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Relabels keys in a dictionary according to the financial_ratios_keys_to_labels mapping.

        Arguments:
            entry (Dict[str, Any]): Dictionary of financial data.

        Returns:
            Dict[str, Any]: Dictionary with relabeled keys.
        '''
        return {self.financial_ratios_keys_to_labels.get(key, key): value for key, value in entry.items()}

    async def fetch_ratios_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Handles retrieval of ratios data from a URL.

        Arguments:
            url (str): URL for data.

        Returns:
            Optional[List[Dict[str, Any]]]: Formatted data or None if not found.
        '''
        response_json = await AsyncSessionManager.request_with_limit(url)
        if not response_json:
            raise f'No json for balance_sheet data.'
                    
        return self.extract_financial_data(response_json)

    def extract_financial_data(self, response_json: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        '''
        Extracts financial data from the response JSON.

        Arguments:
            response_json (Dict[str, Any]): JSON response from the data request.

        Returns:
            Optional[List[Dict[str, Any]]]: Extracted financial data or None if not found.
        '''
        nodes = response_json.get('nodes')
        if not nodes or len(nodes) < 3:
            raise BaseException('Target node does not exist.')

        target_node = nodes[2]
        data = target_node.get('data')
        if not data:
            raise BaseException('No data was found in the target node.')

        financial_data_indices = self.get_financial_data_indices(data)
        if financial_data_indices is None:
            raise BaseException('Could not find target index node.')

        financial_data = {
            key: [data[target_index] for target_index in indices] for key, indices in financial_data_indices.items()
        }

        # Format the keys to labels
        formatted_data = [self.convert_keys_to_labels(financial_data)]
        return formatted_data

    def get_financial_data_indices(self, data: List[Dict[str, Any]]) -> Optional[Dict[str, List[int]]]:
        '''
        Extracts indices for financial data from the provided data.

        Arguments:
            data (List[Dict[str, Any]]): The raw data list.

        Returns:
            Optional[Dict[str, List[int]]]: Mapping of financial keys to their indices.
        '''
        financial_glossary_index = data[0].get('financialData')
        if financial_glossary_index is None:
            raise BaseException('No index for financialData was found.')

        financial_glossary_object = data[financial_glossary_index]
        if not financial_glossary_object:
            raise BaseException('No object existed at financialData index.')

        return {key: data[target_index] for key, target_index in financial_glossary_object.items()}
