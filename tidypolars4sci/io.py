import polars as pl
from .tibble_df import from_pandas
import copy
import os
import pandas as pd
from pyreadr import read_r
import pyreadstat


__all__ = [
    "read_data",
   ]

class read_data():
    
    def __new__(self, **kws):
        '''
        fn         filename with path
        '''
         
        fn=kws.get('fn')
        fn_type=os.path.splitext(fn)[1]
        big_data=kws.get("big_data", False)
        if big_data:
            kws.pop('big_data', 0)
         
        assert fn, "fn (filepath) must be provided."

        if kws.get("silently", None) is not None:
            silently = kws.get("silently", False)
            kws.pop("silently")
        else:
            silently = False
        if not silently:
            print(f"Loading data '{os.path.basename(fn)}'...",
                  end=" ",  flush=True)
         
        if fn_type=='.csv' or fn_type=='.CSV':
            df =self.read_csv(big_data=big_data, **kws)
         
        elif fn_type=='.dta' or fn_type=='.DTA':
            df =self.read_dta(big_data=big_data, **kws)
         
        elif fn_type=='.sav':
            df = self.read_sav(**kws)
         
        elif (fn_type=='.xls' or fn_type=='.xlsx' or
              fn_type=='.xltx' or fn_type=='.XLTX' or
              fn_type=='.ods' or fn_type=='.ODS' or
              fn_type=='.XLS' or fn_type=='.XLSX'):
            df =self.read_xls(big_data=big_data, **kws)

        elif fn_type=='.tsv':
            df =self.read_tsv(big_data=big_data, **kws)

        elif fn_type=='.txt':
            df =self.read_txt(big_data=big_data, **kws)

        elif fn_type=='.tex':
            df =self.read_tex(big_data=big_data, **kws)

        elif fn_type=='.dat':
            df =self.read_dat(big_data=big_data, **kws)

        elif fn_type=='.rds':
            df =self.read_rds(big_data=big_data, **kws)

        elif fn_type=='.Rdata' or fn_type=='.rdata' or fn_type=='.rda':
            df =self.read_Rdata(big_data=big_data, **kws)

        elif kws.get('gs_api', None):
            df =self.read_gspread(**kws)
         
        else:
            print(f"No reader for file type {fn_type}. If you are trying to read "+
                  "a Google spreadsheet, provide the gs_api parameter with path to "+
                  "the local API json file for the Google spreadsheet, and the "+
                  "parameter sn with the sheet name in the spreadsheet")
            df = None

        if not silently:
            if big_data:
                print("done! <--- using dask dataframe for big data")
            else:
                print("done!")
        return df
    
    def read_csv (big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        if not kws.get('sep', None):
            kws['sep']=";"
        if not big_data:
            df = pd.read_csv(filepath_or_buffer=fn, **kws)
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df
    
    def read_dta (big_data, **kws):
        # 
        fn=kws.get('fn')
        if not big_data:
            df = pd.read_stata(fn, convert_categoricals=False)
        else:
            df = read_data.read_dask(fn, **kws)
        df = from_pandas(df) if not big_data else df
        # 
        # labels
        labels    = pd.read_stata(fn, iterator=True)
        variables = labels.variable_labels()
        values    = labels.value_labels()
        return df, labels

    def read_xls (big_data, **kws):
        fn=kws.get('fn'); kws.pop('fn')
        if not big_data:
            df = from_pandas(pd.read_excel(io=fn, **kws))
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_xltx(big_data, **kws):
        fn=kws.get('fn'); kws.pop('fn')
        if not big_data:
            df = from_pandas(pd.read_excel(io=fn, **kws))
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_ods (big_data, **kws):
        fn=kws.get('fn'); kws.pop('fn')
        if not big_data:
            df = from_pandas(pd.read_excel(io=fn, **kws))
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_tsv (big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        # 
        kws['sep'] = '\t'
        # 
        if not big_data:
            df = pd.read_csv(filepath_or_buffer=fn, **kws)
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_txt (big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        #
        big_data=kws.get("big_data", False)
        kws.pop('big_data', 0)
        # 
        if not big_data:
            df = pd.read_table(filepath_or_buffer=fn, **kws)
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_tex (big_data, **kws):
        fn = os.path.expanduser(kws['fn'])
        with open(fn) as f:
            content=f.readlines()
        return content

    def read_dat (big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        kws['sep']="\\s+"
        if not big_data:
            df = pd.read_csv(fn, **kws)
        else:
            df = read_data.read_dask(fn, **kws)
        return from_pandas(df) if not big_data else df

    def read_sav(**kws):
        fn=kws.get('fn')
        kws.pop('fn')

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

        df, meta = pyreadstat.read_sav(fn,
                                       usecols=cols,
                                       row_offset=row_first,
                                       row_limit=row_last,
                                       **kws)

        # collect labels
        labels_vars = meta.column_names_to_labels
        labels_values = meta.variable_value_labels
        labels = {'variables':{},
                  'values':{}}
        for var, label in labels_vars.items():
            if var not in labels_values.keys() :
                labels_values[var] = {}
            labels['variables'] |= {var:label}
            labels['values']   |= {var:labels_values[var]}
        
        return from_pandas(df), labels

    def read_rds(big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        #
        df = read_r(fn, **kws)[None]
        return from_pandas(df)

    def read_Rdata(big_data, **kws):
        fn=kws.get('fn')
        kws.pop('fn')
        #
        df = read_r(fn)
        return from_pandas(df[list(df.keys())[0]])

    def read_dask(fn, **kws):
        # return eDask(fn, **kws)
        return ddf.read_csv(fn, **kws)

    def read_gspread(**kws):
        '''
        Load google spreadsheet
        Note: Remember to share the spreadsheet with e-mail client in json file, 
        which is found under the item "client_email" of the json information. Ex:

             "client_email": "..."

        Input 
        -----
        fn     : filename of the google spreadsheet
        gs_api : json file with API info
        sn     : spreadsheet name

        Output 
        ------
        from_pandas
        '''
        assert kws.get("gs_api", None),"A json file with google spreadsheet API"+\
            "must be provided."
        assert kws.get("sheet_name", None), "The sheet_name must be provided."
        # 
        fn=kws.get("fn", None)
        json_file=kws.get("gs_api", None)
        sheet_name=kws.get("sheet_name", None)
        # credentials (see https://gspread.readthedocs.io/en/latest/oauth2.html)
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        credentials = (
            ServiceAccountCredentials
            .from_json_keyfile_name(json_file, scope)
        )
        # 
        print('getting credentials...')
        gc = gspread.authorize(credentials)
        # 
        print("loading worksheet...")
        wks = gc.open(fn).worksheet(sheet_name)
        # 

        print(f"File: '{wks.spreadsheet.title}'\nSheet name: '{sheet_name}'!")
        wks = from_pandas(wks.spreadsheet.sheet1.get_all_records())
        # 
        return wks
