from main import forecasting
# local python script equivalent to AWS Lambda function call


event = {
  "predictor_id": "<ticker>/<predictor>",
  "gluonts_dataset_id": "<ticker>/<dataset>.json",
}

forecasting(event=event, context=None)