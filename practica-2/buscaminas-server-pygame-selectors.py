import socket
import random
import time
import json
import pygame
import sys
import selectors

class BuscaminasServidorPygame:
    def __init__(self):
        self.tablero = []
        self.tablero_visible = []  # Lo que el cliente puede ver
        self.filas = 0
        self.columnas = 0
        self.minas = 0
        self.banderas = []
        self.casillas_destapadas = 0
        self.tiempo_inicio = 0
        self.tiempo_fin = 0
        self.servidor_socket = None
        self.cliente_socket = None
        self.dificultad = ""
        self.ip = ""
        self.puerto = 0
        self.juego_terminado = False
        self.cliente_conectado = False
        
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
            "mina": (0, 0, 0)
        }
        
        # Estado del juego
        self.mensaje_estado = "Esperando conexión..."
        self.tiempo_transcurrido = 0
        
        # Selector para manejar los sockets
        self.selector = selectors.DefaultSelector()
        
        # Buffer para recibir datos
        self.buffer_recepcion = ""

    def inicializar_pygame(self):
        """Inicializa Pygame y configura la pantalla"""
        pygame.init()
        self.ancho_pantalla = self.columnas * self.tamano_celda + 20
        self.alto_pantalla = self.filas * self.tamano_celda + 100  # Espacio extra para mensajes
        self.pantalla = pygame.display.set_mode((self.ancho_pantalla, self.alto_pantalla))
        pygame.display.set_caption(f"Buscaminas Servidor - {self.dificultad}")
        self.fuente = pygame.font.SysFont("Arial", 18)
        self.fuente_grande = pygame.font.SysFont("Arial", 24, bold=True)

    def configurar_servidor(self):
        """Configura los parámetros del servidor y la dificultad del juego utilizando Pygame"""
        pygame.init()
        pantalla_config = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("Configurar Servidor Buscaminas")
        
        fuente = pygame.font.SysFont("Arial", 18)
        
        ip_input = "localhost"
        puerto_input = "12345"
        input_activo = "ip"
        dificultad_seleccionada = "principiante"
        
        while True:
            pantalla_config.fill((240, 240, 240))
            
            # Dibujar campos de entrada
            pygame.draw.rect(pantalla_config, (255, 255, 255), (100, 50, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 50, 200, 30), 1)
            
            pygame.draw.rect(pantalla_config, (255, 255, 255), (100, 100, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 100, 200, 30), 1)
            
            # Opciones de dificultad
            pygame.draw.rect(pantalla_config, (200, 230, 200) if dificultad_seleccionada == "principiante" else (255, 255, 255), 
                            (100, 150, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 150, 200, 30), 1)
            
            pygame.draw.rect(pantalla_config, (200, 230, 200) if dificultad_seleccionada == "avanzado" else (255, 255, 255), 
                            (100, 190, 200, 30))
            pygame.draw.rect(pantalla_config, (0, 0, 0), (100, 190, 200, 30), 1)
            
            # Resaltar campo activo
            if input_activo == "ip":
                pygame.draw.rect(pantalla_config, (200, 200, 255), (100, 50, 200, 30), 3)
            elif input_activo == "puerto":
                pygame.draw.rect(pantalla_config, (200, 200, 255), (100, 100, 200, 30), 3)
            
            # Dibujar textos
            texto_ip = fuente.render(f"IP: {ip_input}", True, (0, 0, 0))
            texto_puerto = fuente.render(f"Puerto: {puerto_input}", True, (0, 0, 0))
            texto_principiante = fuente.render("Principiante (9x9, 10 minas)", True, (0, 0, 0))
            texto_avanzado = fuente.render("Avanzado (16x16, 40 minas)", True, (0, 0, 0))
            texto_iniciar = fuente.render("Presiona ENTER para iniciar servidor", True, (0, 0, 0))
            
            pantalla_config.blit(texto_ip, (110, 55))
            pantalla_config.blit(texto_puerto, (110, 105))
            pantalla_config.blit(texto_principiante, (110, 155))
            pantalla_config.blit(texto_avanzado, (110, 195))
            pantalla_config.blit(texto_iniciar, (80, 240))
            
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
                        elif 150 <= y <= 180:
                            dificultad_seleccionada = "principiante"
                        elif 190 <= y <= 220:
                            dificultad_seleccionada = "avanzado"
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_TAB:
                        if input_activo == "ip":
                            input_activo = "puerto"
                        else:
                            input_activo = "ip"
                    elif evento.key == pygame.K_RETURN:
                        try:
                            self.ip = ip_input
                            self.puerto = int(puerto_input)
                            self.dificultad = dificultad_seleccionada
                            
                            # Configurar tamaño de tablero según dificultad
                            if self.dificultad == "principiante":
                                self.filas = 9
                                self.columnas = 9
                                self.minas = 10
                            else:
                                self.filas = 16
                                self.columnas = 16
                                self.minas = 40
                            
                            # Inicializar Pygame con el tamaño correcto
                            self.inicializar_pygame()
                            
                            # Generar tablero
                            self.generar_tablero()
                            
                            # Iniciar servidor usando selectores
                            self.iniciar_servidor()
                            
                            return True
                        except Exception as e:
                            mensaje_error = f"Error: {e}"
                            texto_error = fuente.render(mensaje_error, True, (255, 0, 0))
                            pantalla_config.blit(texto_error, (50, 270))
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

    def iniciar_servidor(self):
        """Inicia el servidor usando selectores"""
        try:
            self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.servidor_socket.bind((self.ip, self.puerto))
            self.servidor_socket.listen(1)
            
            # Configurar el socket como no bloqueante
            self.servidor_socket.setblocking(False)
            
            # Registrar socket con el selector para aceptar conexiones
            self.selector.register(self.servidor_socket, selectors.EVENT_READ, self.aceptar_conexion)
            
            self.mensaje_estado = f"Servidor iniciado en {self.ip}:{self.puerto}"
            self.mensaje_estado += "\nEsperando conexión del cliente..."
            
        except Exception as e:
            self.mensaje_estado = f"Error al iniciar servidor: {e}"
            if self.servidor_socket:
                self.servidor_socket.close()
    
    def aceptar_conexion(self, socket_servidor, mascara):
        """Callback para aceptar una nueva conexión"""
        cliente_socket, direccion = socket_servidor.accept()
        cliente_socket.setblocking(False)
        
        self.cliente_socket = cliente_socket
        self.cliente_conectado = True
        self.mensaje_estado = f"Cliente conectado desde {direccion[0]}:{direccion[1]}"
        
        # Registrar cliente para eventos de lectura
        self.selector.register(cliente_socket, selectors.EVENT_READ, self.recibir_datos)
        
        # Enviar confirmación y dificultad al cliente
        mensaje_inicial = {
            "tipo": "configuracion", 
            "dificultad": self.dificultad, 
            "filas": self.filas, 
            "columnas": self.columnas,
            "minas": self.minas
        }
        self.enviar_mensaje(mensaje_inicial)
        
        # Iniciar el tiempo de juego
        self.tiempo_inicio = time.time()
    
    def recibir_datos(self, socket_cliente, mascara):
        """Callback para manejar datos recibidos del cliente"""
        try:
            datos = socket_cliente.recv(4096).decode('utf-8')
            
            if not datos:
                # Conexión cerrada por el cliente
                self.desconectar_cliente(socket_cliente)
                return
            
            # Agregar datos al buffer
            self.buffer_recepcion += datos
            
            # Procesar mensajes completos
            while '\n' in self.buffer_recepcion:
                # Extraer un mensaje completo
                mensaje_texto, self.buffer_recepcion = self.buffer_recepcion.split('\n', 1)
                
                # Procesar el mensaje
                self.procesar_mensaje(mensaje_texto)
                
        except Exception as e:
            self.mensaje_estado = f"Error al recibir datos: {e}"
            self.desconectar_cliente(socket_cliente)
    
    def desconectar_cliente(self, socket_cliente):
        """Maneja la desconexión de un cliente"""
        self.selector.unregister(socket_cliente)
        socket_cliente.close()
        self.cliente_conectado = False
        self.mensaje_estado = "Cliente desconectado"
    
    def procesar_mensaje(self, mensaje_texto):
        """Procesa un mensaje completo recibido del cliente"""
        try:
            mensaje = json.loads(mensaje_texto)
            
            if mensaje["tipo"] == "coordenada":
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                
                # Verificar si la casilla ya está destapada
                if self.tablero_visible[fila][columna] != '□':
                    respuesta = {
                        "tipo": "control",
                        "estado": "casilla_ocupada",
                        "mensaje": "Esta casilla ya está destapada"
                    }
                    self.enviar_mensaje(respuesta)
                else:
                    # Verificar si hay mina
                    if self.tablero[fila][columna] == '*':
                        # Juego perdido
                        self.tablero_visible[fila][columna] = '*'
                        self.juego_terminado = True
                        
                        # Revelar todas las minas
                        for i in range(self.filas):
                            for j in range(self.columnas):
                                if self.tablero[i][j] == '*':
                                    self.tablero_visible[i][j] = '*'
                        
                        # Enviar tablero actualizado
                        respuesta = {
                            "tipo": "control",
                            "estado": "mina_pisada",
                            "mensaje": "¡BOOM! Has perdido.",
                            "tablero": self.tablero_visible
                        }
                        self.enviar_mensaje(respuesta)
                        
                        # Enviar mensaje de fin de juego
                        self.tiempo_fin = time.time()
                        duracion = round(self.tiempo_fin - self.tiempo_inicio)
                        
                        fin_juego = {
                            "tipo": "fin",
                            "resultado": "derrota",
                            "duracion": duracion
                        }
                        self.enviar_mensaje(fin_juego)
                        
                    else:
                        # Revelar casilla
                        valor = self.tablero[fila][columna]
                        self.tablero_visible[fila][columna] = valor
                        
                        respuesta = {
                            "tipo": "control",
                            "estado": "casilla_libre",
                            "valor": valor,
                            "fila": fila,
                            "columna": columna
                        }
                        self.enviar_mensaje(respuesta)
                        
                        # Si es un 0, descubrir casillas adyacentes
                        if valor == 0:
                            self.revelar_adyacentes(fila, columna)
                        
                        # Incrementar contador de casillas destapadas
                        self.casillas_destapadas += 1
                        
                        # Verificar victoria
                        if self.casillas_destapadas == (self.filas * self.columnas - self.minas):
                            self.juego_terminado = True
                            
                            # Enviar mensaje de victoria
                            self.tiempo_fin = time.time()
                            duracion = round(self.tiempo_fin - self.tiempo_inicio)
                            
                            fin_juego = {
                                "tipo": "fin",
                                "resultado": "victoria",
                                "duracion": duracion
                            }
                            self.enviar_mensaje(fin_juego)
            
            elif mensaje["tipo"] == "bandera":
                fila = mensaje["fila"]
                columna = mensaje["columna"]
                accion = mensaje["accion"]
                
                # Verificar que las coordenadas estén dentro del rango
                if not (0 <= fila < self.filas and 0 <= columna < self.columnas):
                    return
                # Verificar que la casilla no esté descubierta
                if self.tablero_visible[fila][columna] != '□':
                    return

                if accion == "colocar" and not self.banderas[fila][columna]:
                    self.banderas[fila][columna] = True
                    respuesta = {
                        "tipo": "control",
                        "estado": "bandera_colocada",
                        "fila": fila,
                        "columna": columna
                    }
                    self.enviar_mensaje(respuesta)
                elif accion == "retirar" and self.banderas[fila][columna]:
                    self.banderas[fila][columna] = False
                    respuesta = {
                        "tipo": "control",
                        "estado": "bandera_retirada",
                        "fila": fila,
                        "columna": columna
                    }
                    self.enviar_mensaje(respuesta)

            elif mensaje["tipo"] == "desconexion":
                if self.cliente_socket:
                    self.desconectar_cliente(self.cliente_socket)
                
        except json.JSONDecodeError:
            self.mensaje_estado = "Error al decodificar mensaje JSON"
        except Exception as e:
            self.mensaje_estado = f"Error al procesar mensaje: {e}"

    def generar_tablero(self):
        """Genera el tablero con las minas colocadas aleatoriamente"""
        # Inicializar tablero vacío
        self.tablero = [[0 for _ in range(self.columnas)] for _ in range(self.filas)]
        self.tablero_visible = [['□' for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Colocar minas aleatoriamente
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            fila = random.randint(0, self.filas - 1)
            columna = random.randint(0, self.columnas - 1)
            
            if self.tablero[fila][columna] != '*':
                self.tablero[fila][columna] = '*'
                minas_colocadas += 1

        # Inicializar la matriz de banderas con False
        self.banderas = [[False for _ in range(self.columnas)] for _ in range(self.filas)]
        
        # Calcular números adyacentes a minas
        for i in range(self.filas):
            for j in range(self.columnas):
                if self.tablero[i][j] != '*':
                    # Contar minas adyacentes
                    minas_adyacentes = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            
                            ni, nj = i + di, j + dj
                            if 0 <= ni < self.filas and 0 <= nj < self.columnas:
                                if self.tablero[ni][nj] == '*':
                                    minas_adyacentes += 1
                    
                    self.tablero[i][j] = minas_adyacentes

    def enviar_mensaje(self, mensaje):
        """Envía un mensaje al cliente en formato JSON"""
        try:
            if self.cliente_socket and self.cliente_conectado:
                mensaje_json = json.dumps(mensaje) + '\n'  # Añadir delimitador
                self.cliente_socket.sendall(mensaje_json.encode('utf-8'))
                return True
            return False
        except Exception as e:
            self.mensaje_estado = f"Error al enviar mensaje: {e}"
            if self.cliente_socket:
                self.desconectar_cliente(self.cliente_socket)
            return False

    def revelar_adyacentes(self, fila, columna):
        """Revela casillas adyacentes cuando se descubre un 0"""
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = fila + di, columna + dj
                
                # Verificar que está dentro del tablero
                if 0 <= ni < self.filas and 0 <= nj < self.columnas:
                    # Verificar que no esté ya destapada
                    if self.tablero_visible[ni][nj] == '□':
                        valor = self.tablero[ni][nj]
                        
                        # No revelar minas por este método
                        if valor != '*':
                            self.tablero_visible[ni][nj] = valor
                            self.casillas_destapadas += 1
                            
                            # Enviar actualización al cliente
                            respuesta = {
                                "tipo": "control",
                                "estado": "casilla_libre",
                                "valor": valor,
                                "fila": ni,
                                "columna": nj
                            }
                            self.enviar_mensaje(respuesta)
                            
                            # Si también es un 0, continuar recursivamente
                            if valor == 0:
                                self.revelar_adyacentes(ni, nj)

    def check_eventos_red(self):
        """Comprueba eventos de red pendientes"""
        # Verificar eventos de socket con timeout de 0 para no bloquear
        eventos = self.selector.select(timeout=0)
        for key, mascara in eventos:
            callback = key.data
            callback(key.fileobj, mascara)

    def ejecutar(self):
        """Método principal para ejecutar el juego"""
        if self.configurar_servidor():
            # Bucle principal del juego
            reloj = pygame.time.Clock()
            ejecutando = True
            
            while ejecutando:
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        ejecutando = False
                
                # Comprobar eventos de red
                self.check_eventos_red()
                
                # Actualizar pantalla
                self.pantalla.fill(self.colores["fondo"])
                
                # Dibujar tablero
                for fila in range(self.filas):
                    for col in range(self.columnas):
                        x = col * self.tamano_celda + 10
                        y = fila * self.tamano_celda + 10
                        
                        # Dibujar celda según estado
                        if self.tablero_visible[fila][col] == '□':
                            pygame.draw.rect(self.pantalla, self.colores["celda"], 
                                            (x, y, self.tamano_celda, self.tamano_celda))
                            
                            # Mostrar banderas si hay
                            if self.banderas[fila][col]:
                                # Dibujar bandera (triángulo rojo)
                                pygame.draw.polygon(self.pantalla, (255, 0, 0), [
                                    (x + self.tamano_celda // 4, y + self.tamano_celda // 4),
                                    (x + self.tamano_celda // 4, y + self.tamano_celda * 3 // 4),
                                    (x + self.tamano_celda * 3 // 4, y + self.tamano_celda // 2)
                                ])
                        else:
                            pygame.draw.rect(self.pantalla, self.colores["celda_visible"], 
                                            (x, y, self.tamano_celda, self.tamano_celda))
                            
                            # Dibujar contenido
                            if self.tablero_visible[fila][col] == '*':
                                # Mina
                                pygame.draw.circle(self.pantalla, self.colores["mina"], 
                                                  (x + self.tamano_celda // 2, y + self.tamano_celda // 2), 
                                                  self.tamano_celda // 3)
                            elif self.tablero_visible[fila][col] != 0:
                                # Número
                                valor = self.tablero_visible[fila][col]
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
                self.pantalla.blit(texto_estado, (10, self.alto_pantalla - 60))
                
                # Mostrar tiempo de juego
                if self.tiempo_inicio > 0 and not self.juego_terminado and self.cliente_conectado:
                    self.tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
                    texto_tiempo = self.fuente.render(f"Tiempo: {self.tiempo_transcurrido} segundos", True, (0, 0, 0))
                    self.pantalla.blit(texto_tiempo, (10, self.alto_pantalla - 30))
                elif self.juego_terminado:
                    duracion = int(self.tiempo_fin - self.tiempo_inicio)
                    texto_tiempo = self.fuente.render(f"Tiempo final: {duracion} segundos", True, (0, 0, 0))
                    self.pantalla.blit(texto_tiempo, (10, self.alto_pantalla - 30))
                
                # Actualizar pantalla
                pygame.display.flip()
                reloj.tick(30)
            
            # Cerrar todos los sockets y el selector al salir
            if self.cliente_socket:
                try:
                    self.selector.unregister(self.cliente_socket)
                except ValueError:
                    # Socket might already be unregistered or closed
                    pass
                self.cliente_socket.close()
            
            if self.servidor_socket:
                try:
                    self.selector.unregister(self.servidor_socket)
                except ValueError:
                    # Socket might already be unregistered or closed
                    pass
                self.servidor_socket.close()
                
            self.selector.close()
            pygame.quit()

# Código para ejecutar el servidor
if __name__ == "__main__":
    servidor = BuscaminasServidorPygame()
    servidor.ejecutar()