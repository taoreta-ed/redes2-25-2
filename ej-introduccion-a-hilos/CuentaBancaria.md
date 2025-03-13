# Control de Cuenta Bancaria con Hilos en Python

## Resumen
Este proyecto implementa una simulación de operaciones bancarias concurrentes usando hilos en Python. El objetivo es demostrar cómo manejar correctamente los problemas de concurrencia que pueden surgir cuando múltiples procesos intentan acceder y modificar un recurso compartido (en este caso, el saldo de una cuenta bancaria).

## Enlaces
- [Repositorio del proyecto](https://github.com/taoreta-ed/redes2-25-2)
- [Documentación en Claude AI](https://claude.ai/share/fdaf80a6-af5e-44dc-ba54-869c1fa8a631)

## Funcionamiento de los Hilos en Python

Los hilos (threads) son unidades de ejecución que permiten que un programa realice varias tareas aparentemente al mismo tiempo. En Python, los hilos se implementan a través del módulo `threading`.

### Concepto de Concurrencia

La concurrencia ocurre cuando múltiples procesos o hilos se ejecutan durante períodos superpuestos. En nuestro caso, estamos simulando tres operaciones bancarias concurrentes:
1. Realizar depósitos
2. Realizar retiros
3. Consultar el saldo

### Problemas de Concurrencia

Cuando múltiples hilos acceden a datos compartidos, pueden ocurrir "condiciones de carrera". Por ejemplo:
- El hilo A lee que el saldo es 500
- El hilo B lee que el saldo es 500
- El hilo A añade 100 y actualiza el saldo a 600
- El hilo B resta 200 y actualiza el saldo a 300
- El resultado final es incorrecto (debería ser 400)

## Implementación

### Clase CuentaBancaria

```python
class CuentaBancaria:
    def __init__(self):
        self.saldo = 0
        self.lock = threading.RLock()  # Usamos RLock para permitir bloqueos anidados
    
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
```

#### Explicación:

1. **Constructor**: Inicializa el saldo a 0 y crea un objeto `RLock` para sincronización.
   
2. **Métodos de Operación**:
   - Cada método utiliza la sentencia `with self.lock` para adquirir el bloqueo antes de acceder o modificar el saldo.
   - Esta técnica garantiza que solo un hilo pueda ejecutar el código dentro del bloque `with` a la vez.

3. **RLock vs Lock**:
   - Se usa `RLock` en lugar de `Lock` para permitir que el mismo hilo pueda adquirir el bloqueo múltiples veces sin provocar un deadlock.
   - Esto es útil si los métodos se llaman entre sí (por ejemplo, si `retirar` llamara a `consultar_saldo`).

### Funciones para los Hilos

```python
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
```

#### Explicación:

1. **Generación de Cantidades Aleatorias**: Se utilizan valores aleatorios para simular diferentes cantidades de depósito y retiro.

2. **Simulación de Tiempo de Operación**: La función `time.sleep()` con un valor aleatorio simula el tiempo que tomaría cada operación en un sistema real.

3. **Concurrencia**: Al ejecutar estas funciones en hilos separados, se ejecutarán de manera concurrente, intercalando sus operaciones.

### Función Principal

```python
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
```

#### Explicación:

1. **Creación de Hilos**: Se crean tres hilos, cada uno con una función objetivo diferente.
   - El parámetro `name` asigna un identificador a cada hilo para seguimiento.
   - El parámetro `target` define la función que ejecutará el hilo.
   - El parámetro `args` proporciona los argumentos para la función.

2. **Inicialización de Hilos**: El método `start()` inicia la ejecución de cada hilo.

3. **Sincronización de Hilos**: El método `join()` hace que el programa principal espere hasta que cada hilo termine antes de continuar.

## Resultados Esperados

La ejecución mostrará cómo los tres hilos realizan operaciones intercaladas:
- El hilo 1 depositará cantidades aleatorias.
- El hilo 2 intentará retirar cantidades aleatorias (algunas pueden fallar por fondos insuficientes).
- El hilo 3 consultará periódicamente el saldo actual.

El uso del mecanismo de bloqueo garantiza que todas las operaciones sean atómicas y que el saldo se mantenga consistente a pesar de la concurrencia.

## Conclusiones

Este ejercicio demuestra:
1. El uso de hilos para simular operaciones concurrentes
2. La implementación de mecanismos de sincronización (RLock) para proteger recursos compartidos
3. La gestión adecuada de condiciones de error (intentar retirar más de lo disponible)
4. La importancia de la sincronización en sistemas concurrentes

Estos conceptos son fundamentales en la programación de cualquier sistema que requiera coordinación entre múltiples procesos concurrentes.
