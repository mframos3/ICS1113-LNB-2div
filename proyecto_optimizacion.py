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
arbitros = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARÁMETROS -----------------------------------------------------
arbitrar_at = {}
for arb in arbitros:   # Al principio intentemos dejandolo todo en 1, despúes variemos estos numeros
    for fecha in fechas:
        arbitrar_at[arb,fecha] = 1

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
# Se añade la variable que determina qué árbitro arbitra cada partido
arbitrar_aijt = {}
for arb in arbitros:
    for i in equipos:
        for j in equipos:
            for fecha in fechas:
                arbitrar_aijt[arb,i,j,fecha] = modelo.addVar(vtype=GRB.BINARY,name = "w_{}_{}_{}_()".format(arb,i,j,fecha))
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
        if local != visita:
            modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for fecha in fechas) == 1)

# R2
for local in equipos:
    modelo.addConstr(quicksum(quicksum(partido_ijt[local,visita,fecha] for visita in equipos) for fecha in fechas) == (len(equipos) - 1))

# R3
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) == 1)

# R4
for fecha in fechas:
    modelo.addConstr(quicksum(quicksum(partido_ijt[local,visita,fecha] for local in equipos) for visita in equipos) == (len(equipos)//2))

# R5
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(partido_ijt[local,local,fecha] == 0)

# R6
for local in equipos:
    modelo.addConstr(quicksum(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) for fecha in range(1,(len(fechas)//2) + 1)) == (len(equipos) - 1))

#R7
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local, visita, fecha] + partido_ijt[visita, local, fecha]) for fecha in range(1,(len(fechas)//2) + 1)) == 1)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES arbitraje-------------------------------------------------------------------

# R8
for arb in arbitros:
    for fecha in fechas:
        modelo.addConstr((quicksum(arbitrar_aijt[arb,local,visita,fecha] for local in equipos for visita in equipos)) <= 1)

# R9
for local in equipos:
    for fecha in fechas:
        modelo.addConstr((quicksum((arbitrar_aijt[arb,local,visita,fecha] + arbitrar_aijt[arb,visita,local,fecha]) for arb in arbitros for visita in equipos)
                         + quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos)) == 2)

# R10
for arb in arbitros:
    for local in equipos:
        for visita in equipos:
            if local != visita:
                for fecha in fechas:
                    modelo.addConstr(arbitrar_aijt[arb,local,visita,fecha] <= partido_ijt[local,visita,fecha])

# R11
for arb in arbitros:
    for local in equipos:
        for visita in equipos:
            if local != visita:
                for fecha in fechas:
                    modelo.addConstr(arbitrar_aijt[arb,local,visita,fecha] <= arbitrar_at[arb,fecha])
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES consideraciones-------------------------------------------------------------------

# R12

for local in equipos:
    for equipok in equipos:
        if equipok != local:
            for visita in equipos:
                if (visita != local) and (visita != equipok):
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
        if equipok != local:
            for visita in equipos:
                if (visita != local) and (visita != equipok):
                    for fecha in range(2, (len(fechas) + 1)):
                        modelo.addConstr((partido_ijt[local, visita, (fecha - 1)] + partido_ijt[local, equipok, fecha] - 1) <= (incumple_itn[local, fecha, 2]))

# R14
for local in equipos:
    for visita in equipos:
        if local != visita:
            for arb in arbitros:
                for fecha1 in range(1, (len(fechas)//2 + 1)):
                    for fecha2 in range((len(fechas)//2 + 1), len(fechas) + 1):
                        modelo.addConstr((arbitrar_aijt[arb,local,visita,fecha1] + arbitrar_aijt[arb,visita,local,fecha2] - 1) <= incumple_itn[local,fecha1,3])

# R15
for local in equipos:
    for arb in arbitros:
        for fecha1 in range(2, (len(fechas) + 1)):
            for fecha2 in range(1, fecha1):
                modelo.addConstr((quicksum((partido_ijt[local,j,fecha1] + partido_ijt[j,local,fecha1] + arbitrar_aijt[arb,local,j,fecha1] + arbitrar_aijt[arb,j,local,fecha1]) for j in equipos)
                                  + quicksum((partido_ijt[local,l,fecha2] + partido_ijt[l,local,fecha2] + arbitrar_aijt[arb,local,l,fecha2] + arbitrar_aijt[arb,l,local,fecha2]) for l in equipos)
                                  - incumple_itn[local,fecha1,4]) <= 3)

# R16
for n in cons:
    modelo.addConstr((quicksum(incumple_itn[equipo, fecha, n] for equipo in equipos for fecha in fechas)) == incumple_n[n])

# R17 (N.V)
for n in cons:
    modelo.addConstr(incumple_n[n] >= 0)

#----------------Optimizar------------------------
modelo.optimize()