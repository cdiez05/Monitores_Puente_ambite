# Monitores_Puente_ambite

En este repositorio vamos a tratar de solucionar el problema del puente Ambite:

Este es un puente compartido por peatones y vehículos. 
La anchura del puente no permite el paso de vehículos en ambos sentidos 
Por motivos de seguridad los peatones y los vehículos no pueden compartir el puente. 
En el caso de los peatones, sí que que pueden pasar peatones en sentido contrario.

Este repositorio consta de dos soluciones:

    - puente_sin_inanicion_comentada.py: resolvemos el problema mediante monitores que cederán el paso a la clase que tenga más individuos esperando.
    Esta solución no resuelve el problema de inanición ya que si el turno es de una clase A en la que continuamente tiene un número alto de indiviudos 
    esperando y resulta haber un individuo de la clase B esperando para cruzar el puente, ese individuo va a morir por inanición y no va a conseguir pasar 
    el puente
    
    - puente_con_inanición.py: resolvemos el problema mediante monitores que funcionarán como un semáforo circular en el que va rotando el turno de cada 
    clase. Con esta solución cumpliremos todos los requisitos (resolviendo problema de inanición entre ellos).
    
Además, se cuenta con un pdf:

  - Demostración práctica 2: explicación escrita de distintas soluciones partiendo de una básica, llegando a una solución mejorada aunque aún sin resolver el problema de inanición (código en:puente_sin_inanicion_comentada.py) y por último la solución final (código en: puente_con_inanición.py)
