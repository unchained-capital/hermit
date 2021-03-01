import asyncio
import json
from unittest.mock import patch

import numpy as np
import pytest
import qrcode

import hermit


@pytest.fixture()
def too_large_bitcoin_signature_request():
    filename = "tests/fixtures/too_large_bitcoin_signature_request.json"
    with open(filename, "r") as f:
        request = json.load(f)
    return json.dumps(request)


@pytest.fixture()
def largest_bitcoin_signature_request():
    filename = "tests/fixtures/largest_bitcoin_signature_request.json"
    with open(filename, "r") as f:
        request = json.load(f)
    return json.dumps(request)


@pytest.fixture()
def opensource_bitcoin_vector_0_array():
    return np.load("tests/fixtures/opensource_bitcoin_test_vector_0.npy")


class TestDisplayQRCode(object):
    @patch("hermit.qrcode.displayer.cv2")
    @patch("hermit.qrcode.displayer.window_is_open")
    async def test_valid_qr_code(
        self,
        mock_window_is_open,
        mock_cv2,
        fixture_opensource_bitcoin_vectors,
        opensource_bitcoin_vector_0_array,
    ):
        request_json = fixture_opensource_bitcoin_vectors["request_json"]
        mock_window_is_open.return_value = True
        future = hermit.qrcode.display_qr_code(request_json)
        await future
        mock_cv2.imshow.assert_called_once()
        call_args = mock_cv2.imshow.call_args
        assert call_args[0][0] == "Preview"
        expected_arg = opensource_bitcoin_vector_0_array
        assert np.array_equal(call_args[0][1], expected_arg)

    # @patch('hermit.qrcode.displayer.cv2')
    # @patch('hermit.qrcode.displayer.window_is_open')
    # def test_task_ends_when_window_closed(self,
    #                                       mock_window_is_open,
    #                                       mock_cv2,
    #                                       fixture_opensource_bitcoin_vector_0):
    #     request_json = fixture_opensource_bitcoin_vector_0['request_json']
    #     mock_window_is_open.return_value = True
    #     future = hermit.qrcode.display_qr_code(request_json)

    #     mock_cv2.destroyWindow.assert_called_once()

    # @patch('hermit.qrcode.displayer.cv2')
    # def test_task_ends_when_q_is_pressed(self,
    #                                      mock_cv2,
    #                                      fixture_opensource_bitcoin_vector_0):
    #     request_json = fixture_opensource_bitcoin_vector_0['request_json']
    #     mock_cv2.waitKey.side_effect = [-1, 113]
    #     future = hermit.qrcode.display_qr_code(request_json)
    #     asyncio.get_event_loop().run_until_complete(future)
    #     mock_cv2.destroyWindow.assert_called_once()


class TestCreateQRCode(object):

    # using gzip, we can store between 50-55 inputs in one qrcode
    #
    # See Version 40:
    # http://www.qrcode.com/en/about/version.html
    def test_fifty_five_inputs_fails(self, too_large_bitcoin_signature_request):
        with pytest.raises(qrcode.exceptions.DataOverflowError):
            hermit.qrcode.create_qr_code_image(too_large_bitcoin_signature_request)

    def test_fifty_inputs_passes(self, largest_bitcoin_signature_request):
        hermit.qrcode.create_qr_code_image(largest_bitcoin_signature_request)
        assert True
