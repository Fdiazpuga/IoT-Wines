#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 01:41:22 2020

@author: pi
"""


from datetime import datetime
from time import sleep
from threading import Lock, Thread
import threading

from OrdenPlanificada import OrdenPlanificada
from ConexionBD import ConexionBD

from Sensor import Sensor
import RPi.GPIO as GPIO

try:
   import queue
except ImportError:
   import Queue as queue

class Proceso(threading.Thread):
    #Registra algun evento realizado por la RPI (ejecucion del script, un error, etc)
    def registrarLog(self, evento):
        fechaHora = datetime.now()  
        fecha = fechaHora.strftime('%Y-%m-%d')  
        hora = fechaHora.strftime("%H:%M:%S")
        conexion = ConexionBD()
        with conexion:
            conexion.conn.cursor().execute("INSERT INTO LogsRPI(fecha, hora, evento) VALUES (?,?,?)", fecha, hora, evento)
            conexion.conn.commit()

    #Cambia el estado de la orden que se encuentra en ejecucion
    def cambiarEstado(self):
        try:
            #while(self.orden.getEstado()<=2):
            validar = True
            while(validar):
                
                #fecha = datetime.now().strftime('%Y-%m-%d')
                #query = "SELECT * FROM OrdenPlanificada WHERE fechaFabricacion = '"+fecha+"' and refOrden = '"+str(self.orden.getRefOrden())+"'"
                query = "SELECT * FROM OrdenPlanificada WHERE refOrden = '"+str(self.orden.getRefOrden())+"'"
                conexion = ConexionBD()
                
                with conexion:
                    datos = conexion.conn.cursor().execute(query).fetchall()
                    conexion.conn.commit()
                    for row in datos:
                        #if(self.orden.getId()==row[0] and self.orden.getEstado()!=row[9]):
                        if(self.orden.getId()==row[0] and row[9]!=self.orden.getEstado()):
                            #print("Cambio de estado a " + str(row[9]))
                            self.orden.setEstado(row[9])   
                            validar = False
                            #self.sensorBotella.getOrden().setEstado(row[9])
                            #self.sensorCaja.getOrden().setEstado(row[9]) 
            #evento = "Se termino de ejecutar la funcion  cambiarEstado en la clase Proceso"
            #print(evento)
        except Exception as e:
            evento = "Ocurrio un error en la funcion cambiarEstado en Main: " + str(e)
            #print(evento)
            self.registrarLog(evento)
        except KeyboardInterrupt:
            evento = "Se ha interrumpido el proceso en la funcion cambiarEStado desde teclado Ctrl+c"
            #GPIO.cleanup() # asegura una salida limpia de sensores 
            self.registrarLog(evento)
            #print(evento)
            
            
    #Obtiene la cantidad de botellas que se encuentran registrada en la base de datos
    def obtenerNumeroMaterial(self, tipoMaterial):
        try:
            query = "SELECT count(*) FROM Material WHERE refOrdenPlan = '" + str(self.orden.getId()) + "' and tipo = '" + tipoMaterial + "'"
            conexion = ConexionBD()
            contMaterial = 1
            
            with conexion:
                datos = conexion.conn.cursor().execute(query).fetchall()
                conexion.conn.commit()
                for row in datos:
                    contMaterial = row[0]+1     
            return contMaterial
            
        except Exception as e:
            evento = "Ocurrio un error en la funcion obtenerNumeroMaterial obteniendo cantidad de " + str(tipoMaterial) + ": " + str(e)
            self.registrarLog(evento)
            #print(evento)    
        except KeyboardInterrupt:
            evento = "Se ha interrumpido el proceso en la funcion obtenerNumeroMaterial desde teclado Ctrl+c"
            #GPIO.cleanup() # asegura una salida limpia de sensores 
            self.registrarLog(evento)
            #print(evento)

    def run(self):
        try:            
            #Ejecuta la funcion principal
            evento = "Se comienza a procesar datos de la orden num. " + str(self.orden.refOrden) + " con "+ str(self.contBotellas-1) + " contBotellas y " + str(self.contCajas-1)+ " contCajas. "
            self.registrarLog(evento)
            #print(evento)
            #self.orden.imprimirOrden()
            
            #Comienza a crear los hilos de ejecucion y va a depender del formato de botella el sensor que se escogera para el conteo de botellas
            listaThreads = []
            #for func in [self.registro_botellas, self.cargar_registro_botellas, self.registro_cajas, self.cargar_registro_cajas, self.cambiarEstado]:
            for func in [self.sensorBotella.registro,  self.sensorBotella.cargar_registro, self.sensorCaja.registro, self.sensorCaja.cargar_registro, self.cambiarEstado]:
                listaThreads.append(Thread(target=func))
                listaThreads[-1].start()
                sleep(1)
            
            #Esto ayuda a que no se sigan creando hilos de ejecucion de la misma orden hasta que se termine la orden 
            while(self.orden.estado==1):
                pass
            
            if(self.orden.estado==2):
                evento = "La orden Num. " + str(self.orden.getRefOrden()) + " se ha pausado con " + str(self.sensorBotella.getContMaterial()-1) + " contBotellas y " + str(self.sensorCaja.getContMaterial()-1)+ " contCajas"
            
            elif(self.orden.estado==3):
                evento = "La orden Num. " + str(self.orden.getRefOrden()) + " se ha pospuesto con " + str(self.sensorBotella.getContMaterial()-1) + " contBotellas y " + str(self.sensorCaja.getContMaterial()-1)+ " contCajas"
            
            elif(self.orden.estado==4):
                evento = "La orden Num. " + str(self.orden.getRefOrden()) + " ha finalizado con " + str(self.sensorBotella.getContMaterial()-1) + " contBotellas y " + str(self.sensorCaja.getContMaterial()-1)+ " contCajas"
            
            #print(evento)
            self.registrarLog(evento)
            
        except Exception as e:
            evento = "Ocurrio un error en la funcion run: " + str(e)
            self.registrarLog(evento)
            #print(evento)
        finally:
            GPIO.cleanup() # asegura una salida limpia de sensores 
            #print("Limpio los sensores")
            
    """def seleccion_sensor_botella(self):
        #if("187,5" in self.orden.formatoCaja or "375" in self.orden.formatoCaja):
        for formato in ["375", "750"]: #botellines
            if(formato in self.orden.formatoCaja):
                evento = "Se utiliza el sensor 2 para contar botellas debido a que la botella tiene el siguiente formato: " + str(self.orden.formatoCaja)
                self.registrarLog(evento)
                #print(evento)
                return 12,300 #indica sensor 2 y el bouncetime(tiempo de rebote) 
        evento = "Se utiliza el sensor 1 para contar botellines debido a que la botella tiene el siguiente formato: " + str(self.orden.formatoCaja)
        self.registrarLog(evento)
        #print(evento)
        return 18, 300 #indica sensor 2 y el bouncetime(tiempo de rebote)"""
   
    def seleccion_sensor_botella(self):
        #if("187,5" in self.orden.formatoCaja or "375" in self.orden.formatoCaja):
        for formato in ["187,5", "375"]: #botellines
            if(formato in self.orden.formatoCaja):
                evento = "Se utiliza el sensor 1 para contar botellines debido ha que tiene el siguiente formato: " + str(self.orden.formatoCaja)
                self.registrarLog(evento)
                print(evento)
                return 12, 100#indica sensor 
        evento = "Se utiliza el sensor 2 para contar botellas debido ha que tiene el siguiente formato: " + str(self.orden.formatoCaja)
        self.registrarLog(evento)
        #print(evento)
        return 17, 100 #indica sensor 2 350 por defecto 
        #return 12, 100 #indica sensor 2 350 por defecto 
    
    def __init__(self, orden):
        threading.Thread.__init__(self)
        #Datos monitoreo de sensores
        self.numProceso = threading.currentThread().getName()
        self.orden = orden
        self.contBotellas = self.obtenerNumeroMaterial("botella")
        self.contCajas = self.obtenerNumeroMaterial("caja")
        self.numProceso = -1
        self.TRIG_BOTELLA, self.bouncetimeBotella = self.seleccion_sensor_botella()
        #self.TRIG_BOTELLA = self.seleccion_sensor_botella()
        self.TRIG_CAJA = 4 #4
        #self.bouncetimeCaja=1500
        GPIO.setmode(GPIO.BCM)
        
        
        #GPIO.setup(TRIG1, GPIO.IN,pull_up_down=GPIO.PUD_UP)     #CONFIGURACION DEL SENSOR FOTOELECTRICO 1 MODO PULL_UP
        #GPIO.add_event_detect(TRIG1, GPIO.RISING, bouncetime= 310) #Botellas

        
        
        GPIO.setup(self.TRIG_BOTELLA, GPIO.IN,pull_up_down=GPIO.PUD_UP)     #CONFIGURACION DEL SENSOR FOTOELECTRICO 1 MODO PULL_UP
        GPIO.add_event_detect(self.TRIG_BOTELLA, GPIO.RISING, bouncetime = self.bouncetimeBotella) #Botellas
        
        #GPIO.setup(self.TRIG_BOTELLA, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)     #CONFIGURACION DEL SENSOR FOTOELECTRICO 1 MODO PULL_UP
        GPIO.setup(self.TRIG_CAJA, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)     #CONFIGURACION DEL SENSOR FOTOELECTRICO 1 MODO PULL_UP

        #self.sensorBotella = Sensor("Botella", self.orden, self.TRIG_BOTELLA, self.contBotellas, self.bouncetimeBotella)
        self.sensorBotella = Sensor("Botella", self.orden, self.TRIG_BOTELLA, self.contBotellas)
        self.sensorCaja = Sensor("Caja", self.orden, self.TRIG_CAJA, self.contCajas)
        #self.sensorCaja = Sensor("Caja", self.orden, self.TRIG_CAJA, self.contCajas, self.bouncetimeCaja)
        
        
        
        
        
        
        
        
        
        #GPIO.setmode(GPIO.BCM)
        #GPIO.setwarnings(False)
        #GPIO.setup(self.TRIG_BOTELLA, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)     #CONFIGURACION DEL SENSOR FOTOELECTRICO 1 MODO PULL_UP
        #GPIO.setup(self.TRIG_CAJAS, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)     #CONFIGURACION DEL SENSOR CAPACITIVO MODO PULL_UP
        #GPIO.add_event_detect(self.TRIG_BOTELLA, GPIO.RISING, bouncetime= self.bouncetime)

        