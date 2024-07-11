import json
import os
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações MQTT a partir das variáveis de ambiente
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))  # Padrão para 1883 se não estiver definido
MQTT_TOPIC = os.getenv('MQTT_TOPIC')

# Configurações InfluxDB a partir das variáveis de ambiente
INFLUXDB_URL = os.getenv('INFLUXDB_URL')
INFLUXDB_TOKEN = os.getenv('INFLUXDB_TOKEN')
INFLUXDB_ORG = os.getenv('INFLUXDB_ORG')
INFLUXDB_BUCKET = os.getenv('INFLUXDB_BUCKET')

# Inicializar o cliente InfluxDB
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

# Callback quando a conexão MQTT é estabelecida
def on_connect(client, userdata, flags, rc):
    print(f"Conectado ao broker MQTT com código de retorno {rc}")
    client.subscribe(MQTT_TOPIC)

# Callback quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())
        measurement = data.get("measurement", "sensor_data")
        point = Point(measurement) \
            .tag("sensor_id", data.get("sensor_id")) \
            .field("tensao", data.get("tensao")) \
            .field("temperatura", data.get("temperatura")) \
            .field("corrente", data.get("corrente")) \
            .time(data.get("timestamp"), WritePrecision.NS)
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    except Exception as e:
        print(f"Erro ao processar a mensagem: {e}")

# Configurar cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
