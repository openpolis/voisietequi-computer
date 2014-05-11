import sys
print sys.path
import web
import json
from computer import config
from computer import status
from computer import mds
from computer import helpers
from computer.proc import computer_proc

urls = (
    '/', 'index',
    '/computation/?', 'compute',
    '/coordinate_partiti/(\w+)/?', 'coordinates',
)

if config.DEBUG:
    urls += ('/configuration/?','configuration')

web.config.debug = config.DEBUG
app = web.application(urls, globals())
current_status = status.ComputerStatus(config.ELECTION_CODE)

logger = helpers.get_logger('computer')

computer = computer_proc.ComputerProcess(push_addr='%s:5557' % config.SITE_HOST, sub_addr='%s:5556' % config.SITE_HOST)
computer.start()


def send_results(code, user_data, user_answers, results):

    computer_proc.save_results('tcp://%s:5557' % config.SITE_HOST, config.ELECTION_CODE, {
        'code': code,
        'user_data': user_data,
        'user_answers': user_answers,
        'results': results,
    })

    logger.info("Results sent")


class index(object):

    def GET(self):
        return "Hello World!"

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
            logger.error("BadRequest: User has answered to only %d questions out of %d" % (len(input.user_answers), len(current_status.questions)))
            ip_address = web.ctx.ip
            if not ip_address or ip_address == '127.0.0.1':
                ip_address = web.ctx.env.get('HTTP_X_FORWARDED_FOR',web.ctx.ip)
            web.sendmail('no-reply@voisietequi.it', ['guglielmo.celata@gmail.com', 'daniele.faraglia@gmail.com'],
                         'Computer Error', """
                Computer Error: User has answered to only %d questions out of %d
                IP: %s
                AGENT: %s
                REQUEST: %s
                INPUT: %s
                QUESTIONS: %s
            """ % (len(input.user_answers), len(current_status.questions), ip_address, web.ctx.env.get('HTTP_USER_AGENT', ''), web.data(), input, current_status.questions))
            raise web.BadRequest("User have to answer to all questions")

        # convert all to integers
        user_answers = {}
        for k,v in input.user_answers.items():
            user_answers[int(k)] = int(v)

        if set(user_answers) != current_status.questions:
            logger.error("BadRequest: User responded to questions that are not in the configuration. %s != %s", set(user_answers), current_status.questions)
            raise web.BadRequest("User have to answer to right questions")

        user_answers = current_status.prepare_answers(user_answers)

        # execute mds calculation
        # TODO: execute can raise an Exception
        results = mds.execute(
            current_status.parties + ['user'],
            current_status.answers + [user_answers]
        )

        input.user_data['ip_address'] = web.ctx.ip
        if not input.user_data['ip_address'] or input.user_data['ip_address'] == '127.0.0.1':
            input.user_data['ip_address'] = web.ctx.env.get('HTTP_X_FORWARDED_FOR',web.ctx.ip)
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

        print current_status.parties
        print current_status.answers

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

computer.join()
