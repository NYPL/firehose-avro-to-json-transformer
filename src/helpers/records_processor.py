import os
import avro
import json

import avro.schema
from nypl_py_utils.functions.log_helper import create_log
from nypl_py_utils.classes.avro_client import AvroDecoder


class RecordsProcessor:
    def __init__(self):
        self.logger = create_log("records_processor")
        self.avro_decoder = AvroDecoder(os.environ["NYPL_DATA_API_BASE_URL"])

    def _format_result_string(self, output_format, decoded_record):
        if output_format == "csv" and isinstance(decoded_record, dict):
            result_string, formatted_value = "", ""
            for value in decoded_record.values():
                if isinstance(value, str):
                    formatted_value = value.replace("|", "\\|")
                result_string += f"{formatted_value}|"
            return result_string[:-1] + "\n"
        else:
            return json.dumps(decoded_record["data"])

    def process_records(self, schema, records, output_format):
        """
        Map records to decoded Avro and return data in desired output
        format to Firehose.
        """
        successes, failures = 0, 0
        output = []
        type = avro.schema.parse(schema).type

        for record in records:
            decoded_record = self.avro_decoder.decode_record(record)

            if decoded_record is None:
                # Unable to decode Avro record
                failures += 1
                output.append(
                    json.dumps(
                        {
                            "recordId": record["recordId"],
                            "result": "ProcessingFailed",
                            "data": record["data"],
                        }
                    )
                )
            else:
                result_string = self._format_result_string(
                    output_format, decoded_record
                )
                successes += 1
                output.append(
                    json.dumps(
                        {
                            "recordId": record["recordId"],
                            "result": "Ok",
                            "data": result_string.encode("base64"),
                        }
                    )
                )
        self.logger.info(
            f"Processing completed.  Successful transformations -  ${successes}.  Failed transformations - ${failures}."
        )
        return output
