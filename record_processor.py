import base64
import csv
import io
import json

from nypl_py_utils.functions.log_helper import create_log
from nypl_py_utils.classes.avro_client import AvroDecoder


class RecordProcessor:
    def __init__(self, schema_url):
        self.logger = create_log("record_processor")
        self.avro_decoder = AvroDecoder(schema_url)
        self.schema = self.avro_decoder.get_json_schema(schema_url)

    def process_record(self, record, output_format):
        """
        Maps records to decoded Avro. Method returns data in
        desired output format for Firehose (JSON or CSV string)
        """
        binary_data = base64.b64decode(record["data"])
        decoded_record = self.avro_decoder.decode_record(binary_data)

        if decoded_record is None:
            # Unable to decode Avro record
            return {
                "recordId": record["recordId"],
                "result": "ProcessingFailed",
                "data": record["data"],
            }
        else:
            result_string = self._format_result_string(output_format, decoded_record)
            return {
                "recordId": record["recordId"],
                "result": "Ok",
                "data": result_string,  # needed for JSON conversion
            }

    def _format_result_string(self, output_format, decoded_record):
        if output_format == "csv" and isinstance(decoded_record, dict):
            decoded_record = self._transform_dictionary_to_csv_string(decoded_record)
        else:
            decoded_record = json.dumps(decoded_record)
        # After decoding, convert to base64. More often than not,
        # the original data is either encoded or not in base64
        to_bytes = decoded_record.encode("utf-8")
        return (base64.b64encode(to_bytes)).decode("utf-8")

    def _transform_dictionary_to_csv_string(self, data):
        # replace vertical bar within data
        output = io.StringIO()
        writer = csv.DictWriter(
            f=output,
            fieldnames=data.keys(),
            delimiter="|",
            quoting=csv.QUOTE_NONE,
            escapechar="\\",
        )
        writer.writerow(data)

        # remove carriage returns
        csv_string = output.getvalue()
        return csv_string.replace("\r", "")
