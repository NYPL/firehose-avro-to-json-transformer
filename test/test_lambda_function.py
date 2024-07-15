import lambda_function
import pytest

class TestLambdaFunction:
    @pytest.fixture
    def test_instance(self, mocker):
        mocker.patch("lambda_function.create_log")
        mocker.patch("nypl_py_utils.functions.config_helper.load_env_file")
        mock_records_processor = mocker.MagicMock()
        mocker.patch(
            "lambda_function.RecordsProcessor", return_value=mock_records_processor
        )

    def test_lambda_handler_success(self, mock_alarm_controller, mocker):
        assert True

    def test_lambda_handler_error(self, mock_alarm_controller, mocker):
        assert False