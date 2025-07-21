import pandas as pd
from config import EXPENSES_CSV
from services.logging import get_logger

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', None)

logging = get_logger(__name__)


def load_data(filename: str, path='data') -> pd.DataFrame:
  try:
    file=path+"/"+filename
    # Search for header line (starting with "Id")
    with open(file, 'r', encoding='utf-8') as f:
      for i, line in enumerate(f):
        if '"Id"' in line.strip():
          header_line_index = i
          break
        elif i >= 10: # Only read the first 10 lines
          break
      else:
        raise ValueError(f"No header line starting with '\"Id\"' found in {file}.")
    df = pd.read_csv(file, skiprows=header_line_index, quotechar='"', decimal='.')
    df.columns = df.columns.str.strip().str.replace('"', '')
    if 'Betrag' in df.columns:
      df['Betrag'] = pd.to_numeric(df['Betrag']).astype(float)
    else:
      logging.error('Column "Betrag" not found in loaded data! Columns: %s', df.columns.tolist())
      return pd.DataFrame()

  except FileNotFoundError:
    logging.error(f"File {file} not found!")
    return pd.DataFrame()
  except Exception as e:
    logging.exception(f"Failed to load data: {e}")
    return pd.DataFrame()
  
  return df

def enrich_date(df: pd.DataFrame) -> pd.DataFrame:
  if 'Datum' not in df.columns:
    return df
  df['Datum'] = pd.to_datetime(df['Datum'], format='%Y%m%d', errors='coerce')
  df = df.dropna(subset=['Datum'])
  df['JahrMonat'] = df['Datum'].dt.strftime('%Y-%m')
  df['Jahr'] = df['Datum'].dt.year
  df['Monat'] = df['Datum'].dt.month

  return df

def data_reorder(df: pd.DataFrame) -> pd.DataFrame:
  cols = df.columns.tolist()
  if "Id" in cols and "Datum" in cols:
    cols.remove("Datum")
    datum_index = cols.index("Id") + 1  # Place Datum filed on index after Id field
    cols.insert(datum_index, "Datum")
    df = df[cols]
  return df