import sys
import os.path
import time
from visa_io import VisaInstrument

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DSOX1000(VisaInstrument):
    def __init__(self, address='USB0::0x2A8D::0x1797::CN57266528::0::INSTR', my_name="my_DSOX100_Scope"):
        # Variables
        self.properties = {
            'Name': my_name,
            'Address': address,
            'Channels': 2,
            'Channels_V_per_Div': [.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
            'WGEN_VPP_MAX': 12,
            'WGEN_VPP_Current': 12
        }

        VisaInstrument.__init__(self, name=my_name, visa_address=address)

    def send_visa_cmd(self, cmd, query=False, ascii=True, single_value=True, verbose=False):
        if verbose:
            print("send_visa_cmd: cmd: %s" % str(cmd))

        r = self.cmd(cmd, query=query, ascii=ascii, single_value=single_value, verbose=verbose)
        if verbose:
            print("send_visa_cmd: Received: %s" % str(r))
        return r

    # ----------------------------------------------------------------------------------
    #
    #             ***** Command List *****
    #
    # ----------------------------------------------------------------------------------

    # Root Commands
    def clear_status(self, query=False, verbose=False):
        # The *CLS common command clears the status data structures, the device-defined error queue, and the
        # Request-for-OPC flag.
        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = self.send_visa_cmd('*CLS', query=query, verbose=verbose)
        else:
            r['msg'] = "*CLS is write only."
            r['err'] = 1
        if verbose:
            print r
        return r

    def identification_number(self, query=True, verbose=False):
        # The *IDN? query identifies the instrument type and software version.
        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = "*IDN is read only."
            r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd('*IDN?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def factory_reset(self, query=False, verbose=False):
        # The *RST command places the instrument in a known state. This is the same as pressing
        # [Save/Recall] > Default/Erase > Factory Default on the front panel.
        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = self.send_visa_cmd('*RST', query=query, verbose=verbose)
        else:
            r['msg'] = "*RST is write only."
            r['err'] = 1
        if verbose:
            print r
        return r

    def event_status_enable(self, bit_mask=0b00000001, query=False, verbose=False):
        # The *ESE common command sets the bits in the Standard Event Status Enable Register.
        # The Standard Event Status Enable Register contains a mask value for the bits to be enabled in the
        # Standard Event Status Register. A "1" in the Standard Event Status Enable Register enables the
        # corresponding bit in the Standard Event Status Register. A zero disables the bit.
        #
        # Bit Name Description
        # 7   PON Power On An OFF to ON transition has occurred.
        # 6   URQ User Request A front-panel key has been pressed.
        # 5   CME Command Error A command error has been detected.
        # 4   EXE Execution Error An execution error has been detected.
        # 3   DDE Device Dependent Error A device-dependent error has been detected.
        # 2   QYE Query Error A query error has been detected.
        # 1   RQL Request Control The device is requesting control. (Not used.)
        # 0   OPC Operation Complete Operation is complete.

        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = self.send_visa_cmd('*ESE %d' % bit_mask, query=query, verbose=verbose)
        else:
            r['msg'] = self.send_visa_cmd('*ESE?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def event_status_register(self, query=True, verbose=False):
        # The *ESR? query returns the contents of the Standard Event Status Register. When
        # you read the Event Status Register, the value returned is the total bit weights of all
        # of the bits that are high at the time you read the byte. Reading the register clears
        # the Event Status Register.
        # The following table shows bit weight, name, and condition for each bit.
        #
        # Bit Name Description When Set (1 = High = True), Ind icates:
        # 7   PON Power On An OFF to ON transition has occurred.
        # 6   URQ User Request A front-panel key has been pressed.
        # 5   CME Command Error A command error has been detected.
        # 4   EXE Execution Error An execution error has been detected.
        # 3   DDE Device Dependent Error A device-dependent error has been detected.
        # 2   QYE Query Error A query error has been detected.
        # 1   RQL Request Control The device is requesting control. (Not used.)
        # 0   OPC Operation Complete Operation is complete.

        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = 'event_status_register: Malformed input.'
            r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd('*ESR?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def autoscale(self, query=False, verbose=False):
        r = {'msg': "", 'err': 0}
        # This is the same as pressing the [Auto Scale] key on the front panel.
        if not query:
            r['msg'] = self.send_visa_cmd(':AUToscale', verbose=verbose)
            # self.wait_for_esr(verbose=verbose)
        else:
            r['msg'] = ":AUToscale is write only."
            r['err'] = 1
        if verbose:
            print r
        return r

    def autoscale_channels(self, channels='ALL', query=False, verbose=False):
        # The :AUTOscale:CHANnels command specifies which channels will be displayed
        # on subsequent :AUToscales.
        # When ALL is selected, all channels that meet the requirements of :AUToscale
        # will be displayed.
        # When DISPlayed is selected, only the channels that are turned on are
        # autoscaled.
        # Use the :VIEW or :BLANk root commands to turn channels on or off.
        r = {'msg': "", 'err': 0}
        if not query:
            if channels in ['All', 'DISPlayed']:
                r['msg'] = self.send_visa_cmd(':AUToscale:CHANnels %s' % channels, verbose=verbose)
            else:
                r['msg'] = 'autoscale_channels(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':AUToscale:CHANnels?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # Acquire commands
    def acquire_count(self, counts=2, query=False, verbose=False):
        # In averaging mode, the :ACQuire:COUNt command specifies the number of values to be averaged for each time
        # bucket before the acquisition is considered to be complete for that time bucket. When :ACQuire:TYPE is set
        # to AVERage, the count can be set to any value from 2 to 65536.

        r = {'msg': "", 'err': 0}
        if not query:
            counts = int(counts)
            r['msg'] = self.send_visa_cmd(':ACQuire:COUNt %s' % counts, verbose=verbose)
        else:
            r['msg'] = self.send_visa_cmd(':ACQuire:COUNt?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def acquire_type(self, acquire_type='Normal', query=False, verbose=False):
        # The :ACQuire:TYPE command selects the type of data acquisition that is to take place.
        # The acquisition types are:
        # NORMal, AVERage, HRESolution, PEAK
        # For AVERage mode, set :ACQuire:COUNt as well for number of averages to take.

        r = {'msg': "", 'err': 0}
        if not query:
            if acquire_type in ['NORMal', 'AVERage', 'HRESolution', 'PEAK']:
                r['msg'] = self.send_visa_cmd(':ACQuire:TYPE %s' % acquire_type, verbose=verbose)
            else:
                r['msg'] = 'acquire_type(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':ACQuire:TYPE?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # Channel commands
    def channel_coupling(self, channel=1, coupling='AC', query=False, verbose=False):
        # The :CHANnel<n>:COUPling command selects the input coupling for the specified channel. The coupling for each
        # analog channel can be set to AC or DC.
        r = {'msg': "", 'err': 0}
        if not query:
            if coupling in ['AC', 'DC']:
                r['msg'] = self.send_visa_cmd(':CHANnel%d:COUPling %s' % (channel, coupling), verbose=verbose)
            else:
                r['msg'] = 'channel_coupling(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':CHANnel%d:COUPling?' % channel, query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def channel_offset(self, channel=1, offset=0.0, query=False, verbose=False):
        # The :CHANnel<n>:OFFSet command sets the value that is represented at center screen for the selected channel.
        r = {'msg': "", 'err': 0}
        if not query:
            while 1:
                my_offset, err = self.get_nr3_format(offset)
                if err:
                    r['msg'] = 'channel_offset: Malformed input (offset).'
                    r['err'] = 1
                    break
                if (channel < 1) or (channel > self.properties['Channels']):
                    r['err'] = 1
                    r['msg'] = 'channel_offset: Channel out of range.'
                    break
                r['msg'] = self.send_visa_cmd(':CHANnel%d:OFFSet %s' % (channel, my_offset), query=query,
                                              verbose=verbose)
                break
        else:
            r['msg'] = self.send_visa_cmd(':CHANnel%d:OFFSet?' % channel, query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def channel_probe(self, channel=1, attenuation_ratio=1.0, query=False, verbose=False):
        # The :CHANnel<n>:PROBe command specifies the probe attenuation factor for the selected channel.
        # The probe attenuation factor may be 0.1 to 10000.
        r = {'msg': "", 'err': 0}
        if not query:
            while 1:
                my_val, err = self.get_nr3_format(attenuation_ratio)
                if err:
                    r['msg'] = 'channel_offset: Malformed input (offset).'
                    r['err'] = 1
                    break
                if (channel < 1) or (channel > self.properties['Channels']):
                    r['err'] = 1
                    r['msg'] = 'channel_offset: Channel out of range.'
                    break
                r['msg'] = self.send_visa_cmd(':CHANnel%d:PROBe %s' % (channel, my_val), query=query,
                                              verbose=verbose)
                break
        else:
            r['msg'] = self.send_visa_cmd(':CHANnel%d:PROBe?' % channel, query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def channel_scale(self, channel=1, scale=2.0, query=False, verbose=False):
        # The :CHANnel<n>:SCALe command sets the vertical scale, or units per division, of the selected channel.
        r = {'msg': "", 'err': 0}
        if not query:
            while 1:
                my_scale, err = self.get_nr3_format(scale)
                if err:
                    r['msg'] = "channel_scale: Malformed input (scale)."
                    r['err'] = 1
                    break
                if (channel < 1) or (channel > self.properties['Channels']):
                    r['err'] = 1
                    r['msg'] = "channel_scale: channel out of range."
                    break
                r['msg'] = self.send_visa_cmd(':CHANnel%d:SCALe %s' % (channel, my_scale), query=query, verbose=verbose)
                break
        else:
            r['msg'] = self.send_visa_cmd(':CHANnel%d:SCALe?' % channel, query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # Frequency Analysis Commands
    def frequency_analysis_data(self, query=True, verbose=False):
        # The :FRANalysis:DATA? query returns the frequency r['msg']onse analysis data.
        # The data is returned in four comma-separated columns of data for each step in the
        # sweep: Frequency (Hz), Amplitude (Vpp), Gain (dB), and Phase (deg).
        r = {'msg': "", 'err': 0}
        if not query:
            r['err'] = 1
            r['msg'] = 'frequency_analysis_data: Malformed input.'
        else:
            # :FRANalysis:DATA?
            # --------------------------------------------------------
            # 800000384#, Frequency (Hz), Amplitude (Vpp), Gain (dB), Phase (<176>)<10>
            # 1, 1000000.0, 0.2000, 0.01, 0.00 < 10 >
            # 2, 1258925.4, 0.2000, 0.02, 0.11 < 10 >
            # 3, 1584893.2, 0.2000, 0.02, -0.16 < 10 >
            # 4, 1995262.3, 0.2000, 0.03, -0.11 < 10 >
            # 5, 2511886.4, 0.2000, 0.01, -0.34 < 10 >
            # < 10 >
            # --------------------------------------------------------
            r['msg'] = self.send_visa_cmd(':FRANalysis:DATA?', ascii=False, single_value=False, query=query,
                                          verbose=verbose)
            if verbose:
                print("frequency_analysis_data(): response: %s" % r)
        return r

    def frequency_analysis_enable(self, enable=True, query=False, verbose=False):
        # The :FRANalysis:ENABle command turns the Frequency r['msg']onse Analysis (FRA) feature on or off.
        r = {'msg': "", 'err': 0}
        if not query:
            if enable:
                r['msg'] = self.send_visa_cmd(':FRANalysis:ENABle 1', verbose=verbose)
            else:
                r['msg'] = self.send_visa_cmd(':FRANalysis:ENABle 0', verbose=verbose)
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:ENABle?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def frequency_analysis_frequency_start(self, frequency=20, query=False, verbose=False):
        # The :FRANalysis:FREQuency:STARt command command sets the frequency sweep start value. The frequency response
        #  analysis is displayed on a log scale Bode plot, so you can select from decade values in addition to the
        # minimum frequency of 20 Hz.
        r = {'msg': "", 'err': 0}
        if not query:
            if frequency in [20, 100, 1000, 10000, 100000, 1000000, 10000000, 20000000]:
                r['msg'] = self.send_visa_cmd(':FRANalysis:FREQuency:STARt %s' % frequency, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'frequency_analysis_frequency_start: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:FREQuency:STARt?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def frequency_analysis_frequency_stop(self, frequency=20000000, query=False, verbose=False):
        # The :FRANalysis:FREQuency:STOP command command sets the frequency sweep stop value. The frequency r['msg']onse
        #  analysis is displayed on a log scale Bode plot, so you can select from decade values in addition to the
        # minimum frequency 100 Hz.
        r = {'msg': "", 'err': 0}
        if not query:
            if frequency in [100, 1000, 10000, 100000, 1000000, 10000000, 20000000]:
                r['msg'] = self.send_visa_cmd(':FRANalysis:FREQuency:STOP %s' % frequency, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'frequency_analysis_frequency_start: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:FREQuency:STOP?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def frequency_analysis_run(self, query=False, verbose=False):
        # The :FRANalysis:RUN command performs the Frequency r['msg']onse Analysis. This analysis controls the built-in
        # waveform generator to sweep a sine wave across a range of frequencies while measuring the input to and
        # output from a device under test (DUT).
        #
        # It takes some time for the frequency sweep analysis to complete. You can query bit 0 of the
        # Standard Event Status Register (*ESR?) to find out when the analysis is complete.
        r = {'msg': "", 'err': 0}
        if not query:
            self.send_visa_cmd(':FRANalysis:RUN', verbose=verbose)
            r['msg'] = self.wait_for_esr(verbose=verbose)
        else:
            r['err'] = 1
            r['msg'] = 'frequency_analysis_run: Malformed input.'
        if verbose:
            print r
        return r

    def frequency_analysis_source_input(self, channel=1, query=False, verbose=False):
        # The :FRANalysis:SOURce:INPut command specifies the analog input channel that is probing the input voltage
        # to the device under test (DUT) in the frequency response analysis.
        r = {'msg': "", 'err': 0}
        if not query:
            if 1 <= channel <= self.properties['Channels']:
                r['msg'] = self.send_visa_cmd(':FRANalysis:SOURce:INPut CHANnel%s' % channel, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'frequency_analysis_source_input: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:SOURce:INPut?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def frequency_analysis_source_output(self, channel=2, query=False, verbose=False):
        # The :FRANalysis:SOURce:OUTPut command specifies the analog input channel that is probing the output voltage
        # from the device under test (DUT) in the frequency response analysis.
        r = {'msg': "", 'err': 0}
        if not query:
            if 1 <= channel <= self.properties['Channels']:
                r['msg'] = self.send_visa_cmd(':FRANalysis:SOURce:OUTPut CHANnel%s' % channel, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'frequency_analysis_source_output: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:SOURce:OUTPut?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def frequency_analysis_wave_gen_voltage(self, volts=1.0, query=False, verbose=False):
        # <amplitude> ::= amplitude in volts in NR3 format
        r = {'msg': "", 'err': 0}
        if not query:
            while 1:
                my_volts, err = self.get_nr3_format(volts)
                if verbose:
                    print("frequency_analysis_wave_gen_voltage: Request: %s, nr3: %s, err: %d" % (str(volts),
                                                                                                  str(my_volts), err))
                if err:
                    r['err'] = 1
                    r['msg'] = "frequency_analysis_wave_gen_voltage: voltage input error."
                    break
                if (volts < 0) or (volts > self.properties['WGEN_VPP_MAX']):
                    r['err'] = 1
                    r['msg'] = "frequency_analysis_wave_gen_voltage: voltage range error."
                    break
                r['msg'] = self.send_visa_cmd(':FRANalysis:WGEN:VOLTage %s' % my_volts, verbose=verbose)
                self.properties['WGEN_VPP_Current'] = float(my_volts)
                break
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:WGEN:VOLTage?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # measurement commands
    def measure_clear(self, query=False, verbose=False):
        # This command clears all selected measurements and markers from the screen.
        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = self.send_visa_cmd(':MEASure:CLEar', verbose=verbose)
        else:
            r['msg'] = 'measurement_clear: Malformed input.'
            r['err'] = 1
        if verbose:
            print r
        return r

    def measure_frequency(self, source="CHANnel1", query=False, verbose=False):
        # The :MEASure:FREQuency command installs a screen measurement and starts a frequency measurement.
        r = {'msg': "", 'err': 0}
        if source in ['CHANnel1', 'CHANnel2', 'FUNCtion', 'MATH', 'WMEMory1', 'WMEMory2', 'EXTernal']:
            if not query:
                r['msg'] = self.send_visa_cmd(':MEASure:FREQuency %s' % source, verbose=verbose)
            else:
                r['msg'] = self.send_visa_cmd(':MEASure:FREQuency? %s' % source, query=query, verbose=verbose)
        else:
            r['err'] = 1
            r['msg'] = 'measure_frequency: Malformed input.'
        if verbose:
            print r
        return r

    def measure_volts_amplitude(self, source="CHANnel1", query=False, verbose=False):
        # The :MEASure:VAMPlitude command installs a screen measurement and starts a vertical amplitude measurement.
        r = {'msg': "", 'err': 0}
        if source in ['CHANnel1', 'CHANnel2', 'FUNCtion', 'MATH', 'WMEMory1', 'WMEMory2', 'EXTernal']:
            if not query:
                r['msg'] = self.send_visa_cmd(':MEASure:VAMPlitude %s' % source, verbose=verbose)
            else:
                r['msg'] = self.send_visa_cmd(':MEASure:VAMPlitude? %s' % source, query=query, verbose=verbose)
        else:
            r['err'] = 1
            r['msg'] = 'measure_volts_amplitude: Malformed input.'
        if verbose:
            print r
        return r

    def measure_volts_pp(self, source="CHANnel1", query=False, verbose=False):
        # The :MEASure:VPP command installs a screen measurement and starts a vertical peak-to-peak measurement.
        r = {'msg': "", 'err': 0}
        if source in ['CHANnel1', 'CHANnel2', 'FUNCtion', 'MATH', 'WMEMory1', 'WMEMory2', 'EXTernal']:
            if not query:
                r['msg'] = self.send_visa_cmd(':MEASure:VPP %s' % source, verbose=verbose)
            else:
                r['msg'] = self.send_visa_cmd(':MEASure:VPP? %s' % source, query=query, verbose=verbose)
        else:
            r['err'] = 1
            r['msg'] = 'measure_volts_pp: Malformed input.'
        if verbose:
            print r
        return r

    # timebase commands
    def timebase_scale(self, scale=500e-9, query=False, verbose=False):
        # The :TIMebase:SCALe command sets the horizontal scale or units per division for the main window.
        r = {'msg': "", 'err': 0}
        if not query:
            my_scale, err = self.get_nr3_format(scale)
            if not err:
                r['msg'] = self.send_visa_cmd(':TIMebase:SCALe %s' % my_scale, query=query, verbose=verbose)
            else:
                r['msg'] = 'timebase_scale: Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':TIMebase:SCALe?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # trigger commands
    def trigger_mode(self, mode='EDGE', query=False, verbose=False):
        # The :TRIGger:MODE command selects the trigger mode (trigger type).
        r = {'msg': "", 'err': 0}
        if not query:
            if mode in ['EDGE', 'GLITch', 'PATTern', 'SHOLd', 'TRANsition', 'TV', 'SBUS1']:
                r['msg'] = self.send_visa_cmd(':TRIGger:MODE %s' % mode, query=query, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'trigger_mode: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':TRIGger:MODE?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def trigger_edge_source(self, source='WGEN', query=False, verbose=False):
        # The :TRIGger[:EDGE]:SOURce command selects the input that produces the trigger.
        # EXTernal : triggers on the rear panel EXT TRIG IN signal.
        # LINE : triggers at the 50% level of the rising or falling edge of the AC power source signal.
        # WGEN : triggers at the 50% level of the rising edge of the waveform generator output signal.
        #         This option is not available when the DC or NOISe waveforms are selected.
        r = {'msg': "", 'err': 0}
        if not query:
            if source in ['CHANnel1', 'CHANnel2', 'EXTernal', 'LINE', 'WGEN']:
                r['msg'] = self.send_visa_cmd(':TRIGger:EDGE:SOURce %s' % source, query=query, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'trigger_edge_source(): Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':TRIGger:EDGE:SOURce?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def trigger_sweep(self, mode='AUTO', query=False, verbose=False):
        # The :TRIGger:SWEep command selects the trigger sweep mode. When AUTO sweep mode is selected, a baseline
        # is displayed in the absence of a signal. If a signal is present but the oscilloscope is not triggered, the
        # unsynchronized signal is displayed instead of a baseline.
        # When NORMal sweep mode is selected and no trigger is present, the instrument does not sweep, and the data
        # acquired on the previous trigger remains on the screen.
        # Note: This feature is called "Mode" on the instrument's front panel.
        r = {'msg': "", 'err': 0}
        if not query:
            if mode in ['AUTO', 'NORMal']:
                r['msg'] = self.send_visa_cmd(':TRIGger:SWEep %s' % mode, query=query, verbose=verbose)
            else:
                r['err'] = 1
                r['msg'] = 'trigger_mode: Malformed input.'
        else:
            r['msg'] = self.send_visa_cmd(':TRIGger:SWEep?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # Waveform Generator Commands
    def wave_gen_function(self, my_shape="SINusoid", query=False, verbose=False):
        # Type of waveform: {SINusoid | SQUare | RAMP | PULSe | NOISe | DC}
        r = {'msg': "", 'err': 0}
        if not query:
            if my_shape in ['SINusoid', 'SQUare', 'RAMP', 'PULSe', 'NOISe', 'DC']:
                r['msg'] = self.send_visa_cmd(':WGEN:FUNCtion %s' % my_shape, verbose=verbose)
            else:
                r['msg'] = 'wave_gen_function(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':WGEN:FUNCtion?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def wave_gen_frequency(self, frequency=1000.0, query=False, verbose=False):
        # <frequency> ::= frequency in Hz in NR3 format
        r = {'msg': "", 'err': 0}
        if not query:
            my_freq, err = self.get_nr3_format(frequency)
            if not err:
                r['msg'] = self.send_visa_cmd(':WGEN:FREQuency %s' % my_freq, query=query, verbose=verbose)
            else:
                r['msg'] = 'wave_gen_frequency(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':WGEN:FREQuency?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def wave_gen_load(self, my_load="ONEMeg", query=False, verbose=False):
        # The :FRANalysis:WGEN:LOAD command selects the expected output load impedance. The output impedance of the
        # Gen Out BNC is fixed at 50 ohms. However, the output load selection lets the waveform generator display the
        # correct amplitude and offset levels for the expected output load.
        # If the actual load impedance is different than the selected value, the displayed amplitude and offset levels
        # will be incorrect.
        r = {'msg': "", 'err': 0}
        if not query:
            if my_load in ['ONEMeg', 'FIFTy']:
                r['msg'] = self.send_visa_cmd(':FRANalysis:WGEN:LOAD %s' % my_load, verbose=verbose)
            else:
                r['msg'] = 'wave_gen_load(): Malformed input.'
                r['err'] = 1
        else:
            r['msg'] = self.send_visa_cmd(':FRANalysis:WGEN:LOAD', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def wave_gen_output(self, enable=1, query=False, verbose=False):
        # The :WGEN:OUTPut command specifies whether the waveform generator signal output is ON (1) or OFF (0).
        r = {'msg': "", 'err': 0}
        if not query:
            r['msg'] = self.send_visa_cmd(':WGEN:OUTPut %s' % enable, query=query, verbose=verbose)
        else:
            r['msg'] = self.send_visa_cmd(':WGEN:OUTPut?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    def wave_gen_voltage(self, volts=1.0, query=False, verbose=False):
        # <amplitude> ::= amplitude in volts in NR3 format
        r = {'msg': "", 'err': 0}
        if not query:
            while 1:
                my_volts, err = self.get_nr3_format(volts)
                if verbose:
                    print("wave_gen_voltage: Request: %s, nr3: %s, err: %d" % (str(volts), str(my_volts), err))
                if err:
                    r['err'] = 1
                    r['msg'] = "wave_gen_voltage(): voltage input error."
                    break
                if (volts < 0) or (volts > self.properties['WGEN_VPP_MAX']):
                    r['err'] = 1
                    r['msg'] = "wave_gen_voltage: voltage range error."
                    break
                r['msg'] = self.send_visa_cmd(':WGEN:VOLTage %s' % my_volts, verbose=verbose)
                self.properties['WGEN_VPP_Current'] = float(my_volts)
                break
        else:
            r['msg'] = self.send_visa_cmd(':WGEN:VOLTage?', query=query, verbose=verbose)
        if verbose:
            print r
        return r

    # Utilities
    def get_nr3_format(self, my_num):
        # For numeric program data, you have the option of using exponential notation or using suffix multipliers
        # to indicate the numeric value. The following numbers are all equal:
        # 28 = 0.28E2 = 280e-1 = 28000m = 0.028K = 28e-3K.
        err = 0
        if self.is_number(my_num):
            a = '%E' % my_num
            val = a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]
        else:
            err = 1
            val = 0
        return val, err

    def wait_for_esr(self, bit_mask=0b00000001, sample_period=1.0, timeout=60, verbose=False):
        # pole the ESR every sample_period seconds until it matches bit_mask, or timeouts
        time_start = time.time()
        ok = False
        while not ok:
            if verbose:
                print("wait_for_esr: Sleeping %s seconds." % sample_period)
            time.sleep(sample_period)
            resp = self.event_status_register()
            # valid response?
            if verbose:
                print("wait_for_esr: received esr value of: %s" % self.make_nice_ascii(resp['msg']))
            my_esr = int(resp['msg'])
            ok = my_esr & bit_mask
            if verbose:
                print("wait_for_esr: esr comparison is: %s" % ok)

            if not ok and ((time.time() - time_start) > timeout):
                return False
        return True

    @staticmethod
    def is_number(s):
        try:
            float(s)
        except ValueError:
            return False
        return True


if __name__ == "__main__":
    my_scope = DSOX1000(address='USB0::0x2A8D::0x1797::CN57266528::0::INSTR', my_name="DSOX1102G")
    my_scope.identification_number(verbose=True)
    my_scope.close()
