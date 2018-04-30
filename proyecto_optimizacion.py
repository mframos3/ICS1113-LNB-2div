# coding=utf-8
from gurobipy import *

# ---------------------------------------  CONJUNTOS ---------------------------------------------------

slots_de_partidos = list(range(1, 33))  # Son 32 fechas
# equipos que compiten en la liga
equipos_1 = ["CD Boston College", "Liceo Curico", "C.D. Aleman", "CDSC Quilcura", "Estadio Español"]
equipos_2 = ["CD Brisas", "C.D Sergio Prepi", "CD Arturo Prat", "Stadio Italiano", "CD Manquehue"]
equipos_3 = ["CD Atletico Puerto Varas", "AB Temuco", "La Union", "Deportes Achao", "CD Palestino", "CD Andino"]
# Se dividieron en 3 para que sea más fácil visualizarlos todos, pero en relidad es un solo conjunto
equipos = equipos_1 + equipos_2 + equipos_3
# Consideraciones
consideraciones = list(range(1, 5))
# conjunto de arbitros que dirigiran los partidos
arbitros = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "m", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARAMETROS -----------------------------------------------------
puede_arbitrar_el_arbitro_i = {}
for arb in arbitros:   # Al principio intentemos dejandolo todo en 1, despúes variemos estos numeros
    for fecha in slots_de_partidos:
        puede_arbitrar_el_arbitro_i[arb,fecha] = 1

# ----------------------------------------------------------------------------------------------------------------

# --------------------------------------------------MODELO----------------------------------------------------------

modelo = Model("Segunda Divsion de Basquetbol Competitiva")

# Se definen las variables
juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita = {}
se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t = {}
# Se añaden las variables que indican si el equipo juega o no en una determinada fecha
for fecha in slots_de_partidos:
    for local in equipos:
        for visita in equipos:
            juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] = modelo.addVar(vtype = GRB.BINARY, name = "x_{}_{}_{}".format(local,visita,fecha))
# Se añade además la variable que lleva el registro de cuantas veces se pasa a llevar una consideracion
consideraciones_n = {}
for i in consideraciones:
    consideraciones_n[i] = modelo.addVar(vtype = GRB.CONTINUOUS,name = "y_{}".format(str(i)))

# Además se crea la variable que indica si para un equipo i se pasó a llevar una consideracion
se_paso_a_llevar_una_consideracion = {} # HAY QUE BORRARLO? ***
for consideracion in consideraciones:
    for equipo in equipos:
        for fecha in slots_de_partidos:
            se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[equipo, fecha, consideracion] = modelo.addVar(vtype = GRB.BINARY, name = "z_{}_{}_{}".format(equipo,fecha,consideracion))
# Se crean las variables que determinan que arbitro arbitra cada partido
arbitra_un_partido = {}
for arb in arbitros:
    for i in equipos:
        for j in equipos:
            for fecha in slots_de_partidos:
                if i!= j:
                    arbitra_un_partido[arb,i,j,fecha] =modelo.addVar(vtype=GRB.BINARY,name = "w_{}_{}_{}_()".format(arb,i,j,fecha))
modelo.update()
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------FUNCION OBJETIVO-------------------------------------------------------------------

funcion_objetivo = quicksum(consideraciones_n[n] for n in consideraciones)
modelo.setObjective(funcion_objetivo,GRB.MINIMIZE)

# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES basicas-------------------------------------------------------------------


# R1
for local in equipos:
    for visita in equipos:
        modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] for fecha in slots_de_partidos ) == 1)

# R2

for local in equipos:
    modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] for visita in equipos for fecha in slots_de_partidos) == len(equipos) - 1)

# R3

for local in equipos:
    for fecha in slots_de_partidos:
        modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[visita,local,fecha] for visita in equipos) == 1)

# R4

for fecha in slots_de_partidos:
    modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] for local in equipos for visita in equipos) == len(equipos)/2)

# R5
for local in equipos:
    for fecha in slots_de_partidos:
        modelo.addConstr(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,local,fecha] == 0)

# R6

for local in equipos:
    modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[visita,local,fecha] for visita in equipos for fecha in list(range(1, 17))) == len(equipos) - 1)

#R7

for local in equipos:
    for visita in equipos:
        modelo.addConstr(quicksum(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, visita, fecha] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[visita, local, fecha] for fecha in list(range(1, 17))) == 1 )



# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES arbitraje-------------------------------------------------------------------

# R8

for arb in arbitros:
    for i in equipos:
        for j in equipos:
            if i != j:
                modelo.addConstr(quicksum(arbitra_un_partido[arb,i,j,fecha] for fecha in slots_de_partidos) <= 1)
# R9

for arb in arbitros:
    for j in equipos:
        for i in equipos:
            if i!=j:
                  for fecha in slots_de_partidos:
                         modelo.addConstr(arbitra_un_partido[arb,i,j,fecha]+arbitra_un_partido[arb,j,i,fecha]+juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[i,j,fecha] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[j,i,fecha] == 2)

# R10

for arb in arbitros:
    for i in equipos:
        for j in equipos:
            if i != j:
                modelo.addConstr(quicksum(arbitra_un_partido[arb,i,j,fecha] - juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[i,j,fecha] for fecha in slots_de_partidos) <=0)
# R11

for arb in arbitros:
    for i in equipos:
        for j in equipos:
            if i != j:
                modelo.addConstr(quicksum(arbitra_un_partido[arb,i,j,fecha]-puede_arbitrar_el_arbitro_i[arb,fecha] for fecha in slots_de_partidos) <=0)
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------RESTRICCIONES consideraciones-------------------------------------------------------------------

# R12

for local in equipos:
    for equipok in equipos:
        for visita in equipos:
            for fecha1 in list(range(2, 17)):
                for fecha2 in list(range(18, 33)):
                    modelo.addConstr(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, visita, fecha1] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[visita, local, fecha1]
                                 + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, equipok, fecha1 - 1] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[equipok, local, fecha1 - 1]
                                 + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, visita, fecha2] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[visita, local, fecha2]
                                 + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, equipok, fecha2 - 1] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[equipok, local, fecha2 - 1]
                                 - se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[local, fecha1, 1] <= 3)

# R13

for local in equipos:
    for equipok in equipos:
        for visita in equipos:
            for fecha in list(range(2, 33)):
                modelo.addConstr(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, visita, fecha - 1] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local, equipok, fecha] - 1
                                 <= se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[local, fecha, 2])



# FALTAN RESTRICCIONES DE ARBITRAJE  R15

# R14

for arb in arbitros:
    for i in equipos:
        for j in equipos:
            if i != j:
                for p_vuelta in slots_de_partidos[:len(slots_de_partidos)//2]:
                    for s_vuelta in slots_de_partidos[len(slots_de_partidos)//2:]:
                        modelo.addConstr(arbitra_un_partido[arb,i,j,p_vuelta]  + arbitra_un_partido[arb,i,j,s_vuelta] - 1 - se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[i,p_vuelta,3] <= 0)
# R15

for arb in arbitros:
    for i in equipos:
        for j in equipos:
            if i!=j:
                for l in equipos:
                    if l!=i and l!=j:
                        for t in slots_de_partidos[2:]:
                            for h in range(1,t):
                                modelo.addConstr(juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[i,j,t] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[j,i,t] + arbitra_un_partido[arb,i,j,t] + arbitra_un_partido[arb,j,i,t] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[i,l,h] + juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[l,i,h] + arbitra_un_partido[arb,i,l,h] + arbitra_un_partido[arb,l,i,h] - se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[i,t] <= 3)


# R16

for n in [1,2,3,4]:
    modelo.addConstr(quicksum(se_incumple_la_consideracion_n_para_el_equipo_i_en_el_slot_t[equipo, fecha, n] for equipo in equipos for fecha in slots_de_partidos) == consideraciones_n[n])


modelo.setObjective(funcion_objetivo,GRB.MINIMIZE)
modelo.optimize()

