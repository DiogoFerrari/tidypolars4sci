from pathlib import Path
from ..io import read_data
from ..type_conversion import as_factor
from ..tibble_df import tibble

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
    df = tibble(df)
    df.__doc__
    doc = """
    A dataset containing the prices and other attributes of almost 54,000 diamonds.

    Description
    -----------

    The variables are as follows:

    |-----------+-----------------------------------------------------------+-----------------------------|
    | Attribute | Description                                               | Range                       |
    |-----------+-----------------------------------------------------------+-----------------------------|
    | Price     | Price in US dollars                                       | $326 – $18,823              |
    | Carat     | Weight of the diamond                                     | 0.2 – 5.01                  |
    | Cut       | Quality of the cut                                        | Fair, Good, Very Good,      |
    |           |                                                           |   Premium, Ideal            |
    | Color     | Diamond colour, from best (D) to worst (J)                | D (best) – J (worst)        |
    | Clarity   | Measurement of clarity (from worst to best)               | I1, SI2, SI1, VS2,          |
    |           |                                                           |   VS1, VVS2, VVS1, IF (best)|
    | X         | Length in mm                                              | 0 – 10.74                   |
    | Y         | Width in mm                                               | 0 – 58.9                    |
    | Z         | Depth in mm                                               | 0 – 31.8                    |
    | Depth     | Total depth percentage: z / mean(x, y) = 2 * z / (x + y)  | 43 – 79                     |
    | Table     | Width of top of diamond relative to widest point          | 43 – 95                     |
    |-----------+-----------------------------------------------------------+-----------------------------|

    References
    ----------
    * SWAPI, the Star Wars API, https://swapi.py4e.com/.
    """
    return df

