import base64
import csv
import io
import json

from nypl_py_utils.classes.avro_client import AvroDecoder
from nypl_py_utils.functions.log_helper import create_log


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
        binary_record_data = base64.b64decode(record["data"])
        decoded_record_data = self.avro_decoder.decode_record(
            binary_record_data)
        result_string = self._format_result_string(
            output_format, decoded_record_data
        )

        return {
            "recordId": record["recordId"],
            "result": "Ok",
            "data": result_string,  # needed for JSON conversion
        }

    def _format_result_string(self, output_format, data):
        if output_format == "csv" and isinstance(data, dict):
            data = self._transform_dictionary_to_csv_string(data)
        else:
            data = json.dumps(data)
        # We need to take original string ("data" ) and convert to hex,
        # which requires using bytes as an intermediate type
        to_bytes = data.encode("utf-8")
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
