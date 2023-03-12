import unittest
import re
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Stranger" in response.get_data(as_text=True))

    def test_register_and_login(self):
        # register a new account
        response = self.client.post(
            "/auth/register",
            data={
                "email": "joe@example.com",
                "username": "joe",
                "password": "cat",
                "password2": "cat",
            },
        )
        # after valid registration, user is redirected to login page
        # on invalid registration page is rendered again, with error messages
        self.assertEqual(response.status_code, 302)

        # login with the new account
        # follow_redirect, make test client work like a browser and
        # automatically issue a GET request for the redirected URL
        # i.e 302 won't be returned instead the response from redirected
        # URL is returned
        response = self.client.post(
            "/auth/login",
            data={"email": "joe@example.com", "password": "cat"},
            follow_redirects=True,
        )
        # print(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        # the string is assembled from static and dynamic portions,
        # so theway jinja2 template was created the final html has extra
        # whitespace in between words
        self.assertTrue(re.search(r"Hello,\s+joe", response.get_data(as_text=True)))
        self.assertTrue(
            "You have not confirmed your account yet" in response.get_data(as_text=True)
        )

        # send a confirmation token
        user = User.query.filter_by(email="joe@example.com").first()
        token = user.generate_confirmation_token()
        # response is redirect to home page, test client requests the redirected
        # page automatically and return it
        response = self.client.get(
            "/auth/confirm/{}".format(token), follow_redirects=True
        )
        # user.confirm(token)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            "You have confirmed your account" in response.get_data(as_text=True)
        )

        # log out
        response = self.client.get("/auth/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("You have been logged out" in response.get_data(as_text=True))
