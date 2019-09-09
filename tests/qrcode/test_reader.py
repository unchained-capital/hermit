from unittest.mock import patch
import unittest

from PIL import Image
import numpy as np
import pytest

import hermit


@pytest.fixture()
def opensource_bitcoin_vector_array():
    return np.load('tests/fixtures/opensource_bitcoin_test_vector_0.npy')


@pytest.fixture()
def opensource_bitcoin_vector_0_image():
    return Image.open('tests/fixtures/opensource_bitcoin_test_vector_0.png')


class TestReadQRCode(object):

    @patch('hermit.qrcode.reader.cv2')
    def test_cannot_open_camera_is_error(self, mock_cv2):
        mock_cv2.VideoCapture().isOpened.return_value = False
        with pytest.raises(IOError) as e_info:
            hermit.qrcode.reader._start_camera()
        assert str(e_info.value) == "Cannot open webcam"

    @patch('hermit.qrcode.reader.cv2')
    @patch('hermit.qrcode.reader.window_is_open')
    # @unittest.skip("TODO: fix this broken test!")
    def test_valid_qr_code(self,
                           mock_window_is_open,
                           mock_cv2,
                           fixture_opensource_bitcoin_vector_0,
                           opensource_bitcoin_vector_0_image):
        request_json = fixture_opensource_bitcoin_vector_0['request_json']
        mock_cv2.VideoCapture().read.return_value = (
            None, np.array(opensource_bitcoin_vector_0_image))
        mock_cv2.resize.return_value = opensource_bitcoin_vector_0_image
        mock_window_is_open.return_value = True
        data = hermit.qrcode.read_qr_code()
        assert data == request_json
        mock_cv2.imshow.assert_called_once()
        mock_cv2.namedWindow.assert_called_once()
        mock_cv2.destroyWindow.assert_called_once()
        assert True

    # @patch('hermit.qrcode.reader.cv2')
    # def test_q_breaks_reader_after_loop(self,
    #                                     mock_cv2):
    #     mock_cv2.VideoCapture().read.return_value = (None, None)
    #     mock_cv2.waitKey.side_effect = [0, 113]
    #     mock_cv2.resize.return_value = np.zeros((800, 800))
    #     hermit.qrcode.read_qr_code()
    #     assert mock_cv2.imshow.call_count == 2
    #     mock_cv2.namedWindow.assert_called_once()
    #     mock_cv2.destroyWindow.assert_called_once()
    #     assert True
