import web
import json
import config, status, mds, helpers

urls = (
    '/computation/?', 'compute',
)


web.config.debug = config.DEBUG
app = web.application(urls, globals())
current_status = status.ComputerStatus(config.ELECTION_CODE)
#current_status.save({"1": {"1": 3, "2": 3, "3": -1, "4": -1, "5": 2, "6": 1, "7": 3, "8": 2, "9": -2, "10": 2, "11": 2, "12": 1, "13": 1, "14": -1, "15": 2, "16": 2, "17": 2, "18": 1, "19": 1, "20": -1, "21": -2, "22": 1, "23": 2, "24": 1, "25": 2}, "2": {"1": 2, "2": 1, "3": 1, "4": 3, "5": -1, "6": -1, "7": -3, "8": 2, "9": 3, "10": 3, "11": 2, "12": -1, "13": -3, "14": -3, "15": 3, "16": 3, "17": 1, "18": -2, "19": -3, "20": 3, "21": 1, "22": 2, "23": 2, "24": -3, "25": 2}, "3": {"1": 2, "2": 2, "3": 1, "4": 3, "5": -1, "6": -1, "7": -1, "8": -2, "9": 3, "10": 3, "11": -2, "12": 1, "13": -2, "14": -2, "15": 2, "16": 2, "17": 2, "18": -2, "19": 1, "20": 2, "21": 2, "22": 2, "23": 3, "24": 2, "25": 1}, "4": {"1": 3, "2": 3, "3": -3, "4": -1, "5": 3, "6": 3, "7": 2, "8": 3, "9": -1, "10": 3, "11": 3, "12": 3, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": -1, "25": 3}, "5": {"1": 1, "2": 1, "3": 1, "4": 2, "5": -1, "6": -1, "7": 3, "8": 1, "9": 1, "10": 1, "11": -2, "12": -2, "13": -3, "14": -3, "15": 1, "16": 3, "17": 3, "18": -3, "19": 3, "20": 3, "21": 2, "22": 3, "23": 3, "24": 3, "25": -2}, "6": {"1": 1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -2, "8": 2, "9": 1, "10": 1, "11": 1, "12": 1, "13": -2, "14": -1, "15": 1, "16": 1, "17": -1, "18": -3, "19": -3, "20": 3, "21": 3, "22": -1, "23": 3, "24": 3, "25": 1}, "7": {"1": 2, "2": 3, "3": 1, "4": 2, "5": 2, "6": 3, "7": 1, "8": 2, "9": 3, "10": 2, "11": 3, "12": 3, "13": 3, "14": 1, "15": 3, "16": -3, "17": -2, "18": 3, "19": 1, "20": -1, "21": 1, "22": 1, "23": 2, "24": 2, "25": 1}, "8": {"1": 2, "2": 3, "3": -1, "4": 3, "5": 3, "6": 3, "7": 2, "8": 3, "9": -2, "10": 3, "11": 3, "12": 2, "13": 2, "14": 3, "15": 3, "16": -2, "17": -2, "18": 1, "19": -3, "20": -2, "21": 1, "22": -2, "23": 3, "24": 2, "25": 3}, "9": {"1": 3, "2": 3, "3": -3, "4": -2, "5": 1, "6": 3, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 2, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "11": {"1": 2, "2": 3, "3": -3, "4": -3, "5": 3, "6": 1, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 3, "15": 2, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "14": {"1": 2, "2": 3, "3": -3, "4": 3, "5": 3, "6": 3, "7": 3, "8": 3, "9": 3, "10": 3, "11": 3, "12": 2, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": 3, "22": -3, "23": -3, "24": 3, "25": 3}, "16": {"1": -1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -3, "8": 1, "9": 1, "10": 1, "11": 1, "12": -1, "13": -3, "14": -1, "15": 1, "16": 1, "17": 1, "18": -3, "19": -3, "20": 3, "21": 3, "22": 2, "23": 2, "24": 3, "25": 1}})


import pika
import multiprocessing
from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

connection = pika.BlockingConnection(pika.URLParameters('amqp://op:opvsq@178.32.141.44:5672/%2f'))
channel = connection.channel()

channel.exchange_declare(exchange=config.MQ_EXCHANGE, exchange_type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=config.MQ_EXCHANGE,
    queue=queue_name,
    routing_key=config.MQ_PREFIX+'deliver')

print ' [*] Waiting for logs. To exit press CTRL+C'

def callback_deliver(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)
    ch.basic_publish(exchange='',
        routing_key=properties.reply_to,
        body=pickle.dumps({
            'last_update': current_status.last_update,
            'timestamp': datetime.now()
        })
    )
#    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(
    consumer_callback=callback_deliver,
    queue=queue_name,
    no_ack=True
)

def f():
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

multiprocessing.Process(target=f).start()


# configuration
def callback_configure(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, body,)
    ch.basic_ack(delivery_tag = method.delivery_tag)
channel.queue_declare(config.MQ_PREFIX+'configure')
channel.queue_bind(
    queue= queue_name,
    exchange= config.MQ_EXCHANGE,
    routing_key= queue_name
)
channel.basic_consume(
    consumer_callback=callback_configure,
    queue=config.MQ_PREFIX+'configure',
)

#import pika
#import multiprocessing
#from datetime import datetime
#try:
#    import cPickle as pickle
#except ImportError:
#    import pickle
#
#class Deliverer(multiprocessing.Process):
#
#    QUEUE = config.MQ_PREFIX + 'deliver'
#    ROUTING_KEY = QUEUE
#    URL = config.MQ_URL
#    EXCHANGE = config.MQ_EXCHANGE
#    EXCHANGE_TYPE = 'topic'
#
#    def run(self):
#        conn = pika.SelectConnection(
#            pika.URLParameters(self.URL),
#            on_open_callback=self.on_open
#        )
#        try:
#            conn.ioloop.start()
#        except KeyboardInterrupt:
#            conn.ioloop.stop()
#
#    def on_open(self, conn):
#        print 'Connection opened'
#        self.connection = conn
#        conn.channel(self.on_channel_open)
#
#    def on_channel_open(self, channel):
#        print 'Channel opened'
#        self.channel = channel
#        self.setup_exchange(self.EXCHANGE)
#
#    def setup_exchange(self, exchange_name):
#        print 'Declaring exchange %s' % exchange_name
#        self.channel.exchange_declare(
#            self.on_exchange_declareok,
#            exchange=exchange_name,
#            exchange_type=self.EXCHANGE_TYPE
#        )
#    def on_exchange_declareok(self, frame):
#        print 'Exchange declared'
#        self.setup_queue(self.QUEUE)
#
#    def setup_queue(self, queue_name):
#        print 'Declaring queue %s' % queue_name
#        self.channel.queue_declare(
#            self.on_queue_declareok,
#            queue=queue_name
#        )
#
#    def on_queue_declareok(self, method_frame):
#        print 'Binding %s to %s with %s' % ( self.EXCHANGE, self.QUEUE, self.ROUTING_KEY )
#        self.channel.queue_bind(
#            self.on_bindok,
#            queue=self.QUEUE,
#            exchange=self.EXCHANGE,
#            routing_key=self.ROUTING_KEY
#        )
#
#    def on_bindok(self, frame):
#        print 'Queue bound'
#        self.start_consuming()
#
#    def start_consuming(self):
#        print 'Issuing consumer related RPC commands'
#        self.consumer_tag = self.channel.basic_consume(self.on_message, self.QUEUE, no_ack=True)
#
#    def on_message(self, channel, basic_deliver, properties, body):
#        print 'Received message # %s from %s: %s' % (basic_deliver.delivery_tag, properties.app_id, pickle.loads(body))
#        self.channel.basic_publish(
#            exchange=self.EXCHANGE,
#            routing_key=properties.reply_to,
#            body=pickle.dumps({
#                'last_update': current_status.last_update,
#                'timestamp': datetime.now()
#            })
#        )
#
#d = Deliverer()
#d.start()



class compute(object):

    def POST(self):
        """
        Input data is a json string, passed as POST request payload.
        """

        if not current_status.is_configured:
            raise web.InternalError("Computer is not configured")

        # read json input
        try:
            # emulate web.input with storify of json decoded POST data
            input = web.storify(
                json.loads( web.data() ),
                # required fields
                'election_code',
                'user_answers',
                'user_data',
            )
        except KeyError: # can be raised from storify if miss some required fields
            raise web.BadRequest

        if 'name' not in input.user_data:
            raise web.BadRequest("User name field not found")

        if 'email' not in input.user_data:
            raise web.BadRequest("User email field not found")
        elif not helpers.regexp(r"[^@]+@[^@]+\.[^@]+",input.user_data['email']):
            raise web.BadRequest("User email is invalid")

        if not isinstance(input.user_answers, dict) \
            or len(input.user_answers) != len(current_status.questions) \
            or set(input.user_answers) != current_status.questions:

            raise web.BadRequest("User have to answer to all questions")

        user_answers = current_status.prepare_answers(input.user_answers)

        # execute mds calculation
        # TODO: execute can raise an Exception
        results = mds.execute(
            current_status.parties + ['user'],
            current_status.answers + [user_answers]
        )

        input.user_data['ip_address'] = web.ctx.ip
        input.user_data['referer'] = web.ctx.env.get('HTTP_REFERER', '')
        input.user_data['agent'] = web.ctx.env.get('HTTP_USER_AGENT', '')

        # generate computation code
        ccode = helpers.md5(input.user_data['name']+input.user_data['email']+input.user_data['ip_address'])

        # TODO: send results to rabbit with user-data (email,name,ip,referral)
        print "to rabbit: ", {
            'user_data': input.user_data,
            'user_answers': input.user_answers,
            'results': results,
            'code': ccode,
        }

        # prepare json response
        web.header('Content-Type', 'application/json')

        try:
            return json.dumps({
                'code': ccode,
                'results': results,
            })
        except Exception, e:
            return json.dumps({'error':e.message})


if __name__ == "__main__":
    app.run()
    application = app.wsgifunc()
