"""
Solution to the one-way bridge

    Solución del problema que no resuelve el problema de inanición con un semáforo basado 
    en el número de individuos esperando de cada clase, cuántos más haya, más preferencia 
    tiene esa clase para pasar el puente
"""


import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 100
NPED = 20
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 3# a new pedestrian enters each 3 s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.patata = Value('i', 0)
        
        self.North_cars_waiting = Value('i', 0)
        self.South_cars_waiting = Value('i', 0)
        self.ped_waiting = Value('i', 0)
        
        self.South_cars_in_bridge = Value('i', 0)
        self.North_cars_in_bridge = Value('i', 0)
        self.ped_in_bridge = Value('i', 0)
        
        self.car_South_turn = Condition(self.mutex)
        self.car_North_turn = Condition(self.mutex)
        self.ped_turn = Condition(self.mutex)
        
    def more_North_cars_waiting(self):
        return self.North_cars_waiting.value >= self.South_cars_waiting.value and self.North_cars_waiting.value + self.South_cars_waiting.value >= self.ped_waiting.value
        
    def more_South_cars_waiting(self):
        return self.South_cars_waiting.value > self.North_cars_waiting.value and self.North_cars_waiting.value + self.South_cars_waiting.value >= self.ped_waiting.value
    
    def more_ped_waiting(self):
        return self.ped_waiting.value > self.North_cars_waiting.value + self.South_cars_waiting.value
    
    def no_car_North_in_bridge(self):
        return self.North_cars_in_bridge.value ==0
    
    def no_car_South_in_bridge(self):
        return self.South_cars_in_bridge.value == 0
    
    def no_ped_in_bridge(self):
        return self.ped_in_bridge.value == 0
            
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        if direction == NORTH:
            self.North_cars_waiting.value += 1
            self.car_North_turn.wait_for(self.more_North_cars_waiting and self.no_car_South_in_bridge and self.no_ped_in_bridge)
            self.North_cars_waiting.value -= 1
            self.North_cars_in_bridge.value += 1
        else:
            self.South_cars_waiting.value +=1
            self.car_South_turn.wait_for(self.more_South_cars_waiting and self.no_car_North_in_bridge and self.no_ped_in_bridge)
            self.South_cars_waiting.value -= 1
            self.South_cars_in_bridge.value += 1
        self.mutex.release()

    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire() 
        self.patata.value += 1
        if direction == NORTH:
            self.North_cars_in_bridge.value -= 1
        else:
            self.South_cars_in_bridge.value -= 1
        self.ped_turn.notify()
        self.car_South_turn.notify()
        self.car_North_turn.notify()
        self.mutex.release()

    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.ped_waiting.value +=1
        self.ped_turn.wait_for(self.more_ped_waiting and self.no_car_North_in_bridge and self.no_car_South_in_bridge)
        self.ped_waiting.value -= 1
        self.ped_in_bridge.value +=1
        self.mutex.release()

    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()
        self.patata.value += 1
        self.ped_in_bridge.value -=1
        self.car_South_turn.notify()
        self.car_North_turn.notify()
        self.ped_turn.notify()
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

def gen_cars(direction: int, time_cars, monitor: Monitor) -> None:
    cid = 0
    plst = []
    for _ in range(NCARS):
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p)
        time.sleep(random.expovariate(1/time_cars))

    for p in plst:
        p.join()

def main():
    monitor = Monitor()
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    gcars_north.start()
    gcars_south.start()
    gped.start()
    gcars_north.join()
    gcars_south.join()
    gped.join()


if __name__ == '__main__':
    main()
