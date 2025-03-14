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