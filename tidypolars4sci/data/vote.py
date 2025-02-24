from pathlib import Path
from ..io import read_data
from ..tibble_df import tibble

DATA_DIR = Path(__file__).parent

def __load_vote__():
    vote = read_data(fn=DATA_DIR / "vote.csv", sep=',', silently=True)
    vote.__doc__ = """
    Synthetic vote experiment data.

    ## Description

    A dataset containing simulated data on vote behavior.

    This dataset is structured as a tibble (data frame) with 2000 rows and 9 variables.

    ## Format
    +-------------+-------+-------------------------------------------------------------------------+
    | Variable           | Type  | Description                                                      |
    +-------------+-------+-------------------------------------------------------------------------+
    | age                | int   | Age                                                              |
    | income             | float | Income (standardized)                                            |
    | gender             | int   | Gender (Male=0; Female=1)                                        |
    | ideology           | float | Ideology self-placement (left=-10 to right=10)                   |
    | treatment          | int   | Treatment group (treated=1; control=0)                           |
    | group              | str   | Group                                                            |
    | partisanship       | str   | Partisanship (Democrat or Republican)                            |
    | vote_conservative  | int   | Voted for the most conservative in-party candidate (Yes=1, No=0) |
    | rate_conservative  | float | Voters  rate of the most conservative in-party candidate         |
    |                    |       | (Dislike=low value; Like=high value)                             |
    +-------------+-------+-------------------------------------------------------------------------+

    """
    vote.__codebook__ = codebook()
    return vote


def codebook():
    data = {
        "Variable": ["age", "income", "gender", "ideology",
                     "treatment", "group", "partisanship",
                     "vote_conservative", "rate_conservative"],
        "Type": ["int", "float", "int", "float", "int",
                 "str", "str", "int", "float"],
        "Description": [
            "Age",
            "Income (standardized)",
            "Gender (Male=0; Female=1)",
            "Ideology self-placement (left=-10 to right=10)",
            "Treatment group (treated=1; control=0)",
            "Group",
            "Partisanship (Democrat or Republican)",
            "Voted for the most conservative in-party candidate (Yes=1, No=0)",
            "Voters rate of the most conservative in-party candidate (Dislike=low value; Like=high value)"
        ]
    }
    return tibble(data)
