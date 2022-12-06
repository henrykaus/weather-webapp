model_backend = 'datastore'

if model_backend == 'datastore':
    from .model_datastore import Model
else:
    raise ValueError("No appropriate databackend configured.")

appmodel = Model()

def get_model():
    return appmodel
