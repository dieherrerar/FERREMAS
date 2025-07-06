"""Clases que contienen respuestas del webservice."""

import pprint
import pandas as pd


class WSResponse:
    """Base class to handle web service responses.

    Each response contains the following attributes:

    Attributes
    ----------
    Codigo : int
        Response code.
    Descripcion : str
        Response code description.
    Series : dict
        Dictionary containing the requested series data from the method
        :meth:`~bcchapi.webservice.Session.get`. It is composed by 4 fields:

        * ``'descripEsp'``: spanish name
        * ``'descripIng'``: english name
        * ``'seriesId'``: series unique id
        * ``'Obs'``: list of dictionaries composed by 3 fields:

            * ``'indexDateString'``: date
            * ``'value'``: observation in text format (or ``'NaN'`` if data
              is missing)
            * ``'statusCode'``: ``'OK'`` if data exists

        If other method initiates this class, then all dictionary fields posses
        the string ``'null'``.
    SeriesInfos : list
        list of dictionaries containing metadata of series found by method
        :meth:`~bcchapi.webservice.Session.search`. Each dictionary is composed
        by 8 keys:

        * ``'seriesId'``: series unique id
        * ``'frequencyCode'``: series frequency
        * ``'spanishTitle'``: spanish name
        * ``'englishTitle'``: english name
        * ``'firstObservation'``: date of first available observation
        * ``'lastObservation'``: date of last available observation
        * ``'updatedAt'``: last update date
        * ``'createdAt'``: creation date

        If other method initiates this class, then SeriesInfos is an empty list.
    """

    def __init__(
        self, Codigo: int, Descripcion: str, Series: dict, SeriesInfos: list
    ) -> None:
        self.Codigo = Codigo
        self.Descripcion = Descripcion
        self.Series = Series
        self.SeriesInfos = SeriesInfos

    def __repr__(self):
        return f"""{self.__class__.__name__}(
    Codigo = {self.Codigo},
    Descripcion = {self.Descripcion},
    Series = {pprint.pformat(self.Series)},
    SeriesInfos = {pprint.pformat(self.SeriesInfos)}
    )"""

    def _to_gsr(self):
        return GSResponse(self.Codigo, self.Descripcion, self.Series, self.SeriesInfos)

    def _to_ssr(self):
        return SSResponse(self.Codigo, self.Descripcion, self.Series, self.SeriesInfos)


class GSResponse(WSResponse):
    """Contains GetSeries responses."""

    def to_series(self) -> pd.Series:
        """Transforms the results to a :class:`pandas.Series` object."""
        date_range = pd.to_datetime(
            [i["indexDateString"] for i in self.Series["Obs"]], dayfirst=True
        )
        obs = [float(i["value"]) for i in self.Series["Obs"]]
        serie = self.Series["seriesId"]
        return pd.Series(obs, date_range, name=serie)

    def to_df(self) -> pd.DataFrame:
        """Transforms the results to a :class:`pandas.DataFrame` object."""
        return self.to_series().to_frame()

    @property
    def nombre(self):
        """Spanish name."""
        return self.Series["descripEsp"]

    @property
    def name(self):
        """English name"""
        return self.Series["descripIng"]

    @property
    def id(self):
        """Series id."""
        return self.Series["seriesId"]


class SSResponse(WSResponse):
    """Contains SearchSeries responses."""

    def to_df(self) -> pd.DataFrame:
        """Transforms the results to a :class:`pandas.DataFrame` object."""

        df = pd.DataFrame(self.SeriesInfos)
        for key in ["firstObservation", "lastObservation", "updatedAt", "createdAt"]:
            df[key] = pd.to_datetime(df[key], errors="coerce", format="%d-%m-%Y")

        return df
