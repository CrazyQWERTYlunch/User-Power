"""
hashing.py

This module provides utilities for password hashing and verification.

Classes:
    Hasher: A class containing static methods for password hashing and verification.

"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hasher:
    """
    A class containing static methods for password hashing and verification.
    """

    @staticmethod
    def verify_password(plain_password, hashed_password):
        """
        Verify if a plain password matches its hashed version.

        Parameters:
            plain_password (str): The plain password.
            hashed_password (str): The hashed password.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """
        Generate a hash for a given password.

        Parameters:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        return pwd_context.hash(password)
