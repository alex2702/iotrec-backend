from enumchoicefield import ChoiceEnum


class ThingType(ChoiceEnum):
    IBEAC = "Bluetooth iBeacon"
    EDDY = "Bluetooth Eddystone Beacon"
