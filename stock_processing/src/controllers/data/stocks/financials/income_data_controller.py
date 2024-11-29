# imports
from asyncio import CancelledError, TimeoutError, create_task
from typing import Dict, List, Optional, Any

from src.async_session_manager import AsyncSessionManager


class IncomeDataController:
    '''Handles retrieving and formatting income data'''

    financial_income_base_url = 'https://stockanalysis.com/stocks/{ticker}/financials/__data.json?p={period}&x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001'

    income_data_keys_to_labels = {
        "datekey": "date_of_financial_data",
        "fiscalYear": "fiscal_year",
        "fiscalQuarter": "fiscal_quarter",
        "revenue": "total_revenue",
        "revenueGrowth": "revenue_growth",
        "cor": "cost_of_revenue",
        "gp": "gross_profit",
        "sgna": "selling_general_and_administrative_expenses",
        "rnd": "research_and_development_expenses",
        "opex": "total_operating_expenses",
        "opinc": "operating_income",
        "interestExpense": "interest_expense",
        "interestIncome": "interest_income",
        "currencyGains": "currency_exchange_gains",
        "otherNonOperating": "other_non_operating_income",
        "ebtExcl": "earnings_before_tax_excluding_non_recurring_items",
        "gainInvestments": "gain_on_investments",
        "mergerRestructureCharges": "merger_and_restructuring_charges",
        "otherUnusualItems": "other_unusual_items",
        "pretax": "pretax_income",
        "taxexp": "tax_expense",
        "netinc": "net_income",
        "netinccmn": "net_income_common_stockholders",
        "netIncomeGrowth": "net_income_growth",
        "sharesBasic": "basic_shares_outstanding",
        "sharesDiluted": "diluted_shares_outstanding",
        "sharesYoY": "year_over_year_shares_growth",
        "epsBasic": "basic_earnings_per_share",
        "epsdil": "diluted_earnings_per_share",
        "epsGrowth": "earnings_per_share_growth",
        "fcf": "free_cash_flow",
        "fcfps": "free_cash_flow_per_share",
        "dps": "dividends_per_share",
        "dividendGrowth": "dividend_growth",
        "grossMargin": "gross_margin",
        "operatingMargin": "operating_margin",
        "profitMargin": "net_profit_margin",
        "fcfMargin": "free_cash_flow_margin",
        "taxrate": "effective_tax_rate",
        "ebitda": "earnings_before_interest_taxes_depreciation_amortization",
        "depAmorEbitda": "depreciation_and_amortization_in_ebitda",
        "ebitdaMargin": "ebitda_margin",
        "ebit": "earnings_before_interest_and_taxes",
        "ebitMargin": "ebit_margin",
        "legalSettlements": "legal_settlements",
        "payoutratio": "dividend_payout_ratio"
    }

    async def get_income_data(self, stock_ticker: str, period: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Gets income data for a stock.

        Arguments:
            stock_ticker (str): Stock ticker.

        Returns:
            Optional[List[Dict[str, Any]]]: income data or None if not found.
        '''
        if not stock_ticker:
            print('No stock ticker provided for income data.')
            return None

        url = self.build_income_url(stock_ticker, period)

        data = create_task(self.fetch_income_data(url))

        if data:
            return {
                'data_type': 'income',
                'data': await data
            }
        else:
            raise BaseException('Ratios data is none.')

    def build_income_url(self, ticker: str, period: str) -> str:
        '''
        Builds URL for income data using the given ticker.

        Arguments:
            ticker (str): Stock ticker.

        Returns:
            str: Constructed URL.
        '''
        
        url = self.financial_income_base_url.replace('{ticker}', ticker)
        url = url.replace('{period}', period)
        
        return url

    def convert_keys_to_labels(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Relabels keys in a dictionary according to the financial_income_keys_to_labels mapping.

        Arguments:
            entry (Dict[str, Any]): Dictionary of financial data.

        Returns:
            Dict[str, Any]: Dictionary with relabeled keys.
        '''
        return {self.income_data_keys_to_labels.get(key, key): value for key, value in entry.items()}

    async def fetch_income_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Handles retrieval of income data from a URL.

        Arguments:
            url (str): URL for data.

        Returns:
            Optional[List[Dict[str, Any]]]: Formatted data or None if not found.
        '''
        response_json = await AsyncSessionManager.request_with_limit(url)
        if not response_json:
            raise f'No json for income data.'

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
