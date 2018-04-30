# coding=utf-8
from gurobipy import *

# ---------------------------------------  CONJUNTOS ---------------------------------------------------
# Conjunto de Fechas T
fechas = list(range(1, 31))  # Son 30 fechas
# Conjunto de Equipos I
equipos_1 = ["CD Boston College", "CD Liceo Curicó", "CD Alemán de Concepción", "CD Quilicura Basket", "Estadio Español"]
equipos_2 = ["CD Brisas", "CD Ceppi", "CD Arturo Prat de San Felipe", "Stadio Italiano", "CD Manquehue"]
equipos_3 = ["Club Atlético Puerto Varas", "CD AB Temuco", "CD La Unión", "CD Achao", "Estadio Palestino", "Club Andino de Los Ángeles"]
equipos = equipos_1 + equipos_2 + equipos_3 # Se dividieron en 3 para que sea más fácil visualizarlos todos, pero en realidad es un solo conjunto
# Consideraciones
cons = list(range(1, 5))
# Conjunto de Árbitros A
arbitros = ["No encontré"]
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARÁMETROS -----------------------------------------------------
puede_arbitrar_el_arbitro_i = {}

# ----------------------------------------------------------------------------------------------------------------

# --------------------------------------------------MODELO----------------------------------------------------------

modelo = Model("Segunda División de Básquetbol Competitiva")

# Se definen las variables
partido_ijt = {}  #local, visita, fecha
incumple_itn = {} #equipo, fecha, consideración
incumple_n = {} #consideración
# Se añade la variable que indica si el equipo juega o no en una determinada fecha
for fecha in fechas:
    for local in equipos:
        for visita in equipos:
            partido_ijt[local,visita,fecha] = modelo.addVar(vtype = GRB.BINARY, name= "x_{}_{}_{}".format(local,visita,fecha))
# Se añade la variable que lleva el registro de cuantas veces se incumple una consideración
for i in cons:
    incumple_n[i] = modelo.addVar(vtype = GRB.INTEGER, name = "y_{}".format(str(i)))
# Se añade la variable que indica si se incumplió una consideración
for con in cons:
    for equipo in equipos:
        for fecha in fechas:
            incumple_itn[equipo, fecha, con] = modelo.addVar(vtype = GRB.BINARY, name = "z_{}_{}_{}".format(equipo,fecha,con))

modelo.update()
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------FUNCION OBJETIVO-------------------------------------------------------------------

objetivo = quicksum(incumple_n[n] for n in cons)
modelo.setObjective(objetivo,GRB.MINIMIZE)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES básicas-------------------------------------------------------------------


# R1
for local in equipos:
    for visita in equipos:
        modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for fecha in fechas) == 1)

# R2
for local in equipos:
    modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for visita in equipos for fecha in fechas) == (len(equipos) - 1))

# R3
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) == 1)

# R4
for fecha in fechas:
    modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for local in equipos for visita in equipos) == (len(equipos)//2))

# R5
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(partido_ijt[local,local,fecha] == 0)

# R6
for local in equipos:
    modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos for fecha in range(1,(len(fechas)//2) + 1)) == (len(equipos) - 1))

#R7
for local in equipos:
    for visita in equipos:
        modelo.addConstr(quicksum((partido_ijt[local, visita, fecha] + partido_ijt[visita, local, fecha]) for fecha in range(1,(len(fechas)//2) + 1)) == 1)



# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES arbitraje-------------------------------------------------------------------



# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES consideraciones-------------------------------------------------------------------

# R12

for local in equipos:
    for equipok in equipos:
        for visita in equipos:
            for fecha1 in range(2, (len(fechas)//2 + 1)):
                for fecha2 in range((len(fechas)//2 + 2), (len(fechas) + 1)):
                    modelo.addConstr((partido_ijt[local, visita, fecha1] + partido_ijt[visita, local, fecha1]
                                 + partido_ijt[local, equipok, (fecha1 - 1)] + partido_ijt[equipok, local, (fecha1 - 1)]
                                 + partido_ijt[local, visita, fecha2] + partido_ijt[visita, local, fecha2]
                                 + partido_ijt[local, equipok, (fecha2 - 1)] + partido_ijt[equipok, local, (fecha2 - 1)]
                                 - incumple_itn[local, fecha1, 1]) <= 3)

# R13
for local in equipos:
    for equipok in equipos:
        for visita in equipos:
            for fecha in range(2, (len(fechas) + 1)):
                modelo.addConstr((partido_ijt[local, visita, (fecha - 1)] + partido_ijt[local, equipok, fecha] - 1) <= (incumple_itn[local, fecha, 2]))



# FALTAN RESTRICCIONES DE ARBITRAJE R14, R15

# R16
for n in cons:
    modelo.addConstr((quicksum(incumple_itn[equipo, fecha, n] for equipo in equipos for fecha in fechas)) == incumple_n[n])

# R17 (N.V)
for n in cons:
    modelo.addConstr(incumple_n[n] >= 0)

#----------------Optimizar------------------------
modelo.update()    
modelo.optimize()
