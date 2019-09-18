# libs
import socket
import sys
import json
import os
import time
import struct
import logging
import csv
import netifaces


# CONSTANTS
DEFAULT_UDP_PORT_NO = 6789                      # UDP Port

def runMulticastListener(interfaceV6, nodelogger):
    multicastaddress = "ff02::1" + "%" + interfaceV6
    hadd = socket.getaddrinfo(multicastaddress, 8080, socket.AF_INET6, socket.SOCK_DGRAM)
    haddr = socket.getaddrinfo(multicastaddress, 8080, socket.AF_INET6, socket.SOCK_DGRAM)[0][-1]

    nodelogger.debug(hadd)
    nodelogger.debug(haddr)
    
    # Initialise socket for IPv6 datagrams
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
     
    # Allows address to be reused
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Binds to all interfaces on the given port
    #sock.bind(('', 8080))
    sock.bind(haddr)

    # Allow messages from this socket to loop back for development
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)

    # Construct message for joining multicast group
    mreq = struct.pack("16s15s".encode('utf-8'), socket.inet_pton(socket.AF_INET6, "ff02::1"), (chr(0) * 16).encode('utf-8'))
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)

    run = True
    try:
        while run==True:
            data, addr = sock.recvfrom(1024)
            nodelogger.debug("\nGot Message: " + str(data) +" | from: " + str(addr))
            print "\nGot Message: " + str(data) +" | from: " + str(addr) + "\n"
  
            messageobject = json.loads(data)

            if messageobject['type'] == "car" or messageobject['type'] == "streetlightcarinfo":
                nodelogger.debug("Received Message from a car/streetlight")
                #print "Received Message from a car/streetlight"
                received_messagetype = messageobject['type']
                received_waypoints = messageobject['waypoints']
                received_timestamp = messageobject['timestamp']
                received_scenarioid = messageobject['scenarioid']
                received_ttl = messageobject['ttl']
                nodelogger.debug("ReceivedMessageType="+str(received_messagetype))
                nodelogger.debug("ReceivedWaypoints="+str(received_waypoints))
                nodelogger.debug("ReceivedTimestamp="+str(received_timestamp))
                nodelogger.debug("ReceivedScenarioID="+str(received_scenarioid))
                nodelogger.debug("ReceivedTimeToLive="+str(received_ttl))
            

    except KeyboardInterrupt:
        sock.close()
        print >>sys.stderr, "terminating ..."
        exit(0)



def setuplogger(wifiinterface, mode):
    starttime = time.strftime("%y_%m_%d-%H_%M_%S")
    filenametext = "zz_log_"+starttime+"_"+wifiinterface +"_"+mode+".log"
     # set up logging to file - see previous section for more details
    log_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
    log_fname = os.path.join(log_dir, filenametext)
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    filename=log_fname,
                    filemode='w')

    

def checkArguments(localConfigExists):
    if len(sys.argv) < 2 and localConfigExists:
        print "No argument specified"
        sys.exit()

    if len(sys.argv) < 3 and localConfigExists == False:
        print "Not enough arguments specified. (Maybe you are missing the initial streetlight number, if no configfile is present.)"
        sys.exit()

    client = False
    server = False
    car = False
    livecar = False
    arbiter = False
    interfaceV6 = ""
    coord_GPS_LAT = "-999"
    coord_GPS_LON = "-999"
    coord_X = "-999"
    coord_Y = "-999"
    coord_Z = "-999"

    if sys.argv[1] == "--livecar":
        print "LIVECAR MODE"
        livecar = True
        if len(sys.argv) > 2:
            if sys.argv[2] != "":
                interfaceV6 = sys.argv[2]
                print "      + INTERFACE ipV6: " + str(interfaceV6)

    if sys.argv[1] == "--arbiter":
        print "ARBITER MODE"
        arbiter = True
        if len(sys.argv) > 2:
            if sys.argv[2] != "":
                interfaceV6 = sys.argv[2]
                print "      + INTERFACE ipV6: " + str(interfaceV6)

    if arbiter != True:                
        if sys.argv[3] == "--xyz" and livecar==True:
            print "XYZ will be set"
            if len(sys.argv) > 6:
                if sys.argv[4] != "":
                    coord_X = sys.argv[4]
                    print "      + COORD_X: " + str(coord_X)
                if sys.argv[5] != "":
                    coord_Y = sys.argv[5]
                    print "      + COORD_Y: " + str(coord_Y)
                if sys.argv[6] != "":
                    coord_Z = sys.argv[6]
                    print "      + COORD_Z: " + str(coord_Z)

    # Now return stuff. 
    if client == False and server == False and arbiter == False and car == False and livecar == False:
        print "No Mode chosen, closing programm."
        sys.exit()

    if arbiter:
        return "arbiter", -999, interfaceV6, coord_GPS_LAT, coord_GPS_LON, coord_X, coord_Y, coord_Z

    if livecar:
        return "livecar", -999, interfaceV6, coord_GPS_LAT, coord_GPS_LON, coord_X, coord_Y, coord_Z


def sendMulticastIPv6(message, interfaceV6):
    multicastaddress = "ff02::1" + "%" + interfaceV6
    socketinfo = socket.getaddrinfo(multicastaddress, 8080, socket.AF_INET6)
    scopeID = socketinfo[0][4][3]
    flowInfo = socketinfo[0][4][2]

    # Create ipv6 datagram socket
    sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

    # Allow own messages to be sent back (for local testing)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
    sock.sendto(message, ("ff02::1", 8080,flowInfo, scopeID))

def runCar(waypoints, timestamp, interfaceV6, withneihbordeamon, DEFAULT_UDP_PORT_NO, carlogger):
    carlogger.debug('Running a car step at ' + str(timestamp))
    
    mymessage = {}
    mymessage['type'] = "car"
    mymessage['scenarioid'] = "1"
    mymessage['waypoints'] = waypoints
    mymessage['timestamp'] = timestamp
    mymessage['ttl'] = 1
    jsonmessage = json.dumps(mymessage)
    Message = jsonmessage
    sendMulticastIPv6(Message, interfaceV6)
    carlogger.debug("Messagesend: " + jsonmessage)


def main():
    # Use only, if not already created:
    # createGlobalStreetlightYaml(lampenkarte50)
    mode, currentid, interfaceV6, coord_GPS_LAT, coord_GPS_LON, coord_X, coord_Y, coord_Z = checkArguments(False)

    if mode == "arbiter":
        setuplogger(interfaceV6,"node")
        nodeloggername = "node_"+interfaceV6
        nodelogger = logging.getLogger(nodeloggername)
        nodelogger.debug("Starting Node " + interfaceV6 + " as arbiter")
        nodelogger.debug("ARGs were: " + str(sys.argv))
        nodelogger.debug("     Mode: " + str(mode))
        nodelogger.debug("     InterfaceV6:" + str(interfaceV6))

        runMulticastListener(interfaceV6, nodelogger)
        sys.exit()

    if mode == "livecar":
        withneighbordeamon = False

        livecar_filenametext = "livecar.csv"
        livecar_dir = os.path.join(os.path.normpath(os.getcwd() + os.sep + os.pardir), 'logs')
        livecar_fname = os.path.join(livecar_dir, livecar_filenametext)

        setuplogger(interfaceV6,"car")
        carloggername = "livecar_"+interfaceV6
        carlogger = logging.getLogger(carloggername)
        carlogger.debug("Starting Node " + interfaceV6 + " as livecar")
        carlogger.debug("Car is currently at:")
        carlogger.debug( coord_X )
        carlogger.debug( coord_Y )
        carlogger.debug( coord_Z )

        # convert to float
        coord_X = float(coord_X)
        coord_Y = float(coord_Y)
        coord_Z = float(coord_Z)

        mode, currentid, interfaceV6, coord_GPS_LAT, coord_GPS_LON, coord_X, coord_Y, coord_Z

        ts = time.time()

        fields=[ts,coord_X,coord_Y,coord_Z]
        with open(livecar_fname, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)

        waypointswithtimestamps = []
        waypoints = []
        with open(livecar_fname, "r") as scraped:
            reader = csv.reader(scraped, delimiter=',')
            row_index = 0
            for row in reader:
                if row:  # avoid blank lines
                    row_index += 1
                    columnswithtimestamp = [row[0], row[1], row[2], row[3]]
                    columns = [float(row[1]), float(row[2]), float(row[3])]
                    waypoints.append(columns)
                    waypointswithtimestamps.append(columnswithtimestamp)
        print "waypoints:"
        print waypoints

        runCar(waypoints[:5], ts,interfaceV6, withneighbordeamon, DEFAULT_UDP_PORT_NO, carlogger)
        sys.exit()

def getV6WithInterfaceString(interfacename):
    addrs = netifaces.ifaddresses(interfacename)
    v6Adress = addrs[netifaces.AF_INET6][0]['addr']
    return v6Adress

if __name__ == "__main__":
    main()

