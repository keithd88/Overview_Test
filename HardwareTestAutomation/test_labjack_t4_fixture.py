import labjack.ljm as ljm
import time

def test_labjack_t4_fixture():
    # define input/output pins
    din = 'DI04'
    dout = 'DI05'
    
    # initialize device
    handle = ljm.openS('T4', 'USB', 'ANY')

    # check initial state on input pin
    digital_input = ljm.eReadName(handle, din)

    # toggle digital output connected to external hardware
    ljm.eWriteName(handle, dout, 1)
    time.sleep(1)
    ljm.eWriteName(handle, dout, 0)

    # read input pin and wait for state change (might not be necessary)
    while(digital_input == ljm.eReadName(handle, din)):
        time.sleep(.1)

    # update new digital input state
    new_digital_input = ljm.eReadName(handle, din)

    # once pin changes, assert digital input changed
    if digital_input == 0:
        assert new_digital_input == 1
    elif digital_input == 1:
        assert new_digital_input == 0

    # close connection once testing is done
    ljm.close(handle)