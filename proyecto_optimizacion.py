# coding=utf-8
from gurobipy import *

def suman_4(x1,x2,x3,x4,x5,x6,x7,x8): # Será usada en restricción 12
    if x1+x2+x3+x4+x5+x6+x7+x8 == 4:
        return 1
    return 0

def suman_2(x1,x2): # Será usada en restricción 13
    if x1+x2:
        return 1
    return 0

def total_es_2(x):
    if x == 2:
        return 1
    return 0
def total_es_4(x):
    if x == 4:
        return 1
    return 0
# ---------------------------------------  CONJUNTOS ---------------------------------------------------
# Conjunto de Equipos I
equipos_1 = ["CD Boston College", "CD Liceo Curicó", "CD Alemán de Concepción", "CD Quilicura Basket", "Estadio Español"]
equipos_2 = ["CD Brisas", "CD Ceppi", "CD Arturo Prat de San Felipe", "Stadio Italiano", "CD Manquehue"]
equipos_3 = ["Club Atlético Puerto Varas", "CD AB Temuco", "CD La Unión", "CD Achao", "Estadio Palestino", "Club Andino de Los Ángeles"]
equipos = equipos_1 + equipos_2 + equipos_3 # Se dividieron en 3 para que sea más fácil visualizarlos todos, pero en realidad es un solo conjunto
# Conjunto de Fechas T
fechas = list(range(1,(len(equipos)*2) - 1))  # Son 30 fechas
# Consideraciones
cons = list(range(1, 5))
# Conjunto de Árbitros A
arbitros = ["a", "b", "c", "d", "e", "f", "g", "h"]  # Se puede variar
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARÁMETROS -----------------------------------------------------
arbitrar_at = {}
for arb in arbitros:   # Por el momento está en 1 este parámetro
    for fecha in fechas:
        arbitrar_at[arb,fecha] = 1

# ----------------------------------------------------------------------------------------------------------------

# --------------------------------------------------MODELO----------------------------------------------------------

modelo = Model("Segunda División de Básquetbol Competitiva")

# Se definen las variables
partido_ijt = {}  #local, visita, fecha
#incumple_itn = {} #equipo, fecha, consideración (no está en uso)
incumple_n = {} #consideración
# Se añade la variable que indica si el equipo juega o no en una determinada fecha
for fecha in fechas:
    for local in equipos:
        for visita in equipos:
            partido_ijt[local,visita,fecha] = modelo.addVar(vtype = GRB.BINARY, name= "x_{}_{}_{}".format(local,visita,fecha))
# Se añade la variable que lleva el registro de cuantas veces se incumple una consideración
for i in cons:
    incumple_n[i] = modelo.addVar(vtype = GRB.INTEGER, name = "y_{}".format(str(i)))
# Se añade la variable que determina qué árbitro arbitra cada partido
arbitrar_aijt = {}
for arb in arbitros:
    for i in equipos:
        for j in equipos:
            for fecha in fechas:
                arbitrar_aijt[arb,i,j,fecha] = modelo.addVar(vtype=GRB.BINARY,name = "w_{}_{}_{}_{}".format(arb,i,j,fecha))
modelo.update()
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------FUNCIÓN OBJETIVO-------------------------------------------------------------------

objetivo = quicksum(incumple_n[n] for n in cons)
modelo.setObjective(objetivo,GRB.MINIMIZE)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES BÁSICAS-------------------------------------------------------------------

# R1
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for fecha in fechas) == 1)

# R2
for local in equipos:
    modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for visita in equipos for fecha in fechas) == (len(equipos) - 1))

# R3
for local in equipos:
    for fecha in fechas:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) == 1)

# R4
for fecha in fechas:
    if local != visita:
        modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for local in equipos for visita in equipos) == (len(equipos)//2))

# R5
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(partido_ijt[local,local,fecha] == 0)

# R6
for local in equipos:
    if local!= visita:
        modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos for fecha in range(1,(len(fechas)//2) + 1)) == (len(equipos) - 1))

#R7
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local, visita, fecha] + partido_ijt[visita, local, fecha]) for fecha in range(1,(len(fechas)//2) + 1)) == 1)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES ARBITRAJE-------------------------------------------------------------------

#R(9,10)
for local in equipos:
    for visita in equipos:
        if local != visita:
            for fecha in fechas:
                modelo.addConstr(quicksum(arbitrar_aijt[arb,local,visita,fecha] for arb in arbitros) == partido_ijt[local,visita,fecha])

# R(8,11)
for arb in arbitros:
    for fecha in fechas:
        modelo.addConstr(quicksum(arbitrar_aijt[arb,local,visita,fecha] for local in equipos for visita in equipos) <=
        arbitrar_at[arb,fecha])

# R12
modelo.addConstr(quicksum(total_es_4(partido_ijt[i,j,t] + quicksum(partido_ijt[i,k,t-1] + quicksum(partido_ijt[i,j,h] +
                                                        partido_ijt[i,k,h-1] for h in fechas[((len(fechas)//2)) + 2:])
                                                        for k in equipos)) for j in equipos for i in equipos
                                                        for t in fechas[2:(len(fechas)//2)+1]) == len(equipos)*len(equipos)*incumple_n[1])

# R13
modelo.addConstr(quicksum(total_es_2(quicksum(partido_ijt[i,j,t-1] for j in equipos) + quicksum(partido_ijt[i,k,t] for k in equipos))
                                   for i in equipos for t in fechas[1:]) == len(equipos)*incumple_n[2])
modelo.addConstr(quicksum(total_es_2(quicksum(partido_ijt[j,i,t-1] for j in equipos) + quicksum(partido_ijt[k,i,t] for k in equipos))
                                   for i in equipos for t in fechas[1:]) == len(equipos)*incumple_n[2])

# R14
modelo.addConstr(quicksum(total_es_2(arbitrar_aijt[arb,i,j,t] +
                                 quicksum(arbitrar_aijt[arb,j,i,h] for h in fechas[(len(fechas)//2) + 1:])) for i in equipos
                                   for j in equipos for t in fechas[:(len(fechas)//2) + 1]) == len(equipos)*len(equipos)*incumple_n[3])

# R15
modelo.addConstr(quicksum((quicksum(total_es_2(total_es_2(quicksum((partido_ijt[local,j,fecha1] +
        arbitrar_aijt[arb,local,j,fecha1])for j in equipos))
        + total_es_2(quicksum((partido_ijt[local,l,fecha2] +
        arbitrar_aijt[arb,local,l,fecha2]) for l in equipos)))
        for fecha2 in range(1,fecha1) for local in equipos
        for arb in arbitros)/(fecha1-1)) for fecha1 in range(2,len(fechas) + 1))  == len(equipos)*len(arbitros)*incumple_n[4])

#----------------Optimizar------------------------
modelo.Params.method = -1 # 2 = Barrier, -1 = Auto
modelo.optimize()
modelo.printAttr("X")