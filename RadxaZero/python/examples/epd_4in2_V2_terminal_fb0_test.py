#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
import time
import hashlib
from PIL import Image, ImageChops, ImageOps

# --- Setup Paths ---
# Assumes this script is in RadxaZero/python/examples/
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd4in2_V2

# --- Configuration ---
FB_W, FB_H = 1024, 768  # Your detected Radxa resolution (adjust if different)
EPD_W, EPD_H = 400, 300 # Waveshare 4.2" V2 resolution

logging.basicConfig(level=logging.INFO)

# --- Blind Mode Override ---
# User reported BUSY pin (10) is stuck Low. We override ReadBusy to avoid hanging.
class EPD_Blind(epd4in2_V2.EPD):
    def ReadBusy(self):
        logging.debug("Blind mode: Ignoring BUSY pin state, sleeping briefly.")
        # Sleep a bit to ensure the controller processes the command.
        # Partial updates are fast, but we need some delay.
        time.sleep(0.05)

def get_frame_hash(data):
    return hashlib.md5(data).hexdigest()

try:
    logging.info("Initializing E-ink (Blind Mode)...")
    epd = EPD_Blind()
    epd.init_fast(epd.Seconds_1_5S) 
    
    # Clear screen first to ensure clean state
    # epd.Clear() # Optional: Clear() takes a while (full refresh)
    
    last_hash = None
    last_image = None
    
    logging.info("Starting framebuffer capture loop...")
    while True:
        try:
            # 1. Grab pixels from the system's hidden screen
            # Adjust /dev/fb0 if your framebuffer is elsewhere
            with open("/dev/fb0", "rb") as f:
                # Read enough bytes for the whole framebuffer
                # 32-bit color = 4 bytes per pixel
                raw_data = f.read(FB_W * FB_H * 4)
            
            # Convert raw bytes to Image
            full_img = Image.frombytes('RGB', (FB_W, FB_H), raw_data, 'raw', 'BGRX')
            
            # Crop to the top-left corner
            # Convert to 'L' (grayscale) first to allow inversion, then invert, then convert to '1'
            terminal_view = full_img.crop((0, 0, EPD_W, EPD_H)).convert('L')
            terminal_view = ImageOps.invert(terminal_view)
            terminal_view = terminal_view.convert('1')

            # Calculate hash based on the visible cropped area
            curr_hash = get_frame_hash(terminal_view.tobytes())

            # 2. Only update the e-ink if the visible area changed
            if curr_hash != last_hash:
                if last_image is not None:
                    diff = ImageChops.difference(last_image, terminal_view)
                    bbox = diff.getbbox()
                    if bbox:
                        logging.info(f"Change detected in region: {bbox}")
                
                # 3. Push to physical screen using Partial Refresh
                # Note: display_Partial handles the "TurnOnDisplay_Partial" command
                epd.display_Partial(epd.getbuffer(terminal_view))
                
                last_hash = curr_hash
                last_image = terminal_view
                logging.info("E-ink Updated (Partial).")

            # Check for changes periodically
            time.sleep(0.1)

        except IOError as e:
            logging.error(f"Error reading framebuffer: {e}")
            time.sleep(1)
        
except KeyboardInterrupt:
    logging.info("Exiting...")
    # epd.sleep() # Avoid sleep() if it hangs on Busy or if we want to keep the image
    epd4in2_V2.epdconfig.module_exit()
    exit()
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    epd4in2_V2.epdconfig.module_exit()
    exit()