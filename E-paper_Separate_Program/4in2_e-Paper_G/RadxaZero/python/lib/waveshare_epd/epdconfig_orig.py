# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.2
# * | Date        :   2022-10-29
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import logging
import sys
import time
import subprocess

from ctypes import *

logger = logging.getLogger(__name__)


class RaspberryPi:
    # Pin definition
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18
    MOSI_PIN = 10
    SCLK_PIN = 11

    def __init__(self):
        import spidev
        import gpiozero
        
        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN    = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN     = gpiozero.LED(self.DC_PIN)
        # self.GPIO_CS_PIN     = gpiozero.LED(self.CS_PIN)
        self.GPIO_PWR_PIN    = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN   = gpiozero.Button(self.BUSY_PIN, pull_up = False)

        

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            if value:
                self.GPIO_RST_PIN.on()
            else:
                self.GPIO_RST_PIN.off()
        elif pin == self.DC_PIN:
            if value:
                self.GPIO_DC_PIN.on()
            else:
                self.GPIO_DC_PIN.off()
        # elif pin == self.CS_PIN:
        #     if value:
        #         self.GPIO_CS_PIN.on()
        #     else:
        #         self.GPIO_CS_PIN.off()
        elif pin == self.PWR_PIN:
            if value:
                self.GPIO_PWR_PIN.on()
            else:
                self.GPIO_PWR_PIN.off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        elif pin == self.RST_PIN:
            return self.RST_PIN.value
        elif pin == self.DC_PIN:
            return self.DC_PIN.value
        # elif pin == self.CS_PIN:
        #     return self.CS_PIN.value
        elif pin == self.PWR_PIN:
            return self.PWR_PIN.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        print(f"spi_writebyte2: {data}")
        self.SPI.writebytes2(data)

    def DEV_SPI_write(self, data):
        self.DEV_SPI.DEV_SPI_SendData(data)

    def DEV_SPI_nwrite(self, data):
        self.DEV_SPI.DEV_SPI_SendnData(data)

    def DEV_SPI_read(self):
        return self.DEV_SPI.DEV_SPI_ReadData()

    def module_init(self, cleanup=False):
        self.GPIO_PWR_PIN.on()
        
        if cleanup:
            find_dirs = [
                os.path.dirname(os.path.realpath(__file__)),
                '/usr/local/lib',
                '/usr/lib',
            ]
            self.DEV_SPI = None
            for find_dir in find_dirs:
                val = int(os.popen('getconf LONG_BIT').read())
                logging.debug("System is %d bit"%val)
                if val == 64:
                    so_filename = os.path.join(find_dir, 'DEV_Config_64.so')
                else:
                    so_filename = os.path.join(find_dir, 'DEV_Config_32.so')
                if os.path.exists(so_filename):
                    self.DEV_SPI = CDLL(so_filename)
                    break
            if self.DEV_SPI is None:
                RuntimeError('Cannot find DEV_Config.so')

            self.DEV_SPI.DEV_Module_Init()

        else:
            # SPI device, bus = 0, device = 0
            self.SPI.open(0, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_PWR_PIN.off()
        logger.debug("close 5V, Module enters 0 power consumption ...")
        
        if cleanup:
            self.GPIO_RST_PIN.close()
            self.GPIO_DC_PIN.close()
            # self.GPIO_CS_PIN.close()
            self.GPIO_PWR_PIN.close()
            self.GPIO_BUSY_PIN.close()

        




class RadxaZeroGPIOD:
    # Absolute Linux GPIO numbers (for role matching only)
    DC_PIN   = 560   # GPIOC_7
    RST_PIN  = 585   # GPIOX_8
    BUSY_PIN = 587   # GPIOX_10
    CS_PIN   = 534   # GPIOH_6

    CHIP_NAME = os.environ.get("EPD_GPIOCHIP", "gpiochip0")

    # Offsets (gpiochip0 starts at 512)
    OFFSET_DC   = int(os.environ.get("EPD_DC_OFFSET", "48"))
    OFFSET_RST  = int(os.environ.get("EPD_RST_OFFSET", "73"))
    OFFSET_BUSY = int(os.environ.get("EPD_BUSY_OFFSET", "75"))
    OFFSET_CS   = int(os.environ.get("EPD_CS_OFFSET", "22"))

    OFFSET_MOSI = int(os.environ.get("EPD_MOSI_OFFSET", "20"))
    OFFSET_SCLK = int(os.environ.get("EPD_SCLK_OFFSET", "23"))

    OFFSET_PWR = os.environ.get("EPD_PWR_OFFSET")
    PWR_ACTIVE_HIGH = os.environ.get("EPD_PWR_ACTIVE_HIGH", "1") == "1"

    def __init__(self):
        import spidev
        import gpiod

        self.spidev = spidev
        self.gpiod = gpiod
        self.SPI = spidev.SpiDev()

        self._chip = None
        self._line_dc = None
        self._line_rst = None
        self._line_busy = None
        self._line_cs = None
        self._line_mosi = None
        self._line_sclk = None
        self._line_pwr = None

        self._use_spidev = (
            os.environ.get("EPD_USE_SPIDEV", "1") == "1"
            and os.environ.get("EPD_BITBANG", "0") != "1"
        )

        self._use_gpio_cs = os.environ.get("EPD_USE_GPIO_CS", "1") == "1"
        self._bb_delay_us = int(os.environ.get("EPD_BB_DELAY_US", "3"))
        self._busy_invert = os.environ.get("EPD_BUSY_INVERT", "0") == "1"
        self._dump_file = open("dump.txt", "w")

    # ------------------------------------------------------------------ GPIO

    def digital_write(self, pin, value):
        v = 1 if value else 0
        if pin == self.DC_PIN and self._line_dc:
            self._line_dc.set_value(v)
        elif pin == self.RST_PIN and self._line_rst:
            self._line_rst.set_value(v)
        elif pin == self.CS_PIN and self._line_cs:
            self._line_cs.set_value(v)

    def digital_read(self, pin):
        if pin == self.BUSY_PIN and self._line_busy:
            val = self._line_busy.get_value()
            return val ^ (1 if self._busy_invert else 0)
        return 0

    def delay_ms(self, ms):
        time.sleep(ms / 1000.0)

    # ------------------------------------------------------------------ SPI

    def spi_writebyte(self, data):
        if self._use_spidev:
            data = list(data)
            log_msg = f"SPI Write: {[f'0x{b:02X}' for b in data]}"
            print(log_msg)
            self._dump_file.write(log_msg + "\n")
            self._dump_file.flush()
            self.SPI.writebytes(data)
        else:
            self._spi_bitbang(data)

    def spi_writebyte2(self, data):
        if self._use_spidev:
            # Use writebytes2 for bulk transfers (proven to work on Radxa Zero)
            log_msg = f"SPI Write2 ({len(data)} bytes): {[f'0x{b:02X}' for b in data]}"
            print(log_msg[:200] + "..." if len(log_msg) > 200 else log_msg) # Truncate console output
            self._dump_file.write(log_msg + "\n")
            self._dump_file.flush()

            if isinstance(data, (bytes, bytearray)):
                self.SPI.xfer3(list(data))
            else:
                self.SPI.xfer3(data)
        else:
            self._spi_bitbang(data)

    def _spi_bitbang(self, data):
        half = self._bb_delay_us / 1_000_000.0
        seq = data if isinstance(data, (bytes, bytearray)) else list(data)

        for b in seq:
            if self._line_cs:
                self._line_cs.set_value(0)

            for i in range(7, -1, -1):
                self._line_sclk.set_value(0)
                self._line_mosi.set_value((b >> i) & 1)
                time.sleep(half)
                self._line_sclk.set_value(1)
                time.sleep(half)

            if self._line_cs:
                self._line_cs.set_value(1)

    # ------------------------------------------------------------------ INIT

    def _request_out(self, line, name, default):
        try:
            line.request(
                consumer=name,
                type=self.gpiod.LINE_REQ_DIR_OUT,
                default_val=default,
            )
        except TypeError:
            line.request(
                consumer=name,
                type=self.gpiod.LINE_REQ_DIR_OUT,
            )
            line.set_value(default)

    def module_init(self):
        self._chip = self.gpiod.Chip(self.CHIP_NAME)

        self._line_dc = self._chip.get_line(self.OFFSET_DC)
        self._line_rst = self._chip.get_line(self.OFFSET_RST)
        self._line_busy = self._chip.get_line(self.OFFSET_BUSY)
        self._line_cs = self._chip.get_line(self.OFFSET_CS)

        if not self._use_spidev:
            self._line_mosi = self._chip.get_line(self.OFFSET_MOSI)
            self._line_sclk = self._chip.get_line(self.OFFSET_SCLK)

        if self.OFFSET_PWR is not None:
            self._line_pwr = self._chip.get_line(int(self.OFFSET_PWR))

        self._request_out(self._line_dc, "epd-dc", 0)
        self._request_out(self._line_rst, "epd-rst", 1)

        self._line_busy.request(
            consumer="epd-busy",
            type=self.gpiod.LINE_REQ_DIR_IN,
        )

        self._request_out(self._line_cs, "epd-cs", 1)

        if not self._use_spidev:
            self._request_out(self._line_mosi, "epd-mosi", 0)
            self._request_out(self._line_sclk, "epd-sclk", 0)

        if self._line_pwr:
            self._request_out(
                self._line_pwr,
                "epd-pwr",
                1 if self.PWR_ACTIVE_HIGH else 0,
            )

        if self._use_spidev:
            bus = int(os.environ.get("EPD_SPI_BUS", "1"))
            dev = int(os.environ.get("EPD_SPI_DEV", "0"))
            self.SPI.open(bus, dev)

            if self._use_gpio_cs:
                try:
                    self.SPI.no_cs = True
                except OSError as e:
                    print(f"WARNING: Failed to set SPI.no_cs=True: {e}")

            self.SPI.max_speed_hz = int(
                os.environ.get("EPD_SPI_HZ", "2000000")
            )
            self.SPI.mode = 0

        for attr in dir(self):
            print("self.%s = %r" % (attr, getattr(self, attr)))
        return 0

    # ------------------------------------------------------------------ EXIT

    def module_exit(self, cleanup=True):
        if self._use_spidev:
            try:
                self.SPI.close()
            except Exception:
                pass

        for line in (
            self._line_dc,
            self._line_rst,
            self._line_cs,
            self._line_mosi,
            self._line_sclk,
            self._line_busy,
            self._line_pwr,
        ):
            if line:
                try:
                    line.release()
                except Exception:
                    pass

        try:
            if self._chip:
                self._chip.close()
        except Exception:
            pass


if sys.version_info[0] == 2:
    process = subprocess.Popen("cat /proc/cpuinfo | grep Raspberry", shell=True, stdout=subprocess.PIPE)
else:
    process = subprocess.Popen("cat /proc/cpuinfo | grep Raspberry", shell=True, stdout=subprocess.PIPE, text=True)
output, _ = process.communicate()
if sys.version_info[0] == 2:
    output = output.decode(sys.stdout.encoding)

implementation = RadxaZeroGPIOD()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))

### END OF FILE ###
