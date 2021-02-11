#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 11:21:54 2020

@author: txominaboitiz
"""

import pandas as pd
import numpy as np

def total_unidades(planilla):
    numeros_unidades = np.array([planilla['Cantidad'][i] for i in planilla.index])
    return sum(numeros_unidades)

def sumkg(datos):
    kg_por_producto = np.array([datos['Cantidad'][i] for i in datos.index
                                if 'kg' in datos['Unidad'][i]
                                and 'dulce de leche' not in datos['Producto'][i].lower()
                                and 'queso' not in datos['Producto'][i].lower()])
    kg_total = sum(kg_por_producto)
    return int(round(kg_total))

def calcular_metricas(clientes, datos, planilla, fecha):
    metricas = pd.DataFrame({
        'Familias': len(clientes),
        'Unidades': total_unidades(planilla),
        'KG Total': sumkg(datos)
        }, index = [fecha])
    return metricas

