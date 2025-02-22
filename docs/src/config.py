import polars as pl

pl.Config(
     tbl_formatting='UTF8_BORDERS_ONLY',
     tbl_cell_numeric_alignment='RIGHT',
     set_tbl_column_data_type_inline=False,
     set_tbl_hide_dtype_separator=True,
     set_tbl_rows=6,
     set_tbl_width_chars=250,
     thousands_separator=',',
     decimal_separator='.',
     float_precision=2,
     fmt_str_lengths=5,
     set_tbl_cols=12,
     set_trim_decimal_zeros=True,
)
