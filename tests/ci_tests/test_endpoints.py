import unittest
from mindsdb_server.server import start_server


class PredictorTest(unittest.TestCase):

    def setUp(self):
        appl = start_server(from_tests=True)
        self.app = appl.test_client()

    def test_predictors(self):
        """
        Call list predictors endpoint
        THEN check the response is success
        """
        response = self.app.get('/predictors/')
        assert response.status_code == 200

    def test_columns_predictor_not_found(self):
        """
        Call unexisting predictor to analyse_dataset
        then check the response is NOT FOUND
        """
        response = self.app.get('/predictors/dummy_predictor/columns')
        assert response.status_code == 404

    def test_predictor_not_found(self):
        """
        Call unexisting predictor
        then check the response is NOT FOUND
        """
        response = self.app.get('/predictors/dummy_predictor')
        assert response.status_code == 404


class DatasourceTest(unittest.TestCase):

    def setUp(self):
        appl = start_server(from_tests=True)
        self.app = appl.test_client()
    
    def test_datasources(self):
        """
        Call list datasources endpoint
        THEN check the response is success
        """
        response = self.app.get('/datasources/')
        assert response.status_code == 200

    def test_datasource_not_found(self):
        """
        Call unexisting datasource
        then check the response is NOT FOUND
        """
        response = self.app.get('/datasource/dummy_source')
        assert response.status_code == 404


class UtilTest(unittest.TestCase):

    def setUp(self):
        appl = start_server(from_tests=True)
        self.app = appl.test_client()

    def test_ping(self):
        """
        Call utilities ping endpoint
        THEN check the response is success
        """
        response = self.app.get('/util/ping')
        assert response.status_code == 200

    def test_shotdown_throws_error(self):
        """
        Call shutdown endpoint
        localhost is not started raise error
        """
        response = self.app.get('/util/shutdown')
        assert response.status_code == 500


if __name__ == "__main__":
    unittest.main()