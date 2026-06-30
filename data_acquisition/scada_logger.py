import time
import csv
from datetime import datetime
from pymodbus.client import ModbusTcpClient

# Modbus Server Configuration (OpenPLC Runtime)
PLC_IP = '127.0.0.1'
PLC_PORT = 502

# Data Logging Configuration
CSV_FILENAME = 'scada_attack_data.csv'
SAMPLING_RATE_SECONDS = 0.5

# Defining the exact dataset headers based on Factory I/O architecture
HEADERS = [
    'Timestamp',
    'Tank0_Level', 'Tank1_Level', 'Tank2_Level', 'Mix_Ratio',
    'Valve0_Fill', 'Valve0_Disch', 'Valve1_Fill', 'Valve1_Disch',
    'Valve2_Fill', 'Valve2_Disch'
]

def main():
    client = ModbusTcpClient(PLC_IP, port=PLC_PORT)

    if not client.connect():
        print("[ERROR] Cannot connect to OpenPLC Modbus server.")
        return

    print("[INFO] Connected. Acquiring accurate baseline data...")
    
    with open(CSV_FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)

        try:
            while True:
                # Based on Factory I/O Driver Mapping:
                # Actuators (Valves) are mapped to Input Registers
                actuators = client.read_input_registers(address=0, count=6)
                
                # Sensors (Levels, Mix Ratio) are mapped to Holding Registers
                sensors = client.read_holding_registers(address=0, count=4)

                if actuators.isError() or sensors.isError():
                    print("[WARNING] Modbus read error. Retrying...")
                    time.sleep(1)
                    continue

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                # Exact hardware-to-memory mapping
                data_row = [
                    timestamp,
                    sensors.registers[0],   # Holding Reg 0: Tank0_Level
                    sensors.registers[1],   # Holding Reg 1: Tank1_Level
                    sensors.registers[2],   # Holding Reg 2: Tank2_Level
                    sensors.registers[3],   # Holding Reg 3: Mix_Ratio
                    actuators.registers[0], # Input Reg 0: Valve0_Fill
                    actuators.registers[1], # Input Reg 1: Valve0_Disch
                    actuators.registers[2], # Input Reg 2: Valve1_Fill
                    actuators.registers[3], # Input Reg 3: Valve1_Disch
                    actuators.registers[4], # Input Reg 4: Valve2_Fill
                    actuators.registers[5]  # Input Reg 5: Valve2_Disch
                ]

                writer.writerow(data_row)
                file.flush() # Force write to disk immediately

                print("Logged ->", data_row)
                time.sleep(SAMPLING_RATE_SECONDS)

        except KeyboardInterrupt:
            print("\n[INFO] Data acquisition stopped. File saved: {}".format(CSV_FILENAME))
        finally:
            client.close()

if __name__ == "__main__":
    main()