import lambda_function
import logging
import pytest


class TestLambdaFunction:
    @pytest.fixture
    def test_instance(self, mocker):
        mocker.patch("lambda_function.load_env_file")
        mock_record_processor = mocker.MagicMock()
        mocker.patch(
            "lambda_function.RecordProcessor", return_value=mock_record_processor
        )

    def test_lambda_handler_no_event_exception(self, test_instance, caplog):
        with caplog.at_level(logging.ERROR):
            lambda_function.lambda_handler(None, None)
        assert "Event is undefined." in caplog.text

    def test_lambda_handler_no_event_records_exception(self, test_instance, caplog):
        event = {
            "invocationId": "invocationIdExample",
            "deliveryStreamArn": "deliveryExample",
            "sourceKinesisStreamArn": "streamExample",
            "region": "us-east-1",
            "records": [],
        }

        with pytest.raises(Exception):
            (lambda_function.lambda_handler(event, None))
        assert "Error processing records: KeyError('Records')" in caplog.text

    # def test_lambda_handler_error(self, test_instance, mocker):
    #     assert False
