from enum import Enum, auto


class Speed(Enum):
    SPEED_1GB = auto()
    SPEED_5GB = auto()
    SPEED_10GB = auto()
    SPEED_25GB = auto()
    SPEED_40GB = auto()
    SPEED_50GB = auto()
    SPEED_100GB = auto()

    def get_gnmi_val(self):
        return f"openconfig-if-ethernet:{self.name}"
    
    def __str__(self) -> str:
        return self.name