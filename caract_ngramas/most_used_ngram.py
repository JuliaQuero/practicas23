# Programa para obtener un json con los n-gramas distintos de cada tipo de malware (cortando en un porcentaje de trazas en el que aparezca), el número de trazas en el que aparece y el número total de ocurrencias.

# Julia Quero Pérez - 792310

#Librerías necesarias
import csv
import json
from collections import Counter, defaultdict
from nltk.util import ngrams
from itertools import chain # Para pasar tuplas a string


#Longitud de los ngramas
#N = 3
N = int(input('Longitud de los ngramas: '))

forma = input('¿Quieres trabajar con API o con Cat?: ')
def entrada(f):
    if f == 'API':
        return 'tratado_API_dataset.csv'
    else:
        return 'tratado_Cat_dataset.csv'
def salida(f):
    if f == 'API':
        return 'ngram_lists/ngram_API.txt'
    else:
        return 'ngram_lists/ngram_Cat.txt'
       

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
#-------------------------------------------------------------

        #Guardo en un counter las APIs del virus row[0]
        lista = list(ngrams(row[2:len(row)],N))
        traza = Counter(lista)

#-------------------------------------------------------------

        # Sumo a la cuenta
        cat_count[row[0]] += 1

#-------------------------------------------------------------
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
# Escribo en un txt la info que quiero
out = open(salida(forma),'w')
for key in data_traza:
    out.write(key)
    out.write('\t')
    out.write(str(cat_count[key]))
    out.write('\n')
    for el in data_res[key]:
        ngr = ','.join(map(str,el))
        out.write(ngr)
        out.write('\t')
        out.write(str(data_traza[key][el]))
        out.write('\t')
        out.write(str(data_ocur[key][el]))
        out.write('\n')
    out.write('\n')

out.close()
#-------------------------------------------------------------

