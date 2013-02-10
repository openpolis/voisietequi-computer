import web
import json
import config, status, mds, helpers

urls = (
    '/computation/?', 'compute',
    '/coordinate_partiti/(\w+)/?', 'coordinates',
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
# logging.basicConfig()
import logging.config
logging.config.fileConfig(config.LOGGING_CONF_PATH)
logger = logging.getLogger('computer')

try:
    connection = pika.BlockingConnection(pika.URLParameters(config.MQ_URL))
    channel = connection.channel()
except pika.exceptions.AMQPConnectionError, e:
    logger.error('Cannot open a channel with MQ server: ' + str(e))
    exit()

logger.debug('Connected to ' + config.MQ_URL)

channel.exchange_declare(exchange=config.MQ_EXCHANGE, exchange_type='topic')

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange=config.MQ_EXCHANGE,
    queue=queue_name,
    routing_key=config.MQ_PREFIX+'discover')


def callback_deliver(ch, method, properties, body):
    logger.info("Deliver message received (%r:%r)" % (method.routing_key, pickle.loads(body) ))

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
    logger.info("Configuration received (%r:%r)" % (method.routing_key, data['election_code']))
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

save_queue = config.MQ_PREFIX+'save'
channel.queue_declare(queue=save_queue, durable=True)
channel.queue_bind(exchange=config.MQ_EXCHANGE, queue=save_queue)

def send_results(code,user_data,user_answers, results):

    channel.basic_publish(
        exchange=config.MQ_EXCHANGE,
        routing_key= save_queue,
        body= pickle.dumps({
            'code':code,'user_data':user_data,'user_answers':user_answers,'results':results
        }),
        properties=pika.BasicProperties(
            delivery_mode = 2, # make message persistent
        )
    )
    logger.info("Results sent")

def f():
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

multiprocessing.Process(target=f).start()

logger.info("To exit press CTRL+C")

class compute(object):

    def POST(self):
        """
        Input data is a json string, passed as POST request payload.
        """
        logger.debug('Start computation')

        if not current_status.is_configured:
            logger.error("Computer is not configured")
            raise web.InternalError("Computer is not configured")
        logger.debug('Computer is configured')

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
        except KeyError, ex: # can be raised from storify if miss some required fields
            logger.error("BadRequest: required field '%s' is missing" % ex)
            raise web.BadRequest

        if 'name' not in input.user_data:
            logger.error("BadRequest: required field 'name' is missing in 'user_data'")
            raise web.BadRequest("User name field not found")

        wants_newsletter = 'wants_newsletter' in input.user_data and input.user_data['wants_newsletter']

        if wants_newsletter:
            if 'email' not in input.user_data:
                logger.error("BadRequest: required field 'email' is missing in 'user_data'")
                raise web.BadRequest("User email field not found")
            elif not helpers.regexp(r"[^@]+@[^@]+\.[^@]+",input.user_data['email']):
                logger.error("BadRequest: required field 'email' is not valid in 'user_data'")
                raise web.BadRequest("User email is invalid")

        if not isinstance(input.user_answers, dict) \
            or len(input.user_answers) != len(current_status.questions):
            logger.error("BadRequest: User has answered to olny %d questions out of %d" % (len(input.user_answers), len(current_status.questions)))
            raise web.BadRequest("User have to answer to all questions")

        # convert all to integers
        user_answers = {}
        for k,v in input.user_answers.items():
            user_answers[int(k)] = int(v)

        if set(user_answers) != current_status.questions:
            logger.error("BadRequest: User responded to questions that are not in the configuration. %s != %s", (set(user_answers), current_status.questions))
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
        input.user_data['wants_newsletter'] = wants_newsletter

        # generate computation code
        code = helpers.md5()

        # TODO: send results to rabbit with user-data (email,name,ip,referral)
        send_results(code,input.user_data,dict(zip(current_status.questions,user_answers)), results)

        # prepare json response
        web.header('Content-Type', 'application/json')
        web.header('Cache-control', 'no-cache')

        try:
            data = json.dumps({
                'code': code,
                'results': results,
                })
            logger.debug('Results data: ' + data)
            return data
        except Exception, e:
            return json.dumps({'error':e.message})


class coordinates(object):

    def GET(self, election_code):

        if not current_status.is_configured:
            logger.error("Computer is not configured")
            raise web.InternalError("Computer is not configured")

        if election_code != config.ELECTION_CODE:
            logger.error("BadRequest: This computer is configured to handle '{0}' as election code, request has '{1}'".format(election_code,config.ELECTION_CODE))
            raise web.BadRequest("Invalid election code")

        results = mds.execute(
            current_status.parties,
            current_status.answers
        )

        try:
            return json.dumps(results)
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
