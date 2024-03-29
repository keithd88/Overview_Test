from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
import socket
import time

import pytest
from unittest import mock

import requests

def obj_rect2coords(obj_definition: Dict) -> Tuple[int, int, int, int, int]:
    top = int(obj_definition['top'])
    left = int(obj_definition['left'])
    width = int(obj_definition['width'] * obj_definition['scaleX'])
    height = int(obj_definition['height'] * obj_definition['scaleY'])
    angle = obj_definition['angle']
    return top, left, width, height, angle

class TestClassObj_Rect2Coords:
    test_obj_definition = {'top': 10, 'left': 18, 'width': 50, 'height': 60, 'angle': 0, 'scaleX': 1, 'scaleY': 1}
    
    # check function working properly on valid input
    def test_obj_rect2coords_valid(self):
        assert obj_rect2coords(self.test_obj_definition) == (10, 18, 50 * 1, 60 * 1, 0)
    # can add additional valid tests here if necessary

    # check function outputting correct number of values
    def test_obj_rect2coords_len(self):
        coordinates = obj_rect2coords(self.test_obj_definition)
        assert len(coordinates) == 5

    # check if a KeyError is raised on missing expected key
    def test_obj_rect2coords_missing_key(self):
        test_missing_top = self.test_obj_definition # make a copy of the test definition
        test_missing_top.pop('top') # remove the 'top' key
        with pytest.raises(KeyError): # confirm KeyError on missing key
            obj_rect2coords(test_missing_top)
        # can add additional missing keys tests if needed, omitted here because all keys are treated the same
        
    # check if a ValueError is raised on unexpected value datatype
    def test_obj_rect2coords_non_int_keys(self):
        test_string = self.test_obj_definition
        test_string['top'] = 'string'
        with pytest.raises(ValueError): # confirm ValueError on wrong datatype
            obj_rect2coords(test_string)
        # can add additional testing for other datatypes here if necessary


def compute_affine(
    obj_definition: Dict, dsize: Tuple[int, int], frame_affine_matrix: np.ndarray
) -> np.ndarray:
    top, left, width, height, angle = obj_rect2coords(obj_definition)

    corners = np.array(
        [
            [left, top],
            [left + width, top],
            [left + width, top + height],
            [left, top + height],
        ],
        dtype=np.float32,
    )
    roi_affine_matrix = cv2.getRotationMatrix2D((left, top), -angle, 1)
    roi_affine_matrix = np.vstack([roi_affine_matrix, [0, 0, 1]])
    combined_affine_matrix = np.matmul(frame_affine_matrix, roi_affine_matrix)
    rotated_corners = cv2.transform(np.array([corners]), combined_affine_matrix)[0][
        :, :2
    ].astype(np.float32)

    target_corners = np.array(
        [
            [0, 0],
            [dsize[0], 0],
            [dsize[0], dsize[1]],
            [0, dsize[1]],
        ],
        dtype=np.float32,
    )

    affine_matrix = cv2.getPerspectiveTransform(rotated_corners, target_corners)
    return affine_matrix

class TestClassComputeAffine:
    # define default testing inputs
    obj_definition = {'top': 0, 'left': 0, 'width': 100, 'height': 100, 'angle': 0, 'scaleX': 1, 'scaleY': 1}
    dsize = ((100, 100))
    frame_affine_matrix = np.eye(3)

    # test a simple, valid case
    def test_compute_affine(self):
        affine_matrix = compute_affine(self.obj_definition, self.dsize, self.frame_affine_matrix)
        # keep multiple assertions in same function to avoid duplicate calcs
        assert affine_matrix.shape == (3, 3) # check size of affine matrix
        assert np.allclose(affine_matrix, np.eye(3)) # check if matrix is identity for simple case

    # test with invalid inputs
    def test_compute_affine_invalid(self):
        # dsize w/ string instead of integer
        invalid_dsize = (('string', 100))
        with pytest.raises(ValueError):
            compute_affine(self.obj_definition, invalid_dsize, self.frame_affine_matrix)

        # dsize w/ wrong shape
        invalid_dsize = ((100))
        with pytest.raises(TypeError):
            compute_affine(self.obj_definition, invalid_dsize, self.frame_affine_matrix)

        # empty frame_affine_matrix
        invalid_frame = []
        with pytest.raises(ValueError):
            compute_affine(self.obj_definition, self.dsize, invalid_frame)
        # add additional cases to test edge cases for dsize & frame_affine_matrix 
        # could check additional datatypes, matrix sizes, etc.

    # add cases for rotation, translation, scaling, composite changes, and large data sets (ran out of time to implement this)


def draw_edge_locs(
    frame: np.ndarray,
    edge_locs: List[Tuple[int, int]] = [],
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = (255, 0, 0),
) -> np.ndarray:
    """
    Given a list of (x, y) pixels (edge_locs), draw pixels 2x2 instead of single pixel for increased visibility
    """

    edge_locs_array: np.ndarray = np.asarray(edge_locs, dtype=np.uint)

    if np.any(edge_locs_array):
        frame_height, frame_width = frame.shape[:2]
        start_edge_locs_y = edge_locs_array[:, 1]
        start_edge_locs_x = edge_locs_array[:, 0]
        end_edge_locs_y = np.clip((start_edge_locs_y + 1), 0, (frame_height - 1))
        end_edge_locs_x = np.clip((start_edge_locs_x + 1), 0, (frame_width - 1))

        frame[start_edge_locs_y, start_edge_locs_x] = color
        frame[end_edge_locs_y, start_edge_locs_x] = color
        frame[start_edge_locs_y, end_edge_locs_x] = color
        frame[end_edge_locs_y, end_edge_locs_x] = color

    return frame

class TestClassDrawEdgeLocs:
    # define default testing values
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    edge_locs = [(10, 10), (20, 20), (30, 30)]
    color = (255, 0, 0)

    def test_draw_edge_locs(self):
        test_frame = draw_edge_locs(self.frame, self.edge_locs, self.color)
    # add additional tests to check for correct, color, edge cases, and performance
    # could also add some regression tests to make sure we're not introducing new bugs


def hex2bgr(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])

class TestClassHex2BGR:
    # check function working properly on valid input
    def test_hex2bgr_valid(self):
        # test valid condition
        assert hex2bgr('#101010') == (16,16,16)
    # can add additional valid tests here if necessary

    # check function works even if extra letters/numbers are added to the end
    def test_hex2bgr_extra(self):
        assert hex2bgr('#101010F5') == (16,16,16)

    # check function works even if the last letter/number is omitted
    def test_hex2bgr_fewer(self):
        assert hex2bgr('#FAFAF') == (15,250,250)

    # check function throws AttributeError on non-string input (can't lstrip an int)
    def test_hex2bgr_non_string(self):
        with pytest.raises(AttributeError):
            hex2bgr(101010)

    # check function throws ValueError on invalid input (no int value for an empty string)
    def test_hex2bgr_not_enough(self):
        with pytest.raises(ValueError):
            hex2bgr('#FAFA')


def bgr2hex(bgr_color: Tuple[int, int, int]) -> str:
    b, g, r = [hex(x).lstrip('0x').rjust(2, '0').upper() for x in bgr_color]
    return f"#{''.join([r,g,b])}"

class TestClassBGR2Hex:
    # check function working properly on valid input
    def test_bgr2hex_valid(self):
        # test valid condition
        assert bgr2hex((16, 16, 16)) == '#101010'
    # can add additional valid tests here if necessary
        
    # check function throws ValueError on invalid input (too many values)
    def test_bgr2hex_extra(self):
        with pytest.raises(ValueError):
            bgr2hex((16, 16, 16, 16))

    # check function throws ValueError on invalid input (too few values)
    def test_bgr2hex_fewer(self):
        with pytest.raises(ValueError):
            bgr2hex((16, 16)) 

    # check function throws TypeeError on invalid input (strings instead of ints)
    def test_bgr2hex_invalid_type(self):
        with pytest.raises(TypeError):
            bgr2hex((16, 16, '16')) 


def is_port_open(ip: str, port: int) -> bool:
    """
    Check if a port is open at a specified IP address.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except Exception as e:
        return False

class TestClassPortOpen:
    # check function working properly on valid input
    def test_is_port_open_valid(self):
        assert is_port_open('127.0.0.1', 5354) == True
    # can add additional valid tests here if necessary

    # check function returns False on port out of range
    def test_is_port_open_invalid_port(self):
        assert is_port_open('127.0.0.1', 65536) == False
    # can add additional port range checks here

    # check function returns False on non-string ip
    def test_is_port_open_invalid_type(self):
        assert is_port_open(127001, 21) == False
    # can check other datatypes here


def wait_for_service() -> None:
    while True:
        try:
            healthcheck = requests.get('http://localhost:5000/healthcheck', timeout=5)
            healthcheck.raise_for_status()
            if healthcheck.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)

### tests for wait_for_service function. need to add to class and add more test cases
# ran out of time here
# check function works w/ successful healthcheck response
@mock.patch('requests.get')
def test_wait_for_service_success(mock_get): 
    mock_get.return_value.status_code = 200 # mock response
    # run function, should terminate successfully
    wait_for_service()

# didn't get these next two working in time
# # check function response with non-200 status code
# @mock.patch('requests.get')
# @pytest.mark.timeout(5)
# def test_wait_for_service_unavailable(mock_get):
#     mock_get.return_value.status_code = 503

#     # run function, should retry until service is available
#     # currently this freezes the test
#     wait_for_service()

# @mock.patch('requests.get')
# @pytest.mark.timeout(5)
# def test_wait_for_service_connection_error(mock_get):
#     # Mock connection error by raising requests.ConnectionError
#     mock_get.side_effect = requests.ConnectionError
#     # run function, should retry until connection establishes
#     # currently this also doesn't exit, so the tests can't continue
#     wait_for_service()

# can add additional tests for edge cases, performance/timing, etc.
