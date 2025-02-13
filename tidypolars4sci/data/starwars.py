from pathlib import Path
from ..io import read_data

DATA_DIR = Path(__file__).parent

starwars = read_data(fn=DATA_DIR / "starwars.rda", sep=',')
starwars.__doc__ = """
Starwars characters dataset.

## Description

A dataset containing information on Star Wars characters, originally sourced from SWAPI 
(https://swapi.py4e.com/) and subsequently revised to reflect additional research into 
the gender and sex determinations of characters.

This dataset is structured as a tibble (data frame) with 87 rows and 14 variables.

## Format

+-------------+-------+-------------------------------------------------------------------------------+
| Variable    | Type  | Description                                                                   |
+-------------+-------+-------------------------------------------------------------------------------+
| name        | str   | Name of the character                                                         |
| height      | float | Height in centimeters                                                         |
| mass        | float | Weight in kilograms                                                           |
| hair_color  | str   | Hair color of the character                                                   |
| skin_color  | str   | Skin color of the character                                                   |
| eye_color   | str   | Eye color of the character                                                    |
| birth_year  | str   | Year the character was born, relative to the Battle of Yavin (BBY)            |
| sex         | str   | Biological sex of the character (e.g., male, female, hermaphroditic, or none) |
| gender      | str   | The character's gender role or identity                                       |
| homeworld   | str   | Name of the character's homeworld                                             |
| species     | str   | Name of the character's species                                               |
+-------------+-------+-------------------------------------------------------------------------------+

## Notes
The data reflect additional research into the representation of gender and sex in the 
Star Wars universe.


## Source

SWAPI, the Star Wars API, https://swapi.py4e.com/.

"""

