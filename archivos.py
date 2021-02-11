#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 10:25:01 2020

@author: txominaboitiz
"""

import pandas as pd
from helpers import est_nombre, escribir_excel
import math
from collections import defaultdict
import os

def clientes_entrega(planilla):
    clientes = planilla.drop_duplicates(subset=['Nombre y apellido']).copy()
    clientes = clientes[['Nombre y apellido','Correo electronico', 'Telefono']]
    clientes['Nombre y apellido'] = clientes['Nombre y apellido'].map(lambda x: est_nombre(x))
    return (clientes.set_index('Nombre y apellido')).sort_index()

def clientes_nuevos(clientes_db, clientes):
    db = (pd.read_excel(clientes_db)).set_index('Nombre y Apellido')
    return clientes.loc[[nombre for nombre in clientes.index if nombre not in db.index]]

def actualizar_db(clientes_db, nuevos):
    db = (pd.read_excel(clientes_db)).set_index('Nombre y Apellido')
    if not nuevos.empty:
        nuevos['Turno'] = '-'
        db = (db.append(nuevos)).sort_index()
    db['Turno'] = db['Turno'].astype(str)
    escribir_excel(db, clientes_db, indice_col = 'Nombre y Apellido')
    return

def def_turnos():
    df_turnos = (pd.read_excel(os.path.join('in','turnos.xlsx'))).astype({'Turno': 'str'})
    dict_turnos = {}
    for i in df_turnos.index:
        dict_turnos[(df_turnos['Turno'][i]).capitalize()] = df_turnos['Horario'][i]
    for t in dict_turnos:
        try:
            if math.isnan(dict_turnos[t]):
                dict_turnos[t] = 'nan'
        except TypeError:
            continue
    return dict_turnos

def juntar_clientes(db, clientes_x_turno):
    for turno in clientes_x_turno:
        for i, cliente in enumerate(clientes_x_turno[turno]):
            if db.loc[cliente]['Cliente asociade'] in clientes_x_turno[turno]:
                clientes_x_turno[turno][i] = f'{cliente} y {db.loc[cliente]["Cliente asociade"]}'
                clientes_x_turno[turno].remove(db.loc[cliente]['Cliente asociade'])
                
def turnos(clientes_db, clientes, archivo_turnos):
    nuevos = clientes_nuevos(clientes_db, clientes)
    actualizar_db(clientes_db, nuevos)
    db = pd.read_excel(clientes_db, index_col = 'Nombre y Apellido')
    # Genero diccionario con clientes y sus turnos
    turnos_x_cliente = {nombre: (str(db.loc[nombre]['Turno'])).capitalize() for nombre in db.index
                        if nombre in clientes.index}
    # Invertir diccionario
    clientes_x_turno = defaultdict(list)
    {clientes_x_turno[v].append(k) for k, v in turnos_x_cliente.items()}
    # Juntar les clientes asociades
    juntar_clientes(db, clientes_x_turno)
    # Extraigo las especificaciones de los turnos
    dict_turnos = def_turnos()
    #Comparo los turnos dict_turnos con los turnos en clientes_db, aseguro que coincidan
    turnos_agendados = [t for t in clientes_x_turno.keys() if t != '-']
    for t in turnos_agendados:
        if t not in dict_turnos:
            print('Los turnos especificados en "turnos.xlsx" no coinciden con los turnos\nasociados a los clientes en "clientes_db.xlsx"\nDebe corregir esto antes de seguir.')
            return    
    # Genero nuevo diccionario con claves para nombres de columna con horario en el excel
    turnos_clavesnuevas = {}
    for t in sorted(clientes_x_turno.keys()):
        if t != '-':
            if dict_turnos[t] in ['-', 'nan']:
                turnos_clavesnuevas[t] = clientes_x_turno[t]
            else:
                turnos_clavesnuevas[f'Turno {t} ({dict_turnos[t]})'] = clientes_x_turno[t]
    if '-' in clientes_x_turno:
        turnos_clavesnuevas['Nuevos'] = clientes_x_turno['-']
    # Genero el archivo de turnos
    turnos = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in turnos_clavesnuevas.items() ]))
    escribir_excel(turnos, archivo_turnos, indice_desde_cero=False)
    print('')
    print('----------------------------------------------------------------------------------------------------')
    print(f'Los turnos fueron generados en el archivo "{archivo_turnos}"')
    print('----------------------------------------------------------------------------------------------------')
    print('')
    return