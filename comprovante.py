# encoding: utf-8

from __future__ import print_function
import pandas as pd
import numpy as np
import tempfile

import os
from datetime import datetime, date, time

from jinja2 import Environment, FileSystemLoader

from weasyprint import HTML

env = Environment(loader=FileSystemLoader('.'))
#template= env.get_template("ModelRecibo.html")
template= env.get_template("modelos/GeradorModel.html")



def VerificaPasta(pasta):
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    return True

def GeraNomeArquivo(*args):

    t=datetime.now()
    tt=t.timetuple()

    nomeArquivo="Comp" + "_"
    for i in args:
        nomeArquivo=nomeArquivo+"_"+i

    nomeArquivo=nomeArquivo+"_"+str(tt[3])+"-"+str(tt[4])

    return nomeArquivo


    #"Comp" + "_" + kwargs["tipoGuia"] + "_" + str(kwargs["compRodape"]) + "_"

def GerarPDF(**kwargs):
    filename = tempfile.mktemp(".txt")
    textoEntrada = open(filename, "w")
    for key, value in kwargs.items():
        if(key=="HORAPAGTO"):
            #atualizando hora pra não dar conflito com o separador ':' do panda
            horaFormatada= value.replace(':','-')
            print(horaFormatada)
            textoEntrada.write("%s : %s\n" %(key,horaFormatada))
        else:
            textoEntrada.write("%s : %s\n" %(key,value))

    textoEntrada.close()

    print(">> %s \n" % filename)

    #gerando arquivo do panda - revisar mais tarde
    data = pd.read_csv(filename,sep=":",header=None)
    data.columns=["Item","Valor"]
    print(data)
    data.head()

    # print(kwargs["VALOR_ENT"])
    # print(type(kwargs["HORAPAGTO"]))

    print("\n")
    file = open(filename, "r")
    print(file.read())


    template_vars = {"banco_pagamento": kwargs["BANCO"].upper(), "guia":kwargs["GUIA"],
                     "CodPagto":kwargs["CodPagto"],"Competencia":kwargs["COMPETENCIA"],
                     "Identificador":kwargs["IDENTIFICADOR"],"ValorPrincipal":kwargs["VALOR PRINCIPAL"],
                     "ValorEntidades":kwargs["VALOR_ENT"], "ValorJuros":kwargs["VALORJUR"],
                     "ValorArrecadado":kwargs["VALORARRECADADO"],"ciclo":kwargs["CICLO"],
                    "data_pagto":kwargs["DATAPAGTO"],"hora_pagto":kwargs["HORAPAGTO"],"agencia":kwargs["AGENCIA"],
                     "ag_pagto":kwargs["AG_PAGTO"],"autenticacao":kwargs["AUTENTICACAO"],"siglaBanco":kwargs["siglaBanco"],
                     "codAgPagto":kwargs["codAgPagto"],"compRodape":kwargs["compRodape"],"tipoGuia":kwargs["tipoGuia"]
                     }

#TODO Revisar conflito com os dos pontos de horas

    VerificaPasta("comprovantes")

    html_out=template.render(template_vars)

    nomearquivo=GeraNomeArquivo(kwargs["tipoGuia"],kwargs["compRodape"])

    HTML(string=html_out).write_pdf("comprovantes/%s.pdf" % nomearquivo)

# pdfdados = {"BANCO":"BANCO DAS GIRAFAS", "GUIA":"GUIA SOCIAL","CodPagto":"0000000",
#              "COMPETENCIA":"000000","IDENTIFICADOR":"0000000000",
#              "VALOR PRINCIPAL":"15.000,89"}
#
# GerarPDF(**dados)
