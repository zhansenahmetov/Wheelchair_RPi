from enum import Enum

# Global state variable
WCState = 0

class State(Enum):
    CHARGER_UNAVAILABLE = 0
    CHARGER_AVAILABLE = 1
    CONNECTED_TO_CHARGER = 2
    CHARGER_COMPATIBLE = 3
    CHARGER_INCOMPATIBLE = 4
    AWAITING_CONNECTION= 5
    READY_TO_CHARGE = 6
    CHARGING_IN_PROGRESS = 7
    CHARGER_FAULTY = 8
    WC_FULLY_CHARGED = 9
    BATTERY_FAULTY = 10
    TERMINATED_BY_USER = 11
    # no 12 because only charger side differentiates plugged/unplugged
    CONNECTING_TO_CHARGER = 13
    REQUESTED = 14
    AWAITING_DISCONNECTION = 15
    # waiting states (unnecessary to the state machine, just to prevent user error)
    STARTING_CHARGE = 16
    DISCONNECTING = 17
    
if __name__ == "__main__":
    WCState = State.CHARGER_AVAILABLE