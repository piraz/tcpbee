# tcpbee
Tcp Bee

# Depencies:

## libcurl

Fedora:

```
sudo dnf install libcurl-devel openssl-devel gcc
```

Centos:

```
sudo yum install libcurl-devel openssl-devel gcc
```

Set pycurl ssl library before instalation as per https://bit.ly/2GfDPCz:

```
export PYCURL_SSL_LIBRARY=openssl
```
