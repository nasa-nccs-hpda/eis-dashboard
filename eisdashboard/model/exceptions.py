class DashboardRuntimeException(Exception):
    """
    A custom exception class for use when
    exceptions are encountered during the runtime
    of the dashboard.
    """

    def __init__(self, message):
        super().__init__(message)
