import sys
import os.path
import visa
# pyvisa from https://pyvisa.readthedocs.io/en/stable/

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Change this variable to the address of your instrument
VISA_ADDRESS = 'USB0::0x2A8D::0x1797::CN57266528::0::INSTR'


class VisaInstrument(object):
    def __init__(self, visa_address=VISA_ADDRESS, name="Default_Visa_Instrument", verbose=True):
        self.timeout = 10000    # specify visa IO timeout in milliseconds.
        self.resourceManager = visa.ResourceManager()
        if verbose:
            print("%s" % self.resourceManager)
            print("Found visa devices:")
            print self.resourceManager.list_resources()
            print("End of devices list.")
            print
            print("Opening VisaInstrument (%s) at: %s" % (name, visa_address))

        self.session = self.resourceManager.open_resource(visa_address)
        self.session.timeout = self.timeout

        print("Opened visa device with timeout = %s" % str(self.session.timeout))
        print

        # For Serial and TCP/IP socket connections enable the read Termination Character, or read's will timeout
        if self.session.resource_name.startswith('ASRL') or self.session.resource_name.endswith('SOCKET'):
            self.session.read_termination = '\n'
        if verbose:
            print("ID: %s" % str(self.identification_number(verbose=True)))
            print

    def cmd(self, s, query=False, ascii=True, single_value=True, verbose=False):
        if query:
            if ascii:
                if single_value:
                    if verbose:
                        print("visa_io.cmd(): Sending ascii query: %s" % self.make_nice_ascii(s))
                    resp = self.session.query(s)  # returns single string
                else:
                    if verbose:
                        print("visa_io.cmd(): Sending ascii query for list: %s" % self.make_nice_ascii(s))
                    resp = self.session.query_ascii_values(s)  # returns a list
                if verbose:
                    print("visa_io.cmd(): Received ascii values: %s" % str(resp))
            else:
                if verbose:
                    print("visa_io.cmd(): Sending binary cmd and read_raw for list: %s" % self.make_nice_ascii(s))
                resp = self.session.write(s)
                if not isinstance(resp, str):
                    if isinstance(resp, (list, tuple)):
                        resp = str(resp[0])
                    else:
                        resp = ""
                if verbose:
                    print("visa_io.cmd(): Sent cmd.  Response acknowledgement: %s" % self.make_nice_ascii(resp))
                resp = self.session.read_raw()  # returns a list
                if verbose:
                    print("visa_io.cmd(): Received RAW binary values: %s" % self.make_nice_ascii(resp))
        else:
            # Normally don't care about responses from writes.  Handle them anyway, who knows...
            if verbose:
                print("visa_io.cmd(): Sending command: %s" % self.make_nice_ascii(s))
            resp = self.session.write(s)
            if not isinstance(resp, str):
                if isinstance(resp, (list, tuple)):
                    resp = str(resp[0])
                else:
                    resp = ""
        return resp

    # Close the connection to the instrument
    def close(self):
        self.session.close()
        self.resourceManager.close()
        return

    @staticmethod
    def make_nice_ascii(ins):
        outs = ""
        if isinstance(ins, basestring):
            for ch in ins:
                if (ord(ch) > 31) and (ord(ch) < 127):
                    outs = outs + ch
                else:
                    outs = outs + '<' + str(ord(ch)) + '>'
            return outs
        else:
            outs = "<" + str(ins) + ">"
            return outs
