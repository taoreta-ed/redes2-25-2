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
        try:
            self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            
        except Exception as e:
            print(f"Error al iniciar servidor: {e}")
            if self.servidor_socket:
                self.servidor_socket.close()

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
        try:
            mensaje_json = json.dumps(mensaje)
            # Añadir delimitador de nueva línea para facilitar la lectura en el cliente
            mensaje_json += '\n'
            self.cliente_socket.sendall(mensaje_json.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            return False

    def recibir_mensaje(self):
        """Recibe un mensaje del cliente en formato JSON"""
        try:
            datos = self.cliente_socket.recv(1024)
            if not datos:
                raise Exception("Conexión cerrada por el cliente")
                
            mensaje = json.loads(datos.decode('utf-8'))
            return mensaje
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            raise
        except Exception as e:
            print(f"Error al recibir mensaje: {e}")
            raise

    def procesar_movimientos(self):
        """Procesa los movimientos enviados por el cliente"""
        while not self.juego_terminado:
            try:
                mensaje = self.recibir_mensaje()
                
                if mensaje["tipo"] == "coordenada":
                    fila = mensaje["fila"]
                    columna = mensaje["columna"]
                    
                    # Validar movimiento
                    self.validar_movimiento(fila, columna)
                    
                    # Verificar si el juego ha terminado
                    self.verificar_estado_juego()
                    
                elif mensaje["tipo"] == "desconexion":
                    print("Cliente desconectado")
                    break
                    
            except Exception as e:
                print(f"Error al procesar movimiento: {e}")
                break
        
        # Cerrar la conexión
        if self.cliente_socket:
            self.cliente_socket.close()
        if self.servidor_socket:
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
            
            # Crear una copia del tablero visible para enviar al cliente
            tablero_para_cliente = []
            for fila in self.tablero_visible:
                tablero_para_cliente.append(fila.copy())
            
            respuesta = {
                "tipo": "control",
                "estado": "mina_pisada",
                "mensaje": "¡Has pisado una mina! Juego terminado.",
                "tablero": tablero_para_cliente
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