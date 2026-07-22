import unittest
from click.testing import CliRunner
from src.main import cli

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_help_command(self):
        result = self.runner.invoke(cli, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Library Management System CLI", result.output)

    def test_book_help(self):
        result = self.runner.invoke(cli, ["book", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Manage Books", result.output)

    def test_member_help(self):
        result = self.runner.invoke(cli, ["member", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Manage Members", result.output)

    def test_loan_help(self):
        result = self.runner.invoke(cli, ["loan", "--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Manage Book Loans", result.output)

if __name__ == "__main__":
    unittest.main()
