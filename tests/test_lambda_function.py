import lambda_function
import logging
import pytest

patron_info_processed_records = [
    {
        "recordId": "49546986683135544286507457936321625675700192471156785154",
        "result": "Ok",
        "data": "eyJwYXRyb25faWQiOiAicGF0cm9uLWlkLTEyMzQ1Njc4OTAiLCAiYWRkcmVzc19oYXNoIjogImFkZHJlc3MtaGFzaC0xMjM0NTY3ODkwIiwgInBvc3RhbF9jb2RlIjogIjU1NTU1IiwgImdlb2lkIjogIjEyMzQ1Njc4OTAxIiwgImNyZWF0aW9uX2RhdGVfZXQiOiAiMjAyMi0xMi0wMSIsICJkZWxldGlvbl9kYXRlX2V0IjogIjIwMjItMTItMDMiLCAiY2lyY19hY3RpdmVfZGF0ZV9ldCI6ICIyMDIyLTEyLTAyIiwgInB0eXBlX2NvZGUiOiAxMjMsICJwY29kZTMiOiA5ODcsICJwYXRyb25faG9tZV9saWJyYXJ5X2NvZGUiOiAibWEifQ==",
    },
    {
        "recordId": "49546986683135544286507457936321625675700192471156785154",
        "result": "Ok",
        "data": "eyJwYXRyb25faWQiOiAicGF0cm9uLWlkLTEyMzQ1Njc4OTEiLCAiYWRkcmVzc19oYXNoIjogImFkZHJlc3MtaGFzaC0xMjM0NTY3ODkxIiwgInBvc3RhbF9jb2RlIjogIjY2NjY2IiwgImdlb2lkIjogbnVsbCwgImNyZWF0aW9uX2RhdGVfZXQiOiAiMjAyMi0xMS0wMSIsICJkZWxldGlvbl9kYXRlX2V0IjogbnVsbCwgImNpcmNfYWN0aXZlX2RhdGVfZXQiOiAiMjAyMi0xMS0wMiIsICJwdHlwZV9jb2RlIjogNDU2LCAicGNvZGUzIjogNjU0LCAicGF0cm9uX2hvbWVfbGlicmFyeV9jb2RlIjogIm1hMiJ9",
    },
    {
        "recordId": "49546986683135544286507457936321625675700192471156785154",
        "result": "Ok",
        "data": "eyJwYXRyb25faWQiOiAicGF0cm9uLWlkLTEyMzQ1Njc4OTIiLCAiYWRkcmVzc19oYXNoIjogImFkZHJlc3MtaGFzaC0xMjM0NTY3ODkyIiwgInBvc3RhbF9jb2RlIjogbnVsbCwgImdlb2lkIjogbnVsbCwgImNyZWF0aW9uX2RhdGVfZXQiOiAiMjAyMi0xMC0wMSIsICJkZWxldGlvbl9kYXRlX2V0IjogbnVsbCwgImNpcmNfYWN0aXZlX2RhdGVfZXQiOiBudWxsLCAicHR5cGVfY29kZSI6IG51bGwsICJwY29kZTMiOiBudWxsLCAicGF0cm9uX2hvbWVfbGlicmFyeV9jb2RlIjogbnVsbH0=",
    },
]

circ_trans_processed_records =[
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


class TestLambdaFunction:
    @pytest.fixture
    def test_instance_3_success(self, mocker, test_data):
        mocker.patch("lambda_function.load_env_file")
        mock_record_processor = mocker.MagicMock()
        mock_record_processor.schema.return_value = test_data["PatronInfo"]
        mock_record_processor.process_record.side_effect = patron_info_processed_records
        mocker.patch(
            "lambda_function.RecordProcessor", return_value=mock_record_processor
        )
    
    @pytest.fixture
    def test_instance_2_success_1_failure(self, mocker, test_data):
        mocker.patch("lambda_function.load_env_file")
        mock_record_processor = mocker.MagicMock()
        mock_record_processor.schema.return_value = test_data["CircTrans"]
        mock_record_processor.process_record.side_effect = circ_trans_processed_records
        mocker.patch(
            "lambda_function.RecordProcessor", return_value=mock_record_processor
        )

    def test_lambda_handler_no_event_error(self, test_instance_3_success, caplog):
        with caplog.at_level(logging.ERROR):
            lambda_function.lambda_handler(None, None)
        assert "Event is undefined." in caplog.text

    def test_lambda_handler_no_event_records_exception(self, test_instance_3_success, caplog):
        event = {
            "invocationId": "invocationIdExample",
            "deliveryStreamArn": "deliveryExample",
            "sourceKinesisStreamArn": "streamExample",
            "region": "us-east-1",
        }
        with pytest.raises(lambda_function.RecordParsingError):
            (lambda_function.lambda_handler(event, None))
        assert "Error processing records: KeyError('records')" in caplog.text

    def test_lambda_handler_success(self, test_instance_3_success, test_data, caplog):
        event = test_data["patron_info_event"]
        assert lambda_function.lambda_handler(event, None) == {
            "records": patron_info_processed_records
        }
        assert (
            "Processing complete. Successful transformations - 3. Failed transformations - 0."
            in caplog.text
        )
        assert "Finished lambda processing." in caplog.text
    
    def test_lambda_handler_one_failure_two_success(self, test_instance_2_success_1_failure, mocker, test_data, caplog):
        event = test_data["patron_info_event"]
        assert lambda_function.lambda_handler(event, None) == {
            "records": circ_trans_processed_records
        }
        assert (
            "Processing complete. Successful transformations - 2. Failed transformations - 1."
            in caplog.text
        )
        assert "Finished lambda processing." in caplog.text
