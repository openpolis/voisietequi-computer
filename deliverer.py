import pika
from computer import config
from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

connection = pika.BlockingConnection(pika.URLParameters(config.MQ_URL))
channel = connection.channel()

channel.exchange_declare(exchange=config.MQ_EXCHANGE, exchange_type='topic')

# rpc
callback_queue = channel.queue_declare(exclusive=True).method.queue
#channel.queue_bind(exchange=config.MQ_EXCHANGE, queue=callback_queue)
def callback(ch, method, properties, body):
    print " [x] Received %r:%r" % (method.routing_key, pickle.loads(body),)
channel.basic_consume(callback, no_ack=True, queue=callback_queue)
#end rpc

routing_key = config.MQ_PREFIX + 'deliver'
message = pickle.dumps(datetime.now())
channel.basic_publish(
    exchange=config.MQ_EXCHANGE,
    routing_key=routing_key,
    body=message,
    properties=pika.BasicProperties( reply_to = callback_queue ), #rpc
)
print " [x] Sent %r:%r" % (routing_key, datetime.now())

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    connection.close()