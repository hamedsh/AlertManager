from pymongo import MongoClient
from collections import deque
import redis


class AlertManager:
    def __init__(self, config: dict):
        self.connection = MongoClient(host=config['mongo']['host'], port=config['mongo']['port'])
        self.db = self.connection[config['mongo']['database']]
        self.service_collection = self.db.services
        self.status_collection = self.db.service_logs
        _services = list(self.service_collection.find({}, {'_id': 0}))
        self.services = {}
        for service in _services:
            service['queue'] = deque(int(service['window'])*[0], int(service['window']))
            self.services[service['name']] = service
        self.redisDB = redis.Redis(host=config['redis']['host'], port=config['redis']['port'], db=config['redis']['db'])

    def add_status(self, status: int, service: str, metadata: object):
        self.status_collection.insert_one({'status': status, 'service': service, 'metadata': metadata})
        if not status == 0:
            self.handle_exception(self.services[service], metadata)
        else:
            self.handle_recovery(self.services[service], metadata)

    def handle_exception(self, service, metadata):
        service['queue'].append(-1)
        if service['queue'].count(-1) >= service['alert_for']:
            if self.redisDB.get(service['name']) is None:
                print('send message')
                self.redisDB.set(service['name'], 1)
                self.redisDB.expire(service['name'], int(service['delay_messages']))
                service['alerted'] = True

    def handle_recovery(self, service, metadata):
        service['queue'].append(0)
        if service['queue'].count(0) >= service['ok_for'] and service['alerted']:
            print('send ok message')
            service['alerted'] = False
