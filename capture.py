
import time
import argparse
import os
from mss import mss

import logging
logger = logging.getLogger('')
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='Take PNG screen captures with set FPS.')

parser.add_argument('--fps', type=int, default=1,
                    help='Desired frames per second (real will be slightly lower, can be calculated from the timestamps of the captures).')
parser.add_argument('--path', type=str, default='captures/',
                    help='Path where the captures will be saved.')
parser.add_argument('--monitor', type=int, default=1,
                    help='Monitor which screen will be captured. Set to -1 to capture all monitors.')
parser.add_argument('--sleep', type=float, default=0.01,
                    help='Advanced setting. Sleep amount in the loop. Higher values reduce the load on the CPU, while recuding the precision of the frame rate.')

def capture_loop():
    logging.info(f"Capturing at {args.fps} FPS to {args.path}")
    prev = time.time()
    with mss() as sct:
        try:
            while True:
                now = time.time()
                if now - prev > period_sec:
                    sct.shot(mon=args.monitor, output=os.path.join(args.path,'{date:%Y-%m-%d %H-%M-%S.%f}.png'))
                    prev = now
                time.sleep(args.sleep)
        except KeyboardInterrupt:
            logging.info("Stopped.")
            
if __name__ == "__main__":
    args = parser.parse_args()
    period_sec = 1/args.fps
    try:
        os.mkdir(args.path)
    except FileExistsError:
        pass
    capture_loop()
