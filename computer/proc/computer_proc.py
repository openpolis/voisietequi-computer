import time
import zmq
from computer.proc import base
from computer import status
from computer import config
from computer.status import InvalidComputerStatus


def save_results(computer_addr, election_code, result):
    context = zmq.Context()
    save_sender = context.socket(zmq.PUSH)
    save_sender.connect(computer_addr)

    # send message to sender
    save_sender.send_json(['save_results', [election_code], result])


class ComputerProcess(base.ZmqProcess):

    def __init__(self, push_addr, sub_addr):
        super(ComputerProcess, self).__init__()

        self.push_addr = push_addr
        self.sub_addr = sub_addr
        self.push_stream = None
        self.sub_stream = None
        self.status = status.ComputerStatus(config.ELECTION_CODE)

    def setup(self):
        """Sets up PyZMQ and creates all streams."""
        print "Aye sir, unit {0} ready for your commands ...".format(self)

        super(ComputerProcess, self).setup()

        # Create the stream and add the message handler
        self.push_stream, _ = self.stream(zmq.PUSH, self.push_addr, bind=False)

        self.sub_stream, _ = self.stream(zmq.SUB, self.sub_addr, bind=False)
        self.sub_stream.on_recv(SubStreamHandler(self.status, self.push_stream))


        print "Computer connected:", self.push_addr

    def run(self):
        """Sets up everything and starts the event loop."""
        print ("Run Computer process")
        self.setup()
        self.loop.start()

    def stop(self):
        """Stops the event loop."""
        print ("Stop Computer process")
        self.loop.stop()

class SubStreamHandler(base.MessageHandler):
    """Handels messages arrvinge at the ComputerProcess's REP stream."""
    def __init__(self, computer_status, push_stream):
        super(SubStreamHandler, self).__init__()
        self._computer_status = computer_status
        self._push_stream = push_stream

    def configure(self, election_code, **party_positions):
        print "Received a configuration: %s %s" % (election_code, party_positions)

        try:
            # save new configuration
            self._computer_status.save(party_positions)
            configured = True
        except InvalidComputerStatus:
            configured = False
            print "Invalid status: %s" % party_positions

        # reply to server
        self._push_stream.send_json(['computer_configured', [], {'configured': configured}])



if __name__ == "__main__":

    cpu1 = ComputerProcess(push_addr='127.0.0.1:5557', sub_addr='127.0.0.1:5556')
    cpu2 = ComputerProcess(push_addr='127.0.0.1:5557', sub_addr='127.0.0.1:5556')

    cpu1.start(), cpu2.start()

    import random
    c = 0
    while True:
        # simulate some very complex computation
        (x, y) = (random.gauss(0, 1), random.gauss(0, 1))
        result = { 'counter': c, 'x' : x, 'y': y}

        # send message to sender
        save_results('tcp://127.0.0.1:5557', config.ELECTION_CODE, result)

        # take it easy
        time.sleep(1)

        c += 1

    cpu1.join(), cpu2.join()


