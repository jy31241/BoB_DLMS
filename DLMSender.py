import argparse
import DLMS

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
    """
    Parses user flags passed to TorBot
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version",
                        action="store_true",
                        help="Show current version of DLMSender.")
    parser.add_argument("-q", "--quiet",
                        action="store_true")
    parser.add_argument("-p", "--port", required=True,
                        help="Enter the port to connect to. (ex. COM9, /dev/ttyUSB0)")
    parser.add_argument("-c", "--client",
                        help="Enter the address of the client to connect to. (decimal) default : 1")
    parser.add_argument("-s", "--server",
                        help="Enter the address of the server to connect to. (decimal) default : 111")


    return parser.parse_args()

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

    else:
        print("    usage: DLMSender.py -h")

    print("\n")

    return port, server, client

if __name__ == '__main__':

    try:
        port, server, client = main()

        con = DLMS.DLMS(port, server, client)
        data = con.SNRMquery()
        print("Request SNRM : " + data[0])
        print("Response SNRM : " + data[1])
        pwd = input("Password : ")
        data = con.AARQquery(pwd)

        print("\nAARQ : " + data[0])
        print("AARE : " + data[1])
        if len(data[1]) > 104:
            print("\nConnect !!!")
            usercmd = input(">> ")
            if usercmd == 'pwchg':
                userinputpw = input(": ")
                data = con.set_password_query(userinputpw)
                print("Set Password Request : " + data[0])
                if data[1][-8:-6] == '00':
                    print("Changed successfully : " + data[1])
                else:
                    print("FAIL !!")
            if usercmd == 'exit':
                exit()
            else:
                print(" ")
        else:
            print("Worng!!")

    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")


