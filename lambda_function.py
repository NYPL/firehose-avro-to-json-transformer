import os

from nypl_py_utils.functions.log_helper import create_log
from nypl_py_utils.functions.config_helper import load_env_file

def lambda_handler(event, context):
    logger = create_log("lambda_function")
    load_env_file(os.environ["ENVIRONMENT"], "config/{}.yaml")

    logger.info("Starting event processing...")

    records = event["Records"]
    if (event is not None) and (records is list) and (len(records) > 0):
        # ^ TODO: this is gross
        schema_name = pull_schema_name(event)
        output_format = "json" if schema_name != "LocationHours" else "csv"

        if ("data" in records[0]):
            os.environ["SCHEMA_NAME"] = schema_name
            os.environ["OUTPUT_FORMAT"] = output_format
        else:
            logger.error("Event contains no records.")
    else:
        logger.error("Event is undefined.")
            
def pull_schema_name(event):
    """Given a Firehouse event, pulls encoded schema type from stream ARN.
    Example input -- "arn:aws:kinesis:us-east-1:946183545209:stream/PcReserve-production"
    Example output -- "PcReserve"
    """
    return (
        event["sourceKinesisStreamArn"]
        .split(":")
        .pop()
        .replace("^stream/", "")
        .replace("-[a-z]+$", "")
        # Against convention, the "CircTransAnon" stream contains "CircTrans"
        # encoded records, so ensure the correct schema name is chosen:
        .replace("^CircTransAnon$", "CircTrans")
    )
