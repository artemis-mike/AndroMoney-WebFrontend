FROM python:3.13-rc-slim
RUN ["python3", "-m", "pip", "install", "pandas", "Flask", "routes", "plotly", "plotly.express"]

RUN mkdir /app
WORKDIR /app
COPY src/ .

EXPOSE 5000

ENTRYPOINT [ "python3", "main.py" ]