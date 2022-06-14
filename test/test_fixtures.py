import os

from unittest import TestCase
from pathlib import Path
import subprocess


class FixtureTestCases(TestCase):

    def test_fixtures(self):
        __enums = dict()
        __schemas = dict()

        old_wd = os.getcwd()

        fixtures_path = Path(__name__).absolute().parent / 'test/fixtures/'

        os.chdir(fixtures_path)

        fname = 'test_schema_1'

        subprocess.run(f'python {fname}.py', shell=True, check=True)

        os.chdir(old_wd)

        with open(fixtures_path / f'{fname}.ts') as f:
            exp = f.read()

        with open(fixtures_path / f'{fname}.ts.export') as f:
            act = f.read()

        self.assertEqual(exp, act)

        # Delete generated file
        os.remove(fixtures_path / f'{fname}.ts.export')
