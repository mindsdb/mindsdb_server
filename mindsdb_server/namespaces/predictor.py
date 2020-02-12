import copy
import os
import shutil
import sys
import time
from io import BytesIO
from multiprocessing import Process

import mindsdb
import lightwood
from dateutil.parser import parse as parse_datetime
from flask import request, send_file
from flask_restplus import Resource, abort

from mindsdb_server.namespaces.configs.predictors import ns_conf
from mindsdb_server.namespaces.datasource import get_datasource
from mindsdb_server.namespaces.entitites.predictor_metadata import (
    predictor_metadata,
    predictor_query_params,
    upload_predictor_params,
    put_predictor_params
)
from mindsdb_server.namespaces.entitites.predictor_status import predictor_status
from mindsdb_server.shared_ressources import get_shared

app, api = get_shared()
global_mdb = mindsdb.Predictor(name='metapredictor')
model_swapping_map = {}


def debug_pkey_type(model, keys=None, reset_keyes=True, type_to_check=list, append_key=True):
    if type(model) != dict:
        return
    for k in model:
        if reset_keyes:
            keys = []
        if type(model[k]) == dict:
            keys.append(k)
            debug_pkey_type(model[k], copy.deepcopy(keys), reset_keyes=False)
        if type(model[k]) == type_to_check:
            print(f'They key {keys}->{k} has type list')
        if type(model[k]) == list:
            for item in model[k]:
                debug_pkey_type(item, copy.deepcopy(keys), reset_keyes=False)


def preparse_results(results, format_flag='explain'):
    response_arr = []

    for res in results:
        if format_flag == 'explain':
            response_arr.append(res.explain())
        elif format_flag == 'epitomize':
            response_arr.append(res.epitomize())
        elif format_flag == 'new_explain':
            response_arr.append(results.explanation)
        else:
            response_arr.append(res.explain())

    if len(response_arr) > 0:
        return response_arr
    else:
        abort(400, "")


def get_datasource_path(data_source_name):
    if data_source_name:
        ds = get_datasource(data_source_name)
        if ds and ds['source']:
            if ds['source_type'] == 'url':
                return ds['source']
            if ds['source_type'] == 'file':
                return os.path.normpath(os.path.abspath(ds['source']))
    return None


@ns_conf.route('/')
class PredictorList(Resource):
    @ns_conf.doc('list_predictors')
    @ns_conf.marshal_list_with(predictor_status, skip_none=True)
    def get(self):
        global global_mdb
        '''List all predictors'''
        models = global_mdb.get_models()
        good_modles = []

        for model in models:
            # model['data_source'] = model['data_source'].split('/')[-1]
            for k in ['train_end_at', 'updated_at', 'created_at']:
                if k in model and model[k] is not None:
                    try:
                        model[k] = parse_datetime(str(model[k]).split('.')[0])
                    except Exception as e:
                        model[k] = parse_datetime(str(model[k]))

            if 'name' in model:
                if 'metapredictor' not in model['name']:
                    good_modles.append(model)

        return good_modles


@ns_conf.route('/<name>')
@ns_conf.param('name', 'The predictor identifier')
@ns_conf.response(404, 'predictor not found')
class Predictor(Resource):
    @ns_conf.doc('get_predictor')
    @ns_conf.marshal_with(predictor_metadata, skip_none=True)
    def get(self, name):
        global global_mdb
        model = global_mdb.get_model_data(name)

        for k in ['train_end_at', 'updated_at', 'created_at']:
            if k in model and model[k] is not None:
                model[k] = parse_datetime(model[k])

        return model

    @ns_conf.doc('delete_predictor')
    def delete(self, name):
        '''Remove predictor'''
        global global_mdb
        global_mdb.delete_model(name)
        return '', 200

    @ns_conf.doc('put_predictor', params=put_predictor_params)
    def put(self, name):
        '''Learning new predictor'''
        global model_swapping_map
        global global_mdb

        data = request.json
        to_predict = data.get('to_predict')

        try:
            kwargs = data.get('kwargs')
        except:
            kwargs = None

        if type(kwargs) != type({}):
            kwargs = {}

        if 'stop_training_in_x_seconds' not in kwargs:
            kwargs['stop_training_in_x_seconds'] = 3600

        if 'equal_accuracy_for_all_output_categories' not in kwargs:
            kwargs['equal_accuracy_for_all_output_categories'] = True

        if 'sample_margin_of_error' not in kwargs:
            kwargs['sample_margin_of_error'] = 0.005

        if 'unstable_parameters_dict' not in kwargs:
            kwargs['unstable_parameters_dict'] = {}

        if 'use_selfaware_model' not in kwargs['unstable_parameters_dict']:
            kwargs['unstable_parameters_dict']['use_selfaware_model'] = False


        try:
            ignore_columns = data.get('ignore_columns')
        except:
            ignore_columns = []

        if type(ignore_columns) != type([]):
            ignore_columns = []

        try:
            retrain = data.get('retrain')
            if retrain in ('true', 'True'):
                retrain = True
            else:
                retrain = False
        except:
            retrain = None

        from_data = get_datasource_path(data.get('data_source_name'))
        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        if name is None or to_predict is None:
            abort(400, "name, to_predict are required")

        if retrain is True:
            original_name = name
            name = name + '_retrained'

        def learn(name, from_data, to_predict, ignore_columns, kwargs):
            '''
            running at subprocess due to
            ValueError: signal only works in main thread

            this is work for celery worker here?
            '''
            mdb = mindsdb.Predictor(name=name)
            if sys.platform not in ['win32','cygwin','windows']:
                lightwood.config.config.CONFIG.HELPER_MIXERS = True

            mdb.learn(
                from_data=from_data,
                to_predict=to_predict,
                ignore_columns=ignore_columns,
                **kwargs
            )

        if sys.platform == 'linux':
            p = Process(target=learn, args=(name, from_data, to_predict, ignore_columns, kwargs))
            p.start()
        else:
            learn(name, from_data, to_predict, ignore_columns, kwargs)

        if retrain is True:
            try:
                model_swapping_map[original_name] = True
                global_mdb.delete_model(original_name)
                global_mdb.rename_model(name, original_name)
                model_swapping_map[original_name] = False
            except:
                model_swapping_map[original_name] = False

        return '', 200

@ns_conf.route('/<name>/analyse_dataset')
@ns_conf.param('name', 'The predictor identifier')
class AnalyseDataset(Resource):
    @ns_conf.doc('analyse_dataset')
    def get(self, name):
        from_data = get_datasource_path(request.args.get('data_source_name'))
        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            print('No valid datasource given')
            return 'No valid datasource given', 400

        analysis = global_mdb.analyse_dataset(from_data, sample_margin_of_error=0.025)

        return analysis, 200



@ns_conf.route('/<name>/columns')
@ns_conf.param('name', 'The predictor identifier')
class PredictorColumns(Resource):
    @ns_conf.doc('get_predictor_columns')
    def get(self, name):
        '''List of predictors colums'''
        global global_mdb
        model = global_mdb.get_model_data(name)

        columns = []
        for array, is_target_array in [(model['data_analysis']['target_columns_metadata'], True),
                                       (model['data_analysis']['input_columns_metadata'], False)]:
            for col_data in array:
                column = {
                    'name': col_data['column_name'],
                    'data_type': col_data['data_type'].lower(),
                    'is_target_column': is_target_array
                }
                if column['data_type'] == 'categorical':
                    column['distribution'] = col_data["data_distribution"]["data_histogram"]["x"]
                columns.append(column)

        return columns, 200


@ns_conf.route('/<name>/predict')
@ns_conf.param('name', 'The predictor identifier')
class PredictorPredict(Resource):
    @ns_conf.doc('post_predictor_predict', params=predictor_query_params)
    def post(self, name):
        '''Queries predictor'''
        global model_swapping_map

        when = request.json.get('when') or {}

        try:
            format_flag = data.get('format_flag')
        except:
            format_flag = 'explain'

        # Not the fanciest semaphor, but should work since restplus is multi-threaded and this condition should rarely be reached
        while name in model_swapping_map and model_swapping_map[name] is True:
            time.sleep(1)

        mdb = mindsdb.Predictor(name=name)
        results = mdb.predict(when=when, run_confidence_variation_analysis=True)
        # return '', 500
        return preparse_results(results, format_flag)


@ns_conf.route('/<name>/predict_datasource')
@ns_conf.param('name', 'The predictor identifier')
class PredictorPredictFromDataSource(Resource):
    @ns_conf.doc('post_predictor_predict', params=predictor_query_params)
    def post(self, name):
        global model_swapping_map

        data = request.json

        from_data = get_datasource_path(data.get('data_source_name'))
        try:
            format_flag = data.get('format_flag')
        except:
            format_flag = 'explain'

        try:
            kwargs = data.get('kwargs')
        except:
            kwargs = {}

        if from_data is None:
            from_data = data.get('from_data')
        if from_data is None:
            from_data = data.get('when_data')
        if from_data is None:
            abort(400, 'No valid datasource given')

        # Not the fanciest semaphor, but should work since restplus is multi-threaded and this condition should rarely be reached
        while name in model_swapping_map and model_swapping_map[name] is True:
            time.sleep(1)

        mdb = mindsdb.Predictor(name=name)
        try:
            results = mdb.predict(when_data=from_data, **kwargs)
        except:
            results = mdb.predict(when=from_data, **kwargs)

        return preparse_results(results, format_flag)


@ns_conf.route('/upload')
class PredictorUpload(Resource):
    @ns_conf.doc('predictor_query', params=upload_predictor_params)
    def post(self):
        '''Upload existing predictor'''
        global global_mdb
        predictor_file = request.files['file']
        fpath = os.path.join(mindsdb.CONFIG.MINDSDB_TEMP_PATH, 'new.zip')
        with open(fpath, 'wb') as f:
            f.write(predictor_file.read())

        global_mdb.load_model(model_archive_path=fpath)
        try:
            os.remove(fpath)
        except Exception:
            pass

        return '', 200


@ns_conf.route('/<name>/download')
@ns_conf.param('name', 'The predictor identifier')
class PredictorDownload(Resource):
    @ns_conf.doc('get_predictor_download')
    def get(self, name):
        '''Export predictor to file'''
        global global_mdb
        global_mdb.export_model(model_name=name)
        fname = name + '.zip'
        original_file = os.path.join(fname)
        fpath = os.path.join(mindsdb.CONFIG.MINDSDB_TEMP_PATH, fname)
        shutil.move(original_file, fpath)

        with open(fpath, 'rb') as f:
            data = BytesIO(f.read())

        try:
            os.remove(fpath)
        except Exception:
            pass

        return send_file(
            data,
            mimetype='application/zip',
            attachment_filename=fname,
            as_attachment=True
        )
