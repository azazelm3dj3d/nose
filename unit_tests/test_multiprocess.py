import pickle
import sys
import unittest

from xnose import case
from xnose.plugins import multiprocess
from xnose.plugins.skip import SkipTest
from xnose.config import Config
from xnose.loader import TestLoader
try:
    # 2.7+
    from unittest.runner import _WritelnDecorator
except ImportError:
    from unittest import _WritelnDecorator


class ArgChecker:
    def __init__(self, target, args):
        self.target = target
        self.args = args
        # skip the id and queues
        pargs = args[7:]
        self.pickled = pickle.dumps(pargs)
        try:
            testQueue = args[1]
            testQueue.get(timeout=0)
        except:
            pass # ok if queue is empty
    def start(self,*args):
        pass
    def is_alive(self):
        return False

        
def setup(mod):
    multiprocess._import_mp()
    if not multiprocess.Process:
        raise SkipTest("multiprocessing not available")
    mod.Process = multiprocess.Process
    multiprocess.Process = ArgChecker
        

class T(unittest.TestCase):
    __test__ = False
    def runTest(self):
        pass

def test_mp_process_args_pickleable():
    # TODO(Kumar) this test needs to be more succint.
    # If you start seeing it timeout then perhaps we need to skip it again.
    # raise SkipTest('this currently gets stuck in poll() 90% of the time')
    test = case.Test(T('runTest'))
    config = Config()
    config.multiprocess_workers = 2
    config.multiprocess_timeout = 5
    runner = multiprocess.MultiProcessTestRunner(
        stream=_WritelnDecorator(sys.stdout),
        verbosity=10,
        loaderClass=TestLoader,
        config=config)
    runner.run(test)
        
