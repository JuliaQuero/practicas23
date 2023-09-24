# Procesador para pasar las APIs a Categoría del fichero de ngramas
# Julia Quero Pérez - 792310

import csv
import json

# Tamaño de los n-gramas 
N = 3

out = open('ngram_to_cat.txt','w',newline='')

with open("winapi_categories.json",'r') as fi:
    json_dict = json.load(fi)

with open('ngram_API.txt','r') as file:
    lines = file.readlines()
    for l in lines:
        aux = l.split(",")
        # Para las líneas con APIs
        if len(aux) == N:
            numbers = aux[N-1].split("\t")
            aux[N-1] = numbers[0]
            for i in range(0,N):
                try:
                    aux[i] = json_dict[aux[i]]['category']
                except Exception:
                    aux[i] = "other"
            # Escribimos el resultado
            for i in range(0,N-1):
                out.write(aux[i])
                out.write(",")
            out.write(aux[N-1])
            out.write('\t')
            out.write(numbers[1])
            out.write('\t')
            out.write(numbers[2])
        else:
            out.write(l)
out.close()
