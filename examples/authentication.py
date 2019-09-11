#!/usr/bin/python

'This example shows how to work with authentication'

import sys

from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi


def topology(encrypt):
    "Create a network."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    if encrypt == 'wpa':
        sta1 = net.addStation('sta1', psk='123456789a', wpa='1')
        sta2 = net.addStation('sta2', psk='123456789a', wpa='1')
        ap1 = net.addAccessPoint('ap1', ssid='simplewifi', mode='g', channel='1',
                                 wpa='1', wpa_key_mgmt='WPA-PSK', wpa_pairwise='CCMP',
                                 wpa_passphrase='123456789a', auth_algs='1',
                                 failMode='standalone', datapath='user')
    elif encrypt == 'wpa2':
        sta1 = net.addStation('sta1', psk='123456789a', wpa='2')
        sta2 = net.addStation('sta2', psk='123456789a', wpa='2')
        ap1 = net.addAccessPoint('ap1', ssid='simplewifi', mode='g', channel='1',
                                 wpa='2', wpa_key_mgmt='WPA-PSK', wpa_pairwise='CCMP',
                                 wpa_passphrase='123456789a', auth_algs='1',
                                 failMode='standalone', datapath='user')
    elif encrypt == 'wpa3':
        sta1 = net.addStation('sta1', psk='123456789a', wpa='2')
        sta2 = net.addStation('sta2', psk='123456789a', wpa='2')
        ap1 = net.addAccessPoint('ap1', ssid='simplewifi', mode='g', channel='1',
                                 wpa='2', wpa_key_mgmt='SAE', wpa_pairwise='CCMP',
                                 wpa_passphrase='123456789a', auth_algs='1',
                                 failMode='standalone', datapath='user')
    elif encrypt == 'wep':
        sta1 = net.addStation('sta1', wep_key0='123456789a')
        sta2 = net.addStation('sta2', wep_key0='123456789a')
        ap1 = net.addAccessPoint('ap1', ssid="simplewifi", mode="g", channel="1",
                                 wep_key0='123456789a', auth_algs='1',
                                 failMode="standalone", datapath='user')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    info("*** Starting network\n")
    net.build()
    ap1.start([])

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    if '-1' == sys.argv[1]:
        encrypt = 'wpa'
    elif '-2' == sys.argv[1]:
        encrypt = 'wpa2'
    elif '-3' == sys.argv[1]:
        encrypt = 'wpa3'
    elif '-4' == sys.argv[1]:
        encrypt = 'wep'
    else:
        encrypt = 'wpa2'
    topology(encrypt)
