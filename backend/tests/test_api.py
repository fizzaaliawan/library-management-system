import sys
import os
import unittest
from fastapi.testclient import TestClient

# Ensure app is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_read_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome to the Library Management System", response.json()["message"])
