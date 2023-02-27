import unittest
from app.models import User, Permission, AnonymousUser, Role, Follow
from app import db, create_app
import time
from datetime import datetime


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password="cat")
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password="cat")
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password="cat")
        self.assertTrue(u.verify_password("cat"))
        self.assertFalse(u.verify_password("mouse"))

    def test_password_salts_are_random(self):
        u = User(password="cat")
        u2 = User(password="cat")
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        # u = User(username="cat", email="cat@cat.com", password="cat")
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):
        u1 = User(password="cat")
        u2 = User(password="dog")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token, expiration=0))
        self.assertTrue(u.confirm(token))
        time.sleep(2)
        self.assertFalse(u.confirm(token, expiration=1))

    def test_valid_reset_token(self):
        u = User(password="Cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, "dog"))
        self.assertTrue(u.verify_password("dog"))

    def test_invalid_reset_token(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + "p", "horse"))
        self.assertTrue(u.verify_password("cat"))

    def test_valid_email_change(self):
        u = User(email="test1@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token("test2@example.com")
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == "test2@example.com")

    def test_invalid_email_change(self):
        u1 = User(email="test1@example.com", password="cat")
        u2 = User(email="tester1@example.com", password="dog")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token("test2@example.com")
        # one users token can't be used to change email of the other user
        self.assertFalse(u2.change_email(token))
        # user have invalid user token
        self.assertFalse(u1.change_email(token + "p"))
        self.assertTrue(u2.email == "tester1@example.com")
        self.assertTrue(u1.email == "test1@example.com")

    def test_duplicate_email_change_token(self):
        u1 = User(email="test1@example.com", password="cat")
        u2 = User(email="tester1@example.com", password="dog")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token("test1@example.com")
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == "tester1@example.com")

    def test_user_role(self):
        u = User(email="m2@example.com", password="cat1")
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):
        r = Role.query.filter_by(name="Moderator").first()
        u = User(email="m2@example.com", password="cat", role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_administrator_role(self):
        r = Role.query.filter_by(name="Administrator").first()
        u = User(email="m2@example.com", password="cat", role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_timestamp(self):
        u = User(password="cat")
        db.session.add(u)
        db.session.commit()
        self.assertTrue((datetime.utcnow() - u.member_since).total_seconds() < 3)
        self.assertTrue((datetime.utcnow() - u.last_seen).total_seconds() < 3)

    def test_ping(self):
        u = User(password="Cat")
        db.session.add(u)
        db.session.commit()
        time.sleep(2)
        last_seen_before = u.last_seen
        u.ping()
        self.assertTrue(u.last_seen > last_seen_before)

    def test_gravatar(self):
        u = User(email="test1@example.com", password="Cat")
        with self.app.test_request_context("/"):
            gravatar = u.gravatar()
            gravatar_256 = u.gravatar(size=256)
            gravatar_pg = u.gravatar(rating="pg")
            gravatar_retro = u.gravatar(default="retro")
        email_hash = "aa99b351245441b8ca95d54a52d2998c"
        # self.assertTrue("http://www.gravatar.com/avatar/" + email_hash in gravatar)
        self.assertTrue("https://secure.gravatar.com/avatar/" + email_hash in gravatar)
        self.assertTrue("s=256" in gravatar_256)
        self.assertTrue("r=pg" in gravatar_pg)
        self.assertTrue("d=retro" in gravatar_retro)

    def test_follows(self):
        u1 = User(email="test1@test.com", password="cat1")
        u2 = User(email="test2@test.com", password="cat2")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertFalse(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        timestamp_before = datetime.utcnow()

        u1.follow(u2)
        db.session.add(u1)
        db.session.commit()
        timestamp_after = datetime.utcnow()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertTrue(u1.followed.count() == 2)
        self.assertTrue(u2.followers.count() == 2)
        f = u1.followed.all()[-1]
        self.assertTrue(f.followed == u2)
        self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)

        f = u2.followers.all()[-1]
        self.assertTrue(f.follower == u1)

        u1.unfollow(u2)
        db.session.add(u1)
        db.session.commit()
        self.assertTrue(u1.followed.count() == 1)
        self.assertTrue(u2.followers.count() == 1)
        self.assertTrue(Follow.query.count() == 2)

        u2.follow(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 3)
        db.session.delete(u2)
        db.session.commit()
        self.assertTrue(Follow.query.count() == 1)
