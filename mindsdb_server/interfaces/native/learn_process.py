import torch.multiprocessing as mp


ctx = mp.get_context('spawn')
class LearnProcess(ctx.Process):
    daemon = True

    def __init__(self, *args):
        super(LearnProcess, self).__init__(args=args)

    def run(self):
        '''
        running at subprocess due to
        ValueError: signal only works in main thread

        this is work for celery worker here?
        '''
        import sys
        import mindsdb
        import lightwood

        from mindsdb_server.utilities.config import Config

        name, from_data, to_predict, kwargs, config = self._args
        config = Config(config)

        mdb = mindsdb.Predictor(name=name)
        if sys.platform not in ['win32','cygwin','windows']:
            lightwood.config.config.CONFIG.HELPER_MIXERS = True

        data_source = getattr(mindsdb, from_data['class'])(*from_data['args'], **from_data['kwargs'])

        mdb.learn(
            from_data=data_source,
            to_predict=to_predict,
            use_gpu=self.config.get('use_gpu', False),
            **kwargs
        )

        stats = mdb.get_model_data()['data_analysis_v2']

        try:
            assert(config['interface']['clickhouse']['enabled'] == True)
            from mindsdb_server.interfaces.clickhouse.clickhouse import Clickhouse
            clickhouse = Clickhouse(config)
            clickhouse.register_predictor(name, stats)
        except:
            pass
