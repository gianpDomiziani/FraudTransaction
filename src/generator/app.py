"""Produce fake transactions into a Kafka topic."""

import json
from time import sleep
import pandas as pd
import threading

from kafka import KafkaProducer, KafkaConsumer
from transactions import create_random_transaction
from config import *

logger = logging.getLogger(__name__)


TRANSACTIONS_PER_SECOND = float(os.environ.get('TRANSACTIONS_PER_SECOND'))
SLEEP_TIME = 1 / TRANSACTIONS_PER_SECOND

TOPICS = [FRAUD_TOPIC, LEGIT_TOPIC]

###########################################
# Load Test Data
###########################################
df_test = pd.read_csv('dataset/test/df_test.csv')
X_test = df_test.iloc[:, :-1]
N = X_test.shape[0]


def start_producer():
    logger.info('Start producer thread')
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL
 )

    logger.info('Transaction Payload:')
    for i in range(N):
        transaction = create_random_transaction(X_test)
        producer.send(TRANSACTIONS_TOPIC, value=json.dumps(transaction).encode('utf-8'))
        producer.flush()
        print(transaction)
        #dockesleep(SLEEP_TIME)

def start_consumer():
    logger.info('Start COnsumer Thread')
    consumer = KafkaConsumer(bootstrap_servers=KAFKA_BROKER_URL)
    consumer.subscribe(TOPICS)

    for msg in consumer:
        message = json.loads(msg.value)
        if "Prediction" in message:
            logger.info('Prediction message:')
            print(f"** CONSUMER: Received prediction {message['Prediction']}")
            print(f"Type Transaction: {message['STATUS']}")



threads = []
t1 = threading.Thread(target=start_consumer)
t2 = threading.Thread(target=start_producer)
threads.append(t1)
threads.append(t2)
for thread in threads:
    thread.start()






