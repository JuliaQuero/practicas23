# Programa para obtener imágenes a partir de las trazas de malware 

# Julia Quero Pérez - 792310

#Librerías necesarias
import csv
import json
from collections import Counter, defaultdict
from nltk.util import ngrams
from math import floor  # Para pasar de decimal a RGB
import numpy as np
from glob import glob
import random as r      # Para la aleatoriedad
# Para las imágenes
from PIL import Image

#------------------------------------------------------------------------------
# OBTENCIÓN DE LOS PARÁMETROS
#------------------------------------------------------------------------------
print('MENÚ DE SELECCIÓN DE PARÁMETROS')
print('-------------------------------\n')

# Traza con la que vas a trabajar
print('Seleccione la traza con la que va a realizar el dataset')
print('Para traza de Kim, pulse 0\nPara traza de Alain pulse 1')
tRazvan = bool('1'==input('Su selección: '))
print('-------------------------------\n')

print('Seleccione la forma de elegir los colores')
print('equid - pulse 1')
print('equiran - pulse 2')
print('rand - pulse 3')
colores = int(input('Su selección: '))
print('-------------------------------\n')

#Longitud de los ngramas
N = int(input('Longitud de los ngramas: '))
print('-------------------------------\n')

# Pixeles de la imagen
#px = int(input('Lado en píxeles de la imagen: '))
px = 224
#print('-------------------------------\n')

#print('Seleccione la traza con la que va a realizar el dataset')
#print('Para API, pulse 0\n Para Categorías pulse 1')
#conCat = bool('1'==input('Su selección: '))
conCat = 1
#print('-------------------------------\n')

print('Seleccione la forma de elegir los ngramas importantes')
print('min_sup - pulse 1')
print('contrast - pulse 2')
print('afinidad - pulse 3')
print('relevant - pulse 4')
importancia = int(input('Su selección: '))
print('-------------------------------\n')

print('Seleccione el formato de la imagen')
print('cat_id - pulse 1')
print('cat_aa - pulse 2')
print('trans_id - pulse 3')
print('trans_aa - pulse 4')
print('diag_sup - pulse 5')
print('diag_inf - pulse 6')
print('mix - pulse 7')
formato = int(input('Su selección: '))
print('-------------------------------\n')

#print('¿Te gustaría que generase solo una imagen para probar?')
#print('Sí (1) / No (0)')
#paro = bool('1'==input('Su selección: '))
#paro = 1
#print('-------------------------------\n')
#------------------------------------------------------------------------------

print('La traza es ',tRazvan,'los colores ',str(colores),'la n ', str(N),
        ' la importancia ', str(importancia), ' y el formato ',str(formato))

#------------------------------------------------------------------------------
# PARÁMETROS COMUNES
#------------------------------------------------------------------------------
def entrada():
    if tRazvan:
        if conCat:
            return 'resumen_Cat_dataset.csv'
        else:
            return 'resumen_API_dataset.csv'
    else:
        if conCat:
            return 'tratado_Cat_dataset.csv'
        else:
            return 'tratado_API_dataset.csv'
# Para el nombre de las imágenes
def salida(n,tope):
    if n <= int(tope*sesgo_data):
        if tRazvan:
            return 'VA/train/'
        else:
            return 'VK/train/'
    else:
        if tRazvan:
            return 'VA/val/'
        else:
            return 'VK/val/'
        
# Porcentaje para el entrenamiento
sesgo_data = 0.8    

# Diccionario para contar ocurrencias de cada virus
cat_count = dict()
# Diccionario para contar y mandar al directorio de train o de val
count = dict()

# Diccionarios según la naturaleza de la traza  
dict_Al = {'Virus':0, 'Worm':0, 'Ransomware':0, 'Trojan':0}
dict_cor = {'Backdoor':0, 'Worm':0, 'Packed':0, 'Trojan':0, 'PUP':0, 'Benigno':0}
if tRazvan:
    cat_count.update(dict_Al)
    count.update(dict_Al)
else:
    cat_count.update(dict_cor)
    count.update(dict_cor)

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# OBTENCIÓN DE LOS COLORES
#------------------------------------------------------------------------------

# Diccionario con los colores por categoría en RGB
cat_color = dict()
def dec_to_tuple(n):
    r = floor(n/(256*256))
    g = floor((n/256)%256)
    b = n % 256
    return (r,g,b)

# Tratamiento y obtención    
with open('categories.txt','r') as f:
    lines = f.readlines()
    trocito = int(16777215/len(lines)) # Partimos el blanco, el hexa
    ley = list()

    # Según lo pulsado los generamos de una forma u otra ----------------------
    if colores < 3:
        ley = [item for item in range(0,len(lines))]
    if colores == 2:
        r.shuffle(ley)
    else: # colores == 3
        while len(ley)<len(lines):
            value = int(16777215*r.random())
            if value not in ley:
                ley.append(value)
    # -------------------------------------------------------------------------

    i=0
    for l in lines:
        # Tengo que quitar el salto de línea del final
        aux = [char for char in l]
        key = ''.join(aux[0:len(aux)-1])
        # Guardo en el diccionario el color que le corresponde
        cat_color.update([(key,dec_to_tuple(trocito*ley[i]))])
        i+=1
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# HALLAR L Y ESTADÍSTICAS DE N-GRAMAS   
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

# Calculo el lado de la imagen
def divisores(n):
    l = list()
    # Empiezo desde el 1 para proteger a los primos
    for i in range(1,int(n/2),1):
        if n%i==0:
            l.append(i)
    l.append(n)
    return l

def error(l):
    if formato <3 or formato == 7:
        return np.abs(px*px/(N*l*l)-media)
    else:
        return np.abs(px*px/(l*l)-media)
    
div = divisores(px)
i = 0
while error(div[i+1]) <= error(div[i]):
   i+=1 
   if i>len(div):
       break
l = div[i]
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# TRATAMIENTO: ¿CUÁLES SON LOS IMPORTANTES?  
#------------------------------------------------------------------------------

# Aquí guardaremos los más importantes por categoría
data_res = dict()

if importancia <4 :
    sesgo_percent = 0.6
    #sesgo_percent = float(input('Porcentaje para min sup: '))
    if importancia == 1:
        for cat in data_traza:
            data_res[cat] = list()
            sesgo = cat_count[cat]*sesgo_percent
            for ngr in data_traza[cat]:
                if data_traza[cat][ngr] > sesgo:
                    data_res[cat].append(ngr)
    else: # min sup + contrast
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
            cat_max=''
            norm_sum = 0.0
            for cat in data_traza:
                try:
                    valor = float(data_ocur[cat][ngr]/cat_count[cat])
                    if valor > norm_max:
                        norm_max = valor
                        cat_max = cat
                except Exception:
                    valor = epsilon
                norm_count.update([(cat,valor)])
                norm_sum += norm_count[cat]
            # Calculamos el contraste
            contraste = norm_max/norm_sum
            lmax.append((ngr,contraste,cat_max))
        #Ordeno de mayor a menor según contraste
        lmax.sort(key=lambda a: a[1], reverse=True) 

        if importancia == 2:   
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
        else:
            L = int(media/len(cat_count))
            for cat in data_traza:
                lresultado = list()
                laux = list() # Pongo los que sean de esa categoría
                for el in lmax:
                    if el[2] == cat:
                        laux.append(el[0])
                while len(lresultado)<L and len(laux)>0:
                    lresultado.append(laux[0])
                    laux.pop(0)
                data_res[cat] = lresultado


else: #importancia == 4:
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

#------------------------------------------------------------------------------
# CREAR IMÁGENES    
#------------------------------------------------------------------------------
# Función para calcular la próxima posición en la que colocar el color
# i es el nº de imágenes que se han colocado, wxh la dimensión de la imagen
def pos_num(i,w,h):
    x = int(l*i)%w
    y = int(l*i/h)*l
    if formato % 2 == 1:
        return (x,y)
    else:
        return (y,x)
    
def pos_anterior(x,y,w,h):
    banda = 1
    if formato == 6:    # diag_inf
        if y<=0:
            if x<=0:#Al final de la parte 2
                return (banda*l,h-banda*l)
            else:   # Al final de una "fila" de 2 o al final de 1
                return (0,x-banda*l)
        elif x>=(w-banda*l):
            if y>=(h-banda*l):# Al final del todo
                return (w,h)
            else:# Al final de una "fila" de la parte 3
                return (y+banda*l,h-banda*l)
        else:# Caso general
            return (x+banda*l,y-banda*l)
    else:
        if x==y:           # diag_sup
            if x < w:
                return (x+l,y+l) # Caso diagonal (1)
            else:
                return (0,banda*l) # Termina la diagonal -> 2
        elif x<y:   # Bajo la diagonal
            if y>=h:
                if x==0:
                    return (banda*l,0) # 2 -> 3
                else:
                    return (0, h-x+banda*l) #Al finalizar "línea" zona 2
            else:
                return (x+l,y+l) # Caso base zona 2
        else:# x>y, zona 3: encima de la diagonal
            if x>=w:
                if y==0:    # El último de todos
                    return (x,y) #Sobreescribo
                else:
                    return (w-y+banda*l,0) # Finalizar "fila" zona 3
            else:
                return (x+l,y+l) # Caso base zona 3
# Nota: para finalizar "filas" he usado la métrica de antes 
# para no sobreescribir y no dejar huecos 
            

# Función para generar la imagen a partir de las listas
def generate_img(imp_list, rest_list, nombre,w,h):
    if formato <=2: # cat
        i=0
        img = Image.new('RGB',(w,h),color='white')
        while len(imp_list)>0:#Si la lista de importantes no está vacía
            cats = imp_list[0][0]   #el primer índice es el el de la lista y el segundo el ngr, no su ocurrencia
            for c in cats:
                aux_img = Image.new('RGB',(l,l),cat_color[c])
                img.paste(aux_img,pos_num(i,w,h))
                i+=1
            imp_list.pop(0)
        while len(rest_list)>0: # Si la lista del resto no está vacía
            cats = rest_list[0][0]
            for c in cats:
                aux_img = Image.new('RGB',(l,l),cat_color[c])
                img.paste(aux_img,pos_num(i,w,h))
                i+=1
            rest_list.pop(0)
        img.save(nombre)
    elif formato<= 4:   #trans
        i=0
        img = Image.new('RGB',(w,h),color='white')
        while len(imp_list)>0:#Si la lista de importantes no está vacía
            cats = imp_list[0][0]
            lim = list()
            for c in cats:
                aux_img = Image.new('RGBA',(l,l),cat_color[c])
                lim.append(aux_img)
            imp_list.pop(0)
            fin_img = Image.blend(lim[0],lim[1],alpha=0.5)
            fin_img = Image.blend(fin_img,lim[2],alpha=0.33)
            img.paste(fin_img,pos_num(i,w,h))
            i+=1
        while len(rest_list)>0: # Si la lista del resto no está vacía
            cats = rest_list[0][0]
            lim = list()
            for c in cats:
                aux_img = Image.new('RGBA',(l,l),cat_color[c])
                lim.append(aux_img)
            rest_list.pop(0)
            fin_img = Image.blend(lim[0],lim[1],alpha=0.5)
            fin_img = Image.blend(fin_img,lim[2],alpha=0.33)
            img.paste(fin_img,pos_num(i,w,h))
            i+=1
        img.save(nombre)
    elif formato == 7:  # mix
        i=0
        img = Image.new('RGB',(w,h),color='white')
        while len(imp_list)>0:#Si la lista de importantes no está vacía
            cats = imp_list[0][0]
            lim = list()
            for c in cats:
                aux_img = Image.new('RGBA',(l,l),cat_color[c])
                lim.append(aux_img)
            imp_list.pop(0)
            fin_img = Image.blend(lim[0],lim[1],alpha=0.5)
            fin_img = Image.blend(fin_img,lim[2],alpha=0.33)
            img.paste(fin_img,pos_num(i,w,h))
            i+=1
        while len(rest_list)>0: # Si la lista del resto no está vacía
            cats = rest_list[0][0]
            for c in cats:
                aux_img = Image.new('RGB',(l,l),cat_color[c])
                img.paste(aux_img,pos_num(i,w,h))
                i+=1
            rest_list.pop(0)
        img.save(nombre)
    else:   #casos diagonales, 5 o 6
        xi=0
        yi=0
        if formato == 6:
            yi = h-l
        img = Image.new('RGB',(w,h),color='white')
        while len(imp_list)>0:#Si la lista de importantes no está vacía
            cats = imp_list[0][0]
            for c in cats:
                aux_img = Image.new('RGB',(l,l),cat_color[c])
                img.paste(aux_img,(xi,yi))
                (xi,yi)=pos_anterior(xi,yi,w,h)
            imp_list.pop(0)
        while len(rest_list)>0: # Si la lista del resto no está vacía
            cats = rest_list[0][0]
            for c in cats:
                aux_img = Image.new('RGB',(l,l),cat_color[c])
                img.paste(aux_img,(xi,yi))
                (xi,yi)=pos_anterior(xi,yi,w,h)
            rest_list.pop(0)
        img.save(nombre)


# Abro el archivo correspondiente
source = open(entrada(),'r',newline='')
reader = csv.reader(source)

for elem in reader:
    lista = list(ngrams(elem[2:len(elem)],N))
    traza = Counter(lista)
    cat = elem[0]
    # ------------Sumo a la cuenta
    count[cat] += 1

    height = px
    width = px
    img_name = 'img_dataset/' + salida(count[cat],cat_count[cat]) + cat + '/' + elem[1] + '.png'

    if importancia != 3:
        # Obtener listas con imp y no importantes
        imp = Counter()
        rest = Counter()
        for el in traza:
            if el in data_res[cat]:
                imp[el] = traza[el]
            else:
                rest[el] = traza[el]
        # He dejado en imp los ngramas importantes y en traza el resto
        imp_list = imp.most_common()   # Lista con los ngramas más importantes
        rest_list = rest.most_common()# Lista con el resto de ngramas

        # Creo la imagen a partir de esas listas    
        generate_img(imp_list,rest_list, img_name,width,height)
    else:
        if tRazvan:
            height = floor(px/2)
            width = floor(px/2)
        else:
            height = floor(px/3)
            width = floor(px/2)
        for cat in data_res:
            imp = Counter()
            for el in traza:
                if el in data_res[cat]:
                    imp[el] = traza[el]
            generate_img(imp.most_common(),[],cat+'.png',width,height)
        # Creo una imagen que tenga todas
        xi=0
        yi=0
        img = Image.new('RGB',(px,px),color='white')
        for cat in data_res:
            aux = Image.open(cat+'.png')
            img.paste(aux,(xi,yi))
            i+=1
            if xi > 0:
                xi = 0
                yi += height
            else:
                xi += width
        img.save(img_name)


#    if paro:
#        print(img_name) # Para saber dónde está la imagen a mirar
#        break   # Pruebo que haga bien la 1ª traza
    
#------------------------------------------------------------------------------
