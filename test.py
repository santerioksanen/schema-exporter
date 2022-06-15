import unittest
import sys


if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = loader.discover('test')
    runner = unittest.TextTestRunner()
    result = runner.run(tests)

    sys.exit(not result.wasSuccessful())
