import argparse
import DLMS
import command

__VERSION = "1.0"

def title():

    title = r"""
    
        ____  __    __  ________                __         
       / __ \/ /   /  |/  / ___/___  ____  ____/ /__  _____ver 1.0
      / / / / /   / /|_/ /\__ \/ _ \/ __ \/ __  / _ \/ ___/
     / /_/ / /___/ /  / /___/ /  __/ / / / /_/ /  __/ /    
    /_____/_____/_/  /_//____/\___/_/ /_/\____/\___/_/     by.bl@ckout
        
     """
    print(title)

def get_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version",
                        action="store_true",
                        help="Show current version of DLMSender.")
    parser.add_argument("-q", "--quiet",
                        action="store_true")
    parser.add_argument("-p", "--port", required=True,
                        help="Enter the port for connecting. (ex. COM9, /dev/ttyUSB0)")
    parser.add_argument("-c", "--client",
                        help="Enter the address of the client for connecting. (decimal) default : 1")
    parser.add_argument("-s", "--server",
                        help="Enter the address of the server for connecting. (decimal) default : 111")
    parser.add_argument("-b", "--baudrate",
                        help="Enter the value of the baudrate for connecting. (decimal) default : 9600")


    return parser.parse_args()
def print_list():
    print("==================================")
    print("1. Change password")
    print("2. BL4CK0UT")
    print("3. Change BaudRate")
    print("4. Active Power Sniff Mode")
    print("5. Exit Program")
    print("==================================")
def main():
    args = get_args()
    if args.version:
        print("DLMSender Version:" + __VERSION)
        exit()
    if not args.quiet:
        title()
    if args.port:
        port = args.port
    if args.client:
        client = args.client
    if args.server:
        server = args.server
    if args.baudrate:
        baudrate = args.baudrate

    else:
        print("    usage: DLMSender.py -h")

    return port, server, client , baudrate

if __name__ == '__main__':

    try:
        port, server, client,baudrate = main()

        con = DLMS.DLMS(port, server, client,baudrate)
        data = con.SNRMquery()
        print("Request SNRM : " + data[0])

        if data[1] == "":
            print("\nNot Response!!")
            exit()

        print("Response SNRM : " + data[1])
        pwd = input("Password : ")
        data = con.AARQquery(pwd)
        print("\nAARQ : " + data[0])
        print("AARE : " + data[1])
        if len(data[1]) > 104:
            print("\nConnected Successfully !!!")
            while True:
                print_list()
                usercmd = input(">> ")
                if usercmd == '1':  # change password
                    userinputpw = input("Enter password to change : ")
                    data = con.set_password_query(userinputpw)
                    print("Set Password Request : " + data[0])
                    if data[1][-8:-6] == '00':
                        print("Changed successfully : " + data[1])
                    else:
                        print("FAIL !!")
                elif usercmd == '2':  # change electric thredhold
                    userinputlimit = input("Enter limit to change (5~#) : ")
                    if 5<userinput<1000:
                        data = con.blackout(userinputlimit)
                        print("Set limit Request : " + data[0])
                        if data[1][-8:-6] == '00':
                            print("Changed successfully : " + data[1])
                        else:
                            print("FAIL !!" + data[1])
                    else:
                        print("Please Input correct number")
                        continue
                elif usercmd == '3': # change baudrate
                    userinput = str(input("Enter limit to change : \n9600, 19200, 38400, 57600, 115200\n"))
                    data = con.set_baudrate(userinput)
                    if data == False:
                        print("Please Input correct value")
                        continue
                    print("Set baudrate Request : " + data[0])
                    if data[1][-8:-6] == '00':
                        print("Changed successfully : " + data[1])
                    else:
                        print("FAIL !!" + data[1])
                elif usercmd == '4':
                    print("Please input the last two digits of the Manufacturing number")
                    print("ex)0145268 => 68")
                    number = int(input(">> "))
                    if number<1 or number >110:
                        print("Please Input correct number")
                        continue
                    con.sniff_mode(number)
                elif usercmd == '5':
                    exit()
                else:
                    print("Please Input correct number")
        else:
            print("Wrong!!")

    except KeyboardInterrupt:
        print("\nInterrupt received! Exiting cleanly...")
    except UnboundLocalError:
        print("    Invalid option. ")
        print("    Please Input correct option\n")


