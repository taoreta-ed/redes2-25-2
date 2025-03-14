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
        self.buffer = ""  # Buffer para almacenar datos recibidos
        self.procesar_multiples_respuestas = False  # Flag para controlar el procesamiento de múltiples respuestas

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
        try:
            mensaje = self.recibir_mensaje()
            
            if mensaje["tipo"] == "configuracion":
                self.dificultad = mensaje["dificultad"]
                self.filas = mensaje["filas"]
                self.columnas = mensaje["columnas"]
                
                # Inicializar el tablero vacío
                self.tablero = [['□' for _ in range(self.columnas)] for _ in range(self.filas)]
                
                print(f"Juego configurado con dificultad: {self.dificultad}")
                print(f"Tablero de {self.filas}x{self.columnas}")
                return True
            else:
                print("Error: No se recibió configuración inicial")
                return False
        except Exception as e:
            print(f"Error al recibir configuración: {e}")
            return False

    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al servidor en formato JSON"""
        try:
            mensaje_json = json.dumps(mensaje)
            self.cliente_socket.sendall(mensaje_json.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            return False

    def recibir_mensaje(self):
        """Recibe un mensaje del servidor en formato JSON"""
        try:
            # Si el buffer ya tiene un mensaje completo, extraerlo
            if '\n' in self.buffer:
                mensaje_json, self.buffer = self.buffer.split('\n', 1)
                return json.loads(mensaje_json)
            
            # Si no hay mensaje completo, recibir más datos
            while '\n' not in self.buffer:
                datos = self.cliente_socket.recv(4096).decode('utf-8')
                if not datos:
                    raise Exception("Conexión cerrada por el servidor")
                self.buffer += datos
            
            # Extraer un mensaje completo
            mensaje_json, self.buffer = self.buffer.split('\n', 1)
            return json.loads(mensaje_json)
                
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print(f"Datos recibidos: {self.buffer}")
            self.buffer = ""  # Limpiar buffer en caso de error
            raise
        except Exception as e:
            print(f"Error al recibir mensaje: {e}")
            raise

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
                
                if not self.enviar_mensaje(coordenada):
                    print("Error al enviar coordenadas. Cerrando conexión.")
                    self.desconectar()
                    break
                
                # Procesar respuesta del servidor
                self.procesar_multiples_respuestas = True
                while self.procesar_multiples_respuestas:
                    if not self.procesar_respuesta():
                        break
                
            except ValueError:
                print("Entrada inválida. Ingrese un número.")
                continue
            except KeyboardInterrupt:
                print("\nJuego interrumpido por el usuario.")
                self.desconectar()
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                self.desconectar()
                break
        
        # Si el juego termina normalmente
        if self.juego_terminado:
            input("\nPresione Enter para salir...")
        
        self.desconectar()

    def procesar_respuesta(self):
        """Procesa la respuesta del servidor"""
        try:
            mensaje = self.recibir_mensaje()
            
            if mensaje["tipo"] == "control":
                if mensaje["estado"] == "casilla_ocupada":
                    print(mensaje["mensaje"])
                    time.sleep(1)
                    self.imprimir_tablero()  # Reimprimir tablero después del mensaje
                    self.procesar_multiples_respuestas = False
                    
                elif mensaje["estado"] == "casilla_libre":
                    # Actualizar casilla en el tablero local
                    valor = mensaje["valor"]
                    fila = mensaje["fila"]
                    columna = mensaje["columna"]
                    
                    # Actualizar la casilla en el tablero local
                    if valor == 0:
                        self.tablero[fila][columna] = ' '
                    else:
                        self.tablero[fila][columna] = str(valor)
                    
                    self.imprimir_tablero()
                    
                    # Solo seguir procesando respuestas para la casilla actual y sus adyacentes
                    # Si hay más mensajes en el buffer, procesarlos
                    if '\n' not in self.buffer:
                        self.procesar_multiples_respuestas = False
                    
                elif mensaje["estado"] == "mina_pisada":
                    # El jugador ha perdido, actualizar tablero con todas las minas
                    for i in range(self.filas):
                        for j in range(self.columnas):
                            if mensaje["tablero"][i][j] == '*':
                                self.tablero[i][j] = '*'
                    
                    self.imprimir_tablero()
                    print(mensaje["mensaje"])
                    self.procesar_multiples_respuestas = True  # Para procesar el mensaje de fin
                    
            elif mensaje["tipo"] == "fin":
                # Juego terminado
                self.juego_terminado = True
                self.procesar_multiples_respuestas = False
                
                if mensaje["resultado"] == "victoria":
                    print("¡FELICIDADES! ¡Has ganado!")
                else:
                    print("¡BOOM! Has perdido.")
                    
                print(f"Duración del juego: {mensaje['duracion']} segundos")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error al procesar respuesta: {e}")
            self.procesar_multiples_respuestas = False
            return False

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