class ResponseException(Exception):
    """Unsuccesful web service response."""

    pass


class InvalidFrequency(ResponseException):
    """Invalid search frequency."""

    pass


class InvalidCredentials(ResponseException):
    """Invalid username or password."""

    pass


class InvalidSeries(ResponseException):
    """Invalid time series id."""

    pass


class InvalidDate(ResponseException):
    """Invalid date format."""

    pass
