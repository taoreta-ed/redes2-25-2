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


## Implementación del Cliente

### Funcionalidades del Cliente

- Conexión con el servidor
- Visualización del tablero de juego
- Envío de coordenadas al servidor
- Interpretación de los mensajes del servidor y actualización del tablero local
- Notificación del resultado final al jugador


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
