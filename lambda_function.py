import os
import re

from nypl_py_utils.functions.config_helper import load_env_file
from nypl_py_utils.functions.log_helper import create_log
from record_processor import RecordProcessor


def lambda_handler(event, context):
    logger = create_log("lambda_function")
    if os.environ["ENVIRONMENT"] == "devel":
        load_env_file(os.environ["ENVIRONMENT"], "config/{}.yaml")

    logger.info("Starting event processing...")

    if event is None:
        logger.error("Event is undefined.")
        raise RecordParsingError("No event found.")
    else:
        # All records under one event will have the same schema
        schema_name = _pull_schema_name(
            event["sourceKinesisStreamArn"])
        schema_url = (
            os.environ["NYPL_DATA_API_BASE_URL"] + "current-schemas/" + f"{schema_name}"
        )
        output_format = "json" if schema_name != "LocationHours" else "csv"

        processor = RecordProcessor(schema_url)
        successes, failures = 0, 0
        processed_records = []

        try:
            # In case of key capitalization
            lowercase_event = {k.lower(): v for k, v in event.items()}

            for record in lowercase_event["records"]:
                if "data" in record:
                    result = processor.process_record(record, output_format)
                    if "ProcessingFailed" in result["result"]:
                        logger.error(
                            f"Error processing record data: {result}")
                        failures += 1
                    else:
                        successes += 1
                    processed_records.append(result)
        except Exception as e:
            # Catch any errors in the case the event has no records, etc
            raise RecordParsingError(e)

        logger.info(
            f"Processing complete. Successful transformations - {successes}. Failed transformations - {failures}."
        )

        logger.info("Finished lambda processing.")
        return {"records": processed_records}


def _pull_schema_name(stream_arn):
    """
    Given a Firehose event's stream ARN, pulls encoded schema type.
    Example input -- "arn:aws:kinesis:us-east-1:946183545209:stream/PcReserve-production"
    Example output -- "PcReserve"
    """
    filtered_for_stream_name = stream_arn.split(":").pop()
    replacements = [
        ("^stream/", ""),
        ("-[a-z]+$", "")
    ]

    for old, new in replacements:
        filtered_for_stream_name = re.sub(
            old, new, filtered_for_stream_name)
    return filtered_for_stream_name


class RecordParsingError(Exception):
    def __init__(self, message=None):
        self.message = message
