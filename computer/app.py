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
            return json.dumps({
                'code': ccode,
                'results': results,
            })
        except Exception, e:
            return json.dumps({'error':e.message})


if __name__ == "__main__":
    app.run()
    application = app.wsgifunc()
