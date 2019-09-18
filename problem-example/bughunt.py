#!/usr/bin/python

"""This example shows how to work in adhoc mode

sta1 <---> sta2 <---> sta3"""

import sys
import subprocess
import csv
from datetime import datetime
from time import sleep


from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


amountOfNodes = 9
wifi_ssid="6mesh"
wifi_mode="g"
wifi_channel=11
csvname="convert_output_xy_in_m.csv"

def setupPacketDumping():
    #now = datetime.today().strftime('%Y_%m_%d-%H_%M_%S')
    print "Starting hwsim0"
    hwsim0up = "ifconfig hwsim0 up"
    processA = subprocess.Popen(hwsim0up.split(), stdout=subprocess.PIPE)
    output, error = processA.communicate()
    print output
    if error:
        print "Error happened"
        print error
        print "Exiting program"
        sys.exit()
    

def topology(autoTxPower):
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    nodes = {}
    
    nodes['sta1'] = net.addStation('sta1', position='10,10,0')
    nodes['sta2'] = net.addStation('sta2', position='30,10,0')
    nodes['sta3'] = net.addStation('sta3', position='50,10,0')
    nodes['sta4'] = net.addStation('sta4', position='70,10,0')
    nodes['sta5'] = net.addStation('sta5', position='90,10,0')

    car1 = net.addStation('car1', position='10.0,20.0,0.0', range=30)
    arbiter1 = net.addStation('arbiter1', position='45.0,20.0,0.0', range=50)

    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    for key in nodes.keys():
        print key
        print nodes.get(key)
        print "Command is addLink" + str(nodes.get(key)) + " cls=" + str(adhoc) + "ssid=" + wifi_ssid
        net.addLink(nodes[key], cls=adhoc, ssid=wifi_ssid, mode=wifi_mode, channel=wifi_channel, ht_cap='HT40+')

    net.addLink(car1, cls=adhoc, ssid='6mesh', mode='g', channel=11, ht_cap='HT40+')
    net.addLink(arbiter1, cls=adhoc, ssid='6mesh', mode='g', channel=11, ht_cap='HT40+')
    
    net.plotGraph(max_x=200, max_y=200)
    info("*** Setting up static mobility\n")
    
    net.startMobility(time=50, repetitions=10)
    net.mobility(car1, 'start', time=51, position='10.0,15.0,0.0')
    net.mobility(car1, 'stop', time=180, position='90.0,15.0,0.0')
    net.stopMobility(time=3600)
    
    # 2:34
    info("*** Starting network\n")
    net.build()
    sleep(10)

    info("*** Start hwsim0\n")
    setupPacketDumping()

    info("*** Addressing...\n")
    
    for key in nodes.keys():
        #print key
        #print nodes.get(key).params['wlan'][0]
        nodes.get(key).cmd('iwconfig %s mode ad-hoc essid 6mesh ap 00:00:26:09:19:88 channel 11' % (nodes.get(key).params['wlan'][0]))
        nodes.get(key).cmd('ip link set up dev %s' % (nodes.get(key).params['wlan'][0]))
        
             
    car1.cmd('iwconfig car1-wlan0 mode ad-hoc essid 6mesh ap 00:00:26:09:19:88 channel 11')
    car1.cmd('ip link set up dev car1-wlan0')

    arbiter1.cmd('iwconfig arbiter1-wlan0 mode ad-hoc essid 6mesh ap 00:00:26:09:19:88 channel 11')
    arbiter1.cmd('ip link set up dev arbiter1-wlan0')

    #print car1.params['position']
    
    info("*** Sleeping for link local generation...\n")
    sleep(10)
   
    info("*** Starting nodes...\n")
    arbiter1.cmd('python2 geonode.py --arbiter arbiter1-wlan0 &')

    for key in nodes.keys():
        command = "python2 loggingnode.py --arbiter "
        commandtext = command + str(nodes.get(key)) + "-wlan0 &"
        nodes.get(key).cmd(commandtext)
    print "Starting nodes: done"

    sleep(10)
    for i in range(0,300):
        car1paramtext = str(str(car1.params['position'][0]) + " " +str( car1.params['position'][1]) + " " + str(car1.params['position'][2]))
        car1.cmd('python2 loggingnode.py --livecar car1-wlan0 --xyz ' + car1paramtext)
        sleep(1)

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('debug') 
    autoTxPower = True if '-a' in sys.argv else False
    topology(autoTxPower)
    

