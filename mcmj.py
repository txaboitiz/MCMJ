#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 10:34:38 2020

@author: txominaboitiz
"""

from metricas import calcular_metricas
from archivos import clientes_entrega, clientes_nuevos, turnos
from pipeline import limpiar_datos
import os
import sys
import pandas as pd

def cerrar():
    sys.exit()

def print_df(df, select):
    print('')
    print('----------------------------------------------------------------------------------------------------')
    if select == 'nuevos':
        if df.empty:
            print('No hay clientes nuevos en esta entrega')
            print('----------------------------------------------------------------------------------------------------')
            print('')
            return
    print(df)
    print('----------------------------------------------------------------------------------------------------')
    if pesos_desconocidos and select == 'metricas':
        print('Se desconocen los pesos de los siguientes productos: ')
        for p in pesos_desconocidos:
            print(f'\t{p}')
    print('')

def print_config():
    print(' ')
    print('----------------------------------------------------------------------------------------------------')
    print('IMPORTANTE: Nunca modificar los nombres de los archivos y directorios listados a continuación.')
    print('De lo contrario, se pudre todo :)')
    print('----------------------------------------------------------------------------------------------------')
    print('Directorio de archivos de lectura: "in"\n')
    print('Archivos de lectura: ')
    print('\tBase de datos de clientes: "clientes_db.xlsx"')
    print('\t\tColumnas: "Nombre y Apellido" | "Correo electronico" | "Telefono" | "Turno" | "Cliente asociade"')
    print('\t-----------------')
    print('\tPesos de productos: "pesos_productos.xlsx"')
    print('\t\tSolapas: "Plantas y atados" | "Cajones" | "Bolsones"')
    print('\t\tColumnas por solapa: "Producto" | "Peso unitario (kg)"')
    print('\t-----------------')
    print('\tDetalle de turnos: "turnos.xlsx"')
    print('\t\tColumnas: "Turno" | "Horario"')
    print('\t-----------------')
    print('\tReporte de pedidos: "reporte_pedidos_AAAA-MM-DD.xlsx"')
    print('\t\tEsta fecha (AAAA-MM-DD) es la que busca el programa cuando se pide ingresar fecha de entrega')
    print('\n-----------------')
    print('\nDirectorio de archivos generados: "out"\n')
    print('----------------------------------------------------------------------------------------------------')
    print('Ante pesos desconocidos de productos vendidos por planta, cajón o bolsón, se utilizan los siguientes pesos:')
    print('\tPlantas y atados: 0.75 kg')
    print('\tCajones: 15 kg')
    print('\tBolsones: 15 kg')
    print('Estos valores son inmodificables. Para actualizar los pesos de los productos, se debe modificar\n\tel archivo "pesos_productos.xlsx", en la solapa correspondiente')
    print('----------------------------------------------------------------------------------------------------')
    print('')


def codes():
    print(' ')
    print('--------------------------------------- MANUAL DE FUNCIONES ----------------------------------------')
    print('| m: Mostrar métricas        | n: Mostrar clientes nuevos | exp: Exportar métricas y nuevos a excel |')
    print('----------------------------------------------------------------------------------------------------')
    print('| t: Generar turnos en excel | config: Mostrar detalles de configuración del programa               |')
    print('----------------------------------------------------------------------------------------------------')
    print('| man: Mostrar manual de funciones                        | exit: Cerrar sesión                     |')
    print('----------------------------------------------------------------------------------------------------')
    print('')

def exportar_info(metricas, nuevos):
    writer = pd.ExcelWriter(os.path.join('out','metricas y nuevos.xlsx'))
    nuevos.to_excel(writer, sheet_name='nuevos')
    metricas.to_excel(writer, sheet_name='metricas')
    writer.save()
    print(' ')
    print('----------------------------------------------------------------------------------------------------')
    print('La información solicitada fue exportada al archivo "out/metricas y nuevos.xlsx"')
    print('----------------------------------------------------------------------------------------------------')
    print('')

def interfaz(archivo_turnos, clientes_db, clientes, nuevos, metricas, pesos_desconocidos):
    codes()
    funciones = {'m': (print_df, (metricas, 'metricas')),
                 'n': (print_df, (nuevos, 'nuevos')),
                 'exp': (exportar_info, (metricas, nuevos)),
                 't': (turnos, (clientes_db, clientes, archivo_turnos)),
                 'man': (codes, ()),
                 'config': (print_config,()),
                 'exit': (cerrar, (),)}
    while True:
        f = str(input('Ingrese funcion: '))
        if f not in funciones.keys():
            print('La funcion ingresada no es valida. Intente nuevamente.')
            continue
        func, args = funciones[f][0], funciones[f][1]
        func(*args)
    return

def main():
    print(' ')
    print('¡Bienvenide!\nPara continuar, ingrese la fecha de entrega en el formato especificado')
    print('Si quiere cerrar la sesión, podrá hacerlo en cualquier momento ingresando "exit".')
    print(' ')
    print('----------------------------------------------------------------------------------------------------')
    check = False
    while not check:
        fecha = str(input('Fecha de entrega (AAAA-MM-DD): '))
        if fecha == 'exit':
            sys.exit()
        pedidos = os.path.join('in', f'reporte_pedidos_{fecha}.xlsx')
        if not os.path.isfile(pedidos):
            print('No se encontró un reporte de pedidos para la fecha ingresada. Intente nuevamente')
        else:
            print('\n¡Reporte encontrado!')
            check = True
    archivo_turnos = os.path.join('out', f'turnos_{fecha}.xlsx')
    planilla = pd.read_excel(pedidos)
    global pesos_desconocidos
    datos, pesos_desconocidos = limpiar_datos(planilla)
    clientes = clientes_entrega(planilla)
    clientes_db = os.path.join('in', 'clientes_db.xlsx')
    nuevos = clientes_nuevos(clientes_db, clientes)
    metricas = calcular_metricas(clientes, datos, planilla, fecha)
    interfaz(archivo_turnos, clientes_db, clientes, nuevos, metricas, pesos_desconocidos)

if __name__ == '__main__':
    main()
