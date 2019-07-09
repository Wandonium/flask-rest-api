import unittest
import os
import json
from ..app import create_app, db

class UsersTest(unittest.TestCase):
  """
  Users Test Case
  """
  def setUp(self):
    """
    Test Setup
    """
    self.app = create_app("testing")
    self.client = self.app.test_client
    self.user = {
      'name': 'wando',
      'email': 'wando@mail.com',
      'password': 'abc'
    }

    with self.app.app_context():
      # create all tables
      db.create_all()

  def test_user_creation(self):
    """ test user creation with valid credentials """
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 201)

  def test_user_creation_with_existing_email(self):
    """ test user creation with already existing email """
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('error'))

  def test_user_creation_with_no_password(self):
    """ test user creation with no password """
    user1 = {
      'name': 'Test Name',
      'email': 'test@mail.com',
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('password'))

  def test_user_creation_with_no_email(self):
    """ test user creation with no email """
    user1 = {
      'name': 'Test Name',
      'email': 'test@mail.com',
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)
    self.assertTrue(json_data.get('email'))

  def test_user_creation_with_empty_request(self):
    """ test user creation with empty request """
    user1 = {}
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 400)

  def test_user_login(self):
    """ User login tests """
    user1 = {
      'name': 'Test Name',
      'email': 'test@mail.com',
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/api/v1/users/login',     headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    json_data = json.loads(res.data)
    self.assertTrue(json_data.get('jwt_token'))
    self.assertEqual(res.status_code, 200)

  def test_user_login_with_invalid_password(self):
    """ User login tests with invalid credentials """
    user1 = {
      'password': 'Test Name',
      'email': 'test@mail.com',
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/api/v1/users/login',     headers={'Content-Type': 'application/json'},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('error'), 'invalid credentials')
    self.assertEqual(res.status_code, 400)

  def test_user_login_with_invalid_email(self):
    """ User login tests with invalid credentials """
    user1 = {
      'password': 'Test Name',
      'email': 'test23@mail.com',
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    res = self.client().post('/api/v1/users/login',     headers={'Content-Type': 'application/json'},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertFalse(json_data.get('jwt_token'))
    self.assertEqual(json_data.get('error'), 'invalid credentials')
    self.assertEqual(res.status_code, 400)

  def test_user_get_me(self):
    """ Test user get me """
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().get('/api/v1/users/me',        headers={'Content-Type': 'application/json',      'api-token': api_token})
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    self.assertEqual(json_data.get('email'), 'test@mail.com')
    self.assertEqual(json_data.get('name'), 'Test Name')

  def test_user_update_me(self):
    """ Test User update me """
    user1 = {
      'name': 'New Name'
    }
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().put('/api/v1/users/me',        headers={'Content-Type': 'application/json',      'api-token': api_token},
      data=json.dumps(user1))
    json_data = json.loads(res.data)
    self.assertEqual(res.status_code, 200)
    self.assertEqual(json_data.get('name'), 'New Name')

  def test_delete_user(self):
    """ Test user delete """
    res = self.client().post('/api/v1/users/',          headers={'Content-Type': 'application/json'},
      data=json.dumps(self.user))
    self.assertEqual(res.status_code, 201)
    api_token = json.loads(res.data).get('jwt_token')
    res = self.client().delete('/api/v1/users/me',        headers={'Content-Type': 'application/json',      'api-token': api_token})
    self.assertEqual(res.status_code, 204)

  def tearDown(self):
    """
    Tear Down
    """
    with self.app.app_context():
      db.session.remove()
      db.drop_all()

if __name__ == "__main__":
  unittest.main()