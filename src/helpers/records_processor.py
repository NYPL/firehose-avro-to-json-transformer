import avro
import base64
import json

from nypl_py_utils.functions.log_helper import create_log

class RecordsProcessor():
    def __init__(self):
        self.logger = create_log("records_processor")

    def decode_avro(self, type, data):
        decoded_data = base64.b64decode(data).decode("utf-8")
        try:
            return decoded_data["type"]
        except Exception as e:
            self.logger.error(f"Decoding fatal error occurred: {e}")
            return None

    # Map records to decode Avro and return data in desired output format to Firehose.
    def process_records(self, schema, records, output_format):
        successes, failures = 0, 0
        output = []

        type = avro.schema.parse(schema).type
        for record in records:
            decoded_data = self.decode_avro(type, record["data"])
            if decoded_data is None:
                # Unable to decode Avro record
                failures += 1
                output.append(json.dumps({
                                  "recordId": record["recordId"], 
                                  "result": "ProcessingFailed", 
                                  "data": record["data"]
                                  }))
            
            if (output_format == "csv"):
                for value in decoded_data.values():
                    output.append(value)



            output.append(decoded_data)
        self.logger.info(f"Processing completed.  Successful transformations -  ${successes}.  Failed transformations - ${failures}.")
        return output
