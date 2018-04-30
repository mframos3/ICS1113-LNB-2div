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
consideraciones = list(range(1,5))
# conjunto de arbitros que dirigiran los partidos
arbitros = ["No encontré"]
# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------- PARAMETROS -----------------------------------------------------
puede_arbitrar_el_arbitro_i = {}

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
            juegan_en_el_slot_t_el_equipo_i_de_local_contra_j_visita[local,visita,fecha] = modelo.addVar(vtype=GRB.BINARY, name="x_{}_{}_{}".format(local,visita,fecha))
# Se añade además la variable que lleva el registro de cuantas veces se pasa a llevar una consideracion
consideraciones_n = {}
for i in consideraciones:
    consideraciones_n[i] = modelo.addVar(vtype = GRB.CONTINUOUS,name = "y_{}".format(str(i)))

# Además se crea la variable que indica si para un equipo i se pasó a llevar una consideracion
se_paso_a_llevar_una_consideracion = {}
for consideracion in consideraciones:
    for equipo in equipos:
        se_paso_a_llevar_una_consideracion[equipo,consideracion] = modelo.addVar(vtype = GRB.BINARY, name = "z_{}_{}".format(equipo,consideracion))

modelo.update()
# -----------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------FUNCION OBJETIVO-------------------------------------------------------------------

funcion_objetivo = quicksum(consideraciones_n[n] for n in consideraciones)
modelo.setObjective(funcion_objetivo,GRB.MINIMIZE)