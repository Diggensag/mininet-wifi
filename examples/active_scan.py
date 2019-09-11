#!/usr/bin/python

'This example shows how to work with active scan'

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import UserAP
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi


def topology():
    "Create a network."
    net = Mininet_wifi(controller=Controller, accessPoint=UserAP)

    info("*** Creating nodes\n")
    net.addStation('sta1', wpa_passphrase='123456789a,123456789a', wpa='2,2',
                   wlans=2, active_scan=1, scan_freq='2412,2437',
                   freq_list='2412,2437', position='5,10,0')
    net.addStation('sta2', wpa_passphrase='123456789a', wpa='2', active_scan=1,
                   scan_freq='2437', freq_list='2437', position='45,10,0')
    ap1 = net.addAccessPoint('ap1', ssid="ssid-1", mode="g", channel="1",
                             wpa_passphrase='123456789a', wpa='2', wpa_key_mgmt='WPA-PSK',
                             wpa_pairwise='CCMP', auth_algs='1', position='10,10,0')
    ap2 = net.addAccessPoint('ap2', ssid="ssid-1", mode="g", channel="6",
                             wpa_passphrase='123456789a', wpa='2', wpa_key_mgmt='WPA-PSK',
                             wpa_pairwise='CCMP', auth_algs='1', position='40,10,0')
    c0 = net.addController('c0')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    net.plotGraph(max_x=120, max_y=120)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology()
