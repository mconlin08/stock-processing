# imports
from asyncio import CancelledError, TimeoutError, create_task
from typing import Dict, List, Optional, Any

from src.async_session_manager import AsyncSessionManager


class RevenueDataController:
    '''Handles retrieving and formatting revenue financial data'''

    revenue_base_url = 'https://stockanalysis.com/stocks/{ticker}/revenue/__data.json?x-sveltekit-trailing-slash=1&x-sveltekit-invalidated=001'

    async def get_revenue_data(self, stock_ticker: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Gets revenue data for a stock.

        Arguments:
            stock_ticker (str): Stock ticker.

        Returns:
            Optional[List[Dict[str, Any]]]: Cash flow data or None if not found.
        '''
        if not stock_ticker:
            raise BaseException('No stock ticker provided for cash flow data.')

        url = self.build_revenue_url(stock_ticker)

        data = create_task(self.fetch_revenue_data(url))

        if data:
            return {
                'data_type': 'revenue',
                'data': await data
            }
        else:
            raise BaseException(f'revenue data is none')

    def build_revenue_url(self, ticker: str) -> str:
        '''
        Builds URL for revenue data using the given ticker.

        Arguments:
            ticker (str): Stock ticker.

        Returns:
            str: Constructed URL.
        '''
        return self.revenue_base_url.replace('{ticker}', ticker)

    def convert_keys_to_labels(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Relabels keys in a dictionary according to the financial_revenue_keys_to_labels mapping.

        Arguments:
            entry (Dict[str, Any]): Dictionary of financial data.

        Returns:
            Dict[str, Any]: Dictionary with relabeled keys.
        '''
        return {self.revenue_keys_to_labels.get(key, key): value for key, value in entry.items()}

    async def fetch_revenue_data(self, url: str) -> Optional[List[Dict[str, Any]]]:
        '''
        Handles retrieval of revenue data from a URL.

        Arguments:
            url (str): URL for data.

        Returns:
            Optional[List[Dict[str, Any]]]: Formatted data or None if not found.
        '''
        response_json = await AsyncSessionManager.request_with_limit(url)
        if not response_json:
            raise f'No json for revenue data.'

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

        # financial_data = {
        #     key: [data[target_index] for target_index in indices] for key, indices in financial_data_indices.items()
        # }
        
        # retrieve values for financial_data values
        financial_data = {
            key: [{dict_key: data[target_index] for dict_key, target_index in item.items()} 
                for item in [data[idx] for idx in indices] if 'limited' not in item.keys()]
            for key, indices in financial_data_indices.items()
        }
            
        return financial_data

    def get_financial_data_indices(self, data: List[Dict[str, Any]]) -> Optional[Dict[str, List[int]]]:
        '''
        Extracts indices for financial data from the provided data.

        Arguments:
            data (List[Dict[str, Any]]): The raw data list.

        Returns:
            Optional[Dict[str, List[int]]]: Mapping of financial keys to their indices.
        '''
        financial_glossary_index = data[0].get('data')
        if financial_glossary_index is None:
            raise BaseException('No index for data was found.')

        financial_glossary_object = data[financial_glossary_index]
        if not financial_glossary_object:
            raise BaseException('No object existed at data index.')

        return {key: data[target_index] for key, target_index in financial_glossary_object.items()}
