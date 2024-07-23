import json
import pytest

from record_processor import RecordProcessor

decoded_records_json = [
    {
        "patron_id": "abc1234567891011121314",
        "patron_retrieval_status": "found",
        "ptype_code": 123,
        "patron_home_library_code": "ma",
        "pcode3": 987,
        "postal_code": "55555",
        "geoid": None,
        "key": "123",
        "minutes_used": 12,
        "transaction_et": "2021-12-13",
        "branch": "branch abc",
        "area": "area 1",
        "staff_override": "StaffOverride",
    },
    {
        "patron_id": "abc123456789101112131415",
        "patron_retrieval_status": "missing",
        "ptype_code": None,
        "patron_home_library_code": None,
        "pcode3": None,
        "postal_code": None,
        "geoid": None,
        "key": "124",
        "minutes_used": 12,
        "transaction_et": "2021-12-14",
        "branch": "branch def",
        "area": "area 2",
        "staff_override": None,
    },
    {
        "patron_id": "abc12345678910111213141516",
        "patron_retrieval_status": "guest pass",
        "ptype_code": None,
        "patron_home_library_code": None,
        "pcode3": None,
        "postal_code": None,
        "geoid": None,
        "key": "125",
        "minutes_used": 15,
        "transaction_et": "2021-12-15",
        "branch": "branch ghi",
        "area": "area 3",
        "staff_override": None,
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
    def test_pc_reserve_instance(self, mocker, test_data):
        mock_avro_decoder = mocker.MagicMock()
        mock_avro_decoder.get_json_schema.return_value = json.dumps(
            test_data["PcReserve"]
        )
        # Must decode second layer of encryption after decoing first layer of base64
        mock_avro_decoder.decode_record.side_effect = lambda x: {
            b"\x00,abc1234567891011121314\x02\nfound\x02\xf6\x01\x02\x04ma\x02\xb6\x0f\x02\n55555\x00\x00\x06123\x02\x18\x02\x142021-12-13\x02\x14branch abc\x02\x0carea 1\x02\x1aStaffOverride": decoded_records_json[
                0
            ],
            b"\x000abc123456789101112131415\x02\x0emissing\x00\x00\x00\x00\x00\x00\x06124\x02\x18\x02\x142021-12-14\x02\x14branch def\x02\x0carea 2\x00": decoded_records_json[
                1
            ],
            b"\x004abc12345678910111213141516\x02\x14guest pass\x00\x00\x00\x00\x00\x00\x06125\x02\x1e\x02\x142021-12-15\x02\x14branch ghi\x02\x0carea 3\x00": decoded_records_json[
                2
            ],
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
        self, test_data, test_pc_reserve_instance, caplog):
        valid_records = test_data["valid_records_json"]["records"]
        expected_processed_records = [
            {
                "recordId": "123",
                "result": "Ok",
                "data": "eyJwYXRyb25faWQiOiAiYWJjMTIzNDU2Nzg5MTAxMTEyMTMxNCIsICJwYXRyb25fcmV0cmlldmFsX3N0YXR1cyI6ICJmb3VuZCIsICJwdHlwZV9jb2RlIjogMTIzLCAicGF0cm9uX2hvbWVfbGlicmFyeV9jb2RlIjogIm1hIiwgInBjb2RlMyI6IDk4NywgInBvc3RhbF9jb2RlIjogIjU1NTU1IiwgImdlb2lkIjogbnVsbCwgImtleSI6ICIxMjMiLCAibWludXRlc191c2VkIjogMTIsICJ0cmFuc2FjdGlvbl9ldCI6ICIyMDIxLTEyLTEzIiwgImJyYW5jaCI6ICJicmFuY2ggYWJjIiwgImFyZWEiOiAiYXJlYSAxIiwgInN0YWZmX292ZXJyaWRlIjogIlN0YWZmT3ZlcnJpZGUifQ==",
            },
            {
                "recordId": "456",
                "result": "Ok",
                "data": "eyJwYXRyb25faWQiOiAiYWJjMTIzNDU2Nzg5MTAxMTEyMTMxNDE1IiwgInBhdHJvbl9yZXRyaWV2YWxfc3RhdHVzIjogIm1pc3NpbmciLCAicHR5cGVfY29kZSI6IG51bGwsICJwYXRyb25faG9tZV9saWJyYXJ5X2NvZGUiOiBudWxsLCAicGNvZGUzIjogbnVsbCwgInBvc3RhbF9jb2RlIjogbnVsbCwgImdlb2lkIjogbnVsbCwgImtleSI6ICIxMjQiLCAibWludXRlc191c2VkIjogMTIsICJ0cmFuc2FjdGlvbl9ldCI6ICIyMDIxLTEyLTE0IiwgImJyYW5jaCI6ICJicmFuY2ggZGVmIiwgImFyZWEiOiAiYXJlYSAyIiwgInN0YWZmX292ZXJyaWRlIjogbnVsbH0=",
            },
            {
                "recordId": "789",
                "result": "Ok",
                "data": "eyJwYXRyb25faWQiOiAiYWJjMTIzNDU2Nzg5MTAxMTEyMTMxNDE1MTYiLCAicGF0cm9uX3JldHJpZXZhbF9zdGF0dXMiOiAiZ3Vlc3QgcGFzcyIsICJwdHlwZV9jb2RlIjogbnVsbCwgInBhdHJvbl9ob21lX2xpYnJhcnlfY29kZSI6IG51bGwsICJwY29kZTMiOiBudWxsLCAicG9zdGFsX2NvZGUiOiBudWxsLCAiZ2VvaWQiOiBudWxsLCAia2V5IjogIjEyNSIsICJtaW51dGVzX3VzZWQiOiAxNSwgInRyYW5zYWN0aW9uX2V0IjogIjIwMjEtMTItMTUiLCAiYnJhbmNoIjogImJyYW5jaCBnaGkiLCAiYXJlYSI6ICJhcmVhIDMiLCAic3RhZmZfb3ZlcnJpZGUiOiBudWxsfQ==",
            },
        ]
        for i, record in enumerate(valid_records):
            assert (
                test_pc_reserve_instance.process_record(record, "json")
                == expected_processed_records[i]
            )

    def test_process_records_csv_no_exception(
        self, test_data, test_location_hours_instance, caplog):
        valid_records = test_data["valid_records_csv"]["records"]
        expected_processed_records = [
            {
                "recordId": "123",
                "result": "Ok",
                "data": "YWF8TGlicmFyeSBBfE1vbnwwOTowMHwxNzowMHwyMDIzLTAxLTAxCg==",
            },
            {
                "recordId": "456",
                "result": "Ok",
                "data": "YmJ8TGlicmFyeSBCfFR1ZXx8fDIwMjMtMDItMDIK",
            },
            {
                "recordId": "789",
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
        self, test_data, test_pc_reserve_instance, test_location_hours_instance):
        invalid_records = test_data["invalid_records"]
        with pytest.raises(Exception):
            test_pc_reserve_instance.process_records(invalid_records, "json")
        with pytest.raises(Exception):
            test_location_hours_instance.process_records(invalid_records, "csv")
