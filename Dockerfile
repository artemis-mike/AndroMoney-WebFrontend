FROM python:3.13-rc-alpine3.18
RUN ["python3", "-m", "pip", "install", "pandas", "Flask", "routes", "plotly", "plotly.express"]