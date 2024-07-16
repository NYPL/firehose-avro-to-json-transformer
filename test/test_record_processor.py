import json
import logging
import pytest

from record_processor import RecordProcessor

decoded_records_json = [
    {
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
    },
    {
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
    },
]

decoded_records_csv = [
    {
        "drupal_location_id": "aa",
        "name": "Library A",
        "weekday": "Mon",
        "regular_open": "09:00",
        "regular_close": "17:00",
        "date_of_change": "2023-01-01",
    },
    {
        "drupal_location_id": "bb",
        "name": "Library B",
        "weekday": "Tue",
        "regular_open": None,
        "regular_close": None,
        "date_of_change": "2023-02-02",
    },
    {
        "drupal_location_id": "cc",
        "name": "Library | C !,=",
        "weekday": "Wed",
        "regular_open": "01:00",
        "regular_close": "23:00",
        "date_of_change": "2023-03-03",
    },
]


class TestRecordProcessor:
    @pytest.fixture
    def test_circ_trans_instance(self, mocker, test_data):
        mock_avro_decoder = mocker.MagicMock()
        mock_avro_decoder.get_json_schema.return_value = json.dumps(
            test_data["CircTrans"]
        )
        # Must decode second layer of encryption after decoing first layer of base64
        mock_avro_decoder.decode_record.side_effect = lambda x: {
            b"\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02,2017-11-14 11:43:49-05\x0csierra\nlocal\x02\x02o\x02\x12\x02,2017-12-05 04:00:00-05\x02\x00\x02\x94\x02\x02\x00\x02\x02-\x02\newa0n\x02\x00\x02\x0410\x02\x02-\x02\x02-\x02\x02\x02\x00\x02\new   \x02\x00\x02\x08": decoded_records_json[
                0
            ],
            b"\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02\xa0\x02\x02,2017-11-14 11:43:50-05\x0csierra\nlocal\x02\x02o\x02X\x02,2017-12-05 04:00:00-05\x02\x00\x02\x92\x03\x02\x00\x02\x02-\x02\nfwj0a\x02\x00\x02\x0460\x02\x02-\x02\x02r\x02\x04\x02\x00\x02\nfw   \x02\x00\x02\n": decoded_records_json[
                1
            ],
            b"\x96\x0b\x02H9a6fbbe9-bd10-4067-9fea-a0838de6c527\x02\x06715\x02\x1e234567890987654\x02\x1c32101096115215\x02\x06PUL\x00\x00\x0222017-10-04T16:41:25-04:00\x00": None,
        }[x]
        mocker.patch("record_processor.AvroDecoder", return_value=mock_avro_decoder)
        processor = RecordProcessor("https://test_schema_url")
        return processor

    @pytest.fixture
    def test_location_hours_instance(self, mocker, test_data):
        mock_avro_decoder = mocker.MagicMock()
        mock_avro_decoder.get_json_schema.return_value = json.dumps(
            test_data["LocationHours"]
        )
        # Must decode second layer of encryption after decoing first layer of base64
        mock_avro_decoder.decode_record.side_effect = lambda x: {
            b"\x00\x04aa\x02\x12Library A\x00\x06Mon\x02\n09:00\x02\n17:00\x02\x142023-01-01": decoded_records_csv[
                0
            ],
            b"\x00\x04bb\x02\x12Library B\x00\x06Tue\x00\x00\x02\x142023-02-02": decoded_records_csv[
                1
            ],
            b"\x00\x04cc\x02\x1eLibrary | C !,=\x00\x06Wed\x02\n01:00\x02\n23:00\x02\x142023-03-03": decoded_records_csv[
                2
            ],
        }[x]
        mocker.patch("record_processor.AvroDecoder", return_value=mock_avro_decoder)
        processor = RecordProcessor("https://test_schema_url")
        return processor

    def test_process_record_json_no_exception(
        self, test_data, test_circ_trans_instance, caplog
    ):
        valid_records = test_data["valid_records_json"]["records"]
        expected_processed_records = [
            {
                "recordId": "789",
                "result": "Ok",
                "data": "eyJpZCI6IDE0NCwgInBhdHJvbl9pZCI6IDE0NCwgIml0ZW1faWQiOiAxNDQsICJ2b2x1bWVfaWQiOiAxNDQsICJiaWJfaWQiOiAxNDQsICJ0cmFuc2FjdGlvbl9nbXQiOiAiMjAxNy0xMS0xNCAxMTo0Mzo0OS0wNSIsICJhcHBsaWNhdGlvbl9uYW1lIjogInNpZXJyYSIsICJzb3VyY2VfY29kZSI6ICJsb2NhbCIsICJvcF9jb2RlIjogIm8iLCAic3RhdF9ncm91cF9jb2RlX251bSI6IDksICJkdWVfZGF0ZV9nbXQiOiAiMjAxNy0xMi0wNSAwNDowMDowMC0wNSIsICJjb3VudF90eXBlX2NvZGVfbnVtIjogMCwgIml0eXBlX2NvZGVfbnVtIjogMTM4LCAiaWNvZGUxIjogMCwgImljb2RlMiI6ICItIiwgIml0ZW1fbG9jYXRpb25fY29kZSI6ICJld2EwbiIsICJpdGVtX2FnZW5jeV9jb2RlX251bSI6IDAsICJwdHlwZV9jb2RlIjogIjEwIiwgInBjb2RlMSI6ICItIiwgInBjb2RlMiI6ICItIiwgInBjb2RlMyI6IDEsICJwY29kZTQiOiAwLCAicGF0cm9uX2hvbWVfbGlicmFyeV9jb2RlIjogImV3ICAgIiwgInBhdHJvbl9hZ2VuY3lfY29kZV9udW0iOiAwLCAibG9hbnJ1bGVfY29kZV9udW0iOiA0fQ==",
            },
            {
                "recordId": "123",
                "result": "Ok",
                "data": "eyJpZCI6IDE0NCwgInBhdHJvbl9pZCI6IDE0NCwgIml0ZW1faWQiOiAxNDQsICJ2b2x1bWVfaWQiOiAxNDQsICJiaWJfaWQiOiAxNDQsICJ0cmFuc2FjdGlvbl9nbXQiOiAiMjAxNy0xMS0xNCAxMTo0Mzo1MC0wNSIsICJhcHBsaWNhdGlvbl9uYW1lIjogInNpZXJyYSIsICJzb3VyY2VfY29kZSI6ICJsb2NhbCIsICJvcF9jb2RlIjogIm8iLCAic3RhdF9ncm91cF9jb2RlX251bSI6IDQ0LCAiZHVlX2RhdGVfZ210IjogIjIwMTctMTItMDUgMDQ6MDA6MDAtMDUiLCAiY291bnRfdHlwZV9jb2RlX251bSI6IDAsICJpdHlwZV9jb2RlX251bSI6IDIwMSwgImljb2RlMSI6IDAsICJpY29kZTIiOiAiLSIsICJpdGVtX2xvY2F0aW9uX2NvZGUiOiAiZndqMGEiLCAiaXRlbV9hZ2VuY3lfY29kZV9udW0iOiAwLCAicHR5cGVfY29kZSI6ICI2MCIsICJwY29kZTEiOiAiLSIsICJwY29kZTIiOiAiciIsICJwY29kZTMiOiAyLCAicGNvZGU0IjogMCwgInBhdHJvbl9ob21lX2xpYnJhcnlfY29kZSI6ICJmdyAgICIsICJwYXRyb25fYWdlbmN5X2NvZGVfbnVtIjogMCwgImxvYW5ydWxlX2NvZGVfbnVtIjogNX0=",
            },
            {
                "recordId": "456",
                "result": "ProcessingFailed",
                "data": "lgsCSDlhNmZiYmU5LWJkMTAtNDA2Ny05ZmVhLWEwODM4ZGU2YzUyNwIGNzE1Ah4yMzQ1Njc4OTA5ODc2NTQCHDMyMTAxMDk2MTE1MjE1AgZQVUwAAAIyMjAxNy0xMC0wNFQxNjo0MToyNS0wNDowMAA=",
            },
        ]
        for i, record in enumerate(valid_records):
            assert (
                test_circ_trans_instance.process_record(record, "json")
                == expected_processed_records[i]
            )

    def test_process_records_csv_no_exception(
        self, test_data, test_location_hours_instance, caplog
    ):
        valid_records = test_data["valid_records_csv"]["records"]
        expected_processed_records = [
            {
                "recordId": "49546986683135544286507457936321625675700192471156785154",
                "result": "Ok",
                "data": "YWF8TGlicmFyeSBBfE1vbnwwOTowMHwxNzowMHwyMDIzLTAxLTAxCg==",
            },
            {
                "recordId": "49546986683135544286507457936321625675700192471156785154",
                "result": "Ok",
                "data": "YmJ8TGlicmFyeSBCfFR1ZXx8fDIwMjMtMDItMDIK",
            },
            {
                "recordId": "49546986683135544286507457936321625675700192471156785154",
                "result": "Ok",
                "data": "Y2N8TGlicmFyeSBcfCBDICEsPXxXZWR8MDE6MDB8MjM6MDB8MjAyMy0wMy0wMwo=",
            },
        ]

        for i, record in enumerate(valid_records):
            assert (
                test_location_hours_instance.process_record(record, "csv")
                == expected_processed_records[i]
            )

    def test_process_records_exception(
        self, test_data, test_circ_trans_instance, test_location_hours_instance
    ):
        invalid_records = test_data["invalid_records"]
        with pytest.raises(Exception):
            test_circ_trans_instance.process_records(invalid_records, "json")
            test_location_hours_instance.process_recordS(invalid_records, "csv")
