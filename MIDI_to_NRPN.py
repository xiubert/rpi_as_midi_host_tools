import mido
mido.set_backend('mido.backends.rtmidi')

globalchan=0
CCtoConvert=82
NRPNparamMSB=1
NRPNparamLSB=97
MIDIkeyboardName="Keystation"
SoundModuleName="Digitone"

#find respective output
inputName = [s for s in mido.get_input_names() if MIDIkeyboardName in s]
outputName = [s for s in mido.get_output_names() if SoundModuleName in s]

outport = mido.open_output(outputName[0])

#define midi CC's for an NRPN message:
nrpn_select_msb_cc = 99 #send first
nrpn_select_lsb_cc = 98 #send second
data_entry_msb_cc = 6 #send third (for coarse adjustment)
data_entry_lsb_cc = 38 #optional for fine adjustment

def send_nrpn(nrpn_MSB,nrpn_LSB,msb_value,chan=globalchan,lsb_value=None):
    msbmsg=mido.Message('control_change',channel=chan,control=nrpn_select_msb_cc,value=nrpn_MSB)
    lsbmsg=mido.Message('control_change',channel=chan,control=nrpn_select_lsb_cc,value=nrpn_LSB)
    msbValMsg=mido.Message('control_change',channel=chan,control=data_entry_msb_cc,value=msb_value)
    outport.send(msbmsg)
    outport.send(lsbmsg)
    outport.send(msbValMsg)
    if lsb_value is not None:
      lsbValMsg=mido.Message('control_change',channel=chan,control=data_entry_msb_cc,value=lsb_value)
      outport.send(lsbValMsg)

def filterCCmsg(port):
    for message in port:
        if message.type is 'control_change' and message.control is CCtoConvert:
            yield message

#test _ works with:
#send_nrpn(1,97,127,2,3)
#send_nrpn(1,97,127,2,55)
#outport.close()

try:
    with mido.open_input(inputName[0]) as port:
        print('Waiting for control...')

        for message in filterCCmsg(port):
            print('Received: ' + str(message.value) + ' | On channel: ' + str(message.channel))
            send_nrpn(NRPNparamMSB,NRPNparamLSB,message.value,message.channel)
except KeyboardInterrupt:
    outport.close()
    pass
