#coding: utf-8
#MODULO de ferramentas de rede

import socket
import urllib
import re

#import netifaces

def bogusNet():
    return("192.168.0.100","192.168.0.1","172.0.8.1")

def pegaNetInfo():
    #pegando o ip local
    ipLocal = socket.gethostbyname(socket.gethostname())

    # pegando o IP do Router

    ipRouter = '0.0.0.0'

    # pegando o IP público
    site = urllib.urlopen("http://checkip.dyndns.org/").read()
    grab = re.findall('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', site)
    ipExterno = grab[0]

    return(ipLocal, ipRouter, ipExterno)