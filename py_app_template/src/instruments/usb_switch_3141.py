from pydoc import describe

import serial
import serial.tools.list_ports
import time

"""
device info:
https://portal.mcci.com/portal/en/kb/articles/model-3141-usb4-switch-documentation
vid: 045E
pid: 0646
BAUD:   9600
8 bit, no parity, 1 stop bit (All default)
New Line Rcv: LF  (\n)
New Line Rcv: CR+LF (\r\n)
Type "?" for help

Commands of interest:
    port1       enables port1
    port2       enables port2
    port0       disables both ports
    port        returns the enabled ports
    
help:
    version
        XXYY - firmware version, shield type
    port [optional port]
        <empty>, shows currently connected port.
        1, connects to port 1
        2, connects to port 2
        0 (or other), disconnects all ports
    superspeed [value]
        Change takes affect next time a port is connected
        0, do not connect superspeed lanes
        other value, connect superspeed lanes
    delay [seconds]
        seconds to delay the next port change
    timeout [milliseconds]
        next port change will disconnect after a specified number of milliseconds
    defaultport [optional port]
        <empty>, shows currently specified default port that is selected at power on
        1, sets the default power on port to port 1
        2, sets the default power on port to port 2
        0 (or other), default power on state is disconnected
    put <index> <value>
        stores byte value at index where index is less than 10
    get <index>
        returns byte value stored at index
    status
        prints useful status information
    reset
        uses a GPIO line to reset the microcontroller
"""
class UsbSw3141:

    def __init__(self):
        self.port = None
        self.con = None
        self.verbose_level = 0
        self.vid_hex = "045E"
        self.pid_hex = "0646"
        self.baud = 9600
        self.connected = False
        self.timeout = 0.1
        self.rtn = {}


    def set_error(self, desc="", code=1):
        self.rtn["desc"] = desc
        self.rtn["code"] = code


    def connect(self):
        vid = int(self.vid_hex, 16)
        pid = int(self.pid_hex, 16)
        self.close()
        self.connected = False
        if self.verbose_level > 0:
            print(f"Looking for vid:pid {self.vid_hex}:{self.pid_hex}")
        self.port = None
        ports = serial.tools.list_ports.comports()
        for port in ports:
            d_vid = port.__dict__['vid']
            d_pid = port.__dict__['pid']
            if self.verbose_level > 1:  # f'{NNNN:0>4X}'
                d_vid_hex = f'{d_vid:0>4X}'
                d_pid_hex = f'{d_pid:0>4X}'
                print(f"Discovered port {port.__dict__['device']} with vid:pid = {d_vid_hex}:{d_pid_hex}")
            if vid == d_vid and pid == d_pid:
                self.port = port.__dict__['device']
                try:
                    self.con = serial.Serial(self.port, self.baud, timeout=self.timeout)
                    self.connected = True
                except (OSError, serial.SerialException):
                    pass
                if self.verbose_level > 0:
                    print(f"Found port {port.__dict__['device']}")
                    print(f"Connected = {self.connected}")
                break
        return self.connected

    def set_port(self, state:int, port_num:int=1):
        if state == 0:
            msg = f"port 0"
        else:
            msg = f"port {port_num}"
        error = self._serial_write(msg)
        return error

    def _serial_write(self, cmd):
        if True or self.verbose_level > 1:
            print("SerWrite " + cmd)
        success = False
        if self.connected:
            try:
                self.con.write(bytearray(f"{cmd}\r\n", 'ascii'))
                success = True
            except:
                pass
        return success

    def _serial_read(self):
        if self.verbose_level > 1:
            print("SerRead")
        lines = []
        max_empty_line_cnt = 1
        empty_line_cnt = 0
        done = False
        if self.connected:
            while not done:
                try:
                    line = self.con.readline().decode()
                    # print(f"EmptyCnt = {empty_line_cnt}, Line = " + line.rstrip())
                    lines.append(line.rstrip())
                    if line.strip() == "":
                        empty_line_cnt += 1
                        if empty_line_cnt >= max_empty_line_cnt:
                            done = True
                    else:
                        empty_line_cnt = 0
                except:
                    pass
                    done = True
        return lines

    def query(self, cmd):
        if self.connected:
            success = self._serial_write(cmd)
            if success:
                lines = self._serial_read()
                for line in lines:
                    print(line)


    def help(self):
        if self.connected:
            success = self._serial_write("?")
            if success:
                lines = self._serial_read()
                for line in lines:
                    print(line)

    def close(self):
        if self.con is not None:
            try:
                self.con.close()
            except:
                pass

# Find device
usbsw = UsbSw3141()
usbsw.verbose_level = 0
success = usbsw.connect()
if success:
    usbsw.help()
    usbsw.query("defaultport")
    print("\nPort 1 ON")
    usbsw.set_port(1, 1)
    print("Query")
    usbsw.query("port")
    print()
    time.sleep(3)
    print("Port 1 OFF")
    usbsw.set_port(0)
    usbsw.query("port")
    print()
    time.sleep(1)
    print("Port 2 ON")
    usbsw.set_port(1, 2)
    usbsw.query("port")
    print()
    time.sleep(3)
    print("Port 2 OFF")
    usbsw.set_port(0)
    usbsw.query("port")
    print()
    print("Done")
else:
    print("Failed to connect")










