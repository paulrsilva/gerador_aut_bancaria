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

import time, calendar, datetime, random, locale

from _datetime import datetime as dt

# import netifaces

HorarioBancario=('10:00','16:00')
HorarioUltimoPagto=0


class ComprovantePagto:
    'classe comum para todos os pagamentos'
    compCount = 0

    def __init__(self, banco, tipoGuia, codigo, data_venc, data_pagto, competencia, identificador, valor_principal,
                 valor_outras_ent, valor_jur, valor_total):
        self.banco=banco
        self.tipoGuia=tipoGuia
        self.codigo=codigo
        self.data_venc=data_venc
        self.data_pagto=data_pagto
        self.competencia=competencia
        self.identificador=identificador
        self.valor_principal=valor_principal
        self.valor_outras_ent=valor_outras_ent
        self.valor_jur=valor_jur
        self.valor_total=valor_total

        ComprovantePagto.compCount +=1

    def Ciclo(self):
        ident = random.randint(11111111111111111, 1299999999999999999)
        identificador = "{:0>19d}".format(ident)
        ciclo=self.competencia.strftime("%d.%m.%Y")+identificador
        return ciclo


    def displayCount(self):
        print("Total de Pagamentos %d") % ComprovantePagto.compCount


    def MostraRecibo(self,ciclo):
        locale.setlocale(locale.LC_ALL, "")
        info = locale.localeconv()  # formatando moeda local
        print("\n\n")
        print(self.banco[2].upper(),"              \n")
        print("COMPROVANTE DE PAGAMENTO DE", self.tipoGuia[2].upper(), "\n")
        print("DADOS DO EMITENTE \nNOME: \nCPF/CNPJ: 00000000000000  \n")
        print("CODIGO DO PAGAMENTO:  ", self.codigo)
        print("COMPETENCIA:  ",self.competencia.strftime("%m/%Y"))
        print( "IDENTIFICADOR:  ",self.identificador,"\n")
        print("VALOR PRINCIPAL:  ",info['currency_symbol'],locale.format("%1.2f",self.valor_principal,1),"\n")
        print("VALOR DE OUTRAS ENT: ",info['currency_symbol'],locale.format("%1.2f",self.valor_outras_ent,1),
              "\nVALOR DO ATM/JUR/MULT:",info['currency_symbol'],locale.format("%1.2f",self.valor_jur,1),
              "\nVALOR ARRECADADO: ", info['currency_symbol'], locale.format("%1.2f", self.valor_total, 1),"\n")
        print("DOCUMENTO PAGO DENTRO DAS CONDICOES \nDEFINIDAS PELA PORTARIA RFB No.\t1976/2008 \n")

        #print("CICLO:   ",ciclo," \nREALIZADO EM:  as  \nAG.0000 Nome Agencia \n")
        print("CICLO:  %s \nREALIZADO EM: %s as  \nAG.0000 Nome Agencia \n" % (ciclo, self.data_pagto.strftime("%d/%m/%Y")))

        print("\t\t\t AUTENTICACAO \n000000000000000000000000000 \n")
        print(self.banco[3]," 806248887   ",self.data_pagto.strftime("%d%m%y"),"   ",locale.format("%1.2f", self.valor_total, 1),"   ",self.tipoGuia[1]+"DIN")


        #print(info['currency_symbol'],locale.format("%1.2f",self.valor_principal,1))
        print('----')



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
        #linhaData=data.split("/")
        #for linha in linhaData:
        #    print(linha)
        #print(linhaData[0])

        diaPagto = datetime.datetime.strptime(data,"%d/%m/%Y")

        diaDaSemana=diaPagto.strftime("%A")
        dataPagto=diaPagto.strftime("%d/%m%/%Y")

        return (diaDaSemana,dataPagto)


#Função para calcular o mes anterior - Competencia
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

#Sistema Principal de Autenticacao
def SistemaAutenticacao():
    print("\n *** Sistema de Autenticações Bancárias. Digite q para sair *** \n")
    _run = True
    while _run:
        # entrada=int(input("Dados: "))
        entrada = input("Digite o codigo do banco ou L para lista: ").lower().strip()
        if entrada == "q":
            print('Sistema Finalizado')
            break
        else:
            # entradaBanco=input("Digite o codigo do banco ou L para lista: ")
            bancoSelecionado = consultaBanco(entrada)
            if (bancoSelecionado):
                # print(bancoSelecionado[0])
                print("\n")
                while _run:
                    guia = input("%s | Dig. o nº da guia ou L para lista ('v' para voltar): " % (
                    bancoSelecionado[3])).lower().strip()
                    if (guia == 'v'):
                        break
                    elif(guia.lower()=='q'):
                        _run=False
                    else:
                        guiaSelecionada = consultaGuia(guia)
                        if (guiaSelecionada):
                            while _run:
                                EntradaDataVencimento = input("%s | %s | Dig. a Data de Venc. ('v' para voltar):" % (
                                bancoSelecionado[3], guiaSelecionada[1]))
                                if (EntradaDataVencimento.lower()=='v'):
                                    break
                                elif (EntradaDataVencimento.lower()=='q'):
                                    _run=False
                                    break
                                else:
                                    pass
                                EntradaData = input("%s | %s | Dig. a Data de Pgto ('v' para voltar):" % (
                                bancoSelecionado[3], guiaSelecionada[1]))
                                # TODO Criar classe de cálculo de juro e mora
                                if (EntradaData.lower() == 'v'):
                                    break
                                elif(EntradaData.lower()=='q'):
                                    _run=False
                                else:
                                    diaDaSemana, dataPagto = consultaData(EntradaData)
                                    if (diaDaSemana == "Saturday"):
                                        print("Esta data cai num Sábado")
                                    elif (diaDaSemana == "Sunday"):
                                        print("Esta data cai num Domingo")
                                    # TODO Fazer aferição de feriados
                                    # TODO Acertar nova data automaticamente
                                    else:
                                        ValorPrincipal = float(input("%s | %s | %s | Valor Principal :" % (
                                        bancoSelecionado[3], guiaSelecionada[1], dataPagto)))
                                        ValorOutrasEnt = float(input(
                                            "%s | %s | %s | Outras Ent :" % (
                                                bancoSelecionado[3], guiaSelecionada[1], dataPagto)))

                                        # TODO criar avaliação de entrada para campos sem nenhum informação (APENAS ENTER)

                                        ValorJurosMulta = float(input(
                                            "%s | %s | %s | ATM/JUR/MULTAS :" % (
                                                bancoSelecionado[3], guiaSelecionada[1], dataPagto)))

                                        #d=datetime.datetime.strptime(DataVencimento, "%d/%m/%Y")

                                        #acertando a hora de pagamento
                                        hoje = dt.today()
                                        horaBancAbertura=int(HorarioBancario[0][0:2])
                                        horaBancFechamento=int(HorarioBancario[1][0:2])

                                        if(hoje.hour < horaBancAbertura or hoje.hour > horaBancFechamento ):
                                            print("\n*** horario bancario excedido. Gerando horario aleatorio ***")
                                            hora = str(random.choice(range(10, 16)))
                                            minuto = "{:0>2d}".format(random.choice(range(0, 59)))
                                            segundo = "{:0>2d}".format(random.choice(range(0, 59)))
                                            horarioPagto=("%s:%s:%s" %(hora, minuto, segundo))
                                        else:
                                            pass


                                        #fim acertando hora de pagto

                                        DataVencimento = datetime.datetime.strptime(EntradaDataVencimento, "%d/%m/%Y")
                                        DataPgto = datetime.datetime.strptime(EntradaData, "%d/%m/%Y")

                                        competencia = monthdelta(
                                            datetime.datetime.strptime(EntradaDataVencimento, "%d/%m/%Y"), -1)

                                        ident = random.randint(1111111111111, 11111111111111)

                                        identificador = "{:0>14d}".format(ident)


                                        ValorArrecadado = ValorPrincipal + ValorOutrasEnt + ValorJurosMulta

                                        pagamentoN = ComprovantePagto(bancoSelecionado, guiaSelecionada, "2100",
                                                                      DataVencimento, DataPgto, competencia,
                                                                      identificador, ValorPrincipal,
                                                                      ValorOutrasEnt, ValorJurosMulta, ValorArrecadado)

                                        ciclo = pagamentoN.Ciclo()

                                        pagamentoN.MostraRecibo(ciclo)

def main():

    if(verificaBD()):
        print("usando lista de bancos locais \n \n")
    else:
        print("novo banco de dados padrão criado \n \n ")

    SistemaAutenticacao()



if __name__ == '__main__':
            main()
