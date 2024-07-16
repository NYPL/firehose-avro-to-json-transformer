import json
import os
import re

from nypl_py_utils.functions.log_helper import create_log
from nypl_py_utils.functions.config_helper import load_env_file
from record_processor import RecordProcessor


def lambda_handler(event, context):
    logger = create_log("lambda_function")
    load_env_file(os.environ["ENVIRONMENT"], "config/{}.yaml")

    logger.info("Starting event processing...")

    if event is None:
        logger.error("Event is undefined.")
        # TODO: raise exception here?
    else:
        # All records under one event will have the same schema
        schema_name = _pull_schema_name(event)
        os.environ["SCHEMA_NAME"] = schema_name
        schema_url = os.environ["NYPL_DATA_API_BASE_URL"] + f"/schemas/{schema_name}"
        output_format = "json" if schema_name != "LocationHours" else "csv"

        processor = RecordProcessor(schema_url)
        successes, failures = 0, 0
        processed_records = []

        try:
            for record in event["Records"]:
                if "data" in record:
                    result = processor.process_record(record, output_format)
                    if "ProcessingFailed" in result["result"]:
                        failures += 1
                    else:
                        successes += 1
                    processed_records.append(result)
        except Exception as e:
            # Catch any errors in the case event has no records, etc
            logger.error(f"Error processing records: {repr(e)}")
            raise RecordParsingError(e)

        logger.info(
            f"Processing complete. Successful transformations - {successes}. Failed transformations - {failures}."
        )

        logger.info("Finished lambda processing.")
        # TODO: What am I supposed to return????
        return {"statusCode": 200, "body": {"records": json.dumps(processed_records)}}


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
