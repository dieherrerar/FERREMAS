"""Object to implement the Web Services for the user."""

import pandas as pd

from .webservice import Session
from .exception import InvalidSeries


class Stat:
    def __init__(self, usr: str = None, pwd: str = None, *, file: str = None):
        self.session = Session(usr, pwd, file=file)

    def table(
        self,
        series: list,
        first: str = "",
        last: str = "",
        *,
        names: list = None,
        frequency=None,
        observed=None,
        variation: int = None,
        stop_invalid: bool = True,
        resample_kw: dict = None,
        aggregate_kw: dict = None,
    ) -> pd.DataFrame:
        """Build a DataFrame with requested time series.

        Parameters
        ----------
        series : str, sequence or dict
            Time series ids to request. If dict is passed, keys are used as column
            names and the values as the series ids.
        first : str or date-like, optional
            The starting date of the table. Must be a string of ``'YYYY-MM-DD'``
            format or a date object with ``strftime`` method. If empty, it defaults to
            the first observation available.
        last : str or date-like, optional
            Last date of the table. Must be a string of ``'YYYY-MM-DD'`` format or a
            date object with ``strftime`` method. If empty, it defaults to the last
            observation available.
        names : list or sequence, optional
            Column names of the table. Must have the same length of series.
        frequency : str, optional
            Desired frequency conversion. This argument is passed to
            :meth:`pandas.DataFrame.resample`. Common values are ``'A'`` for
            annual, ``'Q'`` for quarterly, ``'M'`` for monthly, ``'D'`` for
            daily. By default these strings will set the date to the last day
            of the period. Including an *S* at the end of these strings (e.g.
            ``'AS'`` for annual) will set the resulting date to the first
            day of the period.
        observed : function, str, sequence, or dict, optional
            Aggregation function used when frecuency changes. Obligatory if
            frequency is not ``None``. This argument is passed directly to
            :meth:`pandas.DataFrame.aggregate` method.
        variation : int or str, optional
            Compute fractional change from previous observations. If variation is int,
            it defaults to monthly change. For example, ``variation=12`` computes a YOY
            change. If variation is str or any other object, it passes directly to the
            freq parameter in :meth:`pandas.DataFrame.pct_change`.
        stop_invalids : bool, optional
            Raise error if a time series is not available or does not exists. By default ``True``.
        resample_kw : dict, optional
            Aditional arguments passed into :meth:`pandas.DataFrame.resample` if
            frequency is changed.
        aggregate_kw : dict, optional
            Aditional arguments passed into :meth:`pandas.DataFrame.aggregate` if
            frequency is changed.

        Returns
        -------
        pandas.DataFrame
            A wide table with requested series.

        """
        if isinstance(series, dict):
            names = series.keys()
            series = series.values()

        elif isinstance(series, str):
            series = series.replace(" ", "").split(",")

        # Check that all series are strings
        for i in series:
            if not isinstance(i, str):
                m = f"Objets inside 'series' must be 'str', not '{type(i)}'"
                raise TypeError(m)

        # Get series
        data = []
        failed = []
        for ts in series:
            try:
                serie = self.session.get(ts, first, last)
            except InvalidSeries as e:
                if stop_invalid:
                    raise e
                failed.append(ts)
            else:
                data.append(serie)

        if len(data) == 0:
            m = "None of the requested series was found."
            raise InvalidSeries(m)

        data = map(lambda x: x.to_df(), data)
        df = pd.concat(data, axis=1)

        # Rearrange columns
        df = df[(i for i in series if i in df.columns)]

        # Rename columns
        if names:
            dnames = dict(zip(series, names))
            df = df.rename(columns=dnames)

        # Resample frequency
        if frequency:
            if not observed:
                m = "An aggregation function must be set in 'observed'."
                raise ValueError(m)

            if isinstance(observed, dict):
                # delete failed requests.
                for i in failed:
                    observed.pop(i)
            if not resample_kw:
                resample_kw = {}
            if not aggregate_kw:
                aggregate_kw = {}

            resampled = df.resample(frequency, **resample_kw)
            df = resampled.aggregate(observed, **aggregate_kw)

        # percent variations
        if variation:
            if isinstance(variation, int):
                # Convert to monthly offset.
                freq = pd.DateOffset(months=variation)
            else:
                freq = variation

            df = df.pct_change(freq=freq)

        return df

    def browse(
        self, contains: str, spanish: bool = False, cache: bool = True
    ) -> pd.DataFrame:
        """Search for strings in series names.

        Parameters
        ----------
        contains: str
            String to look at. Accepts regular expressions.
        spanish : bool, optional
            Search in spanish names. By default `False`.
        cache : bool, optional
            Use cache data if exists. By default `True`.

        Returns
        -------
        pandas.DataFrame
            A DataFrame object with matched series and their metadata.

        """

        if cache and hasattr(self, "_cache"):
            full_data = self._cache  # use cache data
        else:
            info = []
            for freq in self.session.FREQUENCIES:
                data = self.session.search(freq)
                data = data.to_df()
                info.append(data)

            full_data = pd.concat(info)

            if cache:
                self._cache = full_data  # save cache

        if spanish:
            column = "spanishTitle"
        else:
            column = "englishTitle"

        criteria = full_data[column].str.contains(contains, case=False)

        res = full_data.loc[criteria].reset_index(drop=True)

        return res


class Siete:
    """Spanish implementation of the Stat Class.

    .. seealso:: :class:`bcchapi.Stat` for the original class.
    """

    def __init__(self, usr: str = None, pwd: str = None, *, file: str = None):
        self.stat = Stat(usr, pwd, file=file)

    def cuadro(
        self,
        series: list,
        desde: str = "",
        hasta: str = "",
        *,
        nombres: list = None,
        frecuencia=None,
        observado=None,
        variacion: int = None,
        detener_invalidas: bool = True,
        resample_kw: dict = None,
        aggregate_kw: dict = None,
    ) -> pd.DataFrame:
        """Constructs a table with requested series.

        This is a spanish implementation of the method :meth:`bcchapi.Stat.table`.
        All parameters are passed without modification.
        """

        return self.stat.table(
            series=series,
            first=desde,
            last=hasta,
            names=nombres,
            frequency=frecuencia,
            observed=observado,
            variation=variacion,
            resample_kw=resample_kw,
            aggregate_kw=aggregate_kw,
            stop_invalid=detener_invalidas,
        )

    def buscar(
        self, contiene: str, ingles: bool = False, cache: bool = True
    ) -> pd.DataFrame:
        """Search for words in series names.

        This is a spanish implementation of the method :meth:`bcchapi.Stat.browse`.
        The only diffrence is that this function searches in the spanish names by
        default.

        Parameters
        ----------
        contiene: str
            Same as `contains`.
        ingles: bool, optional
            Filter by the english name instead of spanish. By default `False`.
        cache: bool
            Same as `cache`.

        """
        if ingles:
            spanish = False
        else:
            spanish = True

        return self.stat.browse(contains=contiene, spanish=spanish, cache=cache)
