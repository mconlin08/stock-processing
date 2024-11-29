# rh_stocks_controller.py
import time

from robin_stocks import robinhood as r

# account controller?
class RHAccountController:
    """
    Handles accessing account information
    """
    @classmethod
    def get_holdings(keys=None):
        # retrieve data
        print("Getting holdings data...")
        try:
            holdings = r.account.build_holdings(with_dividends=True)
        # catch exceptions
        except ConnectionError as conn_err:
            raise ConnectionError(f"{__name__}: CONNECTION ERROR: {conn_err.strerror}")
        except Exception as exception:
            raise Exception(f"{__name__}: UNEXPECTED EXCEPTION: {exception}")

        # # null check
        if holdings is None:
            raise ValueError("Falied to build holdings")

        # make dictionary for comprehensive data
        print("Building dataset...")
        data = list()
        for ticker, details in holdings.items():
            holding_data = dict()
            holding_data['ticker'] = ticker
            for key, value in details.items():
                holding_data[f'{key}'] = value

            # add amount_paid_to_date
            if 'amount_paid_to_date' not in holding_data.keys():
                holding_data['amount_paid_to_date'] = None;

            data.append(holding_data)
            print(f"Processed {len(data)} of {len(holdings)}", end="\r", flush=True)
        print("\n", end="\r", flush=True)

        print("Done.")
        return data  # only need values

    @classmethod
    def get_profile():
        print("Getting profile data...")
        try:
            profile = r.account.build_user_profile()
        except ConnectionError as conn_err:
            raise ConnectionError(f"{__name__}: CONNECTION ERROR: {conn_err.strerror}")
        except Exception as exception:
            raise Exception(f"{__name__}: UNEXPECTED EXCEPTION: {exception}")

        if profile is None:
            raise ValueError("Falied to build profile data")

        return profile
