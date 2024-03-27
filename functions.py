from typing import Dict, List, Tuple, Union

import cv2
import numpy as np
import socket
import time

import requests

def obj_rect2coords(obj_definition: Dict) -> Tuple[int, int, int, int, int]:
    top = int(obj_definition['top'])
    left = int(obj_definition['left'])
    width = int(obj_definition['width'] * obj_definition['scaleX'])
    height = int(obj_definition['height'] * obj_definition['scaleY'])
    angle = obj_definition['angle']
    return top, left, width, height, angle

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

def hex2bgr(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])


def bgr2hex(bgr_color: Tuple[int, int, int]) -> str:
    b, g, r = [hex(x).lstrip('0x').rjust(2, '0').upper() for x in bgr_color]
    return f"#{''.join([r,g,b])}"

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

def wait_for_service() -> None:
    while True:
        try:
            healthcheck = requests.get('http://localhost:5000/healthcheck', timeout=5)
            healthcheck.raise_for_status()
            if healthcheck.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
