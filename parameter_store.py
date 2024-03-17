import boto3
import logging


logging.basicConfig(level=logging.INFO)


def get_config_from_param_store(param_name: str, with_description: bool = True) -> str:
    logging.info(f"loading... get_config_from_param_store : {param_name}")
    region = boto3.session.Session().region_name
    ssm = boto3.client("ssm", region)
    parameter = ssm.get_parameter(Name=param_name, WithDecryption=with_description)

    return parameter["Parameter"]["Value"]


class SingletonInstance:
    __instance = None

    @classmethod
    def __get_instance(cls):
        return cls.__instance

    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__get_instance
        return cls.__instance


class AppConfig(SingletonInstance):
    def __init__(self):
        self.SECRET_KEY =  get_config_from_param_store(
             "/taf-application-back/jwt_secret_key"
         )
        self.PREDICTOR_BUCKET =  get_config_from_param_store(
             "/taf-application-back/s3/predictors"
         )
        self.DATASET_BUCKET =  get_config_from_param_store(
             "/taf-application-back/s3/datasets"
         )
        self.ENTRY_BUCKET =  get_config_from_param_store(
             "/taf-application-back/s3/entries"
         )
        self.LOCAL_ROOT =  get_config_from_param_store(
             "/taf-application-back/lambda/local_directory"
         )

app_config = AppConfig()