class WSPSError(Exception):
    """
    Base WSPS error class
    """

class WSPSUsageError(WSPSError):
    """
    User seems to be using the WSPS client in an invalid way
    """
