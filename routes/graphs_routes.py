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
  df = data_loader.load_data(filename)
  df = data_loader.enrich_date(df)
  df = data_loader.data_reorder(df)
  df.columns = df.columns.str.strip()

  df['Betrag'] = pd.to_numeric(df['Betrag'], errors='coerce')
  df = df.dropna(subset=['Betrag'])
  daily_sum = df.groupby('Datum', as_index=False)['Betrag'].sum()
  daily_sum['Datum'] = pd.to_datetime(daily_sum['Datum'])
  daily_sum = daily_sum.sort_values('Datum')

  # Create Plotly figure
  fig = px.line(daily_sum, x='Datum', y='Betrag', title='Täglich summierte Ausgabe')

  # Convert to JSON for embedding in template
  graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

  return render_template('graph_view.html', graphJSON=graphJSON)
