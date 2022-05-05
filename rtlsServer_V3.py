#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Version : Pyhton 3.9
# @Time    : 2021/5/4 9:29 PM
# @Author  : Jihu Sun
# @File    : rtlsServer_V3.py

import argparse
import binascii
import hashlib
import hmac
from socket import socket, AF_INET, SOCK_DGRAM
from tabulate import tabulate

# Message Codes
AR_AS_CONFIG_SET = b'0000'
AR_STATION_REQUEST = b'0001'
AR_ACK = b'0010'
AR_NACK = b'0011'
AR_TAG_REPORT = b'0012'
AR_STATION_REPORT = b'0013'
AR_COMPOUND_MESSAGE_REPORT = b'0014'
AR_AP_NOTIFICATION = b'0015'
AR_MMS_CONFIG_SET = b'0016'
AR_STATION_EX_REPORT = b'0017'
AR_AP_EX_REPORT = b'0018'


class RtlsServer:
    def __init__(self, host, udp_port, key, client_mac, ap_mac, client_type):
        self.host = host
        self.udp_port = udp_port
        self.key = key

        self.UdpSock = socket(AF_INET, SOCK_DGRAM)
        self.serverStatus = True
        self.data = b''
        self.addr = ()
        self.index = 0

        self.client_mac = client_mac
        self.ap_mac = ap_mac
        self.client_type = client_type

        try:
            self.UdpSock.bind((self.host, self.udp_port))
            print('rtls服务器已经启动，udp端口：{}'.format(self.udp_port))
            # print(self.client_type)
        except:
            print('rtls服务器启动失败')

    # 读取一次udp data
    def get_udp_data(self):
        try:
            data, self.addr = self.UdpSock.recvfrom(1024)
            self.data = binascii.b2a_hex(data)
            return self.data, self.addr
        except KeyboardInterrupt:
            print('rtls服务器手动关闭!')
            self.stop()
            self.serverStatus = False

    # 停止udp服务
    def stop(self):
        self.UdpSock.close()
        print('rtls服务器已停止')

    # 获取message type
    def message_type(self):
        data = self.data
        return data[0:4]

    # decode header
    def get_rtls_hdr(self):
        data, addr = self.data, self.addr
        key = ['Message_Type', 'Message_ID', 'Major_version', 'Minor_Version', 'Data_Length', 'AP_MAC', 'Padding']
        value = [data[0:4], data[4:8], data[8:10], data[10:12], data[12:16], data[16:28], data[28:32]]
        rtls_hdr = dict(zip(key, value))
        return rtls_hdr

    # 获取一个udp报文包含的rtls报文数量
    def get_rtls_counts(self):
        data, addr = self.data, self.addr
        rtls_counts = int(data[32:36].decode(), 16)
        return rtls_counts

    # decode rtls payload
    def get_rtls_payload(self):
        data, addr = self.data, self.addr
        rtls_payload = data[40:-40].decode()
        # print(rtls_payload)
        rtls_msg = []
        rtls_payload = [rtls_payload[i:i + 88] for i in range(0, len(rtls_payload), 88)]

        for i in range(len(rtls_payload)):
            mac = rtls_payload[i][16:28]
            client_mac = rtls_payload[i][32:44]
            try:
                noise_floor = int(rtls_payload[i][44:46], 16)
            except ValueError:
                noise_floor = ''
            datarate = rtls_payload[i][46:48]
            try:
                channel = int(rtls_payload[i][48:50], 16)
            except ValueError:
                channel = ''
            try:
                rssi = int(rtls_payload[i][50:52], 16) - 256
            except ValueError:
                rssi = ''
            client_type = 'AR_WLAN_CLIENT' if rtls_payload[i][52:54] == '01' else 'AR_WLAN_AP'
            associated = rtls_payload[i][54:56] == '01'
            radio_bssid = rtls_payload[i][56:68]
            mon_bssid = rtls_payload[i][68:80]
            try:
                age = int(rtls_payload[i][80:88], 16)
            except ValueError:
                age = ''

            value = [mac, client_mac, noise_floor, datarate, channel, rssi, client_type, associated, radio_bssid,
                     mon_bssid, age]
            rtls_msg.append(value)

        return rtls_msg

    # 发送AR_ACK报文
    def send_ar_ack(self):
        data, addr_port = self.data, self.addr
        message = AR_ACK + data[4:32]
        ar_ack = binascii.a2b_hex(message + self.generate_signature(message))
        self.UdpSock.sendto(ar_ack, addr_port)
        return ar_ack

    # 生成ack签名
    def generate_signature(self, message):
        keys = self.key.encode()
        # 将message转化为字节流（不能用字符串生成）
        message = binascii.a2b_hex(message)
        # hamc-sha1 hash
        signature = (hmac.new(keys, message, hashlib.sha1)).hexdigest().encode()
        return signature

    # 运行程序
    def run(self):
        headers = ['ap_wired_mac', 'client_mac', 'noise_floor', 'datarate', 'channel', 'rssi', 'client_type',
                   'associated', 'radio_bssid', 'mon_bssid', 'age']
        table = []

        self.get_udp_data()
        if self.message_type() == AR_AP_NOTIFICATION:
            self.send_ar_ack()

        elif self.message_type() == AR_COMPOUND_MESSAGE_REPORT:
            rtls_counts = self.get_rtls_counts()
            if len(self.get_rtls_payload()) != 0:
                # 根据不同的client_type，不同的输出结果
                if self.client_type == 1:
                    for i in self.get_rtls_payload():
                        if i[6] == 'AR_WLAN_CLIENT':
                            table.append(i)
                elif self.client_type == 2:
                    for i in self.get_rtls_payload():
                        if i[6] == 'AR_WLAN_AP':
                            table.append(i)
                elif self.client_type == 3:
                    table = self.get_rtls_payload()
            if table:
                # print('Revice {} counts rtls data:'.format(rtls_counts))
                print(tabulate(table, headers=headers, tablefmt="grid"), '\n')
        else:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', metavar='--key', required=True, help='rtls服务器密码')
    parser.add_argument('-p', metavar='--port', required=True, help='rtls服务器端口', type=int)
    parser.add_argument('-a', metavar='--AccessPoint', help='获取指定AP(mac地址)的rtls信息,格式为"aabbccddeeff"')
    parser.add_argument('-c', metavar='--client', help='获取指定终端(mac地址)的rtls信息,格式为"aabbccddeeff"')
    parser.add_argument('-t', metavar='--client_type', default=1,
                        help='获取AP或者Client的RTLS信息，1:AR_WLAN_CLIENT, 2:AR_WLAN_AP，3,ALL。默认为1')

    args = parser.parse_args()
    key = args.k
    udp_port = args.p
    ap_mac = args.a
    client_mac = args.c
    client_type = int(args.t)

    r1 = RtlsServer(host='', udp_port=udp_port, key=key, client_mac=client_mac, ap_mac=ap_mac, client_type=client_type)
    while r1.serverStatus:
        r1.run()


if __name__ == '__main__':
    main()
