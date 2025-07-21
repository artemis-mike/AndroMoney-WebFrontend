import io
from flask import Blueprint, request, render_template
import plotly
import plotly.express as px
import pandas as pd
import json
from services import data_loader

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/graph')
def daily_expense_graph():
  filename = request.args.get('file', 'example.csv')
  group_by = request.args.get('group_by', 'day')
  df = data_loader.load_data(filename)
  if df.empty or 'Datum' not in df.columns:
    error = 'No data available or missing required column "Datum".'
    return render_template('graph_view.html', labels='[]', data='[]', group_by=group_by, file=filename, error=error)
  df = data_loader.enrich_date(df)
  df = data_loader.data_reorder(df)
  df.columns = df.columns.str.strip()

  df['Betrag'] = pd.to_numeric(df['Betrag'], errors='coerce')
  df = df.dropna(subset=['Betrag'])

  # Grouping logic
  if group_by == 'day':
    df['Datum_group'] = df['Datum'].dt.date
    grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
    grouped = grouped.rename(columns={'Datum_group': 'Datum'})
    labels = grouped['Datum'].astype(str).tolist()
  elif group_by == 'week':
    df['Datum_group'] = df['Datum'].dt.to_period('W')
    grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
    grouped = grouped.rename(columns={'Datum_group': 'Datum'})
    labels = grouped['Datum'].astype(str).tolist()
  elif group_by == 'month':
    df['Datum_group'] = df['Datum'].dt.to_period('M')
    grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
    grouped = grouped.rename(columns={'Datum_group': 'Datum'})
    labels = grouped['Datum'].astype(str).tolist()
  else:
    df['Datum_group'] = df['Datum'].dt.date
    grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
    grouped = grouped.rename(columns={'Datum_group': 'Datum'})
    labels = grouped['Datum'].astype(str).tolist()

  data = grouped['Betrag'].tolist()
  print(df)

  return render_template('graph_view.html', labels=json.dumps(labels), data=json.dumps(data), group_by=group_by, file=filename, error=None)
