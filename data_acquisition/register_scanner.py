import time
from pymodbus.client import ModbusTcpClient

# Modbus Server Configuration (OpenPLC Runtime)
PLC_IP = '127.0.0.1'
PLC_PORT = 502

def scan_plc_memory():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)
    
    if not client.connect():
        print("[ERROR] Cannot connect to PLC Modbus Server.")
        return

    print("[INFO] Memory Scanner Active. Press Ctrl+C to stop.")
    print("[INFO] Watching Registers 0 to 14...\n")

    try:
        while True:
            # Read first 15 Input Registers (%IW)
            input_regs = client.read_input_registers(address=0, count=15)
            
            # Read first 15 Holding Registers (%MW / %QW)
            holding_regs = client.read_holding_registers(address=0, count=15)

            if not input_regs.isError() and not holding_regs.isError():
                print("------------------------------------------------------------------")
                print("[Input Registers   0..14] : {}".format(input_regs.registers))
                print("[Holding Registers 0..14] : {}".format(holding_regs.registers))
            else:
                print("[WARNING] Read Error occurred during scan.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Memory scan terminated by user.")
    finally:
        client.close()

if __name__ == "__main__":
    scan_plc_memory()