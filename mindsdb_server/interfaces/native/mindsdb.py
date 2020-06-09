# Mindsdb native interface
import sys
import mindsdb
import lightwood
from multiprocessing import Process
from dateutil.parser import parse as parse_datetime


class MindsdbNative():
    def __init__(self, config):
        self.config = config
        self.metapredictor = mindsdb.Predictor('metapredictor')
        self.register_to = []

        try:
            assert(config['interface']['clickhouse']['enabled'] == True)
            from mindsdb_server.interfaces.clickhouse.clickhouse import Clickhouse
            self.register_to.append(Clickhouse(self.config))
        except:
            pass

    def _learn(self, name, from_data, to_predict, kwargs):
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
            **kwargs
        )

        stats = mdb.get_model_data()['data_analysis_v2']
        for entity in self.register_to:
            register_func = getattr(entity,register_predictor)
            register_func(name, stats)


    def learn(self, name, from_data, to_predict, kwargs={}):
        p = Process(target=self._learn, args=(name, from_data, to_predict, kwargs))
        p.start()

    def predict(self, name, when=None, when_data=None, kwargs={}):
        mdb = mindsdb.Predictor(name=name)

        if when is not None:
            predictions = mdb.predict(when=when, run_confidence_variation_analysis=True, **kwargs)
        else:
            predictions = mdb.predict(when_data=when_data, run_confidence_variation_analysis=True, **kwargs)

        return predictions

    def analyse_dataset(self, ds):
        return self.metapredictor.analyse_dataset(ds, sample_margin_of_error=0.025)

    def get_model_data(self, name):
        return self.metapredictor.get_model_data(name)

    def get_models(self, status='any'):
        models = self.metapredictor.get_models()
        models = [x for x in models if x['name'] != 'metapredictor']
        if status != 'any':
            models = [x for x in models if x['status'] == status]

        for i in range(len(models)):
            for k in ['train_end_at', 'updated_at', 'created_at']:
                if k in models[i] and models[i][k] is not None:
                    try:
                        models[i][k] = parse_datetime(str(models[i][k]).split('.')[0])
                    except Exception as e:
                        models[i][k] = parse_datetime(str(models[i][k]))
        return models

    def delete_model(self, name):
        self.metapredictor.delete_model(name)

    def rename_model(self, name, new_name):
        self.metapredictor.rename_model(name, new_name)

    def load_model(self, fpath):
        self.metapredictor.load_model(model_archive_path=fpath)

    def export_model(self,name):
        self.metapredictor.export_model(model_name=name)
