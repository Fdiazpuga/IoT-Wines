#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 01:42:30 2020

@author: fabian
"""


from Proceso import Proceso
from time import sleep
from datetime import datetime
from OrdenPlanificada import OrdenPlanificada
import RPi.GPIO as GPIO
from ConexionBD import ConexionBD

#Registra algun evento realizado por la RPI (ejecucion del script, un error, etc)
def registrarLog(evento):
    fechaHora = datetime.now()  
    fecha = fechaHora.strftime('%Y-%m-%d')  
    hora = fechaHora.strftime("%H:%M:%S")
    conexion = ConexionBD()
    with conexion:
        conexion.conn.cursor().execute("INSERT INTO LogsRPI(fecha, hora, evento) VALUES (?,?,?)", fecha, hora, evento)
        conexion.conn.commit()
       
#Obtiene una orden que se encuentre iniciada en la base de datos
def obtenerOrdenIniciada():
    try:
        query = "SELECT OrdenPlanificada.*, Orden.formatoCaja FROM OrdenPlanificada JOIN Orden on Orden.ordenFabricacion=OrdenPlanificada.refOrden WHERE OrdenPlanificada.estadoFinal='Abierta' Order by OrdenPlanificada.fechaFabricacion, OrdenPlanificada.secuencia"
        #fecha = datetime.now().strftime('%Y-%m-%d')
        #query = "SELECT OrdenPlanificada.*, Orden.formatoCaja FROM OrdenPlanificada JOIN Orden ON Orden.ordenFabricacion=OrdenPlanificada.refOrden WHERE fechaFabricacion = '"+fecha+"'"
        conexion = ConexionBD()
        
        with conexion:
            datos = conexion.conn.cursor().execute(query).fetchall()
            conexion.conn.commit()

            for row in datos:
                if(row[9]==1):
                    orden = OrdenPlanificada(row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[9],row[10],row[11], row[13])
                    return orden
        return None
        
    except Exception as e:
        evento = "Ocurrio un error en la funcion obtenerOrdenIniciada: " + str(e)
        #print(evento)
        registrarLog(evento)

#Cambia el estado de la orden que se encuentra en ejecucion
def cambiarEstado(orden):
    try:
        #fecha = datetime.now().strftime('%Y-%m-%d')
        #query = "SELECT * FROM OrdenPlanificada WHERE fechaFabricacion = '"+fecha+"' and refOrden = '"+str(orden.getRefOrden())+"'"
        query = "SELECT * FROM OrdenPlanificada WHERE refOrden = '"+str(orden.getRefOrden())+"'"

        conexion = ConexionBD()
        
        with conexion:
            datos = conexion.conn.cursor().execute(query).fetchall()
            conexion.conn.commit()
            for row in datos:
                if(orden.getId()==row[0]):
                    orden.setEstado(row[9])                
        return orden
        
    except Exception as e:
        evento = "Ocurrio un error en la funcion cambiarEstado en Main: " + str(e)
        #print(evento)
        registrarLog(evento)
        
#Funcion principal para ejecutar una orden iniciada
def main():
    try:        
        #i=False
        
        while True:
            orden = obtenerOrdenIniciada()
            if(orden!=None):
                #orden.imprimirOrden()
                td = Proceso(orden)
                #sleep(3) #Ayuda a que inicien los sensores sin que cuenten
                td.start()
                
                while(orden.getEstado()==1):
                    orden = cambiarEstado(orden)
                    sleep(3)
                    
                
                #i=False
                
            """elif(i!=True):
                print("\nNo hay ordenes iniciadas\n")
                sleep(0.3)
                print("\nEsperando nueva orden...\n")
                i = True"""
 
                
    except Exception as e:
        evento = "Ocurrio un error en la funcion main: " + str(e)
        registrarLog(evento)
        #print(evento)
        
    except KeyboardInterrupt:
        evento = "Se ha interrumpido el proceso en la funcion main desde teclado Ctrl+c"
        registrarLog(evento)
        #print(evento)
    finally:
        GPIO.cleanup() # asegura una salida limpia de sensores
        
        
#Ejecuta la funcion principal
evento = "Se comienza a ejecutar el script para procesar datos"
registrarLog(evento)
#print(evento)
main()        
        
        

    

