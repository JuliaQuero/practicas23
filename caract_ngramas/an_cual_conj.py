# Programa para obtener dos matrices, una con los n-gramas distintos 
# y otra con (el nombre de) los n-gramas iguales
# de cada categoría de virus con cada una de las demás

# Julia Quero Pérez - 792310

#Librerías necesarias
import csv
from collections import Counter, defaultdict
from nltk.util import ngrams


#Longitud de los ngramas
#N = 3
N = int(input('Longitud de los ngramas: '))

forma = input('¿Quieres trabajar con API o con Cat?: ')
def entrada(f):
    if f == 'API':
        return 'tratado_API_dataset.csv'
    else:
        return 'tratado_Cat_dataset.csv'
def salida1(f):
    if f == 'API':
        return 'tablas/nom_diff_matrix_API.txt'
    else:
        return 'tablas/nom_diff_matrix_Cat.txt'
def salida2(f):
    if f == 'API':
        return 'tablas/nom_same_matrix_API.txt'
    else:
        return 'tablas/nom_same_matrix_Cat.txt'
       
# Parte del total de las trazas en las que ha de aparecer un ngrama para considerarse relevante
#sesgo_percent = 0.61
sesgo_percent = float(input('Porcentaje a considerar: '))


# Diccionario para contar ocurrencias de cada virus
cat_count = {'Backdoor':0, 'Worm':0, 'Packed':0, 'Trojan':0, 'PUP':0, 'Benigno':0}

with open(entrada(forma),'r',newline='') as file:
    reader = csv.reader(file)

    # Guarda el número de trazas en las que aparece cierto ngrama para cada categoría
    data_traza = defaultdict()
    # Guarda el número ocurrencias totales para cierto ngrama para cada categoría
    data_ocur  = defaultdict()

    for row in reader:

        #Guardo en un counter las APIs del virus row[0]
        lista = list(ngrams(row[2:len(row)],N))
        traza = Counter(lista)

        # Sumo a la cuenta
        cat_count[row[0]] += 1

        # Añado al diccionario
        if row[0] in data_traza:
            for k in traza:
                if k in data_traza[row[0]]:
                    data_traza[row[0]][k]+=1
                    data_ocur[row[0]][k]+=traza[k]
                else:
                    data_traza[row[0]][k]=1
                    data_ocur[row[0]][k] = traza[k]
        else:
            data_traza.update({row[0]:dict()})
            data_ocur.update({row[0]:dict()})
            for k in traza:
                data_traza[row[0]][k] = 1
                data_ocur[row[0]][k] = traza[k]
            
#-------------------------------------------------------------
# Ahora hago el tratamiento: guardo los más comunes
data_res = dict()
for cat in data_traza:
    data_res[cat] = list()
    sesgo = cat_count[cat]*sesgo_percent
    for ngr in data_traza[cat]:
        if data_traza[cat][ngr] > sesgo:
            data_res[cat].append(ngr)
#-------------------------------------------------------------

#-------------------------------------------------------------
# Parte de análisis cuantitativo conjunto
# Algoritmo de fuerza bruta. 
# Nótese que la matriz data_same es simétrica, por lo que existe un algoritmo mejor.


# Ahora guardo los ngramas distintas
# También guardo los ngramas iguales
data_diff = defaultdict()
data_same = defaultdict()
for kRow in data_res:
    data_diff[kRow] = dict()
    data_same[kRow] = dict()
    for kCol in data_res:
        data_diff[kRow][kCol] = list()
        data_same[kRow][kCol] = list()
        for el in data_res[kRow]:
            if el not in data_res[kCol]:
                data_diff[kRow][kCol].append(el)
            else:
                data_same[kRow][kCol].append(el)

#-------------------------------------------------------------


#-------------------------------------------------------------
# Escritura de los resultados.
# Pongo en un txt los nombre{n-gramas distintos}
out = open(salida1(forma),'w',newline='')
for key in data_diff:
    for jey in data_diff:
        if jey != key:
            out.write(key)
            out.write(' se diferencia a ')
            out.write(jey)
            out.write(' en: ')
            out.write('\n')
            for el in data_diff[key][jey]:
                out.write(str(el))
                out.write('\n')
            out.write('\n')
            out.write('\n')
out.close()

# Pongo en un txt los nombre{n-gramas iguales}
out = open(salida2(forma),'w',newline='')
keyList = list(data_same.keys())
for i in range(0,len(keyList)):
    for j in range(i+1,len(keyList)):
        out.write(keyList[i])
        out.write(' coincide con ')
        out.write(keyList[j])
        out.write(' en: ')
        out.write('\n')
        for el in data_same[keyList[i]][keyList[j]]:
            out.write(str(el))
            out.write('\n')
        out.write('\n')
        out.write('\n')
out.close()

#-------------------------------------------------------------
