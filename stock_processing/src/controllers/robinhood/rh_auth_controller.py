
# rh_auth_controller.py
import asyncio
import os
import pyotp

from asyncio import create_task

from robin_stocks import robinhood as r

# Interacts with robin_stocks library
# Tests at tests/test_auth_controller.py
class RHAuthController:
    """
    Interacts with the robin_stocks authentication module. Providing
    robust methods for retrieving "rh_usr", "rh_pwd", and "rh_totp"
    from the environment and handling the log in process.
    """

    """Current logged in status"""
    logged_in: bool = False 
    

    @classmethod
    def get_logged_in_status(cls) -> bool:
        """
        Returns logged in status as a string.
        @return (bool)
        """
        return cls.logged_in

    @classmethod
    def get_mfa_totp(cls) -> str:
        """
        Retrieves TOTP code from the "rh_totp" environment variable.
        @return (str) totp_code
        """
        mfa_code = os.getenv("rh_totp")
        if mfa_code is None:
             raise ValueError("MFA code is none.")

        totp = pyotp.TOTP(mfa_code).now()
        if not totp:
            raise ValueError("TOTP is none.")

        return totp  # code for login
    
    @classmethod
    def get_password(cls) -> str:
        """
        Retrieves password  from the "rh_pwd" environment variable.
        @return (str) password
        """

        pwd = os.getenv("rh_pwd")
        if pwd is None:
            raise ValueError("Username is none.")
        return pwd

    @classmethod
    def get_username(cls) -> str:
        """
        Retrieves username from the "rh_usr" environment variable.
        @return (str) username
        """
        usr = os.getenv("rh_usr")
        if usr is None:
            raise ValueError("Username is none.")
        return usr

    @classmethod
    def login(cls, username: str, password: str, totp: str) -> None:
        """
        Gracefully attempts programmatic log in.
        @param (str) username: Account email.
        @param (str) password: Account password.
        @param (str) totp: TOTP code
        @returns None
        """
        if username is None or password is None or totp is None: # check args
            raise ValueError("Username, TOTP, or password is empty.")

        # try login
        try:
            print("Logging in...")
            r.authentication.login(username=username, password=password, mfa_code=totp)
            cls.logged_in = True
        except Exception as e:      
            print("There was an error logging in.")
            raise e
        
    @classmethod
    def logout(cls) -> None:
        """
        Handles logging out of session.
        @returns None
        """
        print("Logging out...")
        if cls.logged_in:
            r.authentication.logout()
            cls.logged_in = False