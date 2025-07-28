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
  start_date_str = request.args.get('start_date', '')
  end_date_str = request.args.get('end_date', '')
  selected_categories = request.args.getlist('categories')
  selected_subcategories = request.args.getlist('subcategories')
  show_total = request.args.get('show_total') == '1'
  df = data_loader.load_data(filename)
  if df.empty or 'Datum' not in df.columns:
    error = 'No data available or missing required column "Datum".'
    return render_template('graph_view.html', labels='[]', data='[]', group_by=group_by, filename=filename, start_date=start_date_str, end_date=end_date_str, selected_categories=[], selected_subcategories=[], all_categories=[], all_subcategories=[], show_total=False, error=error)
  df = data_loader.enrich_date(df)
  df = data_loader.data_reorder(df)
  df.columns = df.columns.str.strip()

  df['Betrag'] = pd.to_numeric(df['Betrag'], errors='coerce')
  df = df.dropna(subset=['Betrag'])

  # Date filtering
  if start_date_str:
    from datetime import datetime
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    df = df[df['Datum'].dt.date >= start_date]

  if end_date_str:
    from datetime import datetime
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    df = df[df['Datum'].dt.date <= end_date]

  # Get unique categories and subcategories
  all_categories = sorted(df['Kategorie'].unique().tolist())
 
  # Filter subcategories based on selected categories
  if selected_categories:
    # Only show subcategories that belong to selected categories
    filtered_df = df[df['Kategorie'].isin(selected_categories)]
    all_subcategories = sorted(filtered_df['Unterkategorie'].unique().tolist())
  else:
    # If no categories selected, show all subcategories
    all_subcategories = sorted(df['Unterkategorie'].unique().tolist())

  # Create mapping of subcategories to their parent categories
  subcategory_to_categories = {}
  for subcat in df['Unterkategorie'].unique():
    parent_categories = df[df['Unterkategorie'] == subcat]['Kategorie'].unique().tolist()
    subcategory_to_categories[subcat] = parent_categories

  # If no categories selected, default to showing all data as one line
  if not selected_categories and not selected_subcategories:
    # Grouping logic for total sum
    if group_by == 'day':
      df['Datum_group'] = df['Datum'].dt.date
      grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
      grouped = grouped.rename(columns={'Datum_group': 'Datum'})
      labels = grouped['Datum'].astype(str).tolist()
      datasets = [{
        'label': 'Total',
        'data': grouped['Betrag'].tolist(),
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)'
      }]
    elif group_by == 'week':
      df['Datum_group'] = df['Datum'].dt.to_period('W')
      grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
      grouped = grouped.rename(columns={'Datum_group': 'Datum'})
      labels = grouped['Datum'].astype(str).tolist()
      datasets = [{
        'label': 'Total',
        'data': grouped['Betrag'].tolist(),
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)'
      }]
    elif group_by == 'month':
      df['Datum_group'] = df['Datum'].dt.to_period('M')
      grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
      grouped = grouped.rename(columns={'Datum_group': 'Datum'})
      labels = grouped['Datum'].astype(str).tolist()
      datasets = [{
        'label': 'Total',
        'data': grouped['Betrag'].tolist(),
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)'
      }]
    else:
      df['Datum_group'] = df['Datum'].dt.date
      grouped = df.groupby('Datum_group', as_index=False)['Betrag'].sum()
      grouped = grouped.rename(columns={'Datum_group': 'Datum'})
      labels = grouped['Datum'].astype(str).tolist()
      datasets = [{
        'label': 'Total',
        'data': grouped['Betrag'].tolist(),
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)'
      }]
  else:
    # Multiple datasets for selected categories/subcategories
    datasets = []
   
    # Add total line if requested
    if show_total:
      if group_by == 'day':
        df_total = df.copy()
        df_total['Datum_group'] = df_total['Datum'].dt.date
        grouped_total = df_total.groupby('Datum_group', as_index=False)['Betrag'].sum()
      elif group_by == 'week':
        df_total = df.copy()
        df_total['Datum_group'] = df_total['Datum'].dt.to_period('W')
        grouped_total = df_total.groupby('Datum_group', as_index=False)['Betrag'].sum()
      elif group_by == 'month':
        df_total = df.copy()
        df_total['Datum_group'] = df_total['Datum'].dt.to_period('M')
        grouped_total = df_total.groupby('Datum_group', as_index=False)['Betrag'].sum()
      else:
        df_total = df.copy()
        df_total['Datum_group'] = df_total['Datum'].dt.date
        grouped_total = df_total.groupby('Datum_group', as_index=False)['Betrag'].sum()
      
      # Get all unique dates for consistent x-axis
      if group_by == 'day':
        all_dates = sorted(df['Datum'].dt.date.unique())
        labels = [str(date) for date in all_dates]
      elif group_by == 'week':
        all_dates = sorted(df['Datum'].dt.to_period('W').unique())
        labels = [str(date) for date in all_dates]
      elif group_by == 'month':
        all_dates = sorted(df['Datum'].dt.to_period('M').unique())
        labels = [str(date) for date in all_dates]
      else:
        all_dates = sorted(df['Datum'].dt.date.unique())
        labels = [str(date) for date in all_dates]
      
      # Create total data array with zeros for missing dates
      total_data = []
      for date in all_dates:
        date_data = grouped_total[grouped_total['Datum_group'] == date]
        if len(date_data) > 0:
          total_data.append(float(date_data['Betrag'].iloc[0]))
        else:
          total_data.append(0)
      
      datasets.append({
        'label': 'Total',
        'data': total_data,
        'borderColor': 'rgba(54, 162, 235, 1)',
        'backgroundColor': 'rgba(54, 162, 235, 0.2)',
        'fill': False,
        'borderWidth': 3
      })
    else:
      # Get all unique dates for consistent x-axis (only if not showing total)
      if group_by == 'day':
        all_dates = sorted(df['Datum'].dt.date.unique())
        labels = [str(date) for date in all_dates]
      elif group_by == 'week':
        all_dates = sorted(df['Datum'].dt.to_period('W').unique())
        labels = [str(date) for date in all_dates]
      elif group_by == 'month':
        all_dates = sorted(df['Datum'].dt.to_period('M').unique())
        labels = [str(date) for date in all_dates]
      else:
        all_dates = sorted(df['Datum'].dt.date.unique())
        labels = [str(date) for date in all_dates]
   
    colors = [
      'rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)',
      'rgba(255, 205, 86, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)',
      'rgba(199, 199, 199, 1)', 'rgba(83, 102, 255, 1)', 'rgba(78, 252, 3, 1)',
      'rgba(252, 3, 244, 1)'
    ]
    
    # Process selected categories
    for i, category in enumerate(selected_categories):
      if category in df['Kategorie'].values:
        cat_df = df[df['Kategorie'] == category]
        if group_by == 'day':
          cat_df['Datum_group'] = cat_df['Datum'].dt.date
          grouped = cat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        elif group_by == 'week':
          cat_df['Datum_group'] = cat_df['Datum'].dt.to_period('W')
          grouped = cat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        elif group_by == 'month':
          cat_df['Datum_group'] = cat_df['Datum'].dt.to_period('M')
          grouped = cat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        else:
          cat_df['Datum_group'] = cat_df['Datum'].dt.date
          grouped = cat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        
        # Create data array with zeros for missing dates
        data = []
        for date in all_dates:
          date_data = grouped[grouped['Datum_group'] == date]
          if len(date_data) > 0:
            data.append(float(date_data['Betrag'].iloc[0]))
          else:
            data.append(0)
        
        datasets.append({
          'label': category,
          'data': data,
          'borderColor': colors[i % len(colors)],
          'backgroundColor': colors[i % len(colors)].replace('1)', '0.2)'),
          'fill': False
        })
    
    # Process selected subcategories
    for i, subcategory in enumerate(selected_subcategories):
      if subcategory in df['Unterkategorie'].values:
        subcat_df = df[df['Unterkategorie'] == subcategory]
        if group_by == 'day':
          subcat_df['Datum_group'] = subcat_df['Datum'].dt.date
          grouped = subcat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        elif group_by == 'week':
          subcat_df['Datum_group'] = subcat_df['Datum'].dt.to_period('W')
          grouped = subcat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        elif group_by == 'month':
          subcat_df['Datum_group'] = subcat_df['Datum'].dt.to_period('M')
          grouped = subcat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        else:
          subcat_df['Datum_group'] = subcat_df['Datum'].dt.date
          grouped = subcat_df.groupby('Datum_group', as_index=False)['Betrag'].sum()
        
        # Create data array with zeros for missing dates
        data = []
        for date in all_dates:
          date_data = grouped[grouped['Datum_group'] == date]
          if len(date_data) > 0:
            data.append(float(date_data['Betrag'].iloc[0]))
          else:
            data.append(0)
        
        datasets.append({
          'label': f"Sub: {subcategory}",
          'data': data,
          'borderColor': colors[(len(selected_categories) + i) % len(colors)],
          'backgroundColor': colors[(len(selected_categories) + i) % len(colors)].replace('1)', '0.2)'),
          'fill': False
        })

  # print(df)

  return render_template(
    'graph_view.html', 
    labels=labels,
    datasets=datasets,
    group_by=group_by, 
    filename=filename, 
    active='graph', 
    start_date=start_date_str,
    end_date=end_date_str,
    selected_categories=selected_categories,
    selected_subcategories=selected_subcategories,
    all_categories=all_categories,
    all_subcategories=all_subcategories,
    show_total=show_total,
    error=None,
    subcategory_to_categories=json.dumps(subcategory_to_categories)
  )
