from pathlib import Path
from ..io import read_data
from ..type_conversion import as_factor

DATA_DIR = Path(__file__).parent

def __load_diamonds__():
    df = read_data(fn=DATA_DIR / "diamonds.csv", sep=',', silently=True)
    df = df.mutate(cut = as_factor('cut',
                                     levels="Fair, Good, Very Good, Premium, Ideal".split(", ")),
                   #  "I1 SI2 SI1 VS2 VS1 VVS2 VVS1 IF".split(),
                   clarity = as_factor('clarity'),
                   # list("DEFGHIJ")
                   color   = as_factor('color'),
                   )
    return df

