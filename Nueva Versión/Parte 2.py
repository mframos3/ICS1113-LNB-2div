from gurobipy import *
modelo = Model()

# ------------------------------------- CONJUNTOS -------------------------------------------------------
equipos_ca = ["CD Boston College", "CD Liceo Curicó", "CD Alemán de Concepción", "CD Quilicura Basket", "Estadio Palestino", "Estadio Español"]
equipos_cb = ["CD Brisas", "Club Andino de Los Ángeles", "CD Ceppi", "CD Arturo Prat de San Felipe", "Stadio Italiano", "CD Manquehue"]
equipos_s = ["Club Atlético Puerto Varas", "CD AB Temuco", "CD La Unión", "CD Achao"]
equipos = equipos_s + equipos_ca +equipos_cb
arbitros = "a b c d e f g h i j k l m n o p q r".split()
fechas = list(range(1,31))      # Son 30 fechas
N = [3,4] # Se utiliza para las consideraciones 3 y 4 más abajo

# -------------------------- PARÁMETROS ------------------------------------------------------------------
# Se ingresan como parámetros los resultados de la primera ronda (de manera de evitar el Carry - Over invirtiendo el orden de partidos de la primera ronda)

archivo = open("1 ronda.txt")
x = []           # Lista de las variables x_ijt de la primera ronda
z = []           # Lista de las variables z_itn de la primera ronda
for i in archivo:
    if i[0] == "x":
        linea = i.strip("\n").split("_")
        x.append([linea[1],linea[2],int(linea[3].split()[0])])
    else:
        linea = i.strip("\n").split("_")
        z.append([linea[1], linea[2], int(linea[3].split()[0])])
archivo.close()
parejas_que_ya_jugaron =[]
for i in x:
    parejas_que_ya_jugaron.append([i[0],i[1]])

ronda_2 = []
for i in x:
    ronda_2.insert(0,[i[1],i[0],15 + i[2]])
jugados = []
partidos = {}
for i in x:
    partidos[i[0],i[1],i[2]] = 1
    jugados.append([i[0],i[1],i[2]])
for i in ronda_2:
    partidos[i[0],i[1],i[2]] = 1
    jugados.append([i[0],i[1],i[2]])

disponible = {}            # Parámetro que indica si el árbitro a está disponible para arbitrar en la fecha t
for a in arbitros:
    for t in fechas:
        disponible[a,t] = 1

peso_n = {}       # Parámetro que indica los pesos de las consideraciones en la función objetivo
for n in N:    # Por el momento está en 1, es decir todas las consideraciones son igual de importantes
        peso_n[n] = 1
# ----------------------------------- VARIABLES -----------------------------------------------------------
# Se añade la variable que indica si el árbitro arbitra un partido en una determinada fecha
w_aijt = {}
for a in arbitros:
    for i in equipos:
        for j in equipos:
            for t in fechas:
                w_aijt[a,i,j,t] = modelo.addVar(vtype=GRB.BINARY,name= "w_aijt_{}_{}_{}_{}".format(a,i,j,t))

# Se añade la variable que cuenta las veces que se incumplen las consideraciones 3 y 4
z_ain = {}
for a in arbitros:
    for i in equipos:
        for n in N:
            z_ain[a,i,n] = modelo.addVar(vtype=GRB.INTEGER,name="z_ain_{}_{}_{}".format(a,i,n))

modelo.update()
# ------------------------------------------------ FUNCIÓN OBJETIVO -------------------------------------------------------------------

objetivo = quicksum(peso_n[n]*z_ain[a,i,n] for a in arbitros for i in equipos for n in N)
modelo.setObjective(objetivo,GRB.MINIMIZE)

# --------------------------------------- RESTRICCIONES ----------------------------------------------------
# R1 (Un árbitro dirige a lo más 1 partido para cada fecha y solo si está disponible para dicha fecha)

for arb in arbitros:
    for fecha in fechas:
        modelo.addConstr(quicksum(w_aijt[arb,local,visita,fecha] for local in equipos for visita in equipos) <=
        disponible[arb,fecha])

# R2 (Por cada partido debe haber un árbitro y sólo se asigna un árbitro si el partido existe)

for i in equipos:
    for j in equipos:
        for t in fechas:
            if [i,j,t] in jugados:
                modelo.addConstr(quicksum(w_aijt[a,i,j,t] for a in arbitros) == partidos[i,j,t])
            else:
                modelo.addConstr(quicksum(w_aijt[a,i,j,t] for a in arbitros) == 0)

# R3 (Representa el incumplimiento de la consideración 3)

for a in arbitros:
    for i in partidos:
        modelo.addConstr(w_aijt[a,i[0],i[1],i[2]] + w_aijt[a,i[1],i[0],i[2]]-1<=z_ain[a,i[0],3])

# R4 (Representa el incumplimiento de la consideración 4)
for a in arbitros:
    for i in equipos:
        modelo.addConstr(quicksum(w_aijt[a,i,j,t] + w_aijt[a,j,i,t] for j in equipos for t in fechas)-1<=z_ain[a,i,4])

#---------------- Optimizar ------------------------------------------------------------------------
modelo.Params.MIPFocus = 3
modelo.optimize()
modelo.printAttr("X") # Imprimir los valores de las variables básicas en el óptimo