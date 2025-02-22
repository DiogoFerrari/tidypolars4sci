## Basic examples

To create new variables based transformation of existing ones:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python-Org*"}
import tidypolars4sci as tp
from tidypolars4sci.data import starwars

df = (starwars
      .head(5) # <= to select onlye the fist 5 for the example
      .select('name', 'mass')
      # create two new variables:
      .mutate(mass2 = tp.col('mass') * 2,
              mass2_squared = tp.col('mass2') * tp.col('mass2'),
              )
      )
df.print()
```

``` python
shape: (5, 4)
┌──────────────────────────────────────────────────┐
│ name               mass    mass2   mass2_squared │
│ str                 f64      f64             f64 │
╞══════════════════════════════════════════════════╡
│ Luke Skywalker    77.00   154.00       23,716.00 │
│ C-3PO             75.00   150.00       22,500.00 │
│ R2-D2             32.00    64.00        4,096.00 │
│ Darth Vader      136.00   272.00       73,984.00 │
│ Leia Organa       49.00    98.00        9,604.00 │
└──────────────────────────────────────────────────┘
```

## Change type of many variables at once

We can change the types of many variables that match a name pattern

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python-Org*"}
# select some rows and varibles
df = (starwars
      .head(5) 
      .select("name", "homeworld", "species")
      )
df.print()

```

``` python
shape: (5, 3)
┌──────────────────────────────────────┐
│ name             homeworld   species │
│ str              str         str     │
╞══════════════════════════════════════╡
│ Luke Skywalker   Tatooine    Human   │
│ C-3PO            Tatooine    Droid   │
│ R2-D2            Naboo       Droid   │
│ Darth Vader      Tatooine    Human   │
│ Leia Organa      Alderaan    Human   │
└──────────────────────────────────────┘
```

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python-Org*"}
# change to factor (i.e., category) those whose name matches hom|sp
df = df.mutate(tp.across(tp.matches("hom|sp"),  tp.as_factor))
df.print()

```

``` python
shape: (5, 3)
┌──────────────────────────────────────┐
│ name             homeworld   species │
│ str              cat         cat     │
╞══════════════════════════════════════╡
│ Luke Skywalker   Tatooine    Human   │
│ C-3PO            Tatooine    Droid   │
│ R2-D2            Naboo       Droid   │
│ Darth Vader      Tatooine    Human   │
│ Leia Organa      Alderaan    Human   │
└──────────────────────────────────────┘
```

## Using dynamic variable names

We can use dynamic names to create the new variable:

``` {.python exports="both" results="output code" tangle="02-mutate.py" cache="yes" noweb="no" session="*Python-Org*"}

new_var = "mass2_squared"
df = (starwars
      .head(5) # <= to select onlye the fist 5 for the example
      .select('name', 'mass')
      # create a new variable using dynamic name:
      .mutate(**{new_var : tp.col('mass') **2 })
      )
df.print()
```

``` python
shape: (5, 3)
┌─────────────────────────────────────────┐
│ name               mass   mass2_squared │
│ str                 f64             f64 │
╞═════════════════════════════════════════╡
│ Luke Skywalker    77.00        5,929.00 │
│ C-3PO             75.00        5,625.00 │
│ R2-D2             32.00        1,024.00 │
│ Darth Vader      136.00       18,496.00 │
│ Leia Organa       49.00        2,401.00 │
└─────────────────────────────────────────┘
```
