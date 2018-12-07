import serial
import pymysql
import make_CRC
import binascii
import obis_code
import os
import time
import struct


header = '7EA0'
footer = '7E'
LLC_Address = 'e6e600'
get_request = 'c00181'
set_request = 'c10181'
while_flag = 1

def strTolist(string):
    string = string.replace(' ','')
    tmp = list(string)
    byte = []
    for i in range(0, len(tmp), 2):
        byte.append(int(tmp[i]+tmp[i+1], 16))
    return byte

class DLMS():
    def __init__(self, serial_port, dst, src,baudrate):
        self.sr = serial.Serial(port=serial_port, baudrate=baudrate, timeout=1)
        self.dst = dst
        self.src = src
        self.control_field = [0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]
        self.control_field_order = 0

    def db_init(self):
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='root', db='dlms', charset='utf8mb4')
        return db
    def db_insert(self,db,data,date):
        cursor = db.cursor()
        cursor.execute("INSERT INTO data(data, date) VALUES ({},'{}')".format(data,date))
        db.commit()

    def getaddress(self):
        client = hex((int(self.src) + 16) * 2 + 1)[-2:]
        server = hex((int(self.dst) + 16) * 2 + 1)[-2:]
        if (int(self.src) + 16) * 2 + 1 > 111:
            client = '02' + client
        if (int(self.dst) + 16) * 2 + 1 > 111:
            server = '02' + server
        return [server, client]

    def SNRMquery(self):
        frame = '93'
        address = DLMS.getaddress(self)
        data = header[-2:]+format(int(len(header+address[0]+address[1]+frame)/2)+2,'#04x')[2:]+address[0]+address[1]+frame
        CRC = make_CRC.fcs16(strTolist(data))
        send_data = header + format(int(len(header+address[0]+address[1]+frame)/2)+2,'#04x')[2:] + address[0] + address[1] + frame + CRC + footer
        #send SNRM
        self.sr.write(serial.to_bytes(strTolist(send_data)))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        return [send_data, recv_data]

    def AARQquery(self, userinputpwd):
        address = DLMS.getaddress(self)
        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        self.control_field_order += 1

        pwd = list(str(userinputpwd))
        for i in range(len(pwd)):
            pwd[i] = hex(ord(pwd[i]))[-2:]
        pwd = "".join(pwd)

        LLC_Address = 'e6e600'
        a_data = '6036A1090607608574050801018A0207808B0760857405080201AC0A8008'
        b_data = 'BE10040E01000000065F1F040000181DFFFF'

        length = hex(int((len(header[-2:] + address[0] + address[
            1] + frame + LLC_Address + a_data + pwd + b_data)/2) + 1 + 4))

        FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))

        HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + a_data + pwd + b_data))

        send_data = header + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + a_data + pwd + b_data + HCS + footer

        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        return [send_data, recv_data]

    def set_password_query(self, userinputpw):
        chg_password_obis = '000f0000280000ff'
        att_id = '0700'
        obis_len = '0908'

        pwd = list(userinputpw)
        for i in range(len(pwd)):
            pwd[i] = hex(ord(pwd[i]))[-2:]
        pwd = "".join(pwd)

        address = DLMS.getaddress(self)

        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        self.control_field_order += 1

        length = hex(int(len(header[-2:] + address[0] + address[
            1] + frame + LLC_Address + set_request + chg_password_obis + att_id + obis_len + pwd)/2 + 1 + 4))  # 1=length_byte, 4=FCS+HCS length

        FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))
        HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS +LLC_Address + set_request + chg_password_obis + att_id + obis_len + pwd))

        send_data = header + length[-2:] + address[0] + address[
            1] + frame +FCS + LLC_Address + set_request + chg_password_obis + att_id + obis_len + pwd + HCS + footer

        #send SNRM
        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        return [send_data, recv_data]

    def blackout(self, inputlimit):
        chg_limit_obis = list(obis_code.electric_thredhold_obis.keys())[0]
        att_id = obis_code.electric_thredhold_obis.get(chg_limit_obis)
        obis_len = '12'
        round(inputlimit,1)
        limit = format(inputlimit,'04x')

        address = DLMS.getaddress(self)

        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        self.control_field_order += 1

        length = hex(int(len(header[-2:] + address[0] + address[
            1] + frame + LLC_Address + set_request + chg_limit_obis + att_id + obis_len + limit)/2 + 1 + 4))  # 1=length_byte, 4=FCS+HCS length

        FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))
        HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS +LLC_Address + set_request + chg_limit_obis + att_id + obis_len + limit))

        send_data = header + length[-2:] + address[0] + address[
            1] + frame +FCS + LLC_Address + set_request + chg_limit_obis + att_id + obis_len + limit + HCS + footer

        #send SNRM
        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        return [send_data, recv_data]

    def set_baudrate(self,userinput):
        chg_baudrate_obis = list(obis_code.baudrate_obis.keys())[0]
        att_id = obis_code.baudrate_obis.get(chg_baudrate_obis)
        obis_len = '16'

        if userinput == '9600':
            userinput = '05'
        elif userinput == '19200':
            userinput = '06'
        elif userinput == '38400':
            userinput = '07'
        elif userinput == '57600':
            userinput = '08'
        elif userinput == '115200':
            userinput = '09'
        else:
            print("Please Input correct value")
            print("your input = {}".format(userinput))
            print("type={}".format(type(userinput)))
            return False
        baudrate = userinput
        address = DLMS.getaddress(self)
        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        self.control_field_order += 1

        length = hex(int(len(header[-2:] + address[0] + address[
            1] + frame + LLC_Address + set_request + chg_baudrate_obis + att_id + obis_len + baudrate) / 2 + 1 + 4))

        FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))
        HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + set_request + chg_baudrate_obis + att_id + obis_len + baudrate))
        print(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + set_request + chg_baudrate_obis + att_id + obis_len + baudrate)

        send_data = header + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + set_request + chg_baudrate_obis + att_id + obis_len + baudrate + HCS + footer

        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        return [send_data, recv_data]

    def get_time(self):
        date_obis = list(obis_code.date_obis.keys())[0]
        att_id = obis_code.date_obis.get(date_obis)
        address = DLMS.getaddress(self)
        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        self.control_field_order += 1

        length = hex(int(len(header[-2:] + address[0] + address[
            1] + frame + LLC_Address + get_request + date_obis + att_id) / 2 + 1 + 4))  # 1=length_byte, 4=FCS+HCS length

        FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))
        HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + get_request + date_obis + att_id))

        send_data = header + length[-2:] + address[0] + address[
            1] + frame + FCS + LLC_Address + get_request + date_obis + att_id + HCS + footer

        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        date = recv_data[-30:-14]
        def date_convert(date):
            import datetime
            year = int(date[0:4],16)
            month = int(date[4:6],16)
            day = int(date[6:8],16)
            hour = int(date[10:12],16)
            minute = int(date[12:14],16)
            second = int(date[14:16],16)
            date = "{}-{}-{} {}:{}:{}".format(year,month,day,hour,minute,second)
            return datetime.datetime.strptime("{}".format(date), "%Y-%m-%d %H:%M:%S")
        date = date_convert(date)
        return date
    def sniff_mode(self,server_addr):
        os.system('CLS')
        print("#########################")
        print("######Sniffing Mode######")
        print("#########################")
        print("현월 누적 전력량\n")
        print("If you want to exit program, raise KeyboardInterrupt by pressing 'Ctrl + C' \n")
        power_obis = list(obis_code.active_power.keys())[0]
        att_id = obis_code.active_power.get(power_obis)
        self.dst = server_addr
        db = self.db_init()
        while True:
            try:
                address = DLMS.getaddress(self)
                frame = hex(self.control_field[self.control_field_order % 8])[-2:]
                self.control_field_order += 1
                length = hex(int(len(header[-2:] + address[0] + address[
                    1] + frame + LLC_Address + get_request + power_obis + att_id) / 2 + 1 + 4))  # 1=length_byte, 4=FCS+HCS length
                FCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[1] + frame))
                HCS = make_CRC.fcs16(strTolist(header[-2:] + length[-2:] + address[0] + address[
                    1] + frame + FCS + LLC_Address + get_request + power_obis + att_id))

                send_data = header + length[-2:] + address[0] + address[
                    1] + frame + FCS + LLC_Address + get_request + power_obis + att_id + HCS + footer
                self.sr.write(serial.to_bytes(strTolist((send_data))))
                recv_data = binascii.hexlify(self.sr.readall()).decode()
                power = int(recv_data[-13:-6],16)
                date = self.get_time()
                self.db_insert(db,power,date)
                print("{} => {}Wh".format(date.strftime("%Y-%m-%d %H:%M:%S"),power))
                time.sleep(5)
            except KeyboardInterrupt:
                exit()

'''con = DLMS('COM7',68,1,9600)
con.SNRMquery()
con.AARQquery('1A2B3C4D')
con.blackout(500)'''