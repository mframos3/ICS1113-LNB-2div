# coding=utf-8
from gurobipy import *
# --------------------------------------- CONJUNTOS---------------------------------------------------
# Conjunto de Equipos y subconjuntos por zona
equipos_ca = ["CD Boston College", "CD Liceo Curicó", "CD Alemán de Concepción", "CD Quilicura Basket", "Estadio Palestino", "Estadio Español"]
equipos_cb = ["CD Brisas", "Club Andino de Los Ángeles", "CD Ceppi", "CD Arturo Prat de San Felipe", "Stadio Italiano", "CD Manquehue"]
equipos_s = ["Club Atlético Puerto Varas", "CD AB Temuco", "CD La Unión", "CD Achao"]
equipos = equipos_s + equipos_ca + equipos_cb
fechas = list(range(1,len(equipos)))  # Son (card(equipos) - 1) fechas en la primera ronda
# Consideraciones
cons = list(range(1, 5))
# Conjunto de Árbitros
arbitros = list("abcdefghijklmnopqrst")  # Se puede variar (deben ser al menos card(equipos)//2)
partidos = []  # Conjunto de partidos de la primera ronda
for i in equipos:
    for j in equipos:
        if i!=j and ([i,j] not in partidos and [j,i] not in partidos):
            partidos.append([i,j])
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARÁMETROS -----------------------------------------------------
arbitrar_at = {}        # Parámetro que indica si el árbitro a está disponible para arbitrar en la fecha t
for arb in arbitros:   # Por el momento está en 1 este parámetro (todos los árbitros pueden arbitrar en todas las fechas)
    for fecha in fechas:
        arbitrar_at[arb,fecha] = 1

peso_n = {}       # Parámetro que indica los pesos de las consideraciones en la función objetivo
for n in cons:# Por el momento está en 1, es decir todas las consideraciones son igual de importantes
        peso_n[n] = 1

juega_i ={}     # Parámetro auxiliar utilizado para las heurísticas
for i in equipos[:len(equipos)//4]:
    for t in fechas:
        juega_i[i,t] = t%2 # 1 de local, 0 de visita
# ----------------------------------------------------------------------------------------------------------------

# -------------------------------------------------- VARIABLES ----------------------------------------------------------

modelo = Model("Segunda División de Básquetbol Competitiva")

# Se definen las variables
partido_ijt = {}  #local, visita, fecha
incumple_itn = {} #equipo, fecha, consideración
# Se añade la variable que indica si el equipo juega o no en una determinada fecha
for fecha in fechas:
    for local in equipos:
        for visita in equipos:
             partido_ijt[local,visita,fecha] = modelo.addVar(vtype = GRB.BINARY, name = "x_{}_{}_{}".format(local,visita,fecha))
# Se añade la variable que indica si se incumplió una consideración
for i in equipos:
    for t in fechas:
        for n in cons:
            if n!=3 and n!=4:
                incumple_itn[i,t,n] = modelo.addVar(vtype = GRB.BINARY,name = "z_{}_{}_{}".format(i,t,n))
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ FUNCIÓN OBJETIVO -------------------------------------------------------------------
# Sólo se usan las consideraciones 1 y 2 para esta parte
objetivo = quicksum(peso_n[n]*incumple_itn[i,t,n] for i in equipos for t in fechas for n in list(range(1,3)))
modelo.setObjective(objetivo,GRB.MINIMIZE)
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ RESTRICCIONES BÁSICAS -------------------------------------------------------------------

# R1 (Cada equipo solo juega 1 partido de liga en cada fecha)

for local in equipos:
        if local != visita:
            for fecha in fechas:
                modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) == 1)

# R2 (Los equipos no pueden jugar contra sí mismos)

modelo.addConstr(quicksum(partido_ijt[local,local,fecha] for local in equipos for fecha in fechas) == 0)

# R3 (Cada equipo i  debe jugar solo 1 vez en la primera ronda contra j)
for par in partidos:
    modelo.addConstr(quicksum(partido_ijt[par[0],par[1],t] + partido_ijt[par[1],par[0],t] for t in fechas) == 1)

# ---------------- HEURÍSTICAS -----------------------------------------------------------------------------------
"""
Las restricciones que se presentan a continuación ayudan a que en la etapa de Branch and Bound el modelo converga más 
rápido al óptimo, la forma en que se obtuvieron estas restricciones fue mediante observación y extrapolación de soluciones
con una menor cantidad de equipos (testeos con 4,6,8,10,12 equipos). Las siguientes restricciones tienen en cuenta que:
- El número mínimo de veces que se puede incumplir la consideración 2 es igual al (número de equipos - 2)
- Solo se puede evitar que para 2 equipos no se incumpla la consideración 2, por lo tanto se escogió al primer equipo y al penúltimo, ya que estos
agilizaban la búsqueda del óptimo entero
- Solo se incumple la consideración 2 en fechas impares, excepto la primera fecha
- Si se incumple la consideración 2 en una fecha, debe ser siempre 2 veces en dicha fecha
- Se utiliza un partido arbitrario inicial para agilizar el modelo
"""
# Se le da un partido inicial al modelo

modelo.addConstr(partido_ijt[equipos[0],equipos[1],1] == 1)

# Se obliga a que el primer equipo y el penúltimo alternen entre local y vista por cada fecha
for t in fechas:
        modelo.addConstr(quicksum(partido_ijt[equipos[0], j, t] for j in equipos) == juega_i[equipos[0], t])
        modelo.addConstr(quicksum(partido_ijt[j, equipos[len(equipos) // 2], t] for j in equipos) >= 1 - juega_i[equipos[0], t])
modelo.addConstr(quicksum(partido_ijt[j, equipos[-2], t] for j in equipos) == juega_i[equipos[0], t])

# ---------------- RESTRICCIONES CONSIDERACIONES -----------------------------------------------------------------------------------

# R4 (Incumplimiento de la consideración 2)

for i in equipos:
    for t in fechas[1:]:
        modelo.addConstr(quicksum(quicksum(partido_ijt[i,j,t-1] for j in equipos) + partido_ijt[i,k,t] for k in equipos) - len(equipos) <= incumple_itn[i,t,2])
        modelo.addConstr(quicksum(quicksum(partido_ijt[j,i,t-1] for j in equipos) + partido_ijt[k,i,t] for k in equipos) - len(equipos)  <= incumple_itn[i,t,2])

# ---------------- HEURÍSTICAS -----------------------------------------------------------------------------------

# Fuerza a incumplir el minimo de veces que se puede incumplir

modelo.addConstr(quicksum(incumple_itn[i,t,2] for t in fechas for i in equipos) == len(equipos) -2)

# Fuerza a no perjudicar al primer equipo de la lista de equipos

modelo.addConstr(quicksum(incumple_itn[equipos[0],t,2] for t in fechas) == 0)

# Fuerza a no perjudicar al penúltimo equipo de la lista de equipos

modelo.addConstr(quicksum(incumple_itn[equipos[-2],t,2] for t in fechas) == 0)

# En la primera fecha es imposible incumplir la consideración 2

modelo.addConstr(quicksum(incumple_itn[i,1,2] for i in equipos) == 0)

# En fechas pares nunca se incumple la consideración, solo se incumple en fechas impares y 2 veces por fecha

modelo.addConstr(quicksum(incumple_itn[i,2,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,3,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,4,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,5,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,6,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,7,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,8,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,9,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,10,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,11,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,12,2] for i in equipos) == 0)
modelo.addConstr(quicksum(incumple_itn[i,13,2] for i in equipos) == 2)
modelo.addConstr(quicksum(incumple_itn[i,14,2] for i in equipos) == 0)
#---------------- Optimizar ---------------------------------------------------------------------------------
modelo.Params.MIPFocus = 3 # Enfocarse en encontrar soluciones enteras más rápido
modelo.optimize()
modelo.printAttr("X") # Imprimir los valores de las variables básicas en el óptimo