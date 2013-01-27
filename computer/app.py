import web
import json
import config, status, mds, helpers

urls = (
    '/computation/?', 'compute',
)


web.config.debug = config.DEBUG
app = web.application(urls, globals())
current_status = status.ComputerStatus(config.ELECTION_CODE)


class compute(object):

    def POST(self):
        """
        Input data is a json string, passed as POST request payload.
        """

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

        except KeyError:
            raise web.BadRequest

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

        # prepare json response
        web.header('Content-Type', 'application/json')

        try:
            return json.dumps(results)
        except Exception, e:
            return json.dumps({'error':e.message})


if __name__ == "__main__":
    app.run()
    application = app.wsgifunc()
