
import time
import argparse
import os
from mss import mss

import logging
logger = logging.getLogger('')
logger.setLevel(logging.INFO)

FPS_DEFAULT = 1
PATH_DEFAULT = "captures/"
MONITOR_DEFAULT = 1
SLEEP_DEFAULT = 0.01

parser = argparse.ArgumentParser(description='Take PNG screen captures with set FPS.')

parser.add_argument('--fps', type=int, default=FPS_DEFAULT,
                    help='Desired frames per second (real will be slightly lower, can be calculated from the timestamps of the captures).')
parser.add_argument('--path', type=str, default=PATH_DEFAULT,
                    help='Path where the captures will be saved.')
parser.add_argument('--monitor', type=int, default=MONITOR_DEFAULT,
                    help='Monitor which screen will be captured. Set to -1 to capture all monitors.')
parser.add_argument('--sleep', type=float, default=SLEEP_DEFAULT,
                    help='Advanced setting. Sleep amount in the loop. Higher values reduce the load on the CPU, while recuding the precision of the frame rate.')

def main(fps=FPS_DEFAULT, path=PATH_DEFAULT, monitor=MONITOR_DEFAULT, sleep=SLEEP_DEFAULT):
    _create_folder(path)
    _capture_loop(fps, path, monitor, sleep)

def _capture_loop(fps, path, monitor, sleep):
    logging.info(f"Capturing at {fps} FPS to {path}")
    period_sec = 1/fps
    prev = time.time()
    with mss() as sct:
        try:
            while True:
                now = time.time()
                if now - prev > period_sec:
                    sct.shot(mon=monitor, output=os.path.join(path,'{date:%Y-%m-%d %H-%M-%S.%f}.png'))
                    prev = now
                time.sleep(sleep)
        except KeyboardInterrupt:
            logging.info("Stopped.")

def _create_folder(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

            
if __name__ == "__main__":
    args = parser.parse_args()
    main(**vars(args))