from enumchoicefield import ChoiceEnum


class ThingType(ChoiceEnum):
    BCN_I = "Bluetooth iBeacon"
    BCN_EDDY = "Bluetooth Eddystone Beacon"
