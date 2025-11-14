from .tibble_df import from_pandas, from_polars
from .utils import _filter_kwargs_for, _expand_to_full_path_or_url
# 
import polars as pl
import copy
import re, os
import pandas as pd
import pyreadstat
# from pyreadr import read_r
from dataclasses import dataclass
from typing import Callable, List
from typing import Callable, List, Any
from typing import Dict, Optional, Tuple
# google spreadsheet
import gspread
from google.oauth2.service_account import Credentials

__all__ = [
    "read_data",
   ]

@dataclass
class DATA_LABELS:
    original: List[str]
    variables: Dict[str, Optional[str]]
    values: Dict[str, Optional[Dict[Any, str]]]

    def __post_init__(self):
        # Keep only variables with a real non-empty string label
        self.variables = {
            k: v
            for k, v in self.variables.items()
            if isinstance(v, str) and v.strip()
        }

        # complete the variable labels dictionary:
        #   for variables with no labels, use varname:varname
        variables_final = {}
        for var in self.original:
            label = var if var not in self.variables else self.variables[var]
            variables_final[var] = label
        self.variables = variables_final

        # Keep only variables with a non-empty value-label dict
        self.values = {
            k: d
            for k, d in self.values.items()
            if isinstance(d, dict) and len(d) > 0
        }

    def as_dict(self) -> Dict[str, Any]:
        return {
            "variables": self.variables,
            "values": self.values,
        }

class read_data():
    '''
    Read data into a tibble.

    Formats supported: csv, dta, xls, xlsx, ods, tsv, txt, tex,
    dat, sav, rds, Rdata, gspread

    Parameters
    ----------
    fn : str
        Full path to file, including filename. The type of file
        is inferred from the file extension. Hierarchical headers
        are accepted (see Notes).
        To see accepted formats, run: "``read_data.get_accepted_file_formats(True)``"
        To read from google spreadsheet directly, use "``credentials``"
        and "``url``" instead of "``fn``".
        To read from a URL with the file other from a google spreadsheet, use "``fn``".

    credentials : str
        Path to the .json file with Google API credentials
        to access the spreadsheet (see Notes).

    url : str
        Google spreadsheet URL

    sheet_name : str
        Name of the sheet to load.

    cols : list of str
        List with names of the columns to return.
        Used with .sav files.

    sep : str (Default ";")
        Specify the column separator for .csv files

    big_data : bool
        If True, uses dask to load the data. Default: False

    silently : bool (optional)
        If True, do now show a completion message

    sheet_name : str | int
        Sheet name or index.

    n_headers : int
        Used for data with hierarchical header.
        Number of header rows at the top of the sheet that are
        header of the columns. See notes.
        Defaults 0.

    header_combine_rule : callable(levels) -> str
        Used for data with hierarchical header.
        How to combine the list of non-empty levels into a final column name.
        Default (None) uses "level 1 (<level 2>, <level 3>... <level n>)" 
        If combine='_', it uses '_'.join(levels).

    combine_parenthesis_sep : str
        Used for data with hierarchical header.
        Used by default combine to separate levels grouped within
        parenthesis in the column name. Default uses ',':  "level 1 (<level 2>, <level 3>... <level n>)" 

    multi_col_sentinel : Any
        Used for data with hierarchical header.
        Value used in upper levels to indicate "continuation" of a merged
        header from the previous column (default: the string "None").

    Notes
    -----
    Other keyword arguments are accepted based on the underlying
    method that reads the file, which can be found in their
    respective documentation provided by the original module.

    Extension => underlying method:

    * .csv => polars.read_csv (uses sep=',' as default)
    * .tsv => polars.read_csv (uses sep='\t' as default)
    * .dat => polars.read_csv (uses sep=' ' as default)

    * .txt => polars.read_csv (lines into list)

    * .xls  => pandas.read_excel
    * .xlsx => pandas.read_excel
    * .xlt  => pandas.read_excel
    * .xltx => pandas.read_excel
    * .ods  => pandas.read_excel

    * .dta   => pandas.read_stata
    * .sav   => pyreadstat.read_sav
    * .rds   => pyreadr.read_r
    * .rda   => pyreadr.read_r
    * .Rdata => pyreadr.read_r

    Big data is handled with Dask

    Hierarchical header:

    Some data contains a hierarchical header, i.e., a multi-line header.
    Here is an example with 2 levels:

        |----------------------------------------|
        |     Party     |      Age      | Gender |
        |---------------|---------------|--------|
        | Code | Value  | value | group |        |
        |------|--------|-------|-------|--------|
        |    1 | Dem    | 23    | 20-29 |  M     |
        |    0 | Rep    | 33    | 30-39 |  F     |
        |----------------------------------------|

    When that is the case, the argument "``n_headers``" can be
    used to specify the number of header levels, or lines containing
    header information. 
    The function falttens the levels and combines the information into the
    header name to maintain a tidy format. The rule is
      * In upper levels (all rows except the last), values equal to
        multi_col_sentinel, None, or empty string are treated as "merged"
        and forward-filled horizontally.
      * In the last level, None or multi_col_sentinel is treated as
        "missing label" and is simply ignored for that level.
    The example above becomes:

        |--------------------------------------------------------------------|
        | Party (code)  | Party (value) | Age (value) | Age (group) | Gender |
        |---------------|---------------|-------------|-------------|--------|
        |    1          | Dem           | 23          | 20-29       |  M     |
        |    0          | Rep           | 33          | 30-39       |  F     |
        |--------------------------------------------------------------------|

    See "``header_combine_rule``" and "``combine_parenthesis_sep``"
    for more settings

    Load data from a google spreadsheet:

    It requires Google credentials. The settings follow Google
    requirements and gspread steps. Steps available here:
    - https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id

    Returns
    ------- 
    tibble when the file has no variable or value labels,
    (tibble, DATA_LABELS) when it does

    '''
    def __new__(self, *args, **kws):
         
        fn = _expand_to_full_path_or_url(kws.get('fn', None))
        url = kws.get('url', None)
        big_data = kws.get("big_data", False)
        silently = kws.get("silently", False)

        assert fn or url, "Either fn or url must be provided."

        if not bool(re.search(pattern="^http", string=fn)):
            assert os.path.isfile(fn), f"File {fn} not found."

        fn_base = os.path.basename(fn)
        fn_type = os.path.splitext(fn)[1] if fn else None
         
        ACCEPTED_FILES = self.get_accepted_file_formats()

        print(f"Loading data '{url or fn_base}'...", end=" ") if not silently else None
        if not big_data:
            
            if fn_type in ACCEPTED_FILES['csv-like']:
                df =self.read_csv(**kws)

            elif fn_type in ACCEPTED_FILES['excel-like']:
                df =self.read_xls(**kws)

            elif fn_type in ACCEPTED_FILES['Stata files']:
                df =self.read_dta(**kws)

            elif fn_type in ACCEPTED_FILES['SPSS files']:
                df = self.read_sav(**kws)

            elif fn_type in ACCEPTED_FILES['R files']:
                df = self.read_Rdata(**kws)

            elif kws.get('url', None) and kws.get('credentials', None):
                df =self.read_gspread(**kws)

            else:
                print(f"No reader for file type {fn_type}. If you are trying to read "+
                      "a Google spreadsheet, check the 'read_data' documentation.")
                df = None
        else:
            read_dask(fn, **kws)

        print("done!") if not silently else None
        return df

    def read_csv(**kws):
        reader = pl.read_csv
        kws_reader = _filter_kwargs_for(reader, kws)
        _, ext = os.path.splitext(kws.get("fn", None))

        sep = kws.get('sep', None)
        if ext in ['.tsv', '.TSV', '.txt', '.TXT']:
            sep =  sep or '\t'
        elif ext in ['.dat', '.DAT']:
            sep = sep or ' '
        else:
            sep = sep or ';'
        kws_reader['separator'] = sep
        
        fn = kws.get("fn", None)
        n = kws.get("n_headers", 0)
        if n>0:
            df  = reader(fn, skip_lines=n, has_header=False, **kws_reader)
            dfh = reader(fn, n_rows=n, has_header=False, **kws_reader)
            df = read_data._apply_multiheader_from_frames(df, dfh, **kws)
        else:
            df = from_polars(reader(fn, **kws_reader))
        return df
    
    def read_xls(**kws):
        reader = pd.read_excel
        kws_reader = _filter_kwargs_for(reader, kws)

        fn = kws.get("fn", None)
        n = kws.get("n_headers", 0)
        if n>0:
            df  = pl.from_pandas(reader(fn, skiprows=n, header=None, **kws_reader))
            dfh = pl.from_pandas(reader(fn, nrows=n, header=None, **kws_reader))
            df = read_data._apply_multiheader_from_frames(df, dfh, **kws)
        else:
            df = from_polars(from_pandas(reader(fn, **kws_reader)))

        return df

    def read_Rdata(**kws):
        from .io_r import load_r

        fn = kws.get("fn", None)
        df, labels = load_r(fn)
        return from_pandas(df), labels

    def read_dta(**kws):
        reader = pd.read_stata
        kws_reader = _filter_kwargs_for(reader, kws)

        fn=kws.get('fn')
        df = reader(fn, convert_categoricals=False, **kws_reader)
        df = from_pandas(df)

        labels    = reader(fn, iterator=True)
        variables = labels.variable_labels()
        values    = labels.value_labels()
        labels    = DATA_LABELS(original=df.names, variables=variables, values=values)
        return df, labels

    def read_sav(**kws):
        reader = pyreadstat.read_sav
        kws_reader = _filter_kwargs_for(reader, kws)

        fn=kws.get('fn')
        cols = kws.get("cols", None)
        if cols is not None:
            kws.pop('cols')

        if 'rows_range' in kws.keys():
            rows = kws.get("rows_range", [0, 0])
            row_first = rows[0] - 1
            row_last = rows[1] - row_first
            kws.pop('rows_range')
        else:
            row_first = 0
            row_last = 0

        df, meta = reader(fn,
                          usecols=cols,
                          row_offset=row_first,
                          row_limit=row_last,
                          **kws_reader)
        df = from_pandas(df)

        # collect labels
        variables = meta.column_names_to_labels
        values    = meta.variable_value_labels
        labels    = DATA_LABELS(original=df.names, variables=variables, values=values)
        
        return df, labels

    def read_gspread(**kws):
        assert kws.get("credentials", None),"A json file with google spreadsheet API"+\
            "credentials must be provided."
        assert kws.get("url", None),"The google spreadsheet URL must be provided."
        
        url = kws.get("url")
        credentials = os.path.abspath(os.path.expanduser(kws.get("credentials")))
        sheet_name = kws.get("sheet_name", 'Sheet1')

        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        auth = Credentials.from_service_account_file(credentials, scopes=scope)

        print('authorizing...', end='')
        gc = gspread.authorize(auth)
        print("loading worksheet...", end='')
        rows = gc.open_by_url(url).worksheet(sheet_name).get_all_values()

        n = kws.get("n_headers", 1)
        dfh = pl.from_pandas(pd.DataFrame(rows[:n]))
        df = pl.from_pandas(pd.DataFrame(rows[n:]))
        df = read_data._apply_multiheader_from_frames(df, dfh, **kws)

        return df

    def get_accepted_file_formats(_print=False):
        ACCEPTED_FILES = {
            'csv-like'                : ['.csv', '.CSV', '.tsv','.TSV', '.dat', '.DAT', '.txt', '.TXT'],
            'excel-like'              : ['.xls', '.xlsx', '.xlt', '.XLT', '.xltx', '.XLTX',
                                         '.ods', '.ODS', '.XLS', '.XLSX'],
            'R files'                 : ['.Rdata', '.rdata', '.rda', '.rds'],
            'Stata files'             : ['.dta', '.DTA'],
            'SPSS files'              : ['.sav'],
            'URL'                     : ['URL with any of the supported file types'],
            'Google Drive Spreadsheet': ['See documentation'],
        }
        if _print:
            res = None
            for file_types, extensions in ACCEPTED_FILES.items():
                exts = sorted(set([s.lower().replace(".", '') for s in extensions]))
                print(f"- {file_types}: {', '.join(exts)}")
        else:
            res = ACCEPTED_FILES
        return res
    
    def _combine_with_parens(levels: list[str], sep: str = ", ") -> str:
        # """
        # Combine levels into 'level1 (level2<sep>level3<sep>...)'.
        # Ignore empty or None lower levels.

        # Parameters
        # ----------
        # levels : list[str]
        #     List of hierarchical header labels, from top (general) to bottom (specific).
        # sep : str, optional
        #     Separator used to join lower-level labels. Default is ", ".
        # """
        # Clean and drop empties
        cleaned = [str(l).strip() for l in levels if l not in (None, "", "None")]
        if not cleaned:
            return ""

        base = cleaned[0]
        lowers = [lvl for lvl in cleaned[1:] if lvl]
        if not lowers:
            return base
        return f"{base} ({sep.join(lowers)})"

    def _apply_multiheader_from_frames(df_data: pl.DataFrame,
                                       df_header: pl.DataFrame,
                                       combine: Callable[[List[str]], str] | None = None,
                                       combine_parenthesis_sep = '; ',
                                       multi_col_sentinel: Any = "None",
                                       *args,
                                       **kws,
                                       ):
        # """
        # Given:
        #   - df_data: data with generic column names (no header rows)
        #   - df_header: header hierarchy, one row per level (top to bottom),
        #                same number of columns as df_data

        # Returns a copy of df_data with flattened column names built from df_header.

        # Semantics:
        #   * In upper levels (all rows except the last), values equal to
        #     multi_col_sentinel, None, or empty string are treated as "merged"
        #     and forward-filled horizontally.
        #   * In the last level, None or multi_col_sentinel is treated as
        #     "missing label" and is simply ignored for that level.

        # Parameters
        # ----------
        # df_data : pl.DataFrame
        #     The main data.
        # df_header : pl.DataFrame
        #     The header hierarchy (n_levels x n_columns).
        # combine : str or callable(levels) -> str, optional
        #     How to combine the list of non-empty levels into a final column name.
        #     Default (None) uses "level 1 (<level 2>, <level 3>... <level n>)" 
        #     If combine='_', it uses '_'.join(levels).
        # combine_parenthesis_sep : str
        #     Used by default combine to separate levels grouped within
        #     parenthesis in the column name. Default uses ',':  "level 1 (<level 2>, <level 3>... <level n>)" 

        # multi_col_sentinel : Any
        #     Value used in upper levels to indicate "continuation" of a merged
        #     header from the previous column (default: the string "None").
        # """
        # df_data = df_data.to_polars()
        # df_header = df_header.to_polars()
        combine = kws.get("header_combine_rule", None)

        if combine is None:
            combine = lambda levels: read_data._combine_with_parens(levels, sep=combine_parenthesis_sep)
        elif combine == '_':
            combine = lambda levels: "_".join(levels)

        # Turn header into a list-of-lists
        header_rows = [list(row) for row in df_header.rows()]
        n_levels = len(header_rows)
        if n_levels == 0:
            raise ValueError("df_header must have at least one row (a header level).")
        n_cols = len(header_rows[0])

        # Sanity check: match number of columns
        if len(df_data.columns) != n_cols:
            raise ValueError(
                f"df_data has {len(df_data.columns)} columns but df_header has {n_cols}."
            )

        # 1) Forward-fill in all upper levels (except last)
        for r in range(n_levels - 1):  # all levels except deepest
            last_val = None
            for c in range(n_cols):
                val = header_rows[r][c]

                is_missing = (
                    val is None
                    or val == ""
                    or (isinstance(val, str) and val == multi_col_sentinel)
                )

                if is_missing:
                    header_rows[r][c] = last_val
                else:
                    last_val = str(val)

        # 2) Clean last level: treat sentinel as missing
        last_idx = n_levels - 1
        for c in range(n_cols):
            val = header_rows[last_idx][c]
            if (
                val is None
                or val == ""
                or (isinstance(val, str) and val == multi_col_sentinel)
            ):
                header_rows[last_idx][c] = None
            else:
                header_rows[last_idx][c] = str(val)

        # --- NEW PART: compute cleaned levels & base counts ---

        cleaned_levels_per_col: list[list[str]] = []
        base_names: list[str | None] = []

        for c in range(n_cols):
            levels = [header_rows[r][c] for r in range(n_levels)]
            levels_clean = [
                str(x).strip()
                for x in levels
                if x is not None and str(x).strip() != ""
            ]
            cleaned_levels_per_col.append(levels_clean)
            base_names.append(levels_clean[0] if levels_clean else None)

        from collections import Counter
        base_counts = Counter(b for b in base_names if b is not None)

        # 3) Build final column names
        new_names: list[str] = []
        for c in range(n_cols):
            levels_clean = cleaned_levels_per_col[c]

            if not levels_clean:
                new_names.append(f"column_{c+1}")
                continue

            base = levels_clean[0]

            # RULE: if this base appears in exactly one column,
            # ignore lower levels and use only base.
            if base is not None and base_counts.get(base, 0) == 1:
                new_names.append(base)
            else:
                new_names.append(combine(levels_clean))

        # 4) Rename df_data columns according to order
        mapping = dict(zip(df_data.columns, new_names))
        res = from_polars(df_data.rename(mapping))
        return res

class read_dask:
         
   def __new__():
        print("To be implemented.")
        #     # return eDask(fn, **kws)
        #     return ddf.read_csv(fn, **kws)
        return None
