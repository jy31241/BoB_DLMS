import make_CRC
import DLMS
"""
    93
    10
    32
    54
    76
    98
    BA
    DC
    FE
    10
    32
    54
"""
#arr4 = '7E A0 24 02 FF 23 32 83 de e6 e6 00 c1 01 81 00 0f 00 00 28 00 00 ff 07 00 09 08 31 31 31 31 31 31 31 31 75 4a 7e'
#arr4 = '7E A0 24 02 ff 23 32 83 de e6 e6 00 c1 01 81 00 0f 00 00 28 00 00 ff 07 00 09 08 31 41 32 42 33 43 34 44 ff 9f 7E
#arr4 = '7E A0 24 02 ff 23 32 83 de e6 e6 00 c1 01 81 00 0f 00 00 28 00 00 ff 07 00 09 08 31 41 32 42 33 43 34 44 ff 9f 7E
header = '7EA0'
footer = '7E'
#CRC = make_CRC.crc16(strTolist(header[-2:] + " " + server + " " + client + " " + frame))


def query(dst, src, password):
    print(DLMS.SNRMquery(dst, src))
    """
    client = hex((int(src) + 16)*2+1)[-2:]
    server = hex((int(dst) + 16)*2+1)[-2:]
    frame = 'xx'
    FCS =
    LLC_Address = 'e6e600'
    set_request = 'c10181'
    chg_password_obis = '0181000f0000280000ff'
    att_id = '0700'
    obis_len = '0908'
    crcsize = 4

    x = '7E A0 08 02 FF 23 93 A1 7D 7E'
    length = hex((len(header+server+client+frame)))

    HCS = header[-2:] + length + server + client + frame
    if (int(src) + 16)*2+1 > 111:
        client = '02' + hex((int(src) + 16)*2+1)[-2:]

    if (int(dst) + 16)*2+1 > 111:
        server = '02' + hex((int(dst) + 16)*2+1)[-2:]

    packet = header + length + server + client + HCS + LLC_Address + set_request + chg_password_obis + att_id + obis_len + password + FCS + footer
    """

query(111, 1, 'asdasd')