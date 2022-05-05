# arubaos-rtls-server

> 1. aruba IAP / Controller启用rtls配置
#### 略

> 2. 安装必要模块
```
pip3 install -r requirement.txt
```

> 3. 运行帮助命令
```
 (venv) $ python3 rtlsServer_V3.py -h
usage: rtlsServer_V3.py [-h] -k --key -p --port [-a --AccessPoint] [-c --client] [-t --client_type]

optional arguments:
  -h, --help        show this help message and exit
  -k --key          rtls服务器密码
  -p --port         rtls服务器端口
  -a --AccessPoint  获取指定AP(mac地址)的rtls信息,格式为"aabbccddeeff"
  -c --client       获取指定终端(mac地址)的rtls信息,格式为"aabbccddeeff"
  -t --client_type  获取AP或者Client的RTLS信息，1:AR_WLAN_CLIENT, 2:AR_WLAN_AP，3,ALL。默认为1

```

> 4. 使用示例：启动服务器，端口为：5555，密码为：123456

```
(venv)$ python3 rtlsServer_V3.py -k 123456 -p 5555
```

> 5. 运行效果如下：
```
rtls服务器已经启动，udp端口：5555
+----------------+--------------+---------------+------------+-----------+--------+----------------+--------------+---------------+--------------+-------+
| ap_wired_mac   | client_mac   |   noise_floor | datarate   |   channel |   rssi | client_type    | associated   | radio_bssid   | mon_bssid    |   age |
+================+==============+===============+============+===========+========+================+==============+===============+==============+=======+
| 9c8cd8c93a4c   | aabbccddeeff |            98 | ff         |         1 |    -49 | AR_WLAN_CLIENT | True         | 9c8cd813a4c0  | 9c8cd813a4c0 |    11 |
+----------------+--------------+---------------+------------+-----------+--------+----------------+--------------+---------------+--------------+-------+
| 9c8cd8c93a4c   | bbaaccddeeff |            98 | ff         |         6 |    -85 | AR_WLAN_CLIENT | True         | 9c8cd813a4c0  | 88c397c053b5 |   568 |
+----------------+--------------+---------------+------------+-----------+--------+----------------+--------------+---------------+--------------+-------+ 
```
