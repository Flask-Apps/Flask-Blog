import unittest
import threading
import re
import time
from selenium import webdriver
from app import create_app, fake, db
from app.models import Role, User


class SeleniumTestCase(unittest.TestCase):
    client = None
    HOST = "localhost"
    PORT = 5000

    @classmethod
    def setUpClass(cls):
        # start Chrome
        options = webdriver.ChromeOptions()
        # run w/o user interface
        # options.add_argument("headless")
        # suppress jibberish from webdriver
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        try:
            cls.client = webdriver.Chrome(
                executable_path="./chromedriver/chromedriver", chrome_options=options
            )
        except:  # noqa
            pass

        # skip these tests if the browser couldnot be started
        if cls.client:
            # create the application
            cls.app = create_app("testing-with-selenium")
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # suppress logging to keep unittest output clean
            import logging

            logger = logging.getLogger("werkzeug")
            logger.setLevel("ERROR")

            # create the database and populate with some fake data
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # add an administrator user
            admin_role = Role.query.filter_by(permissions=0xFF).first()
            admin = User(
                email="joe@example.com",
                username="joe",
                password="cat",
                role=admin_role,
                confirmed=True,
            )
            db.session.add(admin)
            db.session.commit()

            # start the Flask server in a thread
            cls.server_thread = threading.Thread(
                target=cls.app.run,
                # pass kwargs to flask run
                # kwargs={"debug": "false", "use_reloader": False, "use_debugger": False},
                kwargs={
                    "host": cls.HOST,
                    "port": cls.PORT,
                    "debug": False,
                    "use_reloader": False,
                    "use_debugger": False,
                },
            )
            # start the server, runs target func in background
            cls.server_thread.start()

            # # give the server a second to ensure it's up
            # time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up actions after all the tests in a test case class have
        been run
        """
        # this way to ensure the background tasks such as code coverage
        # can cleanly complete their work
        if cls.client:
            # stop the Flask server and the browser
            cls.client.get(f"http://{cls.HOST}:{cls.PORT}/shutdown")
            cls.client.quit()
            # time.sleep(2)

            # ensure the server has stopped
            cls.server_thread.join()

            # destroy database
            db.drop_all()
            db.session.remove()

            # remove application context
            cls.app_context.pop()

    def setUp(self):
        """Skip tests if selenium cannot start the web browser in setUpClass"""
        if not self.client:
            self.skipTest("Web browser not available")

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # navigate to home page
        self.client.get(f"http://{self.HOST}:{self.PORT}/")
        # print(self.client.page_source)
        self.assertTrue("Stranger" in self.client.page_source)

        # navigate to login page
        self.client.find_element("link text", "Log In").click()
        self.assertIn("<h1>Login</h1>", self.client.page_source)

        # log in
        # time.sleep(2000)
        self.client.find_element("name", "email").send_keys("joe@example.com")
        self.client.find_element("name", "password").send_keys("cat")
        self.client.find_element("name", "submit").click()
        # print(self.client.page_source)
        self.assertTrue(re.search(r"Hello,\s+Joe", self.client.page_source))

        # navigate to the user's profile page
        self.client.find_element("link text", "Profile").click()
        self.assertIn("<h1>joe</h1>", self.client.page_source)
