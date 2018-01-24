# encoding: utf-8

from __future__ import print_function
import pandas as pd
import numpy as np
import tempfile
from jinja2 import Environment, FileSystemLoader

from weasyprint import HTML

env = Environment(loader=FileSystemLoader('.'))
template= env.get_template("ModelRecibo.html")

def GerarPDF(**kwargs):
    filename = tempfile.mktemp(".txt")
    textoEntrada = open(filename, "w")
    for key, value in kwargs.items():
        textoEntrada.write("%s : %s\n" %(key,value))
    textoEntrada.close()
    print(">> %s \n" % filename)

    data = pd.read_csv(filename,sep=":",header=None)

    data.columns=["Item","Valor"]
    print(data)
    data.head()

    # print(kwargs["BANCO"])

    print("\n")
    file = open(filename, "r")
    print(file.read())

    template_vars = {"banco_pagamento": kwargs["BANCO"].upper(), "guia":kwargs["GUIA"],
                     "CodPagto":kwargs["CodPagto"],"Competencia":kwargs["COMPETENCIA"],
                     "Identificador":kwargs["IDENTIFICADOR"],"ValorPrincipal":kwargs["VALOR PRINCIPAL"]
                     }

    html_out=template.render(template_vars)

    HTML(string=html_out).write_pdf("comprovante.pdf")



dados = {"BANCO":"BANCO DAS GIRAFAS", "GUIA":"GUIA SOCIAL","CodPagto":"0000000",
             "COMPETENCIA":"000000","IDENTIFICADOR":"0000000000",
             "VALOR PRINCIPAL":"15.000,89"}

GerarPDF(**dados)
