import json
import pandas as pd
import numpy as np
from gluonts.evaluation import make_evaluation_predictions
from gluonts.dataset.common import ListDataset


def gluonts_dataset_sample(
    custom_series,
    n_time=10,
    prediction_length:int =10,
    freq='1D'
    ):
    start = pd.Period(custom_series.index[0], freq=freq)
    custom_ds = np.tile(custom_series.values.flatten(), (n_time, 1))
    train_ds = ListDataset(
        [
            {'target': x, "start": start} for x in custom_ds[:, :-prediction_length]
        ],
        freq=freq
    )
    test_ds = ListDataset(
        [
            {"target": x, "start": start} for x in custom_ds
        ], freq=freq
    )
    return train_ds, test_ds

def dataset_decoder(json_object, freq='h'):
  deserialized = json.loads(json_object)
  for data in deserialized:
    data['target'] = np.array(data['target'])
    data['start'] = pd.Period(data['start'], freq=freq)
  return deserialized

def entry_encoder(forecast_entry):
  dict_ = {
    "forecast_arrays": forecast_entry.forecast_array.tolist(),
    "start_date": str(forecast_entry.start_date.to_timestamp()),
    "forecast_keys": forecast_entry.forecast_keys,
    "item_id": forecast_entry.item_id,
    "info": forecast_entry.info
  }
  return json.dumps(dict_)

def gluonts_predict(predictor, test_ds):
  forecast_it, ts_it = make_evaluation_predictions(
      dataset=test_ds,  # test dataset
      predictor=predictor,  # predictor
      num_samples=len(test_ds),  # number of sample paths we want for evaluation
  )
  forecasts = list(forecast_it)
  tss = list(ts_it)
  return forecasts, tss