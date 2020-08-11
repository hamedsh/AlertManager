from pymongo import MongoClient


class AlertManager:
    def __init__(self, config: dict):
        self.connection = MongoClient(host=config['mongo']['host'], port=config['mongo']['port'])
        self.db = self.connection[config['mongo']['database']]
        alert_service = self.db.alert_service.find({})
        print(list(alert_service))

    def add_status(self, status: int, metadata: object):
        if status != 1:
            self.db.status.insert_one({'status': status, 'metadata': metadata})


