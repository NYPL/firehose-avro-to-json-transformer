import json
import os
import re

from nypl_py_utils.functions.log_helper import create_log
from nypl_py_utils.functions.config_helper import load_env_file
from records_processor import RecordsProcessor


def lambda_handler(event):
    logger = create_log("lambda_function")
    load_env_file(os.environ["ENVIRONMENT"], "config/{}.yaml")

    logger.info("Starting event processing...")

    if event is not None:
        records = event["Records"]
        schema_name = _pull_schema_name(event)
        output_format = "json" if schema_name != "LocationHours" else "csv"
        if (records is list) and (len(records) > 0) and ("data" in records[0]):
            os.environ["SCHEMA_NAME"] = schema_name
            try:
                schema_url = (
                    os.environ["NYPL_DATA_API_BASE_URL"] + f"/schemas/{schema_name}"
                )
                processor = RecordsProcessor(schema_url)
                processor.process_records(records, output_format)
            except Exception as e:
                logger.error(f"Error processing records: {e}")
                raise e
        else:
            logger.error("Event contains no records.")
    else:
        logger.error("Event is undefined.")
    
    logger.info("Finished lambda processing.")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Job ran successfully."
        })
    }


def _pull_schema_name(event):
    """Given a Firehouse event, pulls encoded schema type from stream ARN.
    Example input -- "arn:aws:kinesis:us-east-1:946183545209:stream/PcReserve-production"
    Example output -- "PcReserve"
    """
    filtered_for_stream_name = event["sourceKinesisStreamArn"].split(":").pop()
    # Against convention, the "CircTransAnon" stream contains "CircTrans"
    # encoded records, so ensure the correct schema name is chosen
    replacements = [
        ("^stream/", ""),
        ("-[a-z]+$", ""),
        ("^CircTransAnon$", "CircTrans"),
    ]

    for old, new in replacements:
        filtered_for_stream_name = re.sub(old, new, filtered_for_stream_name)
    return filtered_for_stream_name


class RecordParsingError(Exception):
    def __init__(self, message=None):
        self.message = message
