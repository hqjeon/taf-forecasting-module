import os
import json
import shutil
import botocore
from pathlib import Path
from parameter_store import app_config
from utils.install_utils import inline_install
from utils.exceptions import exception_handler
from utils.s3_utils import download_dir, get_object, put_object_contents

inline_install(["gluonts", "gluonts-0.14.4.dist-info", "mxnet", "mxnet-1.7.0.post2.dist-info"])
from gluonts.model.predictor import Predictor
from utils.gluonts_utils import gluonts_predict, dataset_decoder, entry_encoder


def forecasting(event, context):
    # get predictor_id & gluonts_dataset_id from request body
    try:
        forecasting_data = event
        if forecasting_data is None:
            raise Exception("ForecastingDataNotProvided")
        predictor_id = forecasting_data.get("predictor_id", None)
        gluonts_dataset_id = forecasting_data.get("gluonts_dataset_id", None)
        if predictor_id is None:
            raise Exception("PredictorIdNotProvided")
        if gluonts_dataset_id is None:
            raise Exception("DatasetIdNotProvided")
    except Exception as e:
            return exception_handler(e)
    
    # load dataset from s3
    try:
        s3_dataset = get_object(gluonts_dataset_id, bucket_name=app_config.DATASET_BUCKET)
    except botocore.exceptions.ClientError as e:
        return exception_handler(e)
    except botocore.exceptions.ParamValidationError as e:
        return exception_handler(e)
    gluonts_dataset = dataset_decoder(s3_dataset["Body"].read())

    # download directory containing predictor parameters from s3 
    ticker_key, predictor_key = predictor_id.split('/')
    local_dir = download_dir(ticker_key, bucket_name=app_config.PREDICTOR_BUCKET)

    # get predicotr from parameters
    predictor_deserialized = Predictor.deserialize(Path(local_dir + '/' + predictor_key))

    # perform forecasting inference & delete local directory containing predictor parameters
    forecasts, _ = gluonts_predict(predictor_deserialized, gluonts_dataset)
    shutil.rmtree(local_dir)

    # upload forecast result to s3
    forecast_entry = forecasts[0]
    forecast_entry_id = gluonts_dataset_id.replace(".json", f"/{predictor_key}.json")
    try:
        put_object_contents(entry_encoder(forecast_entry), forecast_entry_id, bucket_name=app_config.ENTRY_BUCKET)
        return {"statusCode": 200, "result": {"gluonts_dataset_id": forecast_entry_id}}
    except botocore.exceptions.ClientError as e:
        return exception_handler(e)