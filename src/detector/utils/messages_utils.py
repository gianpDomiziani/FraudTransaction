import json
import pickle

from utils.config import *
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER_URL)

def publish_prediction(pred, request_id):
    producer.send('app_messages',
                  json.dumps({'request_id': request_id, 'prediction': float(pred)}).encode('utf-8'))
    producer.flush()


def publish_traininig_completed(model_id):
    producer.send('retrain_topic',
                  json.dumps({'training_completed': True, 'model_id': model_id}).encode('utf-8'))
    producer.flush()


def read_messages_count(path, repeat_every):
    file_list=list(path.iterdir())
    nfiles = len(file_list)
    if nfiles == 0:
        return 0
    else:
        return ((nfiles-1)*repeat_every) + len(file_list[-1].open().readlines())


def append_message(message, path, batch_id):
    message_fname = f'messages_{batch_id}_.txt'
    with open(path/message, 'a') as f:
        f.write("%s\n" % (json.dumps(message)))



def send_retrain_message(model_id, batch_id):
    producer.send('retrain_topic',
                  json.dumps({'retrain': True, 'model_id': model_id, 'batch_id': batch_id}).encode('utf-8'))
    producer.flush()