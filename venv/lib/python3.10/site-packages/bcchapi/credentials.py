"""Functions to get credentials."""

from getpass import getpass


def get_credentials() -> tuple:
    """Ask for username and password.

    Returns
    -------
    tuple
        A tuple of two strings: username and password.
    """
    user = input("user: ")
    password = getpass("pass: ")
    return user, password


def read_credentials(file: str) -> tuple:
    """Read credentails from a file.

    The first and second lines must be the username and password respectively.

    Parameters
    ----------
    file : str or Path
        A string string path or Path object.

    Returns
    -------
    tuple
        A tuple of two strings: username and password.
    """

    with open(file, "r") as f:
        user = next(f).rstrip("\n")
        password = next(f).rstrip("\n")

    return user, password
