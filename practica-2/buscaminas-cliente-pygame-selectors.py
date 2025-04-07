import socket
import json
import os
import sys
import time
import pygame
import selectors  # Importamos el módulo selectors en lugar de threading

class BuscaminasClientePygame:
    def __init__(self):
        self.tablero = []
        self.banderas = []  # Nueva matriz para almacenar las banderas
        self.filas = 0
        self.columnas = 0
        self.cliente_socket = None
        self.ip_servidor = ""
        self.puerto_servidor = 0
        self.juego_terminado = False
        self.dificultad = ""
        self.buffer = ""  # Buffer para almacenar datos recibidos
        self.procesar_multiples_respuestas = False  # Flag para controlar el procesamiento de múltiples respuestas
        
        # Variables de Pygame
        self.tamano_celda = 40
        self.ancho_pantalla = 0
        self.alto_pantalla = 0
        self.pantalla = None
        self.fuente = None
        self.fuente_grande = None
        
        # Colores
        self.colores = {
            "fondo": (220, 220, 220),
            "celda": (180, 180, 180),
            "celda_visible": (200, 200, 200),
            "grid": (120, 120, 120),
            "texto": {
                0: (0, 0, 0),      # Vacío
                1: (0, 0, 255),    # Azul
                2: (0, 128, 0),    # Verde
                3: (255, 0, 0),    # Rojo
                4: (0, 0, 128),    # Azul oscuro
                5: (128, 0, 0),    # Marrón
                6: (0, 128, 128),  # Cian
                7: (0, 0, 0),      # Negro
                8: (128, 128, 128) # Gris
            },
            "mina": (0, 0, 0),
            "bandera": (255, 0, 0)  # Color para las banderas (rojo)
        }
        
        # Estado del juego
        self.mensaje_estado = "Conectando al servidor..."
        self.celda_seleccionada = None
        self.tiempo_transcurrido = 0
        self.tiempo_inicio = 0
        self.resultado_juego = None
        self.duracion_final = 0
        self.banderas_colocadas = 0  # Contador de banderas colocadas
        
        # Selector para E/S no bloqueante (reemplaza threads)
        self.selector = selectors.DefaultSelector()

    def inicializar_pygame(self):
        """Inicializa Pygame y configura la pantalla"""
        self.ancho_pantalla = self.columnas * self.tamano_celda + 20
        self.alto_pantalla = self.filas * self.tamano_celda + 100  # Espacio extra para mensajes
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption(f"Buscaminas Cliente - {self.dificultad}")
        self.fuente = pygame.font.SysFont("Arial", 18)
        self.fuente_grande = pygame.font.SysFont("Arial", 24, bold=True)

    def configurar_conexion(self):
        """Configura la conexión al servidor utilizando Pygame"""
        pygame.init()
        pantalla_config = pygame.display.set_mode((400, 200))
        pygame.display.set_caption("Conectar a Servidor Buscaminas")
        
        fuente = pygame.font.SysFont("Arial", 18)
        
        ip_input = "localhost"
        puerto_input = "12345"
        input_activo = "ip"
        
        while True:
            pantalla_config.fill((240, 240, 240))
            
            # Dibujar campos de entrada
            pygame.draw.rect(pantalla_config, (255, 255, 255), (100, 50, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 50, 200, 30), 1)
            
            pygame.draw.rect(pantalla_config, (255, 255, 255), (100, 100, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 100, 200, 30), 1)
            
            # Resaltar campo activo
            if input_activo == "ip":
                pygame.draw.rect(pantalla_config, (200, 200, 255), (100, 50, 200, 30), 3)
            elif input_activo == "puerto":
                pygame.draw.rect(pantalla_config, (200, 200, 255), (100, 100, 200, 30), 3)
            
            # Dibujar textos
            texto_ip = fuente.render(f"IP: {ip_input}", True, (0, 0, 0))
            texto_puerto = fuente.render(f"Puerto: {puerto_input}", True, (0, 0, 0))
            texto_iniciar = fuente.render("Presiona ENTER para conectar", True, (0, 0, 0))
            
            pantalla_config.blit(texto_ip, (110, 55))
            pantalla_config.blit(texto_puerto, (110, 105))
            pantalla_config.blit(texto_iniciar, (100, 150))
            
            pygame.display.flip()
            
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif evento.type == pygame.MOUSEBUTTONDOWN:
                    # Verificar clicks en opciones
                    x, y = evento.pos
                    if 100 <= x <= 300:
                        if 50 <= y <= 80:
                            input_activo = "ip"
                        elif 100 <= y <= 130:
                            input_activo = "puerto"
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_TAB:
                        if input_activo == "ip":
                            input_activo = "puerto"
                        else:
                            input_activo = "ip"
                    elif evento.key == pygame.K_RETURN:
                        try:
                            self.ip_servidor = ip_input
                            self.puerto_servidor = int(puerto_input)
                            
                            # Mostrar mensaje mientras se conecta
                            mensaje_conectando = fuente.render("Conectando...", True, (0, 100, 0))
                            pantalla_config.blit(mensaje_conectando, (150, 180))
                            pygame.display.flip()
                            
                            # Conectar directamente (sin hilo)
                            self.conectar_servidor()
                            
                            # Verificar si la conexión fue exitosa
                            if self.filas > 0 and self.columnas > 0:
                                # Si tenemos filas y columnas, la configuración se recibió correctamente
                                return True
                            else:
                                # Mostrar mensaje de error si no se recibió configuración
                                mensaje_error = "Error en la conexión"
                                texto_error = fuente.render(mensaje_error, True, (255, 0, 0))
                                pantalla_config.blit(texto_error, (130, 180))
                                pygame.display.flip()
                                pygame.time.wait(2000)  # Mostrar error por 2 segundos
                                
                        except Exception as e:
                            mensaje_error = f"Error: {e}"
                            texto_error = fuente.render(mensaje_error, True, (255, 0, 0))
                            pantalla_config.blit(texto_error, (50, 180))
                            pygame.display.flip()
                            pygame.time.wait(2000)  # Mostrar error por 2 segundos
                    elif evento.key == pygame.K_BACKSPACE:
                        if input_activo == "ip":
                            ip_input = ip_input[:-1]
                        elif input_activo == "puerto":
                            puerto_input = puerto_input[:-1]
                    else:
                        if input_activo == "ip":
                            if evento.unicode in "0123456789.":
                                ip_input += evento.unicode
                        elif input_activo == "puerto":
                            if evento.unicode in "0123456789":
                                puerto_input += evento.unicode

    def conectar_servidor(self):
        """Establece la conexión con el servidor"""
        try:
            self.cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cliente_socket.connect((self.ip_servidor, self.puerto_servidor))
            self.mensaje_estado = f"Conectado al servidor {self.ip_servidor}:{self.puerto_servidor}"
            
            # Recibir configuración inicial
            if self.recibir_configuracion():
                self.tiempo_inicio = time.time()
                
                # Configurar socket como no bloqueante
                self.cliente_socket.setblocking(False)
                
                # Registrar socket en el selector para leer datos cuando estén disponibles
                self.selector.register(self.cliente_socket, selectors.EVENT_READ, self.procesar_mensaje)
                
                return True
            else:
                if self.cliente_socket:
                    self.cliente_socket.close()
                return False
            
        except Exception as e:
            self.mensaje_estado = f"Error al conectar con el servidor: {e}"
            return False

    def recibir_configuracion(self):
        """Recibe la configuración inicial del juego"""
        try:
            # Establecer un timeout para evitar bloqueo infinito
            self.cliente_socket.settimeout(5.0)
            
            # Recibir datos hasta encontrar un carácter de nueva línea
            buffer = ""
            while '\n' not in buffer:
                chunk = self.cliente_socket.recv(4096).decode('utf-8')
                if not chunk:
                    raise Exception("Conexión cerrada por el servidor")
                buffer += chunk
            
            # Restaurar el comportamiento de bloqueo para luego cambiarlo a no bloqueante
            self.cliente_socket.settimeout(None)
            
            # Extraer el mensaje completo y guardar el resto en el buffer
            mensaje_json, resto = buffer.split('\n', 1)
            self.buffer = resto
            
            mensaje = json.loads(mensaje_json)
            
            if mensaje["tipo"] == "configuracion":
                self.dificultad = mensaje["dificultad"]
                self.filas = mensaje["filas"]
                self.columnas = mensaje["columnas"]
                self.minas = mensaje["minas"]
                
                # Inicializar el tablero vacío
                self.tablero = [['□' for _ in range(self.columnas)] for _ in range(self.filas)]
                # Inicializar la matriz de banderas
                self.banderas = [[False for _ in range(self.columnas)] for _ in range(self.filas)]
                
                # Inicializar Pygame con el tamaño correcto
                self.inicializar_pygame()
                
                self.mensaje_estado = f"Juego configurado con dificultad: {self.dificultad}"
                return True
            else:
                self.mensaje_estado = "Error: No se recibió configuración inicial"
                return False
        except socket.timeout:
            self.mensaje_estado = "Tiempo de espera agotado al conectar al servidor"
            return False
        except Exception as e:
            self.mensaje_estado = f"Error al recibir configuración: {e}"
            return False

    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al servidor en formato JSON"""
        try:
            mensaje_json = json.dumps(mensaje)
            self.cliente_socket.sendall((mensaje_json + '\n').encode('utf-8'))
            return True
        except Exception as e:
            self.mensaje_estado = f"Error al enviar mensaje: {e}"
            return False

    # Método de callback para el selector
    def procesar_mensaje(self, sock, mask):
        """Procesa mensajes entrantes del servidor cuando están disponibles"""
        try:
            # Leer datos disponibles
            datos = sock.recv(4096).decode('utf-8')
            if not datos:
                # Si no hay datos, el servidor cerró la conexión
                self.mensaje_estado = "Conexión cerrada por el servidor"
                self.selector.unregister(sock)
                sock.close()
                return
            
            # Añadir datos al buffer
            self.buffer += datos
            
            # Procesar todos los mensajes completos en el buffer
            while '\n' in self.buffer:
                # Extraer un mensaje completo
                mensaje_json, self.buffer = self.buffer.split('\n', 1)
                
                try:
                    mensaje = json.loads(mensaje_json)
                    self.manejar_mensaje(mensaje)
                except json.JSONDecodeError as e:
                    self.mensaje_estado = f"Error al decodificar JSON: {e}"
                    
        except Exception as e:
            self.mensaje_estado = f"Error al recibir datos: {e}"
            self.selector.unregister(sock)
            sock.close()
    
    def manejar_mensaje(self, mensaje):
        """Maneja un mensaje recibido del servidor"""
        if mensaje["tipo"] == "control":
            if mensaje["estado"] == "casilla_ocupada":
                self.mensaje_estado = mensaje["mensaje"]
                
            elif mensaje["estado"] == "casilla_libre":
                # Actualizar casilla en el tablero local
                valor = mensaje["valor"]
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                
                # Asegurarse de que no hay una bandera en esa posición
                self.banderas[fila][columna] = False
                
                # Actualizar la casilla en el tablero local
                if valor == 0:
                    self.tablero[fila][columna] = ' '
                else:
                    self.tablero[fila][columna] = str(valor)
                    
            elif mensaje["estado"] == "mina_pisada":
                # El jugador ha perdido, actualizar tablero con todas las minas
                for i in range(self.filas):
                    for j in range(self.columnas):
                        if mensaje["tablero"][i][j] == '*':
                            self.tablero[i][j] = '*'
                
                self.mensaje_estado = mensaje["mensaje"]
                
            elif mensaje["estado"] == "bandera_colocada":
                # Actualizar estado de la bandera en el tablero local
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                self.banderas[fila][columna] = True
                self.banderas_colocadas += 1
                
            elif mensaje["estado"] == "bandera_retirada":
                # Actualizar estado de la bandera en el tablero local
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                self.banderas[fila][columna] = False
                self.banderas_colocadas -= 1
                
        elif mensaje["tipo"] == "fin":
            # Juego terminado
            self.juego_terminado = True
            self.resultado_juego = mensaje["resultado"]
            self.duracion_final = mensaje["duracion"]
            
            if mensaje["resultado"] == "victoria":
                self.mensaje_estado = "¡FELICIDADES! ¡Has ganado!"
            else:
                self.mensaje_estado = "¡BOOM! Has perdido."
            
            self.mensaje_estado += f" Duración: {mensaje['duracion']} segundos"

    def enviar_coordenada(self, fila, columna):
        """Envía una coordenada al servidor"""
        # Validar que las coordenadas estén dentro del tablero
        if fila < 0 or fila >= self.filas or columna < 0 or columna >= self.columnas:
            self.mensaje_estado = "Coordenadas fuera del tablero."
            return False
        
        # Validar que la casilla no esté ya destapada
        if self.tablero[fila][columna] != '□':
            self.mensaje_estado = "Esta casilla ya está destapada."
            return False
        
        # Validar que no haya una bandera en la casilla
        if self.banderas[fila][columna]:
            self.mensaje_estado = "No puedes destapar una casilla con bandera."
            return False
        
        # Enviar coordenadas al servidor
        coordenada = {
            "tipo": "coordenada",
            "fila": fila,
            "columna": columna
        }
        
        return self.enviar_mensaje(coordenada)

    def alternar_bandera(self, fila, columna):
        """Alterna la colocación/retirada de una bandera"""
        # Validar que las coordenadas estén dentro del tablero
        if fila < 0 or fila >= self.filas or columna < 0 or columna >= self.columnas:
            self.mensaje_estado = "Coordenadas fuera del tablero."
            return False
        
        # Validar que la casilla no esté ya destapada
        if self.tablero[fila][columna] != '□':
            self.mensaje_estado = "No puedes poner una bandera en una casilla destapada."
            return False
        
        # Crear mensaje según el estado actual de la bandera
        if not self.banderas[fila][columna]:
            # Colocar bandera
            bandera = {
                "tipo": "bandera",
                "accion": "colocar",
                "fila": fila,
                "columna": columna
            }
        else:
            # Retirar bandera
            bandera = {
                "tipo": "bandera",
                "accion": "retirar",
                "fila": fila,
                "columna": columna
            }
        
        return self.enviar_mensaje(bandera)

    def ejecutar(self):
        """Método principal para ejecutar el cliente"""
        if self.configurar_conexion():
            # Esperar a que se inicialice el tablero
            espera_inicio = 0
            while self.filas == 0 or self.columnas == 0:
                pygame.time.wait(100)
                espera_inicio += 1
                if espera_inicio > 50:  # 5 segundos máximo de espera
                    self.mensaje_estado = "Tiempo de espera agotado. No se recibió configuración del servidor."
                    pygame.quit()
                    return
            
            # Bucle principal del juego
            reloj = pygame.time.Clock()
            ejecutando = True
            
            instrucciones_mostradas = True
            tiempo_instrucciones = pygame.time.get_ticks()
            
            while ejecutando:
                # Procesar eventos de Pygame
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        ejecutando = False
                        break
                    
                    # Procesar clicks solo si el juego está en curso
                    elif not self.juego_terminado and self.cliente_socket:
                        if evento.type == pygame.MOUSEBUTTONDOWN:
                            # Ignorar clicks con botón de rueda/scroll (botón 2)
                            if evento.button != 2:
                                x, y = evento.pos
                                
                                # Verificar si el click es dentro del tablero
                                if (10 <= x < 10 + self.columnas * self.tamano_celda and 
                                    10 <= y < 10 + self.filas * self.tamano_celda):
                                    
                                    # Calcular fila y columna de la celda clickeada
                                    col = (x - 10) // self.tamano_celda
                                    fila = (y - 10) // self.tamano_celda
                                    
                                    # Botón izquierdo: destapar celda
                                    if evento.button == 1:
                                        self.enviar_coordenada(fila, col)
                                    # Botón derecho: colocar/quitar bandera
                                    elif evento.button == 3:
                                        self.alternar_bandera(fila, col)
                
                # Verificar mensajes del servidor solo si hay conexión activa
                if self.cliente_socket:
                    try:
                        # Intentar procesar eventos del selector con manejo de errores
                        eventos = self.selector.select(0)  # Timeout de 0 para que no bloquee
                        for key, mask in eventos:
                            callback = key.data
                            callback(key.fileobj, mask)
                    except (OSError, ValueError, Exception) as e:
                        # Manejar cualquier error con el socket o selector
                        self.mensaje_estado = f"Error de conexión: {str(e)}"
                        self.desconectar()  # Desconectar limpiamente
                
                # Actualizar pantalla
                self.pantalla.fill(self.colores["fondo"])
                
                # Mostrar instrucciones por 5 segundos al inicio
                if instrucciones_mostradas and pygame.time.get_ticks() - tiempo_instrucciones < 5000:
                    texto_instrucciones = [
                        "¡Bienvenido a Buscaminas!",
                        "Instrucciones:",
                        "- Botón izquierdo: Destapar casilla",
                        "- Botón derecho: Colocar/quitar bandera",
                        "- Evita las minas",
                        "- Los números indican minas adyacentes"
                    ]
                    
                    for i, linea in enumerate(texto_instrucciones):
                        texto = self.fuente.render(linea, True, (0, 0, 0))
                        self.pantalla.blit(texto, (self.ancho_pantalla // 2 - texto.get_width() // 2, 
                                                20 + i * 20))
                else:
                    instrucciones_mostradas = False
                    
                    # Dibujar tablero
                    for fila in range(self.filas):
                        for col in range(self.columnas):
                            x = col * self.tamano_celda + 10
                            y = fila * self.tamano_celda + 10
                            
                            # Dibujar celda según estado
                            if self.tablero[fila][col] == '□':
                                pygame.draw.rect(self.pantalla, self.colores["celda"], 
                                                (x, y, self.tamano_celda, self.tamano_celda))
                                
                                # Dibujar bandera si existe
                                if self.banderas[fila][col]:
                                    # Dibujar un triángulo rojo como bandera
                                    puntos = [
                                        (x + self.tamano_celda // 2, y + self.tamano_celda // 4),
                                        (x + self.tamano_celda * 3 // 4, y + self.tamano_celda // 2),
                                        (x + self.tamano_celda // 2, y + self.tamano_celda * 3 // 4)
                                    ]
                                    pygame.draw.polygon(self.pantalla, self.colores["bandera"], puntos)
                                    
                                    # Mástil de la bandera
                                    pygame.draw.line(self.pantalla, (0, 0, 0), 
                                                (x + self.tamano_celda // 2, y + self.tamano_celda // 4),
                                                (x + self.tamano_celda // 2, y + self.tamano_celda * 3 // 4),
                                                2)
                            else:
                                pygame.draw.rect(self.pantalla, self.colores["celda_visible"], 
                                                (x, y, self.tamano_celda, self.tamano_celda))
                                
                                # Dibujar contenido
                                if self.tablero[fila][col] == '*':
                                    # Mina
                                    pygame.draw.circle(self.pantalla, self.colores["mina"], 
                                                    (x + self.tamano_celda // 2, y + self.tamano_celda // 2), 
                                                    self.tamano_celda // 3)
                                elif self.tablero[fila][col] != ' ':
                                    # Número
                                    valor = int(self.tablero[fila][col])
                                    texto = self.fuente_grande.render(str(valor), True, 
                                                                self.colores["texto"][valor])
                                    self.pantalla.blit(texto, 
                                                    (x + self.tamano_celda // 2 - texto.get_width() // 2, 
                                                    y + self.tamano_celda // 2 - texto.get_height() // 2))
                            
                            # Dibujar borde
                            pygame.draw.rect(self.pantalla, self.colores["grid"], 
                                            (x, y, self.tamano_celda, self.tamano_celda), 1)
                
                # Mostrar estado
                texto_estado = self.fuente.render(self.mensaje_estado, True, (0, 0, 0))
                self.pantalla.blit(texto_estado, (10, self.alto_pantalla - 80))
                
                # Mostrar contador de banderas
                if self.minas > 0:  # Asumiendo que el servidor envía el número de minas
                    texto_banderas = self.fuente.render(f"Banderas: {self.banderas_colocadas}", True, (0, 0, 0))
                    self.pantalla.blit(texto_banderas, (10, self.alto_pantalla - 55))
                
                # Mostrar tiempo de juego
                if self.tiempo_inicio > 0 and not self.juego_terminado:
                    self.tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
                    texto_tiempo = self.fuente.render(f"Tiempo: {self.tiempo_transcurrido} segundos", True, (0, 0, 0))
                    self.pantalla.blit(texto_tiempo, (10, self.alto_pantalla - 30))
                elif self.juego_terminado:
                    texto_tiempo = self.fuente.render(f"Tiempo final: {self.duracion_final} segundos", True, (0, 0, 0))
                    self.pantalla.blit(texto_tiempo, (10, self.alto_pantalla - 30))
                
                # Actualizar pantalla
                pygame.display.flip()
                reloj.tick(30)
            
            # Desconectar limpiamente antes de salir
            self.desconectar()
            pygame.quit()

    def desconectar(self):
        """Cierra la conexión con el servidor"""
        if self.cliente_socket:
            try:
                # Enviar mensaje de desconexión si es posible
                try:
                    desconexion = {"tipo": "desconexion"}
                    self.enviar_mensaje(desconexion)
                except:
                    pass
                
                # Deregistrar el socket del selector
                try:
                    self.selector.unregister(self.cliente_socket)
                except:
                    pass
                
                # Cerrar el socket
                try:
                    self.cliente_socket.close()
                except:
                    pass
                
                # Marcar el socket como None para evitar intentar usarlo nuevamente
                self.cliente_socket = None
                self.mensaje_estado = "Desconectado del servidor"
            except Exception as e:
                print(f"Error al desconectar: {e}")

# Código principal para ejecutar el cliente
if __name__ == "__main__":
    cliente = BuscaminasClientePygame()
    cliente.ejecutar()