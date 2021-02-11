#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 10:17:41 2020

@author: txominaboitiz
"""

import pandas as pd
import numpy as np
import unicodedata

def convertir_float(numero):
    valores = numero.split('/')
    if len(valores) == 2:
        nom = float(valores[0])
        denom = float(valores[1])
        return nom / denom
    else:
        return float(numero)

def escribir_excel(data, archivo, indice_desde_cero=True, indice_col=False):
    if not indice_desde_cero:
        data.index = np.arange(1, len(data) + 1)
    writer = pd.ExcelWriter(archivo)
    if not indice_col:
        data.to_excel(writer)
    else:
        data.to_excel(writer, index_label=indice_col)
    writer.save()
    return

def est_nombre(nombre):
    nombre_est = [n.capitalize() for n in nombre.split()]
    nombre_est = ' '.join(nombre_est)
    return nombre_est

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')