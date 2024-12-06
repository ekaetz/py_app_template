import serial
import serial.tools.list_ports
import time

class SerialPortMgr:
    def __init__(self, portname=None, baud=9600, stopbits=serial.STOPBITS_ONE, timeout=0.1, write_timeout=0.1, verbose_level=0):
        self.s = None
        self.connected = False
        self.portname = portname
        self.baud = baud
        self.parity = serial.PARITY_NONE
        self.stopbits = serial.STOPBITS_ONE
        self.timeout = timeout  # Rx Timeout
        self.write_timeout = write_timeout  # Tx Timeout
        self.vid_hex = None
        self.pid_hex = None
        self.tx_newline = "\n"  # Typically '\n'
        self.rx_newline = "\r\n"  # Typically '\r\n'
        self.verbose_level = verbose_level

    def open(self, portname=None, vid_hex=None, pid_hex=None):
        # Init
        rsltcode, rsltdesc = 0, ""
        self.connected = False
        if portname is not None:
            self.portname = portname
        if vid_hex is not None:
            self.vid_hex = vid_hex
        if pid_hex is not None:
            self.pid_hex = pid_hex
        # Close connection if one exists
        if self.s is not None:
            try:
                self.con.close()
            except:
                pass
        # Look up port
        if name in [None, ""]:
            if self.vid_hex not in [None, ""] and self.pid_hex not in [None, ""]:
                rsltcode, rsltdesc, self.name = self._lookup_port()
            else:
                rsltcode = 1
                rsltdesc = f"Invalid port name: name = {self.name}"
        # Connect
            if rsltcode == 0:
                self.s = serial.Serial()
                self.s.port = self.portname
                self.s.baudrate = self.baud
                self.s.parity = self.parity
                self.s.stopbits = self.stopbits
                self.s.timeout = self.timeout
                self.s.write_timeout = self.write_timeout
                try:
                    print("comPortSetup: " + str(self.serialCom))
                    self.s.open()
                    self.connected = False
                except Exception as e:
                    rsltcode = 1
                    rsltdesc = f"Failed to connect to serial port {self.portname}: {e}"
        if self.verbose_level > 0:
            if rsltcode == 0:
                print(f"Serial Connect to port {self.portname}")
            else:
                print(f"Serial Connect error: {self.rsltdesc}")
        # Return
        return rsltcode, rsltdesc

    def close(self):
        if self.s is not None:
            if self.verbose_level > 1:
                if rsltcode == 0:
                    print(f"Serial Close {self.portname}")
            try:
                self.s.close()
            except:
                pass

    def readline(self, timeout=None):
        # Init
        rsltcode, rsltdesc = 0, ""
        line = ""
        # Check state
        if not self.connected:
            rsltcode = 1
            rsltdesc = f"Serial Read Error: Serial port is not connected"
        else:
            # Read line
            try:
                self.s.timeout = timeout
                line = self.s.readline().decode().rstrip()
            except Exception as e:
                rsltcode = 1
                rsltdesc = f"Failed to connect to serial port {self.portname}: {e}"
        # Verbose Info
        if self.verbose_level > 0:
            if rsltcode == 0:
                print(f"Serial Readline: '{line}'")
            else:
                print(f"Serial Read Error: {self.rsltdesc}")
        # Return
        return rsltcode, rsltdesc, line

    def readlines(self, maxlinecnt=-1, skipemptylines=False, timeout=0.1, termination_str=None):
        # Init
        rsltcode, rsltdesc = 0, ""
        lines = []
        # Check state
        if not self.connected:
            rsltcode = 1
            rsltdesc = f"Serial Read Error: Serial port is not connected"
        else:
            # Read lines
            done = False
            linecnt = 0
            start_time = time.time()
            while rsltcode == 0 and not done:
                try:
                    line = self.s.readline().decode()
                    if line != "" or not skipemptylines:
                        linecnt += 1
                        lines.append(line.rstrip())
                    # Done Check
                    if linecnt > maxlinecnt or time.time() - start_time > timeout:
                        done = True
                    elif termination_str is not None and line.strip() == termination_str:
                        done = True
                except Exception as e:
                    rsltcode = 1
                    rsltdesc = f"Failed to connect to serial port {self.portname}: {e}"
        # Verbose Info
        if self.verbose_level > 0:
            if rsltcode == 0:
                print(f"Serial Readlines:---\n{lines}\n---")
            else:
                print(f"Serial Read Error: {self.rsltdesc}")
        # Return
        return rsltcode, rsltdesc

    def write(self, cmd:str, clearbuffer=False):
        # Init
        rsltcode, rsltdesc = 0, ""
        # Check state
        if not self.connected:
            # try to connect
            if self.portname not in [None, ""]:
                rsltcode, rsltdesc = self.open()
        # Serial Write
        if rsltcode == 0:
            # Clear buffer
            if clearbuffer:
                self.s.reset_input_buffer()
            # Prepare cmd
            cmd_bytes = bytearray(f"{cmd}{self.tx_newline}", 'ascii')
            try:
                self.s.write(cmd_bytes)
            except Exception as e:
                rsltcode = 3
                rsltdesc = f"Serial Write Error: {e}"
        # Verbose
        if self.verbose_level > 0:
            if rsltcode == 0:
                print(f"Serial Write '{cmd}'")
            else:
                print(f"Serial Write Error: {self.rsltdesc}")
        # Return
        return rsltcode, rsltdesc

    def _lookup_port(self, vid_hex=None, pid_hex=None):
        # Init
        rsltcode, rsltdesc = 0, ""
        found_port = ""
        available = False
        local_debug = 0
        if vid_hex is not None:
            self.vid_hex = vid_hex
        if pid_hex is not None:
            self.pid_hex = pid_hex
        # Check for input errors
        if self.vid_hex in [None, ""] or self.vid_hex in [None, ""]:
            rsltcode, rsltdesc = 1, f"Serial port Lookup error, Invalid input vid/pid: {self.vid_hex}/{self.vid_pex}"
        # Lookup Port
        if rsltcode == 0:
            vid_int = int(self.vid_hex, 16)
            pid_int = int(self.pid_hex, 16)
            if local_debug > 0:
                print(f"Looking for vid:pid {vid_hex}:{pid_hex}")
            ports = serial.tools.list_ports.comports()
            for port in ports:
                d_vid = port.__dict__['vid']
                d_pid = port.__dict__['pid']
                if local_debug > 1:  # f'{NNNN:0>4X}'
                    d_vid_hex = f'{d_vid:0>4X}'
                    d_pid_hex = f'{d_pid:0>4X}'
                    print(f"Discovered port {port.__dict__['device']} with vid:pid = {d_vid_hex}:{d_pid_hex}")
                if vid_int == d_vid and pid_int == d_pid:
                    found_port = port.__dict__['device']
                    try:
                        s = serial.Serial(found_port)
                        available = True
                        s.close()
                        break
                    except (OSError, serial.SerialException):
                        pass
            # Check results
            if found_port == "":
                rsltcode, rsltdesc = 2, f"Serial port lookup vid/pid not found: {self.vid_hex}/{self.vid_pex}"
            elif not available:
                rsltcode, rsltdesc = 3, f"Serial port '{found_port}' is not available for connection."
        if local_debug > 0:
            if rsltcode == 0:
                print(f"Serial port lookup success: port='{found_port}'")
            else:
                print(f"Port lookup failure:  rsltcode={rsltcode}, desc='{rsltdesc}'")
        # Return
        return rsltcode, rsltdesc, found_port

