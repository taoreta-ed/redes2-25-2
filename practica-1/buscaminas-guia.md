# Implementación de Buscaminas Cliente-Servidor usando Sockets

## Índice
1. [Introducción](#introducción)
2. [Elección del Protocolo](#elección-del-protocolo)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Implementación del Servidor](#implementación-del-servidor)
5. [Implementación del Cliente](#implementación-del-cliente)
6. [Protocolo de Comunicación](#protocolo-de-comunicación)
7. [Ejecución del Juego](#ejecución-del-juego)
8. [Ejemplos de Juego](#ejemplos-de-juego)

## Introducción

Este proyecto consiste en la implementación de un juego de Buscaminas utilizando el modelo Cliente-Servidor con comunicación a través de sockets. El juego sigue las reglas tradicionales del Buscaminas donde:

- El tablero contiene minas ocultas
- El jugador debe descubrir todas las casillas que no contienen minas
- Si el jugador descubre una casilla con mina, pierde el juego
- Las casillas revelan números que indican cuántas minas hay en las casillas adyacentes

Según las especificaciones de la práctica, el servidor mantendrá el estado real del tablero mientras que el cliente mostrará un tablero local que se actualizará con la información recibida del servidor.

## Elección del Protocolo

Para esta implementación, utilizaremos **sockets de flujo (TCP)** por las siguientes razones:

1. **Fiabilidad**: TCP garantiza la entrega de los datos en el orden correcto, lo que es crucial para un juego por turnos como el Buscaminas donde cada acción depende del estado actual del tablero.

2. **Control de conexión**: TCP establece una conexión entre cliente y servidor que se mantiene durante toda la partida, lo que facilita el seguimiento del estado del juego.

3. **Integridad de los datos**: Para un juego como el Buscaminas, es esencial que no se pierdan mensajes entre el cliente y el servidor, ya que cada acción del jugador debe ser validada correctamente.

4. **Orientado a la conexión**: Aunque UDP podría ser más rápido, para este juego la velocidad no es crítica y es más importante la fiabilidad de la comunicación.

## Estructura del Proyecto

El proyecto constará de dos aplicaciones principales:

1. **Servidor de Buscaminas**: Gestiona el estado real del tablero, valida los movimientos y determina el resultado del juego.
2. **Cliente de Buscaminas**: Permite al jugador interactuar con el juego, envía las coordenadas al servidor y muestra el tablero actualizado.

## Implementación del Servidor

### Funcionalidades del Servidor

- Configuración del socket y espera de conexiones
- Generación aleatoria del tablero con minas
- Validación de los movimientos del jugador
- Control del tiempo de la partida
- Determinación del resultado del juego (victoria/derrota)

### Código del Servidor

```python
import socket
import random
import time
import json
from datetime import datetime

class BuscaminasServidor:
    def __init__(self):
        self.tablero = []
        self.tablero_visible = []  # Lo que el cliente puede ver
        self.filas = 0
        self.columnas = 0
        self.minas = 0
        self.casillas_destapadas = 0
        self.tiempo_inicio = 0
        self.tiempo_fin = 0
        self.servidor_socket = None
        self.cliente_socket = None
        self.dificultad = ""
        self.ip = ""
        self.puerto = 0
        self.juego_terminado = False

    def configurar_servidor(self):
        """Configura los parámetros del servidor y la dificultad del juego"""
        self.ip = input("Ingrese la dirección IP del servidor: ")
        self.puerto = int(input("Ingrese el puerto del servidor: "))
        
        print("\nSeleccione la dificultad:")
        print("1. Principiante (9x9 tablero con 10 minas)")
        print("2. Avanzado (16x16 tablero con 40 minas)")
        opcion = input("Opción (1-2): ")
        
        if opcion == "1":
            self.dificultad = "principiante"
            self.filas = 9
            self.columnas = 9
            self.minas = 10
        else:
            self.dificultad = "avanzado"
            self.filas = 16
            self.columnas = 16
            self.minas = 40
            
        print(f"Servidor configurado con dificultad: {self.dificultad}")

    def iniciar_servidor(self):
        """Inicia el servidor y espera la conexión de un cliente"""
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((self.ip, self.puerto))
        self.servidor_socket.listen(1)
        
        print(f"Servidor iniciado en {self.ip}:{self.puerto}")
        print("Esperando la conexión del cliente...")
        
        self.cliente_socket, direccion_cliente = self.servidor_socket.accept()
        print(f"Cliente conectado desde {direccion_cliente[0]}:{direccion_cliente[1]}")
        
        # Generar el tablero al recibir la conexión
        self.generar_tablero()
        
        # Enviar confirmación y dificultad al cliente
        mensaje_inicial = {
            "tipo": "configuracion", 
            "dificultad": self.dificultad, 
            "filas": self.filas, 
            "columnas": self.columnas
        }
        self.enviar_mensaje(mensaje_inicial)
        
        # Iniciar el tiempo de juego
        self.tiempo_inicio = time.time()
        
        # Procesar movimientos del cliente
        self.procesar_movimientos()

    def generar_tablero(self):
        """Genera el tablero con las minas colocadas aleatoriamente"""
        # Inicializar tablero vacío
        self.tablero = [[0 for _ in range(self.columnas)] for _ in range(self.filas)]
        self.tablero_visible = [['□' for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Colocar minas aleatoriamente
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            fila = random.randint(0, self.filas - 1)
            col = random.randint(0, self.columnas - 1)
            
            if self.tablero[fila][col] != -1:  # -1 representa una mina
                self.tablero[fila][col] = -1
                minas_colocadas += 1
                
                # Actualizar números en casillas adyacentes
                for i in range(max(0, fila-1), min(self.filas, fila+2)):
                    for j in range(max(0, col-1), min(self.columnas, col+2)):
                        if self.tablero[i][j] != -1:
                            self.tablero[i][j] += 1
        
        print("Tablero generado:")
        self.imprimir_tablero()

    def imprimir_tablero(self):
        """Imprime el tablero actual (para el servidor)"""
        print("  " + " ".join(str(i) for i in range(self.columnas)))
        for i in range(self.filas):
            print(f"{i} ", end="")
            for j in range(self.columnas):
                if self.tablero[i][j] == -1:
                    print("* ", end="")
                else:
                    print(f"{self.tablero[i][j]} ", end="")
            print()

    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al cliente en formato JSON"""
        mensaje_json = json.dumps(mensaje)
        self.cliente_socket.send(mensaje_json.encode('utf-8'))

    def recibir_mensaje(self):
        """Recibe un mensaje del cliente en formato JSON"""
        mensaje = self.cliente_socket.recv(1024).decode('utf-8')
        return json.loads(mensaje)

    def procesar_movimientos(self):
        """Procesa los movimientos enviados por el cliente"""
        while not self.juego_terminado:
            try:
                mensaje = self.recibir_mensaje()
                
                if mensaje["tipo"] == "coordenada":
                    fila = mensaje["fila"]
                    columna = mensaje["columna"]
                    
                    # Validar movimiento
                    resultado = self.validar_movimiento(fila, columna)
                    
                    # Verificar si el juego ha terminado
                    self.verificar_estado_juego()
                    
                elif mensaje["tipo"] == "desconexion":
                    print("Cliente desconectado")
                    break
                    
            except Exception as e:
                print(f"Error al procesar movimiento: {e}")
                break
        
        # Cerrar la conexión
        self.cliente_socket.close()
        self.servidor_socket.close()
        print("Conexión cerrada")

    def validar_movimiento(self, fila, columna):
        """Valida el movimiento del jugador y envía el resultado al cliente"""
        # Verificar si la casilla ya está destapada
        if self.tablero_visible[fila][columna] != '□':
            respuesta = {
                "tipo": "control",
                "estado": "casilla_ocupada",
                "mensaje": "Esta casilla ya está destapada"
            }
            self.enviar_mensaje(respuesta)
            return False
            
        # Verificar si hay mina
        if self.tablero[fila][columna] == -1:
            # El jugador ha perdido
            self.tablero_visible[fila][columna] = '*'
            
            # Revelar todas las minas
            for i in range(self.filas):
                for j in range(self.columnas):
                    if self.tablero[i][j] == -1:
                        self.tablero_visible[i][j] = '*'
            
            respuesta = {
                "tipo": "control",
                "estado": "mina_pisada",
                "mensaje": "¡Has pisado una mina! Juego terminado.",
                "tablero": self.tablero_visible
            }
            self.enviar_mensaje(respuesta)
            
            self.juego_terminado = True
            self.tiempo_fin = time.time()
            duracion = round(self.tiempo_fin - self.tiempo_inicio)
            
            # Enviar mensaje final
            mensaje_final = {
                "tipo": "fin",
                "resultado": "derrota",
                "duracion": duracion,
                "mensaje": f"Has perdido. Duración del juego: {duracion} segundos."
            }
            self.enviar_mensaje(mensaje_final)
            
            print(f"Juego terminado. El jugador ha perdido. Duración: {duracion} segundos.")
            return False
            
        else:
            # No hay mina, revelar el número
            valor = self.tablero[fila][columna]
            self.tablero_visible[fila][columna] = str(valor) if valor > 0 else ' '
            self.casillas_destapadas += 1
            
            respuesta = {
                "tipo": "control",
                "estado": "casilla_libre",
                "valor": valor,
                "fila": fila,
                "columna": columna
            }
            self.enviar_mensaje(respuesta)
            
            # Si es un 0, revelar las casillas adyacentes (función recursiva)
            if valor == 0:
                self.revelar_casillas_adyacentes(fila, columna)
                
            return True

    def revelar_casillas_adyacentes(self, fila, columna):
        """Revela recursivamente las casillas adyacentes a una casilla con valor 0"""
        for i in range(max(0, fila-1), min(self.filas, fila+2)):
            for j in range(max(0, columna-1), min(self.columnas, columna+2)):
                # Si la casilla ya está revelada o es la misma, continuar
                if (i == fila and j == columna) or self.tablero_visible[i][j] != '□':
                    continue
                    
                # Revelar la casilla
                valor = self.tablero[i][j]
                if valor != -1:  # No revelar minas
                    self.tablero_visible[i][j] = str(valor) if valor > 0 else ' '
                    self.casillas_destapadas += 1
                    
                    # Notificar al cliente
                    respuesta = {
                        "tipo": "control",
                        "estado": "casilla_libre",
                        "valor": valor,
                        "fila": i,
                        "columna": j
                    }
                    self.enviar_mensaje(respuesta)
                    
                    # Si es 0, continuar la recursión
                    if valor == 0:
                        self.revelar_casillas_adyacentes(i, j)

    def verificar_estado_juego(self):
        """Verifica si el jugador ha ganado"""
        casillas_totales = self.filas * self.columnas
        if self.casillas_destapadas == casillas_totales - self.minas and not self.juego_terminado:
            self.juego_terminado = True
            self.tiempo_fin = time.time()
            duracion = round(self.tiempo_fin - self.tiempo_inicio)
            
            # Enviar mensaje final
            mensaje_final = {
                "tipo": "fin",
                "resultado": "victoria",
                "duracion": duracion,
                "mensaje": f"¡Has ganado! Duración del juego: {duracion} segundos."
            }
            self.enviar_mensaje(mensaje_final)
            
            print(f"Juego terminado. El jugador ha ganado. Duración: {duracion} segundos.")

# Código principal para ejecutar el servidor
if __name__ == "__main__":
    servidor = BuscaminasServidor()
    servidor.configurar_servidor()
    servidor.iniciar_servidor()
```

## Implementación del Cliente

### Funcionalidades del Cliente

- Conexión con el servidor
- Visualización del tablero de juego
- Envío de coordenadas al servidor
- Interpretación de los mensajes del servidor y actualización del tablero local
- Notificación del resultado final al jugador

### Código del Cliente

```python
import socket
import json
import os
import sys
import time

class BuscaminasCliente:
    def __init__(self):
        self.tablero = []
        self.filas = 0
        self.columnas = 0
        self.cliente_socket = None
        self.ip_servidor = ""
        self.puerto_servidor = 0
        self.juego_terminado = False
        self.dificultad = ""

    def conectar_servidor(self):
        """Establece la conexión con el servidor"""
        self.ip_servidor = input("Ingrese la dirección IP del servidor: ")
        self.puerto_servidor = int(input("Ingrese el puerto del servidor: "))
        
        # Crear socket y conectar al servidor
        try:
            self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente_socket.connect((self.ip_servidor, self.puerto_servidor))
            print(f"Conectado al servidor {self.ip_servidor}:{self.puerto_servidor}")
            
            # Recibir configuración inicial
            self.recibir_configuracion()
            
            # Iniciar el juego
            self.iniciar_juego()
            
        except Exception as e:
            print(f"Error al conectar con el servidor: {e}")
            sys.exit(1)

    def recibir_configuracion(self):
        """Recibe la configuración inicial del juego"""
        mensaje = self.recibir_mensaje()
        
        if mensaje["tipo"] == "configuracion":
            self.dificultad = mensaje["dificultad"]
            self.filas = mensaje["filas"]
            self.columnas = mensaje["columnas"]
            
            # Inicializar el tablero vacío
            self.tablero = [['□' for _ in range(self.columnas)] for _ in range(self.filas)]
            
            print(f"Juego configurado con dificultad: {self.dificultad}")
            print(f"Tablero de {self.filas}x{self.columnas}")
        else:
            print("Error: No se recibió configuración inicial")
            self.desconectar()
            sys.exit(1)

    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al servidor en formato JSON"""
        mensaje_json = json.dumps(mensaje)
        self.cliente_socket.send(mensaje_json.encode('utf-8'))

    def recibir_mensaje(self):
        """Recibe un mensaje del servidor en formato JSON"""
        mensaje = self.cliente_socket.recv(1024).decode('utf-8')
        return json.loads(mensaje)

    def imprimir_tablero(self):
        """Imprime el estado actual del tablero"""
        # Limpiar pantalla
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"=== BUSCAMINAS - Dificultad: {self.dificultad} ===\n")
        
        # Imprimir encabezado de columnas
        print("  ", end="")
        for j in range(self.columnas):
            print(f"{j} ", end="")
        print("\n")
        
        # Imprimir filas del tablero
        for i in range(self.filas):
            print(f"{i} ", end="")
            for j in range(self.columnas):
                print(f"{self.tablero[i][j]} ", end="")
            print()
        print()

    def iniciar_juego(self):
        """Inicia el ciclo principal del juego"""
        self.imprimir_tablero()
        
        print("¡Bienvenido a Buscaminas!")
        print("Instrucciones:")
        print("- Debes descubrir todas las casillas sin minas")
        print("- Si descubres una mina, pierdes")
        print("- Los números indican cuántas minas hay en las casillas adyacentes")
        print("- Ingresa las coordenadas de la casilla que quieres descubrir\n")
        
        while not self.juego_terminado:
            try:
                # Solicitar coordenadas al jugador
                fila = int(input("Ingrese la fila: "))
                columna = int(input("Ingrese la columna: "))
                
                # Validar que las coordenadas estén dentro del tablero
                if fila < 0 or fila >= self.filas or columna < 0 or columna >= self.columnas:
                    print("Coordenadas fuera del tablero. Intente de nuevo.")
                    continue
                
                # Validar que la casilla no esté ya destapada
                if self.tablero[fila][columna] != '□':
                    print("Esta casilla ya está destapada. Intente otra.")
                    continue
                
                # Enviar coordenadas al servidor
                coordenada = {
                    "tipo": "coordenada",
                    "fila": fila,
                    "columna": columna
                }
                self.enviar_mensaje(coordenada)
                
                # Procesar respuesta del servidor
                self.procesar_respuesta()
                
            except ValueError:
                print("Entrada inválida. Ingrese un número.")
            except KeyboardInterrupt:
                print("\nJuego interrumpido por el usuario.")
                self.desconectar()
                break
        
        # Si el juego termina normalmente
        if self.juego_terminado:
            input("\nPresione Enter para salir...")
        
        self.desconectar()

    def procesar_respuesta(self):
        """Procesa la respuesta del servidor"""
        mensaje = self.recibir_mensaje()
        
        if mensaje["tipo"] == "control":
            if mensaje["estado"] == "casilla_ocupada":
                print(mensaje["mensaje"])
                time.sleep(1)
                
            elif mensaje["estado"] == "casilla_libre":
                # Actualizar casilla en el tablero local
                valor = mensaje["valor"]
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                
                self.tablero[fila][columna] = str(valor) if valor > 0 else ' '
                self.imprimir_tablero()
                
            elif mensaje["estado"] == "mina_pisada":
                # El jugador ha perdido, actualizar tablero con todas las minas
                self.tablero = mensaje["tablero"]
                self.imprimir_tablero()
                print(mensaje["mensaje"])
                
                # Esperar el mensaje final
                self.procesar_respuesta()
                
        elif mensaje["tipo"] == "fin":
            # Juego terminado
            self.juego_terminado = True
            
            if mensaje["resultado"] == "victoria":
                print("¡FELICIDADES! ¡Has ganado!")
            else:
                print("¡BOOM! Has perdido.")
                
            print(f"Duración del juego: {mensaje['duracion']} segundos")

    def desconectar(self):
        """Cierra la conexión con el servidor"""
        if self.cliente_socket:
            try:
                # Enviar mensaje de desconexión
                desconexion = {"tipo": "desconexion"}
                self.enviar_mensaje(desconexion)
                
                # Cerrar el socket
                self.cliente_socket.close()
                print("Desconectado del servidor")
            except:
                pass

# Código principal para ejecutar el cliente
if __name__ == "__main__":
    cliente = BuscaminasCliente()
    cliente.conectar_servidor()
```

## Protocolo de Comunicación

El protocolo de comunicación entre cliente y servidor utiliza mensajes en formato JSON con los siguientes tipos:

### Mensajes del Servidor al Cliente:

1. **Configuración Inicial**:
```json
{
  "tipo": "configuracion",
  "dificultad": "principiante",
  "filas": 9,
  "columnas": 9
}
```

2. **Respuesta a Movimiento** (Casilla Libre):
```json
{
  "tipo": "control",
  "estado": "casilla_libre",
  "valor": 1,
  "fila": 3,
  "columna": 4
}
```

3. **Respuesta a Movimiento** (Casilla Ocupada):
```json
{
  "tipo": "control",
  "estado": "casilla_ocupada",
  "mensaje": "Esta casilla ya está destapada"
}
```

4. **Respuesta a Movimiento** (Mina Pisada):
```json
{
  "tipo": "control",
  "estado": "mina_pisada",
  "mensaje": "¡Has pisado una mina! Juego terminado.",
  "tablero": [["□", "□", "*"], ["□", "□", "□"], ["□", "*", "□"]]
}
```

5. **Fin de Juego**:
```json
{
  "tipo": "fin",
  "resultado": "victoria",
  "duracion": 45,
  "mensaje": "¡Has ganado! Duración del juego: 45 segundos."
}
```

### Mensajes del Cliente al Servidor:

1. **Coordenadas**:
```json
{
  "tipo": "coordenada",
  "fila": 3,
  "columna": 4
}
```

2. **Desconexión**:
```json
{
  "tipo": "desconexion"
}
```

## Ejecución del Juego

Para ejecutar el juego, sigue estos pasos:

1. **Iniciar el Servidor**:
   ```
   python servidor_buscaminas.py
   ```
   
   - Introduce la dirección IP y el puerto en el que escuchará el servidor.
   - Selecciona la dificultad (principiante o avanzado).
   - El servidor generará el tablero y esperará la conexión del cliente.

2. **Iniciar el Cliente**:
   ```
   python cliente_buscaminas.py
   ```
   
   - Introduce la dirección IP y el puerto del servidor.
   - El cliente se conectará al servidor y mostrará el tablero vacío.

3. **Jugar**:
   - El cliente mostrará el tablero y pedirá al jugador las coordenadas de la casilla a destapar.
   - El servidor validará el movimiento y enviará el resultado al cliente.
   - El cliente actualizará el tablero local con la información recibida.
   - El juego continúa hasta que el jugador gane (destape todas las casillas sin minas) o pierda (destape una mina).

4. **Fin del Juego**:
   - Al finalizar la partida, el servidor enviará un mensaje indicando si el jugador ganó o perdió.
   - El servidor mostrará la duración del juego.
   - Ambas aplicaciones cerrarán la conexión.

## Ejemplos de Juego

### Ejemplo de Tablero Inicial (Cliente)

```
=== BUSCAMINAS - Dificultad: principiante ===

  0 1 2 3 4 5 6 7 8 

0 □ □ □ □ □ □ □ □ □ 
1 □ □ □ □ □ □ □ □ □ 
2 □ □ □ □ □ □ □ □ □ 
3 □ □ □ □ □ □ □ □ □ 
4 □ □ □ □ □ □ □ □ □ 
5 □ □ □ □ □ □ □ □ □ 
6 □ □ □ □ □ □ □ □ □ 
7 □ □ □ □ □ □ □ □ □ 
8 □ □ □ □ □ □ □ □ □ 
```

### Ejemplo de Tablero en Juego (Cliente)

```
=== BUSCAMINAS - Dificultad: principiante ===

  0 1 2 3 4 5 6 7 8 

0   1 □ □ □ □ □ □ □ 
1   1 □ □ □ □ □ □ □ 
2 1 2 □ □ □ □ □ □ □ 
3 □ □ □ □ □ □ □ □ □ 
4 □ □ □ □ □ □ □ □ □ 
5 □ □ □ □ □ □ □ □ □ 
6 □ □ □ □ □ □ □ □ □ 
7 □ □ □ □ □ □ □ □ □ 
8 □ □ □ □ □ □ □ □ □ 
```

### Ejemplo de Tablero Final (Victoria)

```
=== BUSCAMINAS - Dificultad: principiante ===

  0 1 2 3 4 5 6 7 8 

0   1 1     1 1 1   
1   1 1     1 □ 1   
2 1 2 1 1   2 2 2   
3 1 □ 1 1   1 □ 1   
4 2 2 2 1 1 2 1 1   
5 □ 2   1 □ 1      
6 2 3   1 1 1      
7 □ 2              
8 1 1              

¡FELICIDADES! ¡Has ganado!
Duración del juego: 78 segundos
```

### Ejemplo de Tablero Final (Derrota)

```
=== BUSCAMINAS - Dificultad: principiante ===

  0 1 2 3 4 5 6 7 8 

0   1 1     1 1 1   
1   1 1     1 * 1   
2 1 2 1 1   2 2 2   
3 1 * 1 1   1 * 1   
4 2 2 2 1 1 2 1 1   
5 * 2   1 * 1      
6 2 3   1 1 1      
7 * 2         *    
8 1 1              

¡BOOM! Has perdido.
Duración del juego: 45 segundos
```
