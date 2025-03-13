import threading
import time
import random

class CuentaBancaria:
    def __init__(self):
        self.saldo = 0
        self.lock = threading.RLock()  # Usamos RLock para permitir bloqueos anidados si es necesario
    
    def ingresar(self, cantidad):
        with self.lock:
            self.saldo += cantidad
            print(f"Hilo {threading.current_thread().name} (depósito): Se ha depositado {cantidad}. Saldo actual: {self.saldo}")
    
    def retirar(self, cantidad):
        with self.lock:
            if self.saldo >= cantidad:
                self.saldo -= cantidad
                print(f"Hilo {threading.current_thread().name} (retirar): Se ha retirado {cantidad}. Saldo actual: {self.saldo}")
            else:
                print(f"Hilo {threading.current_thread().name} (retirar): Fondos insuficientes para retirar {cantidad}.")
    
    def consultar_saldo(self):
        with self.lock:
            print(f"Hilo {threading.current_thread().name} (consulta): Saldo actual: {self.saldo}")
            return self.saldo

# Funciones para los hilos
def realizar_depositos(cuenta, num_operaciones):
    for _ in range(num_operaciones):
        cantidad = random.randint(100, 1000)
        cuenta.ingresar(cantidad)
        time.sleep(random.uniform(0.1, 0.5))  # Simular tiempo de operación

def realizar_retiros(cuenta, num_operaciones):
    for _ in range(num_operaciones):
        cantidad = random.randint(50, 800)
        cuenta.retirar(cantidad)
        time.sleep(random.uniform(0.1, 0.5))  # Simular tiempo de operación

def consultar_saldo(cuenta, num_operaciones):
    for _ in range(num_operaciones):
        cuenta.consultar_saldo()
        time.sleep(random.uniform(0.2, 0.7))  # Simular tiempo de operación

def main():
    # Crear la cuenta bancaria
    cuenta = CuentaBancaria()
    
    # Número de operaciones para cada hilo
    num_operaciones = 5
    
    # Crear los hilos
    hilo_deposito = threading.Thread(name="1", target=realizar_depositos, args=(cuenta, num_operaciones))
    hilo_retiro = threading.Thread(name="2", target=realizar_retiros, args=(cuenta, num_operaciones))
    hilo_consulta = threading.Thread(name="3", target=consultar_saldo, args=(cuenta, num_operaciones))
    
    # Iniciar los hilos
    hilo_deposito.start()
    hilo_retiro.start()
    hilo_consulta.start()
    
    # Esperar a que todos los hilos terminen
    hilo_deposito.join()
    hilo_retiro.join()
    hilo_consulta.join()
    
    # Mostrar el saldo final
    print(f"\nOperaciones finalizadas. Saldo final: {cuenta.consultar_saldo()}")

if __name__ == "__main__":
    main()