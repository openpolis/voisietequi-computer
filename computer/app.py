import web
import json
import config, status, mds, helpers

urls = (
    '/computation/?', 'compute',
)

if config.DEBUG:
    urls += ('/configuration/?','configuration')

web.config.debug = config.DEBUG
app = web.application(urls, globals())
current_status = status.ComputerStatus(config.ELECTION_CODE)

import pika
import multiprocessing
from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle
import logging
logging.basicConfig()

connection = pika.BlockingConnection(pika.URLParameters(config.MQ_URL))
channel = connection.channel()

channel.exchange_declare(exchange=config.MQ_EXCHANGE, exchange_type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=config.MQ_EXCHANGE,
    queue=queue_name,
    routing_key=config.MQ_PREFIX+'discover')


def callback_deliver(ch, method, properties, body):
    print " [x] %r:%r" % (method.routing_key, pickle.loads(body),)
    import socket
    ch.basic_publish(exchange='',
        routing_key=properties.reply_to,
        body=pickle.dumps({
            'last_update': current_status.last_update,
            'timestamp': datetime.now(),
            'host':socket.gethostname()
        })
    )
#    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_consume(
    consumer_callback=callback_deliver,
    queue=queue_name,
    no_ack=True
)


# configuration
def callback_configure(ch, method, properties, body):
    data = pickle.loads(body)
    print " [x] %r:%r" % (method.routing_key, data['election_code'])
    current_status.save(data['configuration'])
    ch.basic_ack(delivery_tag = method.delivery_tag)
#channel.queue_declare(config.MQ_PREFIX+'configure')
queue_name = channel.queue_declare(exclusive=True).method.queue
binding_key = config.MQ_PREFIX+'configure'
channel.queue_bind(
    queue= queue_name,
    exchange= config.MQ_EXCHANGE,
    routing_key= binding_key
)
channel.basic_consume(
    consumer_callback=callback_configure,
    queue=queue_name,
)


def f():
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

multiprocessing.Process(target=f).start()


save_queue = config.MQ_PREFIX+'save'
channel.queue_declare(queue=save_queue, durable=True)
channel.queue_bind(exchange=config.MQ_EXCHANGE, queue=queue_name)

def send_results(code,user_data,user_answers, results):

    channel.basic_publish(
        exchange=config.MQ_EXCHANGE,
        routing_key= save_queue,
        body= pickle.dumps({
            'code':code,'user_data':user_data,'user_answers':user_answers,'results':results
        })
    )
    print ' [x] Results sent'


print ' [*] To exit press CTRL+C'

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
            or len(input.user_answers) != len(current_status.questions):
            raise web.BadRequest("User have to answer to all questions")

        # convert all to integers
        user_answers = {}
        for k,v in input.user_answers.items():
            user_answers[int(k)] = int(v)

        if set(user_answers) != current_status.questions:
            raise web.BadRequest("User have to answer to right questions")

        user_answers = current_status.prepare_answers(user_answers)

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
        code = helpers.md5(input.user_data['name']+input.user_data['email']+input.user_data['ip_address'])

        # TODO: send results to rabbit with user-data (email,name,ip,referral)
        send_results(code,input.user_data,dict(zip(current_status.questions,user_answers)), results)
#        print
#        print 'user_data: ', input.user_data
#        print 'user_answers: ', user_answers
#        print 'results: ', results
#        print 'code: ', ccode


        # prepare json response
        web.header('Content-Type', 'application/json')

        try:
            return json.dumps({
                'code': code,
                'results': results,
            })
        except Exception, e:
            return json.dumps({'error':e.message})



class configuration(object):

    def GET(self):
        return json.dumps({
            'last_update': current_status.last_update.isoformat(),
            'parties' : current_status.parties,
            'questions' : list(current_status.questions),
            'answers' : current_status.answers,
        })


if __name__ == "__main__":
    app.run()
    application = app.wsgifunc()
