# Mindsdb native interface
import mindsdb
from dateutil.parser import parse as parse_datetime

from mindsdb_server.interfaces.native.learn_process import LearnProcess


class MindsdbNative():
    def __init__(self, config):
        self.config = config
        self.metapredictor = mindsdb.Predictor('metapredictor')
        self.unregister_from = []

        try:
            from mindsdb_server.interfaces.clickhouse.clickhouse import Clickhouse
            self.unregister_from.append(Clickhouse(self.config))
        except:
            pass

        try:
            assert(config['integrations']['mariadb']['enabled'] == True)
            from mindsdb_server.interfaces.mariadb.mariadb import Mariadb
            self.unregister_from.append(Mariadb(self.config))
        except:
            pass

    def learn(self, name, from_data, to_predict, kwargs={}):
        p = LearnProcess(name, from_data, to_predict, kwargs, self.config.get_all())
        p.start()

    def predict(self, name, when=None, when_data=None, kwargs={}):
        mdb = mindsdb.Predictor(name=name)

        use_gpu = self.config.get('use_gpu', False)
        if when is not None:
            predictions = mdb.predict(
                when=when,
                run_confidence_variation_analysis=True,
                use_gpu=use_gpu,
                **kwargs
            )
        else:
            predictions = mdb.predict(
                when_data=when_data,
                run_confidence_variation_analysis=False,
                use_gpu=use_gpu,
                **kwargs
            )

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
        for entity in self.unregister_from:
            unregister_func = getattr(entity, 'unregister_predictor')
            unregister_func(name)

    def rename_model(self, name, new_name):
        self.metapredictor.rename_model(name, new_name)

    def load_model(self, fpath):
        self.metapredictor.load_model(model_archive_path=fpath)

    def export_model(self,name):
        self.metapredictor.export_model(model_name=name)
