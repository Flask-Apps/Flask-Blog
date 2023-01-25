import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        # runs before each tests
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        # binds the app context to the current context
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # runs after each tests
        db.session.remove()
        db.drop_all()
        # pops the app context
        self.app_context.pop()

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config["TESTING"])
