import subprocess
import unittest
import requests
import time
import MySQLdb

class PredictorTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_put_ds_put_pred(self):
        PRED_NAME = 'test_predictor_name'
        DS_NAME = 'test_ds_name'
        DS_URL = 'https://raw.githubusercontent.com/mindsdb/mindsdb-examples/master/benchmarks/pulsar_stars/dataset/train.csv'

        # PUT datasource
        params = {
            'name': DS_NAME,
            'source_type': 'url',
            'source': DS_URL
        }
        url = 'http://{}:{}/datasources/put_datasource'.format('localhost', 47334)
        res = requests.put(url, json=params)
        print(res)
        assert res.status_code == 200

        # PUT predictor
        params = {
            'name': PRED_NAME,
            'data_source_name': DS_NAME,
            'to_predict': 'target_class'
        }
        url = 'http://{}:{}/predictors/put_predictor'.format('localhost', 47334)
        res = requests.put(url, json=params)
        assert res.status_code == 200
        time.sleep(50)

        # MySQL interface: check if table for the predictor exists
        '''
        DBNAME = 'mysql'

        con = MySQLdb.connect(
            host='127.0.0.1',
            port=3306,
            user='mindsdb',
            passwd='mindsdb',
            db='mindsdb'
        )

        cur = con.cursor()
        cur.execute("SELECT * FROM information_schema.tables WHERE table_schema = '{}' AND table_name = '{}' LIMIT 1;".format(DBNAME, PRED_NAME))
        assert cur.fetchall() == 1
        '''

        # HTTP clickhouse interface: try to make a prediction
        where = {
            'Mean_integrated': 140.5625,
            'Standard_integrated': 55.68378214,
            'Excess_kurtosis': -0.23457141199999998,
            'Skewness': -0.699648398,
            'Mean_DM-SNR': 3.199832776,
            'Standard_DM-SNR': 19.11042633,
            'kurtosis_DM-SNR': 7.975531794,
            'Skewness_DM-SNR': 74.24222492
        }

        query = "SELECT target_class FROM {} WHERE {} FORMAT JSON".format(
            PRED_NAME,
            'AND'.join('{} = {}'.format(k, v) for k, v in where.items())
        )

        res = requests.post('http://{}:{}'.format(
            CONFIG['api']['clickhouse']['host'],
            CONFIG['api']['clickhouse']['port']
        ), data=query)
        assert res.status_code == 200

        data = res.json()['data']
        assert 'target_class' in data and data['target_class'] is not None

'''
@TODO: Fix these
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
'''

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 47334
    sp = subprocess.Popen(['python3', '-m', 'mindsdb_server', '--api', 'mysql,http', '--config', 'mindsdb_server/default_config.json'])

    # less fancy
    try:
        time.sleep(12)
        unittest.main()

        '''
        t_0 = time.time()
        while True:
            try:
                res = requests.get('http://{}:{}/util/ping'.format(HOST, PORT), timeout=0.1)
                res.raise_for_status()
                unittest.main()
                break
            except requests.exceptions.ConnectionError:
                if (time.time() - t_0) > 15:
                    print('Failed to connect to server')
                    break
                time.sleep(1)
        '''
        print('Tests passed !')
    except:
        print('Tests Failed !')
        pass
    finally:
        print('Shutting Down Server !')
        time.sleep(2)
        sp.terminate()
