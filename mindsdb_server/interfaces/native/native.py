# Mindsdb native interface
import mindsdb


def train():
    pass

def predict():
    pass

def analyze():
    metapredictor = Predictor.name('metapredictor')
    pass

def get_model_data():
    metapredictor = Predictor.name('metapredictor')
    pass

def get_models(status='any'):
    metapredictor = Predictor.name('metapredictor')
    models = metapredictor.get_models()
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
