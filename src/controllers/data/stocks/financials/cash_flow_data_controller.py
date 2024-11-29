# imports
from asyncio import CancelledError, TimeoutError, create_task
from typing import Dict, List, Optional, Any

from src.async_session_manager import AsyncSessionManager


class CashFlowDataController:
    '''Handles retrieving and formatting cash flow financial data'''
    
    cash_flow_base_url = 'https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/__data.json?x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001'
    
    cash_flow_keys_to_labels = {
        "datekey": "date_of_financial_data",
        "fiscalYear": "fiscal_year",
        "fiscalQuarter": "fiscal_quarter",
        "netIncomeCF": "net_income_operating_cash_flow_basis",
        "totalDepAmorCF": "total_depreciation_amortization",
        "sbcomp": "stock_based_compensation",
        "changeAR": "change_in_accounts_receivable",
        "changeInventory": "change_in_inventory",
        "changeAP": "change_in_accounts_payable",
        "changeUnearnedRev": "change_in_unearned_revenue",
        "changeOtherNetOperAssets": "change_in_other_net_operating_assets",
        "otheroperating": "other_operating_cash_flow_items",
        "ncfo": "net_cash_from_operating_activities",
        "ocfGrowth": "operating_cash_flow_growth",
        "capex": "capital_expenditures",
        "cashAcquisition": "cash_used_for_acquisitions",
        "salePurchaseIntangibles": "sale_purchase_of_intangibles",
        "investInSecurities": "investment_in_securities",
        "otherinvesting": "other_investing_cash_flow_items",
        "ncfi": "net_cash_from_investing_activities",
        "debtIssuedShortTerm": "short_term_debt_issued",
        "debtIssuedLongTerm": "long_term_debt_issued",
        "debtIssuedTotal": "total_debt_issued",
        "debtRepaidShortTerm": "short_term_debt_repaid",
        "debtRepaidLongTerm": "long_term_debt_repaid",
        "debtRepaidTotal": "total_debt_repaid",
        "netDebtIssued": "net_debt_issued",
        "commonIssued": "common_stock_issued",
        "commonRepurchased": "common_stock_repurchased",
        "commonDividendCF": "common_dividend_cash_flow",
        "otherfinancing": "other_financing_cash_flow_items",
        "ncff": "net_cash_from_financing_activities",
        "ncf": "net_cash_flow",
        "fcf": "free_cash_flow",
        "fcfGrowth": "free_cash_flow_growth",
        "fcfMargin": "free_cash_flow_margin",
        "fcfps": "free_cash_flow_per_share",
        "leveredFCF": "levered_free_cash_flow",
        "unleveredFCF": "unlevered_free_cash_flow",
        "cashInterestPaid": "cash_interest_paid",
        "cashTaxesPaid": "cash_taxes_paid",
        "changeNetWorkingCapital": "change_in_net_working_capital"
    }

    async def get_cash_flow_data(self, stock_ticker: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Gets Cash Flow data for a stock.

        Arguments:
            stock_ticker (str): Stock ticker.

        Returns:
            Optional[List[Dict[str, Any]]]: Cash flow data or None if not found.
        '''
        if not stock_ticker:
            raise BaseException('No stock ticker provided for cash flow data.')

        url = self.build_cash_flow_url(stock_ticker)
        
        data = create_task(self.fetch_cash_flow_data(url))
        
        if data:
            return {
                'data_type': 'cash_flow',
                'data': await data
            }
        else:
            raise BaseException(f'No cash flow data')

    def build_cash_flow_url(self, ticker: str) -> str:
        '''
        Builds URL for cash flow data using the given ticker.

        Arguments:
            ticker (str): Stock ticker.

        Returns:
            str: Constructed URL.
        '''
        return self.cash_flow_base_url.replace('{ticker}', ticker)

    def convert_keys_to_labels(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Relabels keys in a dictionary according to the cash_flow_keys_to_labels mapping.

        Arguments:
            entry (Dict[str, Any]): Dictionary of financial data.

        Returns:
            Dict[str, Any]: Dictionary with relabeled keys.
        '''
        return {self.cash_flow_keys_to_labels.get(key, key): value for key, value in entry.items()}

    async def fetch_cash_flow_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Handles retrieval of cash flow data from a URL.

        Arguments:
            url (str): URL for data.

        Returns:
            Optional[List[Dict[str, Any]]]: Formatted data or None if not found.
        '''
        response_json = await AsyncSessionManager.request_with_limit(url)
        if not response_json:
            raise f'No json for cash_flow data.'
                
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
            raise BaseException('No target financial index node.')

        financial_data = {
            key: [data[target_index] for target_index in indices]
            for key, indices in financial_data_indices.items()
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
