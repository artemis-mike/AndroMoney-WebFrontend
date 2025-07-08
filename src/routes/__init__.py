from .main_routes import main_bp
#from .expenses_routes import expenses_bp   # example route
from .graphs_routes import graph_bp

def register_routes(app):
  app.register_blueprint(main_bp)
#  app.register_blueprint(expenses_bp) # example route
  app.register_blueprint(graph_bp)
