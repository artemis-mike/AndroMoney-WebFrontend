from flask import Blueprint, render_template, request
from datetime import datetime
from services import data_loader

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def show_data_table():
  DEFAULT_COLUMNS = ['Datum', 'Betrag', 'Kategorie', 'Unterkategorie', 'Ausgaben']
  filename = request.args.get('file', 'example.csv')
  page = int(request.args.get('page', 1))
  per_page = int(request.args.get('per_page', 50))
  selected_columns = request.args.getlist('columns') or DEFAULT_COLUMNS
  start_date_str = request.args.get('start_date', '')
  end_date_str = request.args.get('end_date', '')

  df = data_loader.load_data(filename)
  df = data_loader.enrich_date(df)
  df = data_loader.data_reorder(df)

  if start_date_str:
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    df = df[df['Datum'].dt.date >= start_date]  # filter dataFrame for values where dt.date is greater or equal start_date

  if end_date_str:
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    df = df[df['Datum'].dt.date <= end_date]    # filter dataFrame for values where dt.date is less or equal end_date

  total_rows = len(df)
  total_pages = (total_rows + per_page - 1) // per_page   # ceiling division

  # Slice dataframe
  start = (page - 1) * per_page
  end = start + per_page
  df_page = df.iloc[start:end]
  df_page = df_page[[col for col in selected_columns if col in df_page.columns]]

  table_html = df_page.to_html(classes='table table-striped', index=False, justify='left')
  return render_template(
    'data_table.html', 
    table_html=table_html, 
    page=page, 
    per_page=per_page, 
    total_pages=total_pages, 
    filename=filename,
    all_columns=list(df.columns),
    selected_columns=selected_columns,
    start_date=start_date_str,
    end_date=end_date_str,
    active='table'
  )
