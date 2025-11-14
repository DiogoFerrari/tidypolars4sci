from __future__ import annotations
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="rpy2.rinterface")

from .io import DATA_LABELS
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

try:
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri, conversion, default_converter
    from rpy2.rinterface_lib.embedded import RRuntimeError
    from rpy2.rinterface_lib.sexp import NULLType
except ImportError as exc:
    raise ImportError(
        "io_r.py requires 'rpy2'. Install it with:\n\n"
        "    pip install rpy2\n"
    ) from exc

R = ro.r  # handle to the R interpreter


def _detect_file_type(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".rds":
        return "rds"
    if ext in {".rdata", ".rda"}:
        return "rdata"
    raise ValueError(f"Unsupported R file extension: {ext!r} (expected .rds or .RData/.rda)")

# --- Safe wrapper around readRDS() that does NOT print to console on error ---
_SAFE_READRDS = R(
    """
    function(path) {
      tryCatch(
        readRDS(path),
        error = function(e) {
          structure(
            list(message = conditionMessage(e)),
            class = "rds_error"
          )
        }
      )
    }
    """
)

def _is_null(x: Any) -> bool:
    # """Return True if x is an R NULL or Python None."""
    return x is None or isinstance(x, NULLType)

def _load_r_dataframe(path: Path, obj_name: Optional[str] = None) -> ro.vectors.DataFrame:
    # """
    # Load an R data.frame from .rds or .RData.

    # Parameters
    # ----------
    # path:
    #     Path to .rds or .RData file.
    # obj_name:
    #     If loading from .RData, optional name of the object to pick.
    #     If None, the first data.frame in the file is used.

    # Returns
    # -------
    # rpy2.robjects.vectors.DataFrame
    # """
    file_type = _detect_file_type(path)

    # --- First attempt: treat .rds as a real RDS file (without console error) ---
    if file_type == "rds":
        safe_res = _SAFE_READRDS(str(path))

        # Is this an "rds_error" object?
        if bool(R["inherits"](safe_res, "rds_error")[0]):
            # Unknown input format, etc. → treat as RData fallback
            file_type = "rdata"
        else:
            r_df = safe_res
            if not bool(R["is.data.frame"](r_df)[0]):
                raise TypeError(f"Object in {path} is not an R data.frame.")
            return r_df

    # --- RData logic (real .RData or “fake RDS” that is actually RData) ---
    if file_type == "rdata":
        loaded_names = list(R["load"](str(path)))  # character vector of object names

        if not loaded_names:
            raise ValueError(f"No objects found in RData file: {path}")

        if obj_name is not None:
            if obj_name not in loaded_names:
                raise ValueError(
                    f"Object {obj_name!r} not found in {path}. "
                    f"Available: {loaded_names}"
                )
            r_obj = ro.globalenv[obj_name]
            if not bool(R["is.data.frame"](r_obj)[0]):
                raise TypeError(f"Object {obj_name!r} in {path} is not an R data.frame.")
            return r_obj

        # Otherwise, pick the first data.frame in the .RData
        for name in loaded_names:
            r_obj = ro.globalenv[name]
            if bool(R["is.data.frame"](r_obj)[0]):
                return r_obj

        raise TypeError(
            f"No R data.frame found in {path}. "
            f"Objects present: {loaded_names}"
        )

    # Should not happen because _detect_file_type() would already have errored
    raise RuntimeError(f"Unexpected file_type for {path}: {file_type}")

# Coerce character columns to factors for safe conversion to pandas,
# preserving 'label' and 'labels' attributes.
_COERCE_CHAR_TO_FACTOR = R(
    """
    function(d) {
      is_char <- vapply(d, is.character, logical(1L))
      if (any(is_char)) {
        d[is_char] <- lapply(d[is_char], function(x) {
          lbl  <- attr(x, "label",  exact = TRUE)
          vlbl <- attr(x, "labels", exact = TRUE)

          xf <- as.factor(x)

          if (!is.null(lbl))  attr(xf, "label")  <- lbl
          if (!is.null(vlbl)) attr(xf, "labels") <- vlbl

          xf
        })
      }
      d
    }
    """
)

def _r_label_extractor() -> ro.functions.SignatureTranslatedFunction:
    # """
    # Build (once) the small R function that extracts variable- and value-labels.

    # It returns a list with:

    #   $var_labels   : named list of variable labels (or NULL)
    #   $value_labels : named list; each element is either
    #                   - NULL if no value labels, or
    #                   - named character vector with names = codes, values = labels
    #                     (code -> label mapping)
    # """
    return R(
        """
        function(d) {
          vars <- names(d)

          # Variable labels (attr(x, "label"))
          var_labels <- lapply(d, function(x) {
            lbl <- attr(x, "label", exact = TRUE)
            if (is.null(lbl)) return(NULL)
            if (length(lbl) == 0 || is.na(lbl[1])) return(NULL)
            as.character(lbl[1])
          })
          names(var_labels) <- vars

          # Value labels (attr(x, "labels"), e.g. haven::labelled)
          value_labels <- lapply(d, function(x) {
            labs <- attr(x, "labels", exact = TRUE)
            if (is.null(labs)) return(NULL)

            # Remove NA codes if any
            labs <- labs[!is.na(labs)]

            if (length(labs) == 0) return(NULL)

            # haven::labelled: names(labs) = labels, values(labs) = codes
            # We want mapping: code -> label
            codes  <- as.character(unname(labs))
            labels <- as.character(names(labs))
            out <- setNames(labels, codes)  # names = codes, values = labels
            out
          })
          names(value_labels) <- vars

          list(
            var_labels   = var_labels,
            value_labels = value_labels
          )
        }
        """
    )

_LABEL_FUN = _r_label_extractor()

def _extract_labels(r_df: ro.vectors.DataFrame) -> DATA_LABELS:
    # """
    # Extract variable and value labels from an R data.frame and return DATA_LABELS.

    # Only variables that actually have labels are included in the dicts.
    # """
    labels_r = _LABEL_FUN(r_df)

    # R objects:
    #   labels_r$var_labels   : named list of labels or NULL
    #   labels_r$value_labels : named list of named vectors or NULL
    var_labels_r = labels_r.rx2("var_labels")
    value_labels_r = labels_r.rx2("value_labels")

    var_names = list(r_df.names)

    # names() themselves can be NULL, so guard that too
    if _is_null(var_labels_r):
        var_label_names = set()
    else:
        vnames = var_labels_r.names
        var_label_names = set([] if _is_null(vnames) else list(vnames))

    if _is_null(value_labels_r):
        value_label_names = set()
    else:
        vlnames = value_labels_r.names
        value_label_names = set([] if _is_null(vlnames) else list(vlnames))

    variables: Dict[str, str] = {}
    values: Dict[str, Dict[Any, str]] = {}

    for var in var_names:
        # ---------- VARIABLE LABELS ----------
        if var in var_label_names and not _is_null(var_labels_r):
            vlabel_vec = var_labels_r.rx2(var)
            if _is_null(vlabel_vec):
                pass
            elif len(vlabel_vec) > 0:
                vlabel = str(vlabel_vec[0])
                if vlabel.strip() and vlabel.lower() != "na":
                    variables[var] = vlabel

        # ---------- VALUE LABELS ----------
        if var in value_label_names and not _is_null(value_labels_r):
            vlabels_vec = value_labels_r.rx2(var)
            if _is_null(vlabels_vec) or len(vlabels_vec) == 0:
                continue

            vnames = vlabels_vec.names
            if _is_null(vnames):
                continue

            # names(vlabels_vec) = codes, values = labels
            codes = [str(c) for c in list(vnames)]
            labs  = [str(x) for x in list(vlabels_vec)]
            mapping = {
                code: lab
                for code, lab in zip(codes, labs)
                if lab.strip()
            }
            if mapping:
                values[var] = mapping

    return DATA_LABELS(original=var_names, variables=variables, values=values)

def load_r(
    path: str,
    obj_name: Optional[str] = None,
) -> Tuple[pd.DataFrame, DATA_LABELS]:
    # """
    # Load an R dataset (.rds or .RData) and extract labels.

    # Parameters
    # ----------
    # path:
    #     Path to the R file (.rds or .RData/.rda).
    # obj_name:
    #     If reading from .RData, optional name of the object to load.
    #     If None, the first R data.frame in the file is used.

    # Returns
    # -------
    # (data, labels)
    #     data   : pandas.DataFrame with the R data.
    #     labels : DATA_LABELS instance with:
    #              - labels.variables: only vars with variable labels
    #              - labels.values   : only vars with value labels
    # """
    path_obj = Path(path)

    r_df = _load_r_dataframe(path_obj, obj_name=obj_name)

    # 1) Extract labels from the ORIGINAL R data.frame
    labels = _extract_labels(r_df)

    # 2) Coerce character columns to factors for safe Python conversion
    r_df_for_py = _COERCE_CHAR_TO_FACTOR(r_df)

    # 3) Convert the coerced data.frame to pandas
    with conversion.localconverter(default_converter + pandas2ri.converter):
        data = conversion.rpy2py(r_df_for_py)

    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"Converted object from {path} is not a pandas DataFrame; got {type(data)}"
        )

    return data, labels

