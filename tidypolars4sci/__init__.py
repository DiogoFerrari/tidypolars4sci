try:
    from importlib.metadata import version
    __version__ = version("tidypolars4sci")
except:
    __version__ = ""


from .io import *
from .funs import *
from .helpers import *
from .reexports import *
from .stringr import *
from .stats import *
from .tibble_df import * 
from .type_conversion import *
from .utils import *

__all__ = (
    io.__all__ +
    tibble_df.__all__ +
    reexports.__all__  +
    helpers.__all__  +
    stats.__all__  +
    type_conversion.__all__  +
    funs.__all__  
)


