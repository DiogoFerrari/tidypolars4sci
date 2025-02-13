from pathlib import Path
from ..io import read_data

DATA_DIR = Path(__file__).parent

mtcars = read_data(fn=DATA_DIR / "mtcars.csv", sep=',')
mtcars.__doc__ = """
Motor Trend Car Road Tests

## Description

The data was extracted from the 1974 *Motor Trend* US magazine,
and comprises fuel consumption and 10 aspects of automobile
design and performance for 32 automobiles (1973–74 models).

## Format

A data frame with 32 observations on 11 variables.

|--------|------------------------------------------|
| Column | Description                              |
|========|==========================================|
| mpg    | Miles/(US) gallon                        |
| cyl    | Number of cylinders                      |
| disp   | Displacement (cu.in.)                    |
| hp     | Gross horsepower                         |
| drat   | Rear axle ratio                          |
| wt     | Weight (1000 lbs)                        |
| qsec   | 1/4 mile time                            |
| vs     | V/S                                      |
| am     | Transmission (0 = automatic, 1 = manual) |
| gear   | Number of forward gears                  |
| carb   | Number of carburetors                    |
|--------|------------------------------------------|

## Source

Henderson and Velleman (1981), Building multiple regression
models interactively. *Biometrics*, **37**, 391–411.
"""

