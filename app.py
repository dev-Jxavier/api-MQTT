from flask import Flask
from mqtt_influxdb import mqtt_client
import routes

app = Flask(__name__)

# Registrar rotas
app.register_blueprint(routes.bp)

# Iniciar o loop em um thread separado
mqtt_client.loop_start()

# Endpoint para testar a API
@app.route('/teste', methods=['GET'])
def teste():
    return "API funcionando"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
