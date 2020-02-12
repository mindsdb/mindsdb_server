import pytest
import unittest

#from mindsdb_server.shared_ressources import get_shared
from mindsdb_server.server import start_server

class EndpointsTest(unittest.TestCase):

    def setUp(self):
        appl = start_server()
        self.app = appl.test_client()

    def test_ping(self):
        """
        Call utilities ping endpoint
        THEN check the response is success
        """
        response = self.app.get('/util/ping')
        assert response.status_code == 200

    def test_datasources(self):
        """
        Call list datasources endpoint
        THEN check the response is success
        """
        response = self.app.get('/datasources/')
        assert response.status_code == 200

    def test_predictors(self):
        """
        Call list predictors endpoint
        THEN check the response is success
        """
        response = self.app.get('/predictors/')
        assert response.status_code == 200

    def test_predictor_not_found(self):
        """
        Call unexisting predictor
        then check the response is NOT FOUND
        """
        response = self.app.get('/predictors/dummy_predictor')
        assert response.status_code == 404

if __name__ == "__main__":
    unittest.main()