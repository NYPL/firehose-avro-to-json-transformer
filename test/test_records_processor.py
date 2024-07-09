import json
import logging
import pytest

from records_processor import RecordsProcessor

response1 = {
    "id": 144,
    "patron_id": 144,
    "item_id": 144,
    "volume_id": 144,
    "bib_id": 144,
    "transaction_gmt": "2017-11-14 11:43:49-05",
    "application_name": "sierra",
    "source_code": "local",
    "op_code": "o",
    "stat_group_code_num": 9,
    "due_date_gmt": "2017-12-05 04:00:00-05",
    "count_type_code_num": 0,
    "itype_code_num": 138,
    "icode1": 0,
    "icode2": "-",
    "item_location_code": "ewa0n",
    "item_agency_code_num": 0,
    "ptype_code": "10",
    "pcode1": "-",
    "pcode2": "-",
    "pcode3": 1,
    "pcode4": 0,
    "patron_home_library_code": "ew   ",
    "patron_agency_code_num": 0,
    "loanrule_code_num": 4,
}
response2 = {
    "id": 144,
    "patron_id": 144,
    "item_id": 144,
    "volume_id": 144,
    "bib_id": 144,
    "transaction_gmt": "2017-11-14 11:43:50-05",
    "application_name": "sierra",
    "source_code": "local",
    "op_code": "o",
    "stat_group_code_num": 44,
    "due_date_gmt": "2017-12-05 04:00:00-05",
    "count_type_code_num": 0,
    "itype_code_num": 201,
    "icode1": 0,
    "icode2": "-",
    "item_location_code": "fwj0a",
    "item_agency_code_num": 0,
    "ptype_code": "60",
    "pcode1": "-",
    "pcode2": "r",
    "pcode3": 2,
    "pcode4": 0,
    "patron_home_library_code": "fw   ",
    "patron_agency_code_num": 0,
    "loanrule_code_num": 5,
}


class TestRecordsProcessor:
    @pytest.fixture
    def valid_records_json(self, test_data):
        return test_data["valid_records_json"]

    @pytest.fixture
    def invalid_records_json(self, test_data):
        return test_data["invalid_records_json"]
    
    @pytest.fixture
    def valid_records_csv(self, test_data):
        return test_data["valid_records_csv"]

    @pytest.fixture
    def test_circ_trans_instance(
        self, mocker, test_data, valid_records_json, invalid_records_json):
        mock_avro_decoder = mocker.MagicMock()
        mock_avro_decoder.get_json_schema.return_value = json.dumps(
            test_data["CircTrans"]
        )
        mock_avro_decoder.decode_record.side_effect = lambda x: {
            valid_records_json["records"][0]["data"]: response1,
            valid_records_json["records"][1]["data"]: response2,
            valid_records_json["records"][2]["data"]: None,
            invalid_records_json["records"][0]["data"]: None,
        }[x]
        mocker.patch("records_processor.AvroDecoder", return_value=mock_avro_decoder)
        processor = RecordsProcessor("https://test_schema_url")
        return processor
    
    @pytest.fixture
    def test_location_hours_instance(
        self, mocker, test_data, valid_records_json, invalid_records_json):
        mock_avro_decoder = mocker.MagicMock()
        mock_avro_decoder.get_json_schema.return_value = json.dumps(
            test_data["LocationHours"]
        )
        # mock_avro_decoder.decode_record.side_effect = lambda x: {
        #     valid_records["records"][0]["data"]: response1,
        #     valid_records["records"][1]["data"]: response2,
        #     valid_records["records"][2]["data"]: None,
        #     invalid_records["records"][0]["data"]: None,
        # }[x]
        mocker.patch("records_processor.AvroDecoder", return_value=mock_avro_decoder)
        processor = RecordsProcessor("https://test_schema_url")
        return processor

    def test_process_records_json_no_exception(
        self, test_circ_trans_instance, valid_records_json, caplog):
        expected_processed_records = '[{"recordId": "789", "result": "Ok", "data": "eyJpZCI6IDE0NCwgInBhdHJvbl9pZCI6IDE0NCwgIml0ZW1faWQiOiAxNDQsICJ2b2x1bWVfaWQiOiAxNDQsICJiaWJfaWQiOiAxNDQsICJ0cmFuc2FjdGlvbl9nbXQiOiAiMjAxNy0xMS0xNCAxMTo0Mzo0OS0wNSIsICJhcHBsaWNhdGlvbl9uYW1lIjogInNpZXJyYSIsICJzb3VyY2VfY29kZSI6ICJsb2NhbCIsICJvcF9jb2RlIjogIm8iLCAic3RhdF9ncm91cF9jb2RlX251bSI6IDksICJkdWVfZGF0ZV9nbXQiOiAiMjAxNy0xMi0wNSAwNDowMDowMC0wNSIsICJjb3VudF90eXBlX2NvZGVfbnVtIjogMCwgIml0eXBlX2NvZGVfbnVtIjogMTM4LCAiaWNvZGUxIjogMCwgImljb2RlMiI6ICItIiwgIml0ZW1fbG9jYXRpb25fY29kZSI6ICJld2EwbiIsICJpdGVtX2FnZW5jeV9jb2RlX251bSI6IDAsICJwdHlwZV9jb2RlIjogIjEwIiwgInBjb2RlMSI6ICItIiwgInBjb2RlMiI6ICItIiwgInBjb2RlMyI6IDEsICJwY29kZTQiOiAwLCAicGF0cm9uX2hvbWVfbGlicmFyeV9jb2RlIjogImV3ICAgIiwgInBhdHJvbl9hZ2VuY3lfY29kZV9udW0iOiAwLCAibG9hbnJ1bGVfY29kZV9udW0iOiA0fQ=="}, {"recordId": "123", "result": "Ok", "data": "eyJpZCI6IDE0NCwgInBhdHJvbl9pZCI6IDE0NCwgIml0ZW1faWQiOiAxNDQsICJ2b2x1bWVfaWQiOiAxNDQsICJiaWJfaWQiOiAxNDQsICJ0cmFuc2FjdGlvbl9nbXQiOiAiMjAxNy0xMS0xNCAxMTo0Mzo1MC0wNSIsICJhcHBsaWNhdGlvbl9uYW1lIjogInNpZXJyYSIsICJzb3VyY2VfY29kZSI6ICJsb2NhbCIsICJvcF9jb2RlIjogIm8iLCAic3RhdF9ncm91cF9jb2RlX251bSI6IDQ0LCAiZHVlX2RhdGVfZ210IjogIjIwMTctMTItMDUgMDQ6MDA6MDAtMDUiLCAiY291bnRfdHlwZV9jb2RlX251bSI6IDAsICJpdHlwZV9jb2RlX251bSI6IDIwMSwgImljb2RlMSI6IDAsICJpY29kZTIiOiAiLSIsICJpdGVtX2xvY2F0aW9uX2NvZGUiOiAiZndqMGEiLCAiaXRlbV9hZ2VuY3lfY29kZV9udW0iOiAwLCAicHR5cGVfY29kZSI6ICI2MCIsICJwY29kZTEiOiAiLSIsICJwY29kZTIiOiAiciIsICJwY29kZTMiOiAyLCAicGNvZGU0IjogMCwgInBhdHJvbl9ob21lX2xpYnJhcnlfY29kZSI6ICJmdyAgICIsICJwYXRyb25fYWdlbmN5X2NvZGVfbnVtIjogMCwgImxvYW5ydWxlX2NvZGVfbnVtIjogNX0="}, {"recordId": "456", "result": "ProcessingFailed", "data": "lgsCSDlhNmZiYmU5LWJkMTAtNDA2Ny05ZmVhLWEwODM4ZGU2YzUyNwIGNzE1Ah4yMzQ1Njc4OTA5ODc2NTQCHDMyMTAxMDk2MTE1MjE1AgZQVUwAAAIyMjAxNy0xMC0wNFQxNjo0MToyNS0wNDowMAA="}]'
        assert (
            test_circ_trans_instance.process_records(valid_records_json, "json")
            == expected_processed_records
        )
        assert (
            "Processing complete. Successful transformations - 2. Failed transformations - 1."
            in caplog.text
        )

    def test_process_records_json_exception(
        self, test_circ_trans_instance, invalid_records_json, caplog):
        with pytest.raises(Exception) and caplog.at_level(logging.INFO):
            test_circ_trans_instance.process_records(
                invalid_records_json, "json"
            )
        assert (
            "Processing complete. Successful transformations - 0. Failed transformations - 1."
            in caplog.text
        )

    def test_process_records_csv_no_exception(self, test_location_hours_instance, valid_records_csv):
        # expected_processed_records = {'drupal_location_id': 'aa', 'name': 'Library A', 'weekday': 'Mon', 'regular_open': '09:00', 'regular_close': '17:00', 'date_of_change': '2023-01-01'}
        # number2 = {'drupal_location_id': 'bb', 'name': 'Library B', 'weekday': 'Tue', 'regular_open': None, 'regular_close': None, 'date_of_change': '2023-02-02'}
        # number3 = {'drupal_location_id': 'cc', 'name': 'Library | C !,=', 'weekday': 'Wed', 'regular_open': '01:00', 'regular_close': '23:00', 'date_of_change': '2023-03-03'}
        result = test_location_hours_instance.process_records(valid_records_csv, "csv")
        return True
