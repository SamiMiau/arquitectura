import json
import pika
import logging


class Emit:
    def send(self, id, action, payload):
        self.connect()
        self.publish(id, action, payload)
        self.close()

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='rabbitmq')
        )

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='inventory',
                                      exchange_type='topic')

    def publish(self, id, action, payload):
        routing_key = f"inventory.{action}.{id}"
        message = json.dumps(payload)

        self.channel.basic_publish(exchange='inventory',
                                   routing_key=routing_key,
                                   body=message)

    def close(self):
        self.connection.close()