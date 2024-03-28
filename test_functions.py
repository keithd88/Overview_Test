import pytest

from functions import *

def test_obj_rect2coords():
    test_top = 10
    test_left = 18
    test_width = 50
    test_height = 60
    test_angle = 0
    test_scaleX = 1
    test_scaleY = 1
    test_obj_definition = {'top': test_top, 'left': test_left, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    
    test_missing_top = {'left': test_left, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    test_missing_left = {'top': test_top, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    test_missing_width = {'top': test_top, 'left': test_left, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    test_missing_height = {'top': test_top, 'left': test_left, 'width': test_width, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    test_missing_angle = {'top': test_top, 'left': test_left, 'width': test_width, 'height': test_height, 'scaleX': test_scaleX, 'scaleY': test_scaleY}
    test_missing_scaleX = {'top': test_top, 'left': test_left, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleY': test_scaleY}
    test_missing_scaleY = {'top': test_top, 'left': test_left, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX}
   
    test_string = {'top': 'string', 'left': test_left, 'width': test_width, 'height': test_height, 'angle': test_angle, 'scaleX': test_scaleX, 'scaleY': test_scaleY}


    # assert obj_rect2coords(test_obj_definition) == (test_top, test_left, test_width * test_scaleX, test_height * test_scaleY, test_angle)
    
    # confirm KeyError on missing key
    with pytest.raises(KeyError):
        obj_rect2coords(test_missing_top)

    # confirm ValueError on wrong datatype
    with pytest.raises(ValueError):
        obj_rect2coords(test_string)


def test_hex2bgr():
    # test valid condition
    assert hex2bgr('#101010') == (16,16,16)


def test_bgr2hex():
    # test valid condition
    assert bgr2hex((16, 16, 16)) == '#101010'


def test_is_port_open():
    # test with valid port
    assert is_port_open('127.0.0.1', 58146) == False

    # test with invalid port
    # assert is_port_open('192.168.1.1', 65536) == False

def test_wait_for_service():
    print()