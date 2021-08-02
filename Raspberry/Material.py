from datetime import datetime
import time
from ConexionBD import ConexionBD

class Material(object):
    def __init__(self, id, fechaHora, refOrdenPlan, tipoMaterial):
        self.id =id
        self.fechaHora = fechaHora
        self.refOrdenPlan = refOrdenPlan
        self.tipoMaterial = tipoMaterial
    
    def getId(self):
        return self.id
        
    def getFechaHora(self):
        return self.fechaHora
    
    def getRefOrdenPlan(self):
        return self.refOrdenPlan

    def getTipoMaterial(self):
        return self.tipoMaterial
    
    def registrarLog(self, evento):
        fechaHora = datetime.now()  
        fecha = fechaHora.strftime('%Y-%m-%d')  
        hora = time.strftime("%H:%M:%S")
        conexion = ConexionBD()
        with conexion:
            conexion.conn.cursor().execute("INSERT INTO LogsRPI(fecha, hora, evento) VALUES (?,?,?)", fecha, hora, evento)
            conexion.conn.commit()
        
    def imprimirMaterial(self):
        print("---------------------------------------------------")
        print("id: " + str(self.id))
        print("fechaHora: " + str(self.fechaHora))
        print("refOrdenPlan: " + str(self.refOrdenPlan))
        print("tipoMaterial: " + str(self.tipoMaterial))
        print("---------------------------------------------------")
    
    def registrarBD(self):
        try:
            conexion = ConexionBD()
            with conexion:
                conexion.conn.cursor().execute("INSERT INTO Material(id, fechaHora,  refOrdenPlan, tipo) VALUES (?,?,?,?)", self.id, self.fechaHora, self.refOrdenPlan, self.tipoMaterial)
                conexion.conn.commit()
        except Exception as e:
            evento = "Ocurrio un error en la funcion registrarBD en la clase Material registrando una " + self.tipoMaterial + ": " + str(e)
            self.registrarLog(evento)
            #print(evento)
            