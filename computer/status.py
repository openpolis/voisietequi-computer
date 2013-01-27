import config
try:
    import cPickle as pickle
except ImportError:
    import pickle

class InvalidComputerStatus(Exception): pass
class ComputerNotConfigured(Exception): pass

class ComputerStatus(object):

    def __init__(self, election_code):

        self.election_code = election_code
        self.answers = list()
        self.parties = list()
        self.questions = set()
        self.is_configured = False

        print "#" * 10, "ComputerStatus(%s)" % election_code, "#" * 10
        self.load()


    def save(self, parties_positions):
        """persist new status, then load it"""
        self.load(parties_positions)
        pickle.dump( parties_positions, open( config.STATUS_PATH, "wb" ) )
        print "Status saved"


    def load(self, parties_positions=None):
        """
        parties_positions is a dictionary of dictionaries of question's answers.
        the results of loading status is to extract parties list from outer keys,
        questions keys list ( check if they are always the same ), and an ordered list of lists of answers
        """
        if not parties_positions:
            # load parties positions from persistent source
            try:
                data = pickle.load( open(config.STATUS_PATH, "rb" ) )
                self.load( data )
            except IOError:
                print "Computer initialized without configuration"
                # raise ComputerNotConfigured
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

        self.is_configured = True
        print "Status loaded"


    def prepare_answers(self, dict_of_answers, questions=None):
        return [ dict_of_answers[question] for question in questions or self.questions] # int(dict_of_answers[question])


