# coding=utf-8
from gurobipy import *
# ---------------------------------------  CONJUNTOS ---------------------------------------------------
# Conjunto de Equipos y subconjuntos por zona
equipos_ca = ["CD Boston College", "CD Liceo Curicó", "CD Alemán de Concepción", "CD Quilicura Basket", "Estadio Palestino", "Estadio Español"]
equipos_cb = ["CD Brisas", "Club Andino de Los Ángeles", "CD Ceppi", "CD Arturo Prat de San Felipe", "Stadio Italiano", "CD Manquehue"]
equipos_s = ["Club Atlético Puerto Varas", "CD AB Temuco", "CD La Unión", "CD Achao"]
#equipos =  ["e1","e2","e3","e4"]# Se resolvieron los partidos para la zona sur, ya que para un número mayor el resolver el modelo se volvía inviable (tardaba mucho)
equipos = equipos_s + equipos_ca +equipos_cb
fechas = list(range(1,((len(equipos)*2) - 1)//2 +1))  # Son 2*(card(equipos) - 1) fechas
# Consideraciones
cons = list(range(1, 5))
# Conjunto de Árbitros
arbitros = list("abcdefghijklmnopqrst")  # Se puede variar (deben ser al menos card(equipos)//2, en esta instancia son 8)
partidos = []
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
peso_n[1] = 1

# ----------------------------------------------------------------------------------------------------------------

# --------------------------------------------------MODELO----------------------------------------------------------

modelo = Model("Segunda División de Básquetbol Competitiva")

# Se definen las variables
partido_ijt = {}  #local, visita, fecha
incumple_itn = {} #equipo, fecha, consideración
incumple_n = {} #consideración
arbitrar_aijt = {} #árbitro, local, visita, fecha
# Se añade la variable que indica si el equipo juega o no en una determinada fecha
for fecha in fechas:
    for local in equipos:
        for visita in equipos:
            partido_ijt[local,visita,fecha] = modelo.addVar(vtype = GRB.BINARY, name = "x_{}_{}_{}".format(local,visita,fecha))
# Se añade la variable que determina qué árbitro arbitra cada partido
#for arb in arbitros:
#    for i in equipos:
#        for j in equipos:
#            for fecha in fechas:
#                arbitrar_aijt[arb,i,j,fecha] = modelo.addVar(vtype = GRB.BINARY,name = "w_{}_{}_{}_{}".format(arb,i,j,fecha))
# Se añade la variable que indica si se incumplió una consideración
for i in equipos:
    for t in fechas:
        for n in cons:
            if n!=3 and n!=4:
                incumple_itn[i,t,n] = modelo.addVar(vtype = GRB.INTEGER,name = "z_{}_{}_{}".format(i,t,n))

#for a in arbitros:
#    for i in equipos:
#        incumple_itn[a,i,4] = modelo.addVar(vtype=GRB.INTEGER,name = "z_{}_{}_{}".format(a,i,4))
#        incumple_itn[a,i,3] = modelo.addVar(vtype = GRB.INTEGER,name = "z_{}_{}_{}".format(a,i,3))


# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------FUNCIÓN OBJETIVO-------------------------------------------------------------------

objetivo = quicksum(peso_n[n]*incumple_itn[i,t,n] for i in equipos for t in fechas for n in list(range(1,3))) # + quicksum(peso_n[n]*incumple_itn[a,i,n] for a in arbitros for i in equipos for n in list(range(3,5)))
modelo.setObjective(objetivo,GRB.MINIMIZE)
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES BÁSICAS-------------------------------------------------------------------

#
"""
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for fecha in fechas) == 1)

# R2
for local in equipos:
    modelo.addConstr(quicksum(partido_ijt[local,visita,fecha] for visita in equipos for fecha in fechas) == (len(equipos) - 1))
"""
# R3
for local in equipos:
    for fecha in fechas:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local,visita,fecha] + partido_ijt[visita,local,fecha]) for visita in equipos) == 1)

# R5
for local in equipos:
    for fecha in fechas:
        modelo.addConstr(partido_ijt[local,local,fecha] == 0)

# R7
"""
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local, visita, fecha] + partido_ijt[visita, local, fecha]) for fecha in range(1,(len(fechas)//2) + 1)) == 1)
"""
for local in equipos:
    for visita in equipos:
        if local != visita:
            modelo.addConstr(quicksum((partido_ijt[local, visita, fecha] + partido_ijt[visita, local, fecha]) for fecha in fechas) == 1)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES ARBITRAJE-------------------------------------------------------------------

# R8
"""
for arb in arbitros:
    for fecha in fechas:
        modelo.addConstr(quicksum(arbitrar_aijt[arb,local,visita,fecha] for local in equipos for visita in equipos) <=
        arbitrar_at[arb,fecha])

# R9
for local in equipos:
    for visita in equipos:
        if local != visita:
            for fecha in fechas:
                modelo.addConstr(quicksum(arbitrar_aijt[arb,local,visita,fecha] for arb in arbitros) == partido_ijt[local,visita,fecha])
"""
# R10 (carry - over)

"""
for i in equipos:
    for j in equipos:
        if j!=i:
            for k in equipos:
                if k!=i and k!=j:
                    for t in fechas[1:(len(fechas)//2)]:
                        for h in fechas[(len(fechas)//2)+1:]:
                            modelo.addConstr(partido_ijt[i,j,t] + partido_ijt[j,i,t] + partido_ijt[i,k,t-1] +
                            partido_ijt[k,i,t-1] + partido_ijt[i,j,h] + partido_ijt[j,i,h] + partido_ijt[i,k,h-1] +
                            partido_ijt[k,i,h-1] - incumple_itn[i,t,1] <= 3)


"""
# R11

for i in equipos:
            for t in fechas[1:]:
                modelo.addConstr(quicksum(quicksum(partido_ijt[i,j,t-1] for j in equipos) + partido_ijt[i,k,t] for k in equipos) - len(equipos) <= incumple_itn[i,t,2])
                modelo.addConstr(quicksum(quicksum(partido_ijt[j,i,t-1] for j in equipos) + partido_ijt[k,i,t] for k in equipos) - len(equipos)  <= incumple_itn[i,t,2])

"""
# R12
for a in arbitros:
    for i in partidos:
        modelo.addConstr(quicksum(arbitrar_aijt[a,i[0],i[1],t] + arbitrar_aijt[a,i[1],i[0],t] for t in fechas)-1<=incumple_itn[a,i[0],3])


# R13
for a in arbitros:
    for i in equipos:
        modelo.addConstr(quicksum(arbitrar_aijt[a,i,j,t] + arbitrar_aijt[a,j,i,t] for j in equipos for t in fechas)-1<=incumple_itn[a,i,4])

"""



#----------------Optimizar------------------------

#modelo.Params.method = 2 # 2 = Barrier, -1 = Auto (método de resolución)
modelo.Params.MIPFocus = 3
modelo.optimize()
modelo.printAttr("X") # Imprimir los valores de las variables básicas en el óptimo
modelo.getVars()