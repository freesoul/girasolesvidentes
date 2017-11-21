# Los Girasoles Videntes
## Qué es
Se trata de un proyecto realizado para el concurso de Impaciencia (www.impaciencia.org), en el que se comprueba la hipótesis de si el lenguaje está especializado en personas con distintas carreras académicas o profesiones.

## Comprobacion de la hipotesis
Se utiliza un clasificador Naive Bayes multinomial, entrenado con informacion de internet, como caracterizador del ambito del texto (Ingenieria, Letras, Bellas Artes...)
El estudio se lleva a cabo comparando las puntuaciones resultantes de aplicar el modelo anterior a las respuestas obtenidas de los distintos grupos de alumnos/profesionales a una serie de pruebas.

## Qué partes tiene
### Harvest.py
Es un generador de corpus automatizado que extrae la informacion de internet a traves de una serie de palabras clave buscadas en Google.
Reconoce los textos principales de las paginas web a traves de Goose, tambien extrae informacion de PDFs, y en su caso, de RSS.

### Preprocess.py
En primer lugar sanitiza un texto eliminando todo lo que no sean palabras. Despues elimina toda palabra que esté en una lista de "stopwords", las cuales se considera que no aportan informacion significante.
Finalmente mide la frecuencia de aparicion de cada palabra, y crea un diccionario con la relacion "palabra-frecuencia"

### Bayes.py
Contiene el modelo multinomial, entrenado a partir del diccionario generado por Preprocess.py.
Crea tantos vectores como clases de textos hayan (Ciencias, ingenieria...), y el largo de los vectores es el minimo necesario para recoger todas las palabras empleadas en todos los grupos.
Se eliminan las palabras bajo un minimo umbral de desviacion tipica, porque no tendrian mucho peso en la clasificacion.
Este mismo archivo genera las predicciones para un texto determinado


