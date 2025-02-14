from pathlib import Path
from .diamonds import __load_diamonds__
from .mtcars import __load_mtcars__
from .starwars import __load_starwars__

__all__ = (
    "diamonds",
    "mtcars",
    "starwars",
)

DATA_DIR = Path(__file__).parent

diamonds = __load_diamonds__()
mtcars = __load_mtcars__()
starwars = __load_starwars__()
