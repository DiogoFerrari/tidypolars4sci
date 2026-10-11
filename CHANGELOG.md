## [0.0.1.23]

* `tp.map()` now always calls the function with one positional argument
  per column, in the order of `cols` (e.g. `tp.map(['a', 'b'], lambda a, b: a + b)`).
  With a single column the function receives the value itself, not a
  one-element list. Functions written as `lambda row: row[0] ...` must
  be updated.
* `tibble.replace()` gains a `strict` argument. By default (`False`),
  variable names in the replacement dictionary that are not in the data
  are ignored; with `strict=True` an error is raised.

## [0.0.1.22] 

* Minor corrections to create latex tables using tibble.to_latex()

## [0.0.1] 

* First release of `tidypolars4sci`
