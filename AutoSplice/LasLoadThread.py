import threading
import lasio
import time


class LasLoadThread(object):
    """ Threading example class
    The run() method will be started and it will run in the background
    until the application exits.
    """

    def __init__(self, files=[],interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.files=files    
        self.Lases=[]  
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()   
                        

    def run(self):
        """ Method that runs forever """
         # Start the execution
        for f in self.files:
            # Do something
            print('Las being loaded in background')
            self.Lases.append(lasio.read(f))
        print('Loading complete...')
            # time.sleep(self.interval)


# lasLoad = LasLoadThread()
# time.sleep(3)
# print('Checkpoint')
# time.sleep(2)
# print('Bye')