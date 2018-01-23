#!/usr/bin/env python
# encoding: utf-8
"""
Created by Paulino Rocha e Silva on 2017-05-23.
Copyright (c) 2017 neoplace. All rights reserved.
"""

import sys
import os
import binascii

import sqlite3
import os.path
from contextlib import closing
import locale

import tempfile
import platform
import subprocess

import time, calendar, datetime, random

from _datetime import datetime as dt


#Importando Módulo para Operações de Rede Adicionais
import ferramentasderede as nt

ipLocal,ipRouter,ipExterno=nt.bogusNet()

HorarioBancario=('10:00','16:00')
# HorarioUltimoPagto=0 - Definida como Global em SistemaAutenticacao



#Classe para identificacao do Sistema Operacional e Metodos de Operação e Impressao
class SistemaUsuario:
    def __init__(self):
        self.sistemaOperacional=os.name
        self.plataforma=platform.system()
        self.versao=platform.release()
    def sistema(self):
        return (self.sistemaOperacional,self.plataforma,self.versao)
    def imprimir(self,*args):
        #print(self.sistemaOperacional,self.plataforma,self.versao)
        if self.plataforma.lower() == "linux" or self.plataforma.lower() == "linux2":
            print("Imprimindo em Linux: %s" % args)
            lpr = subprocess.Popen("/usr/bin/lpr", stdin=subprocess.PIPE)
            lpr.stdin.write(args)
        elif self.plataforma.lower() == "darwin":
            print("Imprimindo em Mac: %s" %(args) )
        elif self.plataformalower() == "win32":
            #print("Imprimindo em Windows 32: %s" % args)
            os.startfile("recibo.txt", "print")
        elif self.plataformalower() == "win62":
            #print("Imprimindo em Windows 64: %s" % args)
            os.startfile("recibo.txt", "print")
        else:
            print("Sistema Operacional Desconhecido")
    def imprima(self,*args):
        texto=str
        for linha in args:
            texto=texto+linha
        return texto

class ComprovantePagto:
    'classe comum para todos os pagamentos'
    compCount = 0
    NumUltimaAutenticacao=None

    usuario=SistemaUsuario

    # criando um objeto com as caracteristicas do computador do usuario
    # para impressão e manipulação correta de arquivos


    def __init__(self, banco, agenciaPagto, tipoGuia, codigo, data_venc, data_pagto, horaPagto, competencia, identificador, valor_principal,
                 valor_outras_ent, valor_jur, valor_total, autenticacao):
        self.banco=banco
        self.agenciaPagto=agenciaPagto
        self.tipoGuia=tipoGuia
        self.codigo=codigo
        self.data_venc=data_venc
        self.data_pagto=data_pagto
        self.horaPagto=horaPagto
        self.competencia=competencia
        self.identificador=identificador
        self.valor_principal=valor_principal
        self.valor_outras_ent=valor_outras_ent
        self.valor_jur=valor_jur
        self.valor_total=valor_total
        self.autenticacao=autenticacao

        ComprovantePagto.compCount +=1

    def Ciclo(self):
        ident = random.randint(11111111111111111, 1299999999999999999)
        identificador = "{:0>19d}".format(ident)
        ciclo=self.competencia.strftime("%d.%m.%Y")+identificador
        return ciclo

    def displayCount(self):
        print("Total de Pagamentos %d" % ComprovantePagto.compCount)
        return ComprovantePagto.compCount


    def GeraRecibo(self,ciclo):
        recibo=open("recibo.txt","w")

        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        info = locale.localeconv()  # formatando moeda local
        siglaMoeda = info['currency_symbol']
        recibo.write("\n%s              \n\n" %(self.banco[2].upper()))
        recibo.write("COMPROVANTE DE PAGAMENTO DE %s \n\n" % self.tipoGuia[2].upper())
        recibo.write("DADOS DO EMITENTE \nNOME: \nCPF/CNPJ: 00000000000000  \n\n")
        recibo.write("CODIGO DO PAGAMENTO:  %s\n" % self.codigo)
        recibo.write("COMPETENCIA:  %s\n" % self.competencia.strftime("%m/%Y"))
        recibo.write("IDENTIFICADOR:  %s\n\n" % self.identificador)

        recibo.write("VALOR PRINCIPAL:  %s %s \n\n" %( siglaMoeda, locale.currency(self.valor_principal, grouping=True, symbol=None)))
        if(self.valor_outras_ent==0):
            recibo.write("VALOR DE OUTRAS ENT: %s \n" % (siglaMoeda))
        else:
            recibo.write("VALOR DE OUTRAS ENT: %s %s\n" %( siglaMoeda, locale.currency(self.valor_outras_ent, grouping=True, symbol=None)))

        if(self.valor_jur==0):
            recibo.write("VALOR DO ATM/JUR/MULT: %s \n" % (siglaMoeda))
        else:
            recibo.write("VALOR DO ATM/JUR/MULT: %s %s\n" %(siglaMoeda, locale.currency(self.valor_jur, grouping=True, symbol=None)))

        recibo.write("VALOR ARRECADADO: %s %s\n\n" %( siglaMoeda, locale.currency(self.valor_total, grouping=True, symbol=None)))
        recibo.write("DOCUMENTO PAGO DENTRO DAS CONDICOES \nDEFINIDAS PELA PORTARIA RFB No.\t1976/2008 \n\n")
        recibo.write("CICLO:  %s \nREALIZADO EM: %s as %s \nAG.%s %s \n\n" % (
            ciclo, self.data_pagto.strftime("%d/%m/%Y"), self.horaPagto, self.agenciaPagto[4][0:4], self.agenciaPagto[5]))
        recibo.write("\t\t\t AUTENTICACAO \n%s \n\n" % (self.autenticacao[2:40].upper()))
        recibo.write("%s %s   %s   %s   %sC   %s\n\n" %(self.banco[3],self.agenciaPagto[4][0:4],"806248887",self.data_pagto.strftime("%d%m%y"),
                                                        locale.currency(self.valor_total, grouping=True, symbol=None),self.tipoGuia[1] + "DIN"))
        recibo.close()


    def GeraNumAutenticacao(self):
        if(self.NumUltimaAutenticacao==None):
            numInicial = ("%s%s" % ("0", str(self.banco[0])))
            numFinal = "{:0>2d}".format(random.randint(1, 10))
            NumAleatorio = ("%s%s" % (numInicial, numFinal))
            self.NumUltimaAutenticacao=NumAleatorio
            return NumAleatorio
        else:
            numAutentica=int(self.NumUltimaAutenticacao)+1
            numAut="{:0>4d}".format(numAutentica)
            self.NumUltimaAutenticacao = numAut
            return numAut


    def MostraAutenticacao(self):
        return("\n%s  %s  %s  %s  %s \t  %sR %s" % (self.banco[3],self.agenciaPagto[4][0:4],self.banco[1],self.data_pagto.strftime("%d%m%y"),self.GeraNumAutenticacao(),
                                             str(self.valor_total).replace(".",","),self.data_venc.strftime("%d/%d")))

    def MostraRecibo(self,ciclo):

        locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")
        info = locale.localeconv()  # formatando moeda local
        siglaMoeda = info['currency_symbol']
        print("\n%s              \n" % (self.banco[2].upper()))
        print("COMPROVANTE DE PAGAMENTO DE %s \n" % self.tipoGuia[2].upper())
        print("DADOS DO EMITENTE \nNOME: \nCPF/CNPJ: 00000000000000  \n\n")
        print("CODIGO DO PAGAMENTO:  %s\nCOMPETENCIA:  %s\nIDENTIFICADOR:  %s\n " % (self.codigo,self.competencia.strftime("%m/%Y"),self.identificador))

        print("VALOR PRINCIPAL:  %s %s \n" % (
        siglaMoeda, locale.currency(self.valor_principal, grouping=True, symbol=None)))

        if (self.valor_outras_ent == 0):
            print("VALOR DE OUTRAS ENT: %s \n" % (siglaMoeda))
        else:
            print("VALOR DE OUTRAS ENT: %s %s\n" % (
            siglaMoeda, locale.currency(self.valor_outras_ent, grouping=True, symbol=None)))

        if (self.valor_jur == 0):
            print("VALOR DO ATM/JUR/MULT: %s \n" % (siglaMoeda))
        else:
            print("VALOR DO ATM/JUR/MULT: %s %s\n" % (
            siglaMoeda, locale.currency(self.valor_jur, grouping=True, symbol=None)))

        print("VALOR ARRECADADO: %s %s\n\n" % (siglaMoeda, locale.currency(self.valor_total, grouping=True, symbol=None)))
        print("DOCUMENTO PAGO DENTRO DAS CONDICOES \nDEFINIDAS PELA PORTARIA RFB No.\t1976/2008 \n\n")
        print("CICLO:  %s \nREALIZADO EM: %s as %s \nAG.%s %s \n\n" % (
            ciclo, self.data_pagto.strftime("%d/%m/%Y"), self.horaPagto, self.agenciaPagto[4][0:4],
            self.agenciaPagto[5]))
        print("\t\t\t AUTENTICACAO \n%s \n\n" % (self.autenticacao[2:40].upper()))
        print("%s %s   %s   %s   %sC   %s\n\n" % (self.banco[3], self.agenciaPagto[4][0:4], "806248887",
                                                  self.data_pagto.strftime("%d%m%y"),locale.currency(self.valor_total,
                                                  grouping=True, symbol=None), self.tipoGuia[1] + "DIN"))
        while True:
            entradaRecibo=input("[A]rquivar | [I]mprimir | [S]air :")
            if(entradaRecibo.lower()=='a'):
                pass
            elif(entradaRecibo.lower()=='i'):
                self.GeraRecibo(self.Ciclo())
                self.Imprimir("recibo.txt")
            elif(entradaRecibo.lower()=='s'):
                break
            else:
                print("Digite A, I ou S\n")

    def Imprimir(self,arquivo):
        usuario=SistemaUsuario()
        usuario.imprimir(arquivo)


bancos = [ ("001", "Banco do Brasil S.A.", "BB"),
           ("104","Caixa Econômica Federal", "CE"),
           ("033","Banco Santander (Brasil) S.A.","SBR"),
           ("341","Itaú Unibanco S.A.","ITAU")
]

tiposDeGuia = [("GPS", "Guia de Previdência Social"),
               ("GRU", "Guia de Recolhimendo da União" )
]

agencias = [ ("BB","RJ","Petropolis","0080", "PETROPOLIS PETROPOLIS"),
             ("CE", "RJ", "Petropolis", "1651", "PETROPOLIS UNIAO"),
             ("SBR", "RJ", "Petropolis", "3242", "PETROPOLIS-CENTRO"),
             ("ITAU","RJ","Petropolis","0087","PETROPOLIS UNIAO")
]



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

        cursor.execute('''
                CREATE TABLE agencias(
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  banco text,
                  UF text,
                  Cidade text,
                  Agencia text,
                  nome_agencia text
                )
        ''')

    cursor.executemany('''
           INSERT INTO agencias(banco,UF,Cidade,Agencia,nome_agencia) VALUES (?,?,?,?,?)
       ''', agencias)

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

def consultaAgencia(sigla_banco):
    #TODO Desenvolver inclusão e consulta de agencias adicionais

    conn = sqlite3.connect('bancos.db')
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM agencias WHERE banco='%s'" %(sigla_banco))
    while True:
        resultado = cursor.fetchone()
        if resultado != None:
            return resultado
            break
        else:
            print('Não existe AG. para o Banco Selecionado\n')
            entradaAgencia=input("Adicionar Agencia?")

def consultaGuia(guia):
    conn = sqlite3.connect('bancos.db')
    cursor = conn.cursor()
    if (guia=='l' or guia=='L'):
        cursor.execute("SELECT * FROM guias")
        resultado = cursor.fetchall()
        for guia in resultado:
            print("Id: %d - Sigla: %s - Tipo: %s" %(guia))
    else:
        try:
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
                    entradaAdGuia=input("Adidionar Guia? S/N :")
                    if(entradaAdGuia.lower()=='n'):
                        break
                    elif(entradaAdGuia.lower()=='s'):
                        print('Codigo para adicionar guia não implementado')
                    else:
                        print("digite apenas S ou N")
        except ValueError:
            print("Entrada de dados inválida. É preciso inserir o nº da guia.")



def consultaData(data):
    if (len(data)<10 or len(data)>10):
        print('a data deve ter o formado dd/mm/aaaa')
        return False
    else:
        #linhaData=data.split("/")
        #for linha in linhaData:
        #    print(linha)
        #print(linhaData[0])

        diaPagto = datetime.datetime.strptime(data,"%d/%m/%Y")

        diaDaSemana=diaPagto.strftime("%A")
        #dataPagto=diaPagto.strftime("%d/%m%/%Y")

        return(diaDaSemana)

#Função para verificar entrada de valores float
def input_float(entrada):
    while True:
        try:
            return (float(entrada))
        except ValueError as e:
            print("Os decimais devem ser separados com ponto '.'")
            print("Apenas números são permitidos")
            print(type(e))
            print(e.args)
            print(e)
            entrada=input("\nDigite o valor novamente: ")
        finally:
            if(type(entrada)==str and len(entrada)==0):
                entrada=0
                print('valor zero atribuido')



#Função para calcular o mes anterior - Competencia
def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

#Sistema Principal de Autenticacao
def SistemaAutenticacao():
    global HorarioUltimoPagto
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
                                    #Verificando se o formato de data está ok
                                    if(consultaData(EntradaData)):
                                        diaDaSemana=consultaData(EntradaData)
                                    else:
                                        print('Formato de Data Invalido')
                                        break

                                    dataPagto=EntradaData

                                    if(consultaData(dataPagto)==False):
                                        print('Formato de Data Invalido')
                                        break

                                    if (diaDaSemana == "Saturday"):
                                        print("Esta data cai num Sábado")
                                    elif (diaDaSemana == "Sunday"):
                                        print("Esta data cai num Domingo")
                                    # TODO Fazer aferição de feriados
                                    # TODO Acertar nova data automaticamente
                                    else:

                                        ValorPrincipal=input_float(input("%s | %s | %s | Valor Principal :" % (
                                            bancoSelecionado[3], guiaSelecionada[1], dataPagto))
                                                                   )
                                        ValorOutrasEnt=input_float(input(
                                            "%s | %s | %s | Outras Ent :" % (
                                                bancoSelecionado[3], guiaSelecionada[1], dataPagto))
                                        )

                                        # TODO criar avaliação de entrada para campos sem nenhum informação (APENAS ENTER)

                                        ValorJurosMulta = input_float(input(
                                            "%s | %s | %s | ATM/JUR/MULTAS : " % (
                                                bancoSelecionado[3], guiaSelecionada[1], dataPagto))
                                        )

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
                                            horaPagto=("%s:%s:%s" %(hora, minuto, segundo))
                                            HorarioUltimoPagto=horaPagto
                                        else:
                                            #horaPagto=time.strftime("%I:%M:%S",time.localtime(hoje.toordinal()))
                                            horaPagto=str("%d:%d:%d" %(hoje.hour,hoje.minute,hoje.second))
                                            HorarioUltimoPagto = horaPagto
                                        #fim acertando hora de pagto

                                        DataVencimento = datetime.datetime.strptime(EntradaDataVencimento, "%d/%m/%Y")
                                        DataPgto = datetime.datetime.strptime(EntradaData, "%d/%m/%Y")

                                        competencia = monthdelta(
                                            datetime.datetime.strptime(EntradaDataVencimento, "%d/%m/%Y"), -1)

                                        ident = random.randint(1111111111111, 11111111111111)

                                        identificador = "{:0>14d}".format(ident)


                                        ValorArrecadado = ValorPrincipal + ValorOutrasEnt + ValorJurosMulta

                                        autenticacao=(str(binascii.b2a_hex(os.urandom(20))))

                                        #agenciaPagto=consultaGuia(bancoSelecionado[3])
                                        agenciaPagto=consultaAgencia(bancoSelecionado[3])

                                        # Criando Dicionario com desempacotamento para facilitar
                                        # versionamento posterior. Tbem facilita a correção de qualquer
                                        # erro de posicionamento

                                        d = {"banco": bancoSelecionado, "agenciaPagto": agenciaPagto,
                                             "tipoGuia": guiaSelecionada, "codigo": "2100", "data_venc": DataVencimento,
                                             "data_pagto": DataPgto, "horaPagto": horaPagto, "competencia": competencia,
                                             "identificador": identificador, "valor_principal": ValorPrincipal,
                                             "valor_outras_ent": ValorOutrasEnt, "valor_jur": ValorJurosMulta,
                                             "valor_total": ValorArrecadado, "autenticacao": autenticacao}

                                        pagamentoN = ComprovantePagto(**d)

                                        while True:
                                            EntradaImpressao = input("Digite R para Recibo ou A para Autenticação: ")
                                            if (EntradaImpressao.lower() == 'r'):
                                                ciclo = pagamentoN.Ciclo()
                                                pagamentoN.GeraRecibo(ciclo)
                                                pagamentoN.MostraRecibo(ciclo)
                                            elif (EntradaImpressao.lower() == 'a'):
                                                print("\n\n %s" %pagamentoN.MostraAutenticacao())
                                                entradaAutOpcoes=input("[I]mprimir | [A]rquivar | [S]air")
                                                while True:
                                                    if(entradaAutOpcoes.lower()=='i'):
                                                        pagamentoN.Imprimir("autenticacao.txt")
                                                        break
                                                        #os.startfile("\n\n %s" %pagamentoN.MostraAutenticacao(), "print")
                                                    elif(entradaAutOpcoes.lower()=='a'):
                                                        pass
                                                    elif(entradaAutOpcoes.lower()=='s'):
                                                        break
                                                    else:
                                                        pass

                                            elif (EntradaImpressao.lower()=='v'):
                                                break
                                            elif (EntradaImpressao.lower()=='q'):
                                                pagamentoN.displayCount()
                                                _run=False
                                                break
                                            else:
                                                print("\nDigite 'R', 'A', 'V' ou 'Q'" )

                                        print("\n %d Pagamentos Efetuados" % (pagamentoN.displayCount()))
def main():

    if(verificaBD()):
        print("usando lista de bancos locais \n \n")
    else:
        print("novo banco de dados padrão criado \n \n ")


    SistemaAutenticacao()

    print("\n\n\n*** SISTEMA FINALIZADO ***\n\n\n")



if __name__ == '__main__':
            main()
