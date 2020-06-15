import unittest
import requests
import os
import csv
import time

from mindsdb_server.interfaces.native.mindsdb import MindsdbNative
from mindsdb_server.utilities import config


test_csv = 'tests/home_rentals.csv'
test_data_table = 'home_rentals_400'
test_predictor_name = 'test_predictor_400'


def query_ch(query):
    if 'CREATE ' not in query.upper() and 'INSERT ' not in query.upper():
        query += ' FORMAT JSON'

    user = config['interface']['clickhouse']['user']
    password = config['interface']['clickhouse']['password']

    connect_string = '{}:{}'
    if user != 'default' or isinstance(password, str) and len(password) > 0:
        connect_string = f'{user}:{password}@' + connect_string

    res = requests.post(connect_string.format(
        'localhost',
        8123
    ), data=query)

    if ' FORMAT JSON' in query:
        res = res.json()['data']

    return res

class ClickhouseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mdb = MindsdbNative(config)

        if os.path.isfile(test_csv) is False:
            r = requests.get("https://s3.eu-west-2.amazonaws.com/mindsdb-example-data/home_rentals.csv")
            with open(test_csv, 'wb') as f:
                f.write(r.content)

        models = cls.mdb.get_models()
        models = [x['name'] for x in models]
        if test_predictor_name in models:
            cls.mdb.delete_model(test_predictor_name)

        query_ch('create database if not exists test')
        test_tables = query_ch('show tables from test')
        test_tables = [x['name'] for x in test_tables]
        if test_data_table not in test_tables:
            query_ch(f'''
                CREATE TABLE test.{test_data_table} (
                number_of_rooms Int8,
                number_of_bathrooms Int8,
                sqft Int32,
                location String,
                days_on_market Int16,
                initial_price Int32,
                neighborhood String,
                rental_price Int32
                ) ENGINE = TinyLog()
            ''')
            with open(test_csv) as f:
                csvf = csv.reader(f)
                i = 0
                for row in csvf:
                    if i > 0:
                        number_of_rooms = int(row[0])
                        number_of_bathrooms = int(row[1])
                        sqft = int(float(row[2].replace(',','.')))
                        location = str(row[3])
                        days_on_market = int(row[4])
                        initial_price = int(row[5])
                        neighborhood = str(row[6])
                        rental_price = int(float(row[7]))
                        query_ch(f'''INSERT INTO test.{test_data_table} VALUES (
                            {number_of_rooms},
                            {number_of_bathrooms},
                            {sqft},
                            '{location}',
                            {days_on_market},
                            {initial_price},
                            '{neighborhood}',
                            {rental_price}
                        )''')
                    i += 1

    def test_1_predictor_record_not_exists(self):
        print('Executing test 1')
        result = query_ch(f"select name from mindsdb.predictors where name='{test_predictor_name}'")
        self.assertTrue(len(result) == 0)
        print('Passed')

    def test_2_predictor_table_not_exists(self):
        print('Executing test 2')
        result = query_ch(f"show tables from mindsdb")
        result = [x['name'] for x in result]
        self.assertTrue(test_predictor_name not in result)
        print('Passed')

    def test_3_learn_predictor(self):
        print('Executing test 3')
        q = f"""
            insert into mindsdb.predictors
                (name, predict_cols, select_data_query)
            values
                ('{test_predictor_name}', 'rental_price', 'select * from test.{test_data_table} limit 100')
        """
        result = query_ch(q)

        # Here we should pool the status using mindsdb native or the http interface but whatever, for now sleep
        time.sleep(80)

        result = query_ch(f"select name from mindsdb.predictors where name='{test_predictor_name}'")
        self.assertTrue(len(result) == 1)

        result = query_ch(f"show tables from mindsdb")
        result = [x['name'] for x in result]
        self.assertTrue(test_predictor_name in result)

    def test_4_query(self):
        print('Executing test 4')
        result = query_ch(f"select rental_price from mindsdb.{test_predictor_name} where sqft=1000 and location='good'")
        self.assertTrue(len(result) == 1 and 'rental_price' in result[0])


if __name__ == "__main__":
    unittest.main()
