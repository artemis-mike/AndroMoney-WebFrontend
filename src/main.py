from flask import Flask, render_template
from routes import register_routes
from services import data_loader

def create_app():
  app = Flask(__name__)
  app.config.from_pyfile('config.py')
  register_routes(app)
  return app

if __name__ == '__main__':
  filename='2025-06.csv'
  app = create_app()
  app.run(host='0.0.0.0', debug=True)

  