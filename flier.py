import rtmidi, time, logging, sys
from cflib import crazyflie, crtp
from threading import Thread
 
logging.basicConfig(level=logging.ERROR)

buttons = {
    58: 'track_left',
    59: 'track_right',
    46: 'cycle',
    60: 'marker_set',
    61: 'marker_left',
    62: 'marker_right',
    43: 'rwd',
    44: 'fwd',
    42: 'stop',
    41: 'play',
    45: 'record',
    32: 's_0',
    33: 's_1',
    34: 's_2',
    35: 's_3',
    36: 's_4',
    37: 's_5',
    38: 's_6',
    39: 's_7',
    48: 'm_0',
    49: 'm_1',
    50: 'm_2',
    51: 'm_3',
    52: 'm_4',
    53: 'm_5',
    54: 'm_6',
    55: 'm_7',
    64: 'r_0',
    65: 'r_1',
    66: 'r_2',
    67: 'r_3',
    68: 'r_4',
    69: 'r_5',
    70: 'r_6',
    71: 'r_7'
}

knobs = [16, 17, 18, 19, 20, 21, 22, 23]

sliders = [0, 1, 2, 3, 4, 5, 6, 7]

class Values:
    def __init__(self):
        self.roll   = 0   #     -50 ->    50
        self.pitch  = 0   #     -50 ->    50
        self.yaw    = 0   #    -200 ->   200
        self.thrust = 0   #   10000 -> 80000
        self.run = True

class Kontroller(Thread):
    def __init__(self, values):
        self.values = values
        Thread.__init__(self)
 
    def run(self):
        self.midiin = rtmidi.MidiIn()
        self.port = self.midiin.open_port(0)
        self.port.set_callback(self.midiCallback)
        while (self.values.run):
            time.sleep(100)

    def buttonDown(self, button):
        if (button == 'cycle'):
            print "Pressed cycle, shutting down"
            self.values.run = False

    def buttonUp(self, button):
        pass

    def twistedKnob(self, idx, value):
        if (idx == 0):
            self.values.thrust = value * 500

    def slidSlider(self, idx, value):
        if (idx == 0):
            self.values.roll = ((value - 64.0) / 64.0) * 50
        elif (idx == 1):
            self.values.pitch = ((value - 64.0) / 64.0) * 50
        elif (idx == 2):
            self.values.yaw = ((value - 64.0) / 64.0) * 200

    def midiCallback(self, message, data):
        control = message[0][1]
        value = message[0][2]
        if (buttons.has_key(control)):
            name = buttons[control]
            if (value == 127):
                return self.buttonDown(name)
            else:
                return self.buttonUp(name)
        else:
            try:
                idx = knobs.index(control)
                return self.twistedKnob(idx, value)
            except ValueError:
                pass
            try:
                idx = sliders.index(control)
                return self.slidSlider(idx, value)
            except ValueError:
                pass

class Flier(Thread):
    def __init__(self, values):
        self.values = values
        self.base_roll  =  0 # Compensating for imbalance in flier
        self.base_pitch =  -3 # Compensating for imbalance in flier
        self.base_yaw   =  0 # Compensating for imbalance in flier

        Thread.__init__(self)

    def connected(self, link):
        print "Connected to flier"

    def run(self):
        self.cf = crazyflie.Crazyflie(ro_cache='./cache/ro/', rw_cache='./cache/rw/')
        crtp.init_drivers()
        available = crtp.scan_interfaces()
        for i in available:
            print "Connecting"
            self.cf.connectSetupFinished.add_callback(self.connected)
            self.cf.open_link(i[0])
            break

        while (self.values.run):
            sys.stdout.write("\rThrust: %d, Roll: %d, Pitch: %d, Yaw: %d            " % (self.values.thrust, self.values.roll, self.values.pitch, self.values.yaw))
            sys.stdout.flush();
            r = self.values.roll + self.base_roll
            p = self.values.pitch + self.base_pitch
            y = self.values.yaw + self.base_yaw
            t = self.values.thrust
            self.cf.commander.send_setpoint(r, p, y, t)

if __name__ == '__main__':
    values = Values()
    flier = Flier(values)
    kontrol = Kontroller(values)
    flier.start()
    kontrol.start()

    while (values.run):
        time.sleep(100)
