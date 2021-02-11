#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 10:36:05 2020

@author: txominaboitiz
"""

import pandas as pd
from helpers import convertir_float, strip_accents
import os

def parse_unidades(datos):
    for i in datos.index:
        producto = datos['Producto'][i].lower() # paso todo a minuscula
        producto = strip_accents(producto) # elimino tildes
        cant = int(datos['Cantidad'][i])
        if producto[-1] == '.': # elimino puntos al final del string
            producto = producto[:-1]
        divisores = [' x ', ' por ']
        sep = False
        for divisor in divisores:
            if divisor in producto:
                prod, uni = producto.split(divisor)
                sep = True
        if not sep:
            prod, uni = producto, 'u'
        yield prod, cant, uni # genero tupla con dos elementos: (producto, unidad)

def parse_est_uni(productos):
    for linea in productos:
        prod = linea[0]
        cant_orig = linea[1]
        if len(linea[2].split()) >= 2:
            cant, uni = linea[2].split()[0], linea[2].split()[1]
        else:
            cant, uni = '1', linea[2]
        cant = convertir_float(cant) # convierto cantidades a float
        # estandarizo unidades
        if uni in ['g', 'gr', 'grs', 'gs']:
            uni = 'kg'
            cant = cant / 1000
        elif uni in ['kg', 'kgs', 'k']:
            uni = 'kg'
        yield prod, cant * cant_orig, uni
        
def conv_planta(prod, pesos_plantas):
    check = False
    for planta in pesos_plantas.keys():
        if planta in prod:
            cant = pesos_plantas[planta]
            check = True
            break
    if check:
        return prod, cant, 'kg'
    else:
        if f'planta de {prod}' not in pesos_desconocidos:
            pesos_desconocidos.append(f'planta de {prod}')
        return prod, .75, 'kg'

def conv_cajon(prod, pesos_cajones):
    check = False
    for cajon in pesos_cajones.keys():
        if cajon in prod:
            cant = pesos_cajones[cajon]
            check = True
            break
    if check:
        return prod, cant, 'kg'
    else:
        if f'cajon de {prod}' not in pesos_desconocidos:
            pesos_desconocidos.append(f'cajon de {prod}')
        return prod, 15, 'kg'

def conv_bolson(prod, pesos_bolsones):
    prod
    check = False
    for bolson in pesos_bolsones.keys():
        if bolson in prod:
            cant = pesos_bolsones[bolson]
            check = True
            break
    if check:
        return prod, cant, 'kg'
    else:
        if f'bolson de {prod}' not in pesos_desconocidos:
            pesos_desconocidos.append(f'bolson de {prod}')
        return prod, 15, 'kg'
    
def parse_conv_kg(productos, pesos_ref):
    for producto in productos:
        prod, cant, uni = producto
        if uni in ['planta', 'atado']:
            camino = 'planta'
        elif 'cajon' in prod:
            camino = 'cajon'
        elif 'bolsa' in prod or 'bolson' in prod:
            camino = 'bolson'
        else:
            camino = None
        caminos = {'planta': conv_planta,
                   'cajon': conv_cajon,
                   'bolson': conv_bolson}
        if not camino:
            yield prod, cant, uni
        else:
            yield caminos[camino](prod, pesos_ref[camino])
            
def df_to_dict(df, key, val):
    return {df[key][i]: df[val][i] for i in df.index}

def pesos_referencia():
    with open(os.path.join('in', 'pesos_productos.xlsx'), 'rb') as f:
        plantas = pd.read_excel(f, sheet_name = 'Plantas y atados')
        cajones = pd.read_excel(f, sheet_name = 'Cajones')
        bolsones = pd.read_excel(f, sheet_name = 'Bolsones')
    for df in [plantas, cajones, bolsones]:
        for i in df.index:
            df.at[i, 'Producto'] = strip_accents(df['Producto'][i].lower())
    pesos_ref = {}
    for key, df in {'planta': plantas, 'cajon': cajones, 'bolson': bolsones}.items():
        pesos_ref[key] = df_to_dict(df, 'Producto', 'Peso unitario (kg)')
    return pesos_ref
        
def limpiar_datos(planilla):
    datos = planilla.copy()
    pesos_ref = pesos_referencia()
    global pesos_desconocidos
    pesos_desconocidos = []
    datos = (dato for dato in parse_unidades(datos))
    datos = (dato for dato in parse_est_uni(datos))
    datos = [dato for dato in parse_conv_kg(datos, pesos_ref)]
    return pd.DataFrame(datos, columns = ['Producto', 'Cantidad', 'Unidad']), pesos_desconocidos


    


    
                    
                
            
            
        
        
        
        