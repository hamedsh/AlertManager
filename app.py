from flask import Flask, request, jsonify
import yaml
import json

from alert_manager import AlertManager

app = Flask(__name__)


@app.route('/add_status', methods=['POST'])
def add_status():
    global alert_manager
    data = json.loads(request.data)
    alert_manager.add_status(data['status'], data['metadata'])
    return jsonify({'res': 'ok'})


if __name__ == '__main__':
    with open('config.yml') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    alert_manager = AlertManager(config)
    app.run()
