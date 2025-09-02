FROM python:3.14-rc-slim
RUN ["python3", "-m", "pip", "install", "pandas", "Flask", "routes", "plotly", "requests", "werkzeug"]

RUN mkdir /app
WORKDIR /app
COPY src/ .
RUN mkdir ./data

EXPOSE 5000

ENV FLASK_APP=main.py
ENV FLASK_ENV=production

ENTRYPOINT [ "python3", "main.py" ]