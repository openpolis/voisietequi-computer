import pika
from computer import config
try:
    import cPickle as pickle
except ImportError:
    import pickle

print ' [*] Connect to %s' % config.MQ_URL
connection = pika.BlockingConnection( pika.URLParameters( config.MQ_URL ) )
channel = connection.channel()
channel.exchange_declare(config.MQ_EXCHANGE, exchange_type='topic')
queue_name = config.MQ_PREFIX  +'configure'
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=config.MQ_EXCHANGE, queue=queue_name)
channel.basic_publish(exchange=config.MQ_EXCHANGE,
    routing_key=queue_name,
    body=pickle.dumps({
        'election_code': config.ELECTION_CODE,
        'configuration': {"1": {"1": 3, "2": 3, "3": -1, "4": -1, "5": 2, "6": 1, "7": 3, "8": 2, "9": -2, "10": 2, "11": 2, "12": 1, "13": 1, "14": -1, "15": 2, "16": 2, "17": 2, "18": 1, "19": 1, "20": -1, "21": -2, "22": 1, "23": 2, "24": 1, "25": 2}, "2": {"1": 2, "2": 1, "3": 1, "4": 3, "5": -1, "6": -1, "7": -3, "8": 2, "9": 3, "10": 3, "11": 2, "12": -1, "13": -3, "14": -3, "15": 3, "16": 3, "17": 1, "18": -2, "19": -3, "20": 3, "21": 1, "22": 2, "23": 2, "24": -3, "25": 2}, "3": {"1": 2, "2": 2, "3": 1, "4": 3, "5": -1, "6": -1, "7": -1, "8": -2, "9": 3, "10": 3, "11": -2, "12": 1, "13": -2, "14": -2, "15": 2, "16": 2, "17": 2, "18": -2, "19": 1, "20": 2, "21": 2, "22": 2, "23": 3, "24": 2, "25": 1}, "4": {"1": 3, "2": 3, "3": -3, "4": -1, "5": 3, "6": 3, "7": 2, "8": 3, "9": -1, "10": 3, "11": 3, "12": 3, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": -1, "25": 3}, "5": {"1": 1, "2": 1, "3": 1, "4": 2, "5": -1, "6": -1, "7": 3, "8": 1, "9": 1, "10": 1, "11": -2, "12": -2, "13": -3, "14": -3, "15": 1, "16": 3, "17": 3, "18": -3, "19": 3, "20": 3, "21": 2, "22": 3, "23": 3, "24": 3, "25": -2}, "6": {"1": 1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -2, "8": 2, "9": 1, "10": 1, "11": 1, "12": 1, "13": -2, "14": -1, "15": 1, "16": 1, "17": -1, "18": -3, "19": -3, "20": 3, "21": 3, "22": -1, "23": 3, "24": 3, "25": 1}, "7": {"1": 2, "2": 3, "3": 1, "4": 2, "5": 2, "6": 3, "7": 1, "8": 2, "9": 3, "10": 2, "11": 3, "12": 3, "13": 3, "14": 1, "15": 3, "16": -3, "17": -2, "18": 3, "19": 1, "20": -1, "21": 1, "22": 1, "23": 2, "24": 2, "25": 1}, "8": {"1": 2, "2": 3, "3": -1, "4": 3, "5": 3, "6": 3, "7": 2, "8": 3, "9": -2, "10": 3, "11": 3, "12": 2, "13": 2, "14": 3, "15": 3, "16": -2, "17": -2, "18": 1, "19": -3, "20": -2, "21": 1, "22": -2, "23": 3, "24": 2, "25": 3}, "9": {"1": 3, "2": 3, "3": -3, "4": -2, "5": 1, "6": 3, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 2, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "11": {"1": 2, "2": 3, "3": -3, "4": -3, "5": 3, "6": 1, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 3, "15": 2, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "14": {"1": 2, "2": 3, "3": -3, "4": 3, "5": 3, "6": 3, "7": 3, "8": 3, "9": 3, "10": 3, "11": 3, "12": 2, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": 3, "22": -3, "23": -3, "24": 3, "25": 3}, "16": {"1": -1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -3, "8": 1, "9": 1, "10": 1, "11": 1, "12": -1, "13": -3, "14": -1, "15": 1, "16": 1, "17": 1, "18": -3, "19": -3, "20": 3, "21": 3, "22": 2, "23": 2, "24": 3, "25": 1}}
    }))
print " [x] Start configuration: %r" % (config.ELECTION_CODE,)
connection.close()

#class Msn(object):
#
#    def __init__(self):
#        self.connection = pika.BlockingConnection( pika.URLParameters( config.MQ_URL ) )
#        self.channel = self.connection.channel()
#        self.channel.queue_declare(queue='rpc_queue')
#
#
#def consume_rpc(self, queue, result_len=1, callback=None, timeout=None, raise_timeout=False):
#    if timeout is None:
#        timeout = self.rpc_timeout
#
#    result_list = []
#
#    def _callback(channel, method, header, body):
#        print "### Got 1/%s RPC result" %(result_len)
#        msg = self.encoder.decode(body)
#        result_dict = {}
#        result_dict.update(msg['content']['data'])
#        result_list.append(result_dict)
#
#        if callback is not None:
#            callback(msg)
#
#        if len(result_list) == result_len:
#            print "### All results are here: stopping RPC"
#            channel.stop_consuming()
#
#    def _outoftime():
#        self.channel.stop_consuming()
#        raise TimeoutError
#
#    if timeout != -1:
#        print "### Setting timeout %s seconds" %(timeout)
#        self.conn_broker.add_timeout(timeout, _outoftime)
#
#    self.channel.basic_consume(_callback, queue=queue, consumer_tag=queue)
#
#    if raise_timeout is True:
#        print "### Start consuming RPC with raise_timeout"
#        self.channel.start_consuming()
#    else:
#        try:
#            print "### Start consuming RPC without raise_timeout"
#            self.channel.start_consuming()
#        except TimeoutError:
#            pass
#
#    return result_list