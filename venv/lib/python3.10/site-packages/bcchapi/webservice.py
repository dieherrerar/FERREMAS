"""Central Bank of Chile Statistical Database Web Service implementation."""

import requests

from .wsresponse import WSResponse, GSResponse, SSResponse
from .exception import InvalidFrequency, InvalidCredentials, InvalidSeries, InvalidDate
from .credentials import read_credentials


class Session:
    """Central Bank of Chile Statistical Database Connection.

    The Central Bank of Chile provides two methods in this web service. The first one
    allows the retrieval of time series data and the second contains a caralogue of
    available timeseries.

    Parameters
    ----------
    usr : str, optional
        Username.
    pwd : str, optional
        Password.
    file : str or Path, optional
        Import credentials from a text file where the first and second lines are the
        username and password respectively.
    """

    def __init__(self, usr: str = None, pwd: str = None, *, file: str = None):
        self._usr = usr
        self._pwd = pwd

        if usr is None and pwd is None:
            if file is None:
                m = "Debe introducir usuario y contraseña o ruta de archivo con credenciales."
                raise ValueError(m)
            self._usr, self._pwd = read_credentials(file)

        self.URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
        self.FREQUENCIES = {"DAILY", "MONTHLY", "QUARTERLY", "ANNUAL"}

    def get(
        self, time_series: str, first_date: str = "", last_date: str = ""
    ) -> GSResponse:
        """Data series retrieving.

        Parameters
        ----------
        time_series : str
            Time series id to be retrieved.
        first_date : str or date-like, optional
            The starting date of the time series. Must be a string in ``'YYYY-MM-DD'``
            format or a date object with ``strftime`` method. If empty, it defaults to
            the first observation available.
        last_date : str or date-like, optional
            The last date of the time series. Must be a string in ``'YYYY-MM-DD'``
            format or a date object with ``strftime`` method. If empty, it defaults to
            the first observation available.

        Returns
        -------
        GSResponse
            A GSResponse object containing the data.

        Raises
        ------
        InvalidSeries
            If the series id is not found.
        InvalidCredentials
            If incorrect username or password.
        InvalidDate
            If date format is not ``'YYY-MM-DD'``.
        """

        if hasattr(first_date, "strftime"):
            first_date = first_date.strftime("%Y-%m-%d")

        if hasattr(last_date, "strftime"):
            last_date = last_date.strftime("%Y-%m-%d")

        params = {
            "user": self._usr,
            "pass": self._pwd,
            "firstdate": first_date,
            "lastdate": last_date,
            "timeseries": time_series,
            "function": "GetSeries",
        }
        response = self._make_request(params)

        if response.Codigo == -50:
            raise InvalidSeries(f"{time_series!r} not found.")

        if response.Codigo == -1:
            raise InvalidDate("Dates must be 'YYYY-MM-DD'.")

        return response._to_gsr()

    def search(self, frequency: str) -> SSResponse:
        """Provides a list of available timeseries per frequency.

        Parameters
        ----------
        frequency : ``{'DAILY', 'MONTHLY', 'QUARTERLY', 'ANNUAL'}``
            Periodicity of the time series to look up.

        Returns
        -------
        SSResponse
            A ``SSResponse`` containing the time series catalog and metadata.

        Raises
        ------
        InvalidFrequency
            If the frequency does not exists.
        InvalidCredentials
            If incorrect username or password.

        """
        params = {
            "user": self._usr,
            "pass": self._pwd,
            "frequency": frequency,
            "function": "SearchSeries",
        }
        response = self._make_request(params)

        if response.Codigo == -1:
            m = f"The 'frequency' argument must be one of {self.FREQUENCIES}, not {frequency!r}."
            raise InvalidFrequency(m)

        return response._to_ssr()

    def _make_request(self, params: dict) -> WSResponse:
        """Make a request to SieteRestWS.

        Parameters
        ----------
        params : dict
            Query parameters.

        Returns
        -------
        WSResponse
            A :class:`bcchapi.webservice.WSResponse` object.

        Raises
        ------
        InvalidCredentials
            If incorrect username or password.
        """
        r = requests.get(self.URL, params=params)
        r.raise_for_status()
        self.last_response = r.json()
        response = WSResponse(**self.last_response)

        if response.Codigo == -5:
            raise InvalidCredentials("Invalid username or password.")

        return response
