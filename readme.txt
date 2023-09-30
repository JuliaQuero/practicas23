La memoria de las prácticas puede encontrarse en Memoria.pdf

El código fuente para extraer n-gramas se encuentra en la carpeta caract_ngramas/. Esta se compone de las carpetas tablas/, con ejemplos de ejecuciones de an_cuant_conj.py y an_cual_conj.py y la carpeta ngram_lists/, con ejemplos de ejecuciones de most_used_ngram.py
	most_used_ngram.py escribe un txt con los ngramas decididos como importantes según el método introducido.
	an_cual_conj.py calcula dos tablas comparando los ngramas importantes por familias de virus: una con los iguales y otra con los distintos.
	an_cuant_conj.py calcula las tablas como el programa anterior, devolviendo en vez de los nombres de los n-gramas, su número.

En la carpeta generar_img se encuentran los datasets de trazas que he utilizado y el código para generar los distintos tipos de imágenes, que se trata del fichero def_traza_to_img.py
	categories.txt es un fichero auxiliar para calcular la selección de colores por categoría.
	
En la carpeta datasets/ se encuentran los datasets con las trazas de ejecución de malware
	tratado_API_dataset.csv se corresponde con las trazas por API del dataset del artículo marcado con [3] en Memoria.pdf
	tratado_Cat_dataset.csv se corresponde con las trazas por categorías del dataset del artículo marcado con [3] en Memoria.pdf
	resumen_API_dataset.csv se corresponde con las trazas por API del dataset creado por otros compañeros de prácticas
	resumen_API_dataset.csv se corresponde con las trazas por categorías del dataset creado por otros compañeros de prácticas

En la carpeta redes_neuronales están los jupyter notebook usados para entrenar las redes:
	obtenF1InceptionV3.ipynb devuelve en un fichero txt la media del average f1-score de 3 entrenamientos de la red InceptionV3 para un dataset de imágenes.
	obtenF1TodaRed.ipynb devuelve en un fichero txt ese valor para cada una de las 5 redes preentrenadas utilizadas por orden de cálculo en el programa.

En la carpeta resultados se encuentran las tablas resumen con los f1 obtenidos. Están en los siguientes ficheros:
	pruebas_Kim.xlsx para las trazas del dataset del artículo marcado con [3] en Memoria.pdf
	pruebas_Alain.xlsx para las trazas del dataset creado por otros compañeros de prácticas

El archivo lisTraza.csv recoge los valores asignados a cada parámetro para la creación de cada dataset de imágenes. Estos datasets se pueden encontrar en el repositorio https://github.com/JuliaQuero/img_dataset 
