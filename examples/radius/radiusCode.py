#!/usr/bin/python

'This example shows how to work with Radius Server'

from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.node import UserAP
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference


def topology():
    "Create a network."
    net = Mininet_wifi( controller=Controller, accessPoint=UserAP,
                        link=wmediumd, wmediumd_mode=interference )

    info("*** Creating nodes\n")
    sta1 = net.addStation('sta1', password='sdnteam', wpa='2', eap='PEAP',
                          identity='joe', phase2='autheap=MSCHAPV2', position='110,120,0')
    sta2 = net.addStation('sta2', password='hello', wpa='2',
                          identity='bob', phase2='autheap=MSCHAPV2', position='200,100,0')
    ap1 = net.addAccessPoint('ap1', ssid='simplewifi', ieee8021x='1',
                             mode='a', channel='36', wpa='2', wpa_key_mgmt='WPA-EAP', auth_algs='1',
                             eap_server='0', eapol_version='2', wpa_pairwise='TKIP CCMP',
                             eapol_key_index_workaround='0', own_ip_addr='127.0.0.1',
                             nas_identifier='ap1.example.com', auth_server_addr='127.0.0.1',
                             radius_server='127.0.0.1', auth_server_port='1812',
                             shared_secret='secret', position='150,100,0')
    c0 = net.addController('c0', controller=Controller, ip='127.0.0.1', port=6653)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating Stations\n")
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)

    net.plotGraph(max_x=300, max_y=300)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start( [c0] )

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    topology()
