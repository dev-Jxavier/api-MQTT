import os
from flask import Blueprint, jsonify, request
from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações InfluxDB a partir das variáveis de ambiente
INFLUXDB_URL = os.getenv('INFLUXDB_URL')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')

# Inicializar o cliente InfluxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = influx_client.query_api()

bp = Blueprint('routes', __name__)

@bp.route('/dados', methods=['GET'])
def listar_dados():
    query = f'from(bucket: "{INFLUXDB_BUCKET}") |> range(start: -1d)'
    tables = query_api.query(query, org=INFLUXDB_ORG)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time(),
                "measurement": record.get_measurement(),
                "sensor_id": record.values.get("sensor_id"),
                "tensao": record.values.get("tensao"),
                "temperatura": record.values.get("temperatura"),
                "corrente": record.values.get("corrente")
            })
    return jsonify(results)

@bp.route('/dados/<sensor_id>', methods=['GET'])
def consultar_dados(sensor_id):
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -1d)
      |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
    '''
    tables = query_api.query(query, org=INFLUXDB_ORG)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time(),
                "measurement": record.get_measurement(),
                "sensor_id": record.values.get("sensor_id"),
                "tensao": record.values.get("tensao"),
                "temperatura": record.values.get("temperatura"),
                "corrente": record.values.get("corrente")
            })
    return jsonify(results)
