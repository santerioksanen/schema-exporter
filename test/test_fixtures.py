import os
import subprocess
from pathlib import Path
from unittest import TestCase


class FixtureTestCases(TestCase):
    def assert_fixture(self, fname) -> None:
        old_wd = os.getcwd()

        fixtures_path = Path(__name__).absolute().parent / "test/fixtures/"

        os.chdir(fixtures_path)

        subprocess.run(f"python {fname}.py", shell=True, check=True)

        os.chdir(old_wd)

        # Typescript
        with open(fixtures_path / f"{fname}.ts") as f:
            exp = f.read()

        with open(fixtures_path / f"{fname}.ts.export") as f:
            act = f.read()

        self.assertEqual(exp, act)

        # Rust
        with open(fixtures_path / f"{fname}.rs") as f:
            exp = f.read()

        with open(fixtures_path / f"{fname}.rs.export") as f:
            act = f.read()

        self.assertEqual(exp, act)

        # Delete generated file
        os.remove(fixtures_path / f"{fname}.ts.export")
        os.remove(fixtures_path / f"{fname}.rs.export")

    def test_marshmallow_1(self) -> None:
        self.assert_fixture("test_marshmallow_1")

    def test_drf_1(self) -> None:
        self.assert_fixture("test_drf_1")
