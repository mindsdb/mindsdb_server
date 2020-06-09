import unittest
from mindsdb_server import __main__


class PredictorTest(unittest.TestCase):

    def setUp(self):
        pass
        #__main__()

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

    def test_analyse_invalid_datasource(self):
        """
        Don't provide datasource
        then check the response is No valid datasource given
        """
        response = self.app.get('/predictors/dummy_predictor/analyse_dataset')
        assert response.status_code == 400

    def test_analyse_valid_datasource(self):
        """
        Add valid datasource as parameter
        then check the response is 200
        """
        from_data = 'https://raw.githubusercontent.com/mindsdb/mindsdb-examples/master/benchmarks/heart_disease/processed_data/train.csv'
        response = self.app.get('/predictors/dummy_predictor/analyse_dataset?from_data='+ from_data)
        assert response.status_code == 200

class DatasourceTest(unittest.TestCase):

    def setUp(self):
        pass
        #__main__()

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
        pass
        #__main__()

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
