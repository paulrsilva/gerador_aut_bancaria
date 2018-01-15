#!/usr/bin/env python
# encoding: utf-8
"""
Created by Paulino Rocha e Silva on 2017-05-23.
Copyright (c) 2017 neoplace. All rights reserved.
"""

import sys
import os
import socket
import urllib
import re

import sqlite3
import os.path
from contextlib import closing

import time

import datetime, calendar

# import netifaces

class ComprovantePagto:
    def __init__(self, banco, tipoGuia, codigo, data_venc, data_pagto, valor_principal,
                 valor_outras_ent, valor_jur):

        self.banco=banco
        self.tipoGuia=tipoGuia
        self.codigo=codigo
        self.data_venc=data_venc
        self.data_pagto=data_pagto
        self.valor_principal=valor_principal
        self.valor_outras_ent=valor_outras_ent
        self.valor_jur=valor_jur




bancos = [ ("001", "Banco do Brasil", "BB"),
           ("104","Caixa Econômica Federal", "CE"),
           ("033","Banco Santander (Brasil) S.A.","SBR"),

]

tiposDeGuia = [("GPS", "Guia de Previdência Social"),
               ("GRU", "Guia de Recolhimendo da União" )

]

def pegaNetInfo():
    #pegando o ip local
    ipLocal = socket.gethostbyname(socket.gethostname())

    # pegando o IP do Router

    ipRouter = '0.0.0.0'

    # pegando o IP público
    site = urllib.urlopen("http://checkip.dyndns.org/").read()
    grab = re.findall('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', site)
    ipExterno = grab[0]

    return ipLocal, ipRouter, ipExterno


def verificaBD():
    if (os.path.exists('bancos.db')):
        return True
    else:
        conn = sqlite3.connect("bancos.db")
        cursor = conn.cursor()

        cursor.execute ('''
                create TABLE bancos(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  cod text,
                  nome text,
                  slug text
                )

        ''')

        cursor.executemany('''
               INSERT INTO bancos (cod, nome, slug) VALUES (?,?,?)
        ''', bancos)

        cursor.execute('''
              CREATE TABLE guias(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sigla text,
                nome text
              )
        ''')
        cursor.executemany('''
            INSERT INTO guias(sigla,nome) VALUES (?,?)
        ''', tiposDeGuia)

        conn.commit()
        cursor.close()
        conn.close()
        return False


#TODO Acertar verificação de tabela
def verificaTabelaDB(dbcon, tablename):
    dbcur = dbcon.cursor()
    dbcur.execute('''
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        ''')
    if dbcur.fetchone()[0] == 1:
        dbcur.close()
        return True

    dbcur.close()
    return False


def consultaBanco(codBanco):
    # pegando a lista de todos os bancos
    # ou pegando um banco específico
    if (codBanco=="l" or codBanco=="L"):
        conn = sqlite3.connect("bancos.db")
        cursor = conn.cursor()
        cursor.execute("select * from bancos")
        resultado = cursor.fetchall()
        for banco in resultado:
            print("Id: %d - Cod: %s - banco: %s - sigla: %s" % (banco))
        cursor.close()
        conn.close()
    else:
        with sqlite3.connect("bancos.db") as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('select * FROM bancos WHERE cod = "%s"' % codBanco )
                while True:
                    resultado = cursor.fetchone()
                    if resultado != None:
                        print("Id: %d - Num: %s - banco: %s - sigla: %s" % (resultado))
                        return resultado
                        break
                    else:
                        print("Código de Banco não encontrado!")
                        entradaAdicionarBanco=input("Gostaria de adicionar banco? (s/n)")
                        if (entradaAdicionarBanco=='s' or entradaAdicionarBanco=="S" ):
                            print("adicionando banco")
                        else:
                            print("ok")
                        return False
                        break


def consultaGuia(guia):
    conn = sqlite3.connect('bancos.db')
    cursor = conn.cursor()
    if (guia=='l' or guia=='L'):
        cursor.execute("SELECT * FROM guias")
        resultado = cursor.fetchall()
        for guia in resultado:
            print("Id: %d - Sigla: %s - Tipo: %s" %(guia))
    else:
        indiceGuia=int(guia)
        cursor.execute("SELECT * from guias WHERE id=%d" % indiceGuia)
        while True:
            resultado=cursor.fetchone()
            if resultado != None:
                print("Id: %d - Sigla: %s - Inst.: %s" %(resultado))
                return resultado
                break
            else:
                print('Cod. Guia não encontrado. \n')
                entradaAdGuia=input("Adidionar Guia?")

def consultaData(data):
    if (len(data)<10 or len(data)>10):
        print('a data deve ter o formado dd/mm/aaaa')
    else:
        linhaData=data.split("/")
        #for linha in linhaData:
        #    print(linha)
        print(linhaData[0])

        diaPagto = datetime.date(linhaData[2],linhaData[1],linhaData[0])

        print(diaPagto.strftime("%A"))


    #return 'hoje'



def main():
    #conn=sqlite3.connect('bancos.db')
    #verificaTabelaDB(conn,bancos)

    if(verificaBD()):
        print("usando lista de bancos locais \n \n")
    else:
        print("novo banco de dados padrão criado \n \n ")


    print("\n *** Sistema de Autenticações Bancárias. Digite q para sair *** \n" )
    while True:
        #entrada=int(input("Dados: "))
        entrada=input("Digite o codigo do banco ou L para lista: ").lower().strip()
        if entrada=="q":
            print('Sistema Finalizado')
            break
        else:
            #entradaBanco=input("Digite o codigo do banco ou L para lista: ")
            bancoSelecionado=consultaBanco(entrada)
            if (bancoSelecionado):
                # print(bancoSelecionado[0])
                print("\n")
                while True:
                    guia=input("%s | Dig. o nº da guia ou L para lista ('v' para voltar): " %(bancoSelecionado[3])).lower().strip()
                    if(guia=='v'):
                        break
                    else:
                        guiaSelecionada=consultaGuia(guia)
                        if(guiaSelecionada):
                            while True:
                                EntradaData=input("%s | %s | Dig. a Data de Pgto ('v' para voltar):" %(bancoSelecionado[3],guiaSelecionada[1]))
                                if (EntradaData=='v' or EntradaData=='V'):
                                    break
                                else:
                                    diaPagto=consultaData(EntradaData)


if __name__ == '__main__':
            main()
