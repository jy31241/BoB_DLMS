import serial
import time
import make_CRC

header = '7EA0'
footer = '7E'
control_field_order = 0
control_field = [0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]


def strTolist(string):
    temp = string.split(' ')  # 공백 제거
    for i in range(len(temp)):
        temp[i] = int(temp[i], 16)
    return temp


class DLMS():
    def __init__(self, serial_port, dst, src):
        self.sr = serial.Serial(port=serial_port, baudrate=9600, timeout=1)
        self.send_list = []
        self.recv_list = []
        self.dst = dst
        self.src = src
        self.control_field = [0x10, 0x32, 0x54, 0x76, 0x98, 0xBA, 0xDC, 0xFE]
        self.control_field_order = 0

    '''def getaddress(self.dst,self.src):

        return client, server
    '''

    def SNRMquery(self):
        frame = '93'
        client = hex((int(self.src) + 16) * 2 + 1)[-2:]
        server = hex((int(self.dst) + 16) * 2 + 1)[-2:]

        if (int(self.src) + 16) * 2 + 1 > 111:
            client = '02' + hex((int(self.src) + 16) * 2 + 1)[-2:]
        if (int(self.dst) + 16) * 2 + 1 > 111:
            server = '02' + hex((int(self.dst) + 16) * 2 + 1)[-2:]

        CRC = make_CRC.fcs16(header+str(int(len(header+server+client+frame)/2,16))+server+client+frame)
        print(int(str(int(len(header + server + client + frame) / 2 + 2)), 16))
        # print(CRC)
        print("{}\n{}\n{}\n{}\n{}\n{}\n{}".format(header, str(len(header + server + client + frame + CRC) / 2), server,
                                                  client, frame, CRC, footer))
        send_data = strTolist(header + str() + server + client + frame + CRC + footer)

        self.send_list.append(send_data)
        # SNRM 전송
        self.sr.write(serial.to_bytes(strTolist((send_data))))
        recv_data = self.sr.readall()
        self.recv_list.append(recv_data)
        time.sleep(1)
        return [send_data, recv_data]


    def AARQquery(self):
        snrm_header = self.SNRMquery()[0][:-8]
        control_byte = control_field[self.control_field_order % 8]
        self.control_field_order += 1
        crc1 = make_CRC.fcs16(snrm_header)
        aarq_header = 'e6 e6 00'
        password = '31 41 32 42 33 43 34 44'


    def connect(self, serialport):
        # SNRM
        self.SNRMquery()
        self.AARQquery()
        arr1 = '7E A0 08 02 FF 23 93 A1 7D 7E'
        # AARQ
        arr2 = '7E A0 45 02 FF 23 10 64 76 E6 E6 00 60 36 A1 09 06 07 60 85 74 05 08 01 01 8A 02 07 80 8B 07 60 85 74 05 08 02 01 AC 0A 80 08 31 41 32 42 33 43 34 44 BE 10 04 0E 01 00 00 00 06 5F 1F 04 00 00 18 1D FF FF 44 e6 7E'
        # set
        # arr3 = '7E A0 24 02 FF 23 54 B3 D8 E6 E6 00 C1 01 81 00 08 00 00 01 00 00 FF 02 00 09 08 07 E2 04 0C 04 0A 22 39 24 d6 7E'
        # get
        # 시간 변경
        # arr4 = '7E A0 28 02 FF 23 32 B3 A9 E6 E6 00 C1 01 81 00 08 00 00 01 00 00 FF 02 00 09 0C 07 E2 0A 0F 01 10 00 00 FF FD E4 5D 83 6B 7E'
        arr4 = '7E A0 1A 02 FF 23 32 EA 6B E6 E6 00 C0 01 81 00 0f 00 00 28 00 00 FF 07 00 2c e0 7E'
        # 패스워드 조회
        # arr4 = '7e a0 24 02 FF 23 32 83 de e6 e6 00 c1 01 81 00 0f 00 00 28 00 00 ff 07 00 09 08 31 31 31 31 31 31 31 31 75 4a 7e'
        # 패스워드 변경
        arr5 = '7E A0 08 02 FF 23 53 AD BB 7E'


con = DLMS('COM9', 111, 1)
data = con.SNRMquery()





