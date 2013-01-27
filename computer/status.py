
class InvalidComputerStatus(Exception): pass
class ComputerNotConfigured(Exception): pass

class ComputerStatus(object):

    def __init__(self, election_code):

        self.election_code = election_code
        self.answers = list()
        self.parties = list()
        self.questions = set()

        print "#" * 10, "ComputerStatus(%s)" % election_code, "#" * 10
        self.load()



    def load(self, parties_positions=None):
        """
        parties_positions is a dictionary of dictionaries of question's answers.
        the results of loading status is to extract parties list from outer keys,
        questions keys list ( check if they are always the same ), and an ordered list of lists of answers
        party key, question key and answers value are forced to int
        """
        if not parties_positions:
            # load parties positions from persistent source
            # TODO: csv, sqlite or pickle file
            self.load({"1": {"1": 3, "2": 3, "3": -1, "4": -1, "5": 2, "6": 1, "7": 3, "8": 2, "9": -2, "10": 2, "11": 2, "12": 1, "13": 1, "14": -1, "15": 2, "16": 2, "17": 2, "18": 1, "19": 1, "20": -1, "21": -2, "22": 1, "23": 2, "24": 1, "25": 2}, "2": {"1": 2, "2": 1, "3": 1, "4": 3, "5": -1, "6": -1, "7": -3, "8": 2, "9": 3, "10": 3, "11": 2, "12": -1, "13": -3, "14": -3, "15": 3, "16": 3, "17": 1, "18": -2, "19": -3, "20": 3, "21": 1, "22": 2, "23": 2, "24": -3, "25": 2}, "3": {"1": 2, "2": 2, "3": 1, "4": 3, "5": -1, "6": -1, "7": -1, "8": -2, "9": 3, "10": 3, "11": -2, "12": 1, "13": -2, "14": -2, "15": 2, "16": 2, "17": 2, "18": -2, "19": 1, "20": 2, "21": 2, "22": 2, "23": 3, "24": 2, "25": 1}, "4": {"1": 3, "2": 3, "3": -3, "4": -1, "5": 3, "6": 3, "7": 2, "8": 3, "9": -1, "10": 3, "11": 3, "12": 3, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": -1, "25": 3}, "5": {"1": 1, "2": 1, "3": 1, "4": 2, "5": -1, "6": -1, "7": 3, "8": 1, "9": 1, "10": 1, "11": -2, "12": -2, "13": -3, "14": -3, "15": 1, "16": 3, "17": 3, "18": -3, "19": 3, "20": 3, "21": 2, "22": 3, "23": 3, "24": 3, "25": -2}, "6": {"1": 1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -2, "8": 2, "9": 1, "10": 1, "11": 1, "12": 1, "13": -2, "14": -1, "15": 1, "16": 1, "17": -1, "18": -3, "19": -3, "20": 3, "21": 3, "22": -1, "23": 3, "24": 3, "25": 1}, "7": {"1": 2, "2": 3, "3": 1, "4": 2, "5": 2, "6": 3, "7": 1, "8": 2, "9": 3, "10": 2, "11": 3, "12": 3, "13": 3, "14": 1, "15": 3, "16": -3, "17": -2, "18": 3, "19": 1, "20": -1, "21": 1, "22": 1, "23": 2, "24": 2, "25": 1}, "8": {"1": 2, "2": 3, "3": -1, "4": 3, "5": 3, "6": 3, "7": 2, "8": 3, "9": -2, "10": 3, "11": 3, "12": 2, "13": 2, "14": 3, "15": 3, "16": -2, "17": -2, "18": 1, "19": -3, "20": -2, "21": 1, "22": -2, "23": 3, "24": 2, "25": 3}, "9": {"1": 3, "2": 3, "3": -3, "4": -2, "5": 1, "6": 3, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 2, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "11": {"1": 2, "2": 3, "3": -3, "4": -3, "5": 3, "6": 1, "7": 3, "8": 3, "9": 1, "10": 3, "11": 2, "12": 2, "13": 3, "14": 3, "15": 2, "16": -3, "17": -3, "18": 2, "19": -3, "20": -3, "21": -3, "22": -3, "23": -3, "24": 1, "25": 1}, "14": {"1": 2, "2": 3, "3": -3, "4": 3, "5": 3, "6": 3, "7": 3, "8": 3, "9": 3, "10": 3, "11": 3, "12": 2, "13": 3, "14": 3, "15": 3, "16": -3, "17": -3, "18": 3, "19": -3, "20": -3, "21": 3, "22": -3, "23": -3, "24": 3, "25": 3}, "16": {"1": -1, "2": 3, "3": -1, "4": 1, "5": 1, "6": 1, "7": -3, "8": 1, "9": 1, "10": 1, "11": 1, "12": -1, "13": -3, "14": -1, "15": 1, "16": 1, "17": 1, "18": -3, "19": -3, "20": 3, "21": 3, "22": 2, "23": 2, "24": 3, "25": 1}})
            return

        parties = parties_positions.keys()

        if not parties:
            # TODO: what i have to do now?
            return
        # parties list length is greater then zero

        # every party has a dict with its answers
        if not all( [ isinstance(parties_positions[party],dict) for party in parties]):
            raise InvalidComputerStatus("Some parties has a invalid questions dict")

        # read questions id list of first parties_positions
        # the result of set(dict()) is a set of dict's keys
        questions = set( parties_positions[parties[0]] )

        if not all( [ questions == set( parties_positions[party] ) for party in parties ] ):
            raise InvalidComputerStatus("All parties have to answer to same questions")

        self.questions = questions # [int(x) for x in questions]
        self.answers, self.parties = [], []
        for party in parties:
            # build answers as list of lists to maintain order of parties and questions
            self.answers.append(self.prepare_answers(parties_positions[party], questions) )
            self.parties.append( party ) # int(party)

        print 'parties', self.parties
        print 'questions', self.questions
        print 'answers', self.answers


    def prepare_answers(self, dict_of_answers, questions=None):
        return [ dict_of_answers[question] for question in questions or self.questions] # int(dict_of_answers[question])


