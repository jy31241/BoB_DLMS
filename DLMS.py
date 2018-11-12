import serial
import time
import make_CRC
import binascii

header = '7EA0'
footer = '7E'
control_field_order = 0
control_field = [0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]


def strTolist(string):
    string = string.replace(' ','')
    tmp = list(string)
    byte = []
    for i in range(0, len(tmp), 2):
        byte.append(int(tmp[i]+tmp[i+1], 16))
    return byte


class DLMS():
    def __init__(self, serial_port, dst, src):
        self.sr = serial.Serial(port=serial_port, baudrate=9600, timeout=1)
        self.send_list = []
        self.recv_list = []
        self.dst = dst
        self.src = src
        self.control_field = [0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]
        self.control_field_order = 0

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
        self.send_list.append(send_data)
        #send SNRM
        self.sr.write(serial.to_bytes(strTolist(send_data)))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        self.recv_list.append(recv_data)
        time.sleep(1)
        return [send_data, recv_data]


    def AARQquery(self, userinputpwd):
        address = DLMS.getaddress(self)
        frame = hex(self.control_field[self.control_field_order % 8])[-2:]
        control_byte = control_field[0]
        self.control_field_order += 1

        pwd = list(userinputpwd)
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
        self.recv_list.append(recv_data)
        time.sleep(1)
        return [send_data, recv_data]

    def set_password_query(self, userinputpw):
        LLC_Address = 'e6e600'
        set_request = 'c10181'
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

        self.send_list.append(send_data)
        #send SNRM
        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = binascii.hexlify(self.sr.readall()).decode()
        self.recv_list.append(recv_data)
        time.sleep(1)
        return [send_data, recv_data]

"""
con = DLMS('/dev/tty.usbserial-143101', 111, 1,'BOBDFNO1')
data = con.SNRMquery()

data = con.AARQquery()

data =con.set_password_query()
"""






