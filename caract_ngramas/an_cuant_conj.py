# Programa para obtener dos matrices, una con el número de n-gramas importantes distintos 
# y otra con el número de n-gramas importantes iguales
# de cada categoría de malware con cada una de las demás

# Julia Quero Pérez - 792310

#Librerías necesarias
import csv
from collections import Counter, defaultdict
from nltk.util import ngrams

#------------------------------------------------------------------------------
# OBTENCIÓN DE LOS PARÁMETROS
#------------------------------------------------------------------------------
print('MENÚ DE SELECCIÓN DE PARÁMETROS')
print('-------------------------------\n')

#Longitud de los ngramas
N = int(input('Longitud de los ngramas: '))
print('-------------------------------\n')

# Traza con la que vas a trabajar
print('Seleccione la traza con la que va a realizar el dataset')
print('Para traza de coreanos, pulse 0\n Para traza de Alain pulse 1')
trazaAl = bool('1'==input('Su selección: '))
print('-------------------------------\n')

print('Seleccione la traza con la que va a realizar el dataset')
print('Para API, pulse 0\n Para Categorías pulse 1')
conCat = bool('1'==input('Su selección: '))
print('-------------------------------\n')

print('Seleccione la forma de elegir los ngramas importantes')
print('min sup - pulse 1')
print('min sup + contrast - pulse 2')
print('relevant n-gram - pulse 3')
importancia = int(input('Su selección: '))
print('-------------------------------\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# PARÁMETROS COMUNES
#------------------------------------------------------------------------------
def entrada():
    if trazaAl:
        if conCat:
            return '../resumen_Cat_dataset.csv'
        else:
            return '../resumen_API_dataset.csv'
    else:
        if conCat:
            return '../tratado_Cat_dataset.csv'
        else:
            return '../tratado_API_dataset.csv'
def salida1():
    if not conCat:
        return 'tablas/diff_matrix_API.csv'
    else:
        return 'tablas/diff_matrix_Cat.csv'
def salida2():
    if not conCat:
        return 'tablas/same_matrix_API.csv'
    else:
        return 'tablas/same_matrix_Cat.csv'
    
# Diccionario para contar ocurrencias de cada virus
cat_count = dict()
# Diccionario para contar y mandar al directorio de train o de val
count = dict()

# Diccionarios según la naturaleza de la traza  
dict_Al = {'Virus':0, 'Worm':0, 'Ransomware':0, 'Trojan':0}
dict_cor = {'Backdoor':0, 'Worm':0, 'Packed':0, 'Trojan':0, 'PUP':0, 'Benigno':0}
if trazaAl:
    cat_count.update(dict_Al)
    count.update(dict_Al)
else:
    cat_count.update(dict_cor)
    count.update(dict_cor)

#------------------------------------------------------------------------------
    
#------------------------------------------------------------------------------
# HALLAR MEDIA Y ESTADÍSTICAS DE N-GRAMAS   
#------------------------------------------------------------------------------

# Calculo la media 
total = 0
# Guarda el número de trazas en las que aparece cierto ngrama para cada categoría
data_traza = defaultdict()
# Guarda el número ocurrencias totales para cierto ngrama para cada categoría
data_ocur  = defaultdict()

# Abro el archivo correspondiente
with open(entrada(),'r',newline='') as source:
    reader = csv.reader(source)

    for el in reader:
        lista = list(ngrams(el[2:len(el)],N))
        traza = Counter(lista)

        # Para la media
        total += len(traza)

        # Para las estadísticas de n-gramas
        cat = el[0]
        # ------------Sumo a la cuenta
        cat_count[cat] += 1

        # ------------Añado al diccionario
        if cat in data_traza:
            for k in traza:
                if k in data_traza[cat]:
                    data_traza[cat][k]+=1
                    data_ocur[cat][k]+=traza[k]
                else:
                    data_traza[cat][k]=1
                    data_ocur[cat][k] = traza[k]
        else:
            data_traza.update({cat:dict()})
            data_ocur.update({cat:dict()})
            for k in traza:
                data_traza[cat][k] = 1
                data_ocur[cat][k] = traza[k]
    # Termino de obtener la media
    numTrazas = reader.line_num
    media = total/numTrazas
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# TRATAMIENTO: ¿CUÁLES SON LOS IMPORTANTES?  
#------------------------------------------------------------------------------

# Aquí guardaremos los más importantes por categoría
data_res = dict()

if importancia <=2 :
    sesgo_percent = float(input('Porcentaje para min sup: '))
    if importancia == 1:
        for cat in data_traza:
            data_res[cat] = list()
            sesgo = cat_count[cat]*sesgo_percent
            for ngr in data_traza[cat]:
                if data_traza[cat][ngr] > sesgo:
                    data_res[cat].append(ngr)
    elif importancia == 2: # min sup + contrast
        # Factor de error para evitar 0's
        epsilon = 0.0000001
        # Lista con todos los ngramas
        lngram = list()
        for cat in data_traza:
            # Minimum support
            iterable = [i for i in data_traza[cat]]
            for ngr in iterable:
                ocur = 0
                for cat in data_traza:
                    try:
                        ocur += data_traza[cat][ngr]                       
                    except Exception:
                        ocur += epsilon
                if ocur > sesgo_percent*numTrazas and ngr not in lngram:
                    lngram.append(ngr)
        # Contrast
        lmax = list()
        for ngr in lngram:
            # Creamos la cuenta normalizada
            norm_count = dict()
            # Para almacenar el máximo para el cálculo del contraste
            norm_max = 0.0
            norm_sum = 0.0
            for cat in data_traza:
                try:
                    valor = float(data_ocur[cat][ngr]/cat_count[cat])
                    if valor > norm_max:
                        norm_max = valor
                except Exception:
                    valor = epsilon
                norm_count.update([(cat,valor)])
                norm_sum += norm_count[cat]
            # Calculamos el contraste
            contraste = norm_max/norm_sum
            lmax.append((ngr,contraste))
        #Ordeno de mayor a menor según contraste
        lmax.sort(key=lambda a: a[1], reverse=True) 

        # Número de elementos a guardar
        L = int(media/2)                                                        
        lresultado = list()
        while len(lresultado)<L and len(lmax)>0:
            for el in lmax[0]:
                lresultado.append(el)
                break
            lmax.pop(0)

        # Replicamos el resultado para toda categoría
        for cat in data_traza:
            data_res[cat] = lresultado
elif importancia == 3:
    # Número de ngramas más frecuentes a seleccionar
    L = int(media/9)
    most_common = dict()
    for cat in data_traza:
        aux = Counter(data_traza[cat])
        laux = aux.most_common(L)
        data_res.update([(cat,laux)])
    # Quitamos los comunes
    for cat in data_res:
        for el in data_res[cat]:
            # Busco si está en otro
            for key in data_res:
                # Si lo he encontrado
                if key!=cat and el in data_res[key]:
                    # Lo elimino de todos
                    for j in data_res:
                        if el in data_res[j]:
                            data_res[j].remove(el)
                    break
#------------------------------------------------------------------------------

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

# Transformo ambos diccionarios bidimensionales en diccionarios unidimensionales
# con el número de ocurrencias de ngramas.
list_diff = dict()
list_same = dict()
for kRow in data_diff:
    list_diff[kRow] = list()
    list_diff[kRow].append(kRow)
    list_same[kRow] = list()
    list_same[kRow].append(kRow)
    for kCol in data_diff:
        list_diff[kRow].append(len(data_diff[kRow][kCol]))
        list_same[kRow].append(len(data_same[kRow][kCol]))
#-------------------------------------------------------------


#-------------------------------------------------------------
# Escritura de los resultados.
# Pongo en un csv la matriz de #{n-gramas distintos}
out = open(salida1(),'w',newline='')
writer = csv.writer(out)
# Escribimos el nombre de las columnas, dejando una celda vacía
leyenda = ['']+list(data_res.keys())
writer.writerow(leyenda)

for key in data_diff:
    writer.writerow(list_diff[key])
out.close()


# Pongo en un csv la matriz de #{n-gramas iguales}
out = open(salida2(),'w',newline='')
writer = csv.writer(out)
# Escribimos el nombre de las columnas, dejando una celda vacía
writer.writerow(leyenda)
# Para escribir la matriz
for key in data_same:
    writer.writerow(list_same[key])
out.close()
#-------------------------------------------------------------