class OrdenPlanificada(object):
    def __init__(self, id, refOrden, fechaFabricacion, horaInicioPlanificada, horaTerminoPlanificada, botellasPlanificadas, cajasPlanificadas, estado, secuencia, version, formatoCaja):
        self.id = id
        self.refOrden = refOrden
        self.fechaFabricacion = fechaFabricacion
        self.horaInicioPlanificada = horaInicioPlanificada
        self.horaTerminoPlanificada = horaTerminoPlanificada
        self.horaInicio = None
        self.horaTermino = None
        self.botellasPlanificadas = botellasPlanificadas
        self.cajasPlanificadas = cajasPlanificadas
        self.estado = estado
        self.secuencia = secuencia
        self.version = version
        self.formatoCaja = formatoCaja

    def getId(self):
        return self.id
        
    def getRefOrden(self):
        return self.refOrden
        
    def getFechaPlanificacion(self):
        return self.fechaFabricacion
    
    def getHoraInicioPlanificada(self):
        return self.horaInicioPlanificada
    
    def getHoraTerminoPlanificada(self):
        return self.horaTerminoPlanificada
    
    def getHoraInicio(self):
        return self.horaInicio
    
    def getHoraTermino(self):
        return self.horaTermino
    
    def getBotellasPlanificadas(self):
        return self.botellasPlanificadas
    
    def getCajasPlanificadas(self):
        return self.cajasPlanificadas
    
    def getEstado(self):
        return self.estado
    
    def getSecuencia(self):
        return self.secuencia
    
    def getVersion(self):
        return self.version
    
    def getFormatoCaja(self):
        return self.formatoCaja
    
    def setEstado(self, estado):
        self.estado = estado
    
    def setHoraInicio(self, horaInicio):
        self.horaInicio = horaInicio
    
    def setHoraTermino(self, horaTermino):
        self.horaTermino = horaTermino
        
    def imprimirOrden(self):
        print("--------------------------------------------------------------------------------------")
        print("Id: "+ str(self.id))
        print("Ref. Orden: "+ str(self.refOrden))
        print("Fecha de fabricacion: "+ str(self.fechaFabricacion))
        print("Hora inicio planificada: "+ self.horaInicioPlanificada)
        print("Hora termino planificada: "+ self.horaTerminoPlanificada)
        print("Hora inicio: "+ str(self.horaInicio))
        print("Hora termino: "+ str(self.horaTermino))
        print("Botellas planificadas: "+ str(self.botellasPlanificadas))
        print("Cajas planificadas: "+ str(self.cajasPlanificadas))
        print("Estado: "+ str(self.estado))
        print("Secuencia: "+ str(self.secuencia))
        print("Version: " + self.version)
        print("Formato de caja: " + self.formatoCaja)
        print("--------------------------------------------------------------------------------------\n")