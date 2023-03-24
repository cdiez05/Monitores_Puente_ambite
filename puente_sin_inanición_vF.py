#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 18:14:32 2023

@author: carlosdm
"""

"""
Solution to the one-way tunnel:
    
    
    Solución que resuelve el problema de inanición utilizando un semáforo circular:
        1. Coches Norte -> 2
        2. Coches Sur -> 3
        3. Peatones -> 1
"""

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

EMPTY = -1
NORTH = 0
SOUTH = 1
PD = 2

NCARS = 100
NPED = 15
TIME_CARS = 0.5  # a new car enters each 0.5s
TIME_PED = 4 # a new pedestrian enters each 4s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (7, 2.5) # normal 7s, 2.5s


class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0) 
        '''
        VARIABLES (compartidas)que se encargan de llevar la cuenta del número de 
        individuos que están esperando de cada clase:
            - NORTH
            - SOUTH
            - PD
        '''
        self.North_cars_waiting = Value('i',0) 
        self.South_cars_waiting = Value('i',0) 
        self.ped_waiting = Value('i',0) 
    
        '''
        Variables que se encargan de llevar la cuenta del número de 
        individuos que están circulando en el puente de cada clase:
            - NORTH
            - SOUTH
            - PD
        
        Una de las conidiciones para que una de ellas sea mayor que 0 es que las otras
        dos deben ser 0.
        '''
        self.North_cars_in_bridge = Value('i',0) 
        self.South_cars_in_bridge = Value('i',0)
        self.ped_in_bridge = Value('i',0) 
        
        '''
        Variables condición para dar paso a cada clase si se cumplen las condiciones óptimas 
        '''
        self.car_North = Condition(self.mutex) 
        self.car_South = Condition(self.mutex) 
        self.ped = Condition(self.mutex) 
        
        '''
        Variable que se encarga de indicar la clase que tiene permiso para cruzar el puente
        
        turnos:
            - NORTH -> 0
            - SOUTH -> 1
            - PD -> 2
        
        '''
        self.turn = Value('i',EMPTY) 
        
        
        
        '''
         · La condición necesaria para garantizar la seguridad del puente es
           que solo puede entrar la clase X al puente si las clases Y,Z 
           no están cruzando por el puente
         · La segunda condición necesaria para poder entrar al puente es que sea su turno 
           o el puente esté vacío
        
        
        '''
        
        
   
    def permission_car_north(self):
        '''
        Función que especifica las condiciones necesarias para que los coches
        del norte puedan cruzar el puente
        '''
        return (self.turn.value == NORTH or self.turn.value == EMPTY or (self.South_cars_waiting.value <=4 and self.ped_waiting.value <=4)) and (self.South_cars_in_bridge.value == 0 and self.ped_in_bridge.value == 0)
   
    def permission_car_south(self):
        '''
        Función que especifica las condiciones necesarias para que los coches
        del sur puedan cruzar el puente
        '''
        return (self.turn.value == SOUTH or self.turn.value == EMPTY or (self.North_cars_waiting.value <=4 and self.ped_waiting.value <=4)) and (self.North_cars_in_bridge.value == 0 and self.ped_in_bridge.value == 0)
                
    def permission_ped(self):
        '''
        Función que especifica las condiciones necesarias para que los peatones
        puedan cruzar el puente
        '''
        return (self.turn.value == PD or self.turn.value == EMPTY or (self.North_cars_waiting.value <=4 and self.South_cars_waiting.value <=4)) and (self.North_cars_in_bridge.value == 0 and self.South_cars_in_bridge.value == 0)
        #return (self.turn.value == PD or self.turn.value == EMPTY) and (self.North_cars_in_bridge.value == 0 and self.South_cars_in_bridge.value == 0)    
    def wants_enter_car(self, direction: int) -> None:
        '''
        Función que solicita el acceso de un coche en una dirección determinada al puente
        y le da acceso cuando este tenga permiso
        '''
        if direction == NORTH:
            self.mutex.acquire()
            self.patata.value += 1
            self.North_cars_waiting.value += 1
            self.car_North.wait_for(self.permission_car_north)
            self.North_cars_waiting.value -= 1
            self.turn.value = NORTH
            self.North_cars_in_bridge.value += 1
            self.mutex.release()
        elif direction == SOUTH:
            self.mutex.acquire()
            self.patata.value += 1
            self.South_cars_waiting.value += 1
            self.car_South.wait_for(self.permission_car_south)
            self.South_cars_waiting.value -= 1
            self.turn.value = SOUTH
            self.South_cars_in_bridge.value += 1
            self.mutex.release()
                
    def leaves_car(self, direction: int) -> None:
        '''
        Función que simula la salida de un coche del puente restando 1 a la variable 
        que representa el número de coches cruzando el puente en la dirección determinada.
        
        Más tarde, una vez que el puente se queda sin coches circulando, 
        cambia el turno a la siguiente clase que tenga individuos esperando.
        '''
        if direction == NORTH:
            self.mutex.acquire()
            self.patata.value += 1
            self.North_cars_in_bridge.value -= 1
            if self.South_cars_waiting.value > 0:
                self.turn.value = SOUTH
                #self.turn.value = (self.turn.value + 1) % 3 (semáforo circular)
            elif self.ped_waiting.value > 0:
                self.turn.value = PD
                #self.turn.value = (self.turn.value + 2) % 3 (semáforo circular)
            if self.North_cars_in_bridge.value == 0:
                self.car_South.notify_all()
                self.ped.notify_all()
                self.car_North.notify_all()
        elif direction == SOUTH:
            self.mutex.acquire()
            self.patata.value += 1
            self.South_cars_in_bridge.value -= 1
            if self.ped_waiting.value > 0:
                self.turn.value = PD
                #self.turn.value = (self.turn.value + 1) % 3 (semáforo circular)
            elif  self.North_cars_waiting.value > 0:
                self.turn.value = NORTH
                #self.turn.value = (self.turn.value + 2) % 3 (semáforo circular)
            if self.South_cars_in_bridge.value == 0:
                self.ped.notify_all()
                self.car_North.notify_all()
                self.car_South.notify_all()
        self.mutex.release()
    
    def wants_enter_pedestrian(self) -> None:
        '''
        Función que solicita el acceso de un peatón al puente y le da acceso 
        cuando este tenga permiso
        '''
        self.mutex.acquire()
        self.patata.value += 1
        self.ped_waiting.value += 1
        self.ped.wait_for(self.permission_ped)
        self.ped_waiting.value -= 1
        self.turn.value = PD
        self.ped_in_bridge.value += 1
        self.mutex.release()
        
    def leaves_pedestrian(self) -> None:
        '''
        Función que simula la salida de un peatón del puente restando 1 a la variable 
        que representa el número de peatones cruzando el puente.
        
        Más tarde, una vez que el puente se queda sin peatones circulando, 
        cambia el turno a la siguiente clase que tenga individuos esperando
        '''
        self.mutex.acquire()
        self.patata.value += 1
        self.ped_in_bridge.value -= 1
        if self.North_cars_waiting.value > 0:
            self.turn.value = NORTH
            #self.turn.value = (self.turn.value + 1) % 3 (semáforo circular)
        elif self.South_cars_waiting.value > 0:
            self.turn.value = SOUTH
            #self.turn.value = (self.turn.value + 2) % 3 (semáforo circular)
        if self.ped_in_bridge.value == 0:
            self.car_North.notify_all()
            self.car_South.notify_all()
            self.ped.notify_all()
        self.mutex.release()

    def __repr__(self) -> str:
        return f'Monitor: {self.patata.value}'

def delay_car_north() -> None:
    time.sleep(abs(random.gauss(1,0.5)))
    
def delay_car_south() -> None:
    time.sleep(abs(random.gauss(1,0.5)))

def delay_pedestrian() -> None:
    time.sleep(abs(random.gauss(7,2.5)))

def car(cid: int, direction: int, monitor: Monitor)  -> None:
    print(f"car {cid} heading {direction} wants to enter. {monitor}")
    monitor.wants_enter_car(direction)
    print(f"car {cid} heading {direction} enters the bridge. {monitor}")
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}")
    monitor.leaves_car(direction)
    print(f"car {cid} heading {direction} out of the bridge. {monitor}")

def pedestrian(pid: int, monitor: Monitor) -> None:
    print(f"pedestrian {pid} wants to enter. {monitor}")
    monitor.wants_enter_pedestrian()
    print(f"pedestrian {pid} enters the bridge. {monitor}")
    delay_pedestrian() 
    print(f"pedestrian {pid} leaving the bridge. {monitor}")
    monitor.leaves_pedestrian()
    print(f"pedestrian {pid} out of the bridge. {monitor}")

def gen_pedestrian(monitor: Monitor) -> None: 
    pid = 0
    plst = []
    for _ in range(NPED):
        pid += 1
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_PED))  

    for p in plst:
        p.join()

def gen_cars(monitor) -> Monitor: 
    cid = 0
    plst = []
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start() 
        plst.append(p)
        time.sleep(random.expovariate(1/TIME_CARS))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars = Process(target=gen_cars, args=(monitor,))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars.start() 
    gped.start()
    gcars.join()
    gped.join()


if __name__ == '__main__':
    main()
