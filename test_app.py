import unittest, json, jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app import app

class TestAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'finals-secret-key'
        self.client = app.test_client()
        self.token = jwt.encode(
            {'user': 'admin', 'exp': datetime.utcnow() + timedelta(hours=1)},
            app.config['SECRET_KEY'], algorithm='HS256'
        )

    def test_login(self):
        r = self.client.post('/login', json={'username':'admin','password':'password'})
        self.assertEqual(r.status_code, 200)

    @patch('app.mysql')
    def test_get_customers(self, mock_mysql):
        cur = MagicMock()
        cur.fetchall.return_value = [{'customer_id':1,'first_name':'Juan'}]
        mock_mysql.connection.cursor.return_value = cur
        r = self.client.get(f'/customers?token={self.token}')
        self.assertEqual(r.status_code, 200)

    @patch('app.mysql')
    def test_get_stores(self, mock_mysql):
        cur = MagicMock()
        cur.fetchall.return_value = [{'store_id':1,'store_name':'Bench'}]
        mock_mysql.connection.cursor.return_value = cur
        r = self.client.get(f'/stores?token={self.token}')
        self.assertEqual(r.status_code, 200)

    @patch('app.mysql')
    def test_xml_output(self, mock_mysql):
        cur = MagicMock()
        cur.fetchall.return_value = [{'store_id':1,'store_name':'Bench'}]
        mock_mysql.connection.cursor.return_value = cur
        r = self.client.get(f'/stores?token={self.token}&format=xml')
        self.assertIn(b'application/xml', r.content_type.encode())

if __name__ == '__main__':
    unittest.main()
