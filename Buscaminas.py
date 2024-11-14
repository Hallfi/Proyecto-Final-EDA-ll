import random
import time
from collections import deque
from colorama import init, Fore, Style
import re
from datetime import datetime

# Inicializar colorama
init(autoreset=True)

# Niveles de dificultad
NIVELES = {
    '1': {'filas': 10, 'columnas': 10, 'minas': 10, 'nombre': 'Fácil'},
    '2': {'filas': 16, 'columnas': 16, 'minas': 40, 'nombre': 'Medio'},
    '3': {'filas': 16, 'columnas': 30, 'minas': 99, 'nombre': 'Difícil'}
}

# Símbolos para representar el tablero
CELDA_OCULTA = '#'
CELDA_MINA = '*'
CELDA_MARCA = '!'
CELDA_VACIA = ' '

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def mostrar_tutorial():
    """Muestra las reglas y un tutorial de cómo jugar."""
    print(Fore.CYAN + "=== BIENVENIDO AL BUSCA MINAS ===\n")
    print("Reglas del juego:")
    print("1. El objetivo es descubrir todas las celdas que no contienen minas.")
    print("2. Si descubres una celda con una mina, pierdes el juego.")
    print("3. Cada número en una celda indica cuántas minas hay en las celdas adyacentes.")
    print("4. Puedes marcar celdas que crees que contienen minas para ayudarte.")
    print("\nCómo jugar:")
    print("- Para descubrir una celda, ingresa las coordenadas en el formato 'fila columna'. Por ejemplo: '3 5'.")
    print("- Para marcar o desmarcar una celda como posible mina, ingresa 'm fila columna'. Por ejemplo: 'm 3 5'.")
    print("- Las filas y columnas comienzan desde 0.")
    print("- ¡Buena suerte!\n")
    input("Presiona Enter para continuar...")

def seleccionar_nivel():
    """Solicita al jugador que seleccione un nivel de dificultad."""
    print("Seleccione un nivel de dificultad:")
    print("1. Fácil (10x10 con 10 minas)")
    print("2. Medio (16x16 con 40 minas)")
    print("3. Difícil (16x30 con 99 minas)")
    while True:
        nivel = input("Ingrese 1, 2 o 3: ")
        if nivel in NIVELES:
            return NIVELES[nivel]
        else:
            print("Entrada inválida. Por favor, ingrese 1, 2 o 3.")

def crear_tablero(filas, columnas):
    """Crea el tablero de juego."""
    tablero = [[{'mina': False, 'adyacentes': 0, 'revelado': False, 'marcado': False} for _ in range(columnas)] for _ in range(filas)]
    return tablero

def colocar_minas(tablero, primera_fila, primera_columna, num_minas):
    """Coloca minas aleatoriamente en el tablero, evitando la primera jugada."""
    filas = len(tablero)
    columnas = len(tablero[0])
    celdas = [(f, c) for f in range(filas) for c in range(columnas) if not (f == primera_fila and c == primera_columna)]
    random.shuffle(celdas)
    for _ in range(num_minas):
        fila, columna = celdas.pop()
        tablero[fila][columna]['mina'] = True

def calcular_adyacentes(tablero):
    """Calcula el número de minas adyacentes para cada celda."""
    filas = len(tablero)
    columnas = len(tablero[0])
    for f in range(filas):
        for c in range(columnas):
            if tablero[f][c]['mina']:
                continue
            conteo = 0
            for df in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < filas and 0 <= nc < columnas and tablero[nf][nc]['mina']:
                        conteo += 1
            tablero[f][c]['adyacentes'] = conteo

def obtener_color_celda(celda_repr):
    """Devuelve el color correspondiente para una celda."""
    if celda_repr == CELDA_OCULTA:
        return Fore.WHITE + celda_repr
    elif celda_repr == CELDA_MARCA:
        return Fore.YELLOW + celda_repr
    elif celda_repr == CELDA_MINA:
        return Fore.RED + celda_repr
    elif celda_repr.isdigit():
        colores_numero = {
            '1': Fore.BLUE,
            '2': Fore.GREEN,
            '3': Fore.RED,
            '4': Fore.MAGENTA,
            '5': Fore.CYAN,
            '6': Fore.LIGHTRED_EX,
            '7': Fore.LIGHTGREEN_EX,
            '8': Fore.LIGHTBLUE_EX
        }
        return colores_numero.get(celda_repr, Fore.WHITE) + celda_repr
    else:
        return Fore.WHITE + celda_repr

def longitud_visible(cadena):
    """Calcula la longitud visible de una cadena sin contar los códigos de color."""
    cadena_sin_escape = ansi_escape.sub('', cadena)
    return len(cadena_sin_escape)

def formatear_celda(celda_repr, ancho=3):
    """Devuelve la celda formateada para ocupar un ancho fijo, incluyendo color."""
    longitud_real = longitud_visible(celda_repr)
    padding_total = ancho - longitud_real
    if padding_total <= 0:
        # El contenido es demasiado largo, lo truncamos
        return celda_repr[:ancho]
    else:
        # Centramos el contenido
        padding_izq = padding_total // 2
        padding_der = padding_total - padding_izq
        return ' ' * padding_izq + celda_repr + ' ' * padding_der

def imprimir_tablero(tablero, revelar_todo=False):
    """Imprime el tablero en la terminal con colores y alineación correcta."""
    filas = len(tablero)
    columnas = len(tablero[0])
    # Imprimir encabezado de columnas
    encabezado_columnas = "    " + "".join(formatear_celda(str(c), ancho=3) for c in range(columnas))
    print(Fore.CYAN + encabezado_columnas)
    for f in range(filas):
        celdas_fila = []
        for c in range(columnas):
            celda = tablero[f][c]
            if celda['revelado'] or (revelar_todo and celda['mina']):
                if celda['mina']:
                    celda_repr = CELDA_MINA
                elif celda['adyacentes'] > 0:
                    celda_repr = str(celda['adyacentes'])
                else:
                    celda_repr = CELDA_VACIA
            elif celda['marcado']:
                celda_repr = CELDA_MARCA
            else:
                celda_repr = CELDA_OCULTA
            celda_coloreada = obtener_color_celda(celda_repr)
            celdas_fila.append(celda_coloreada)
        # Alineación de las celdas
        celdas_formateadas = [formatear_celda(celda, ancho=3) for celda in celdas_fila]
        fila_imprimible = f"{f:2}  " + "".join(celdas_formateadas)
        print(Fore.CYAN + fila_imprimible)

def revelar_celdas(tablero, fila_inicial, columna_inicial):
    """Algoritmo BFS para revelar celdas vacías."""
    filas = len(tablero)
    columnas = len(tablero[0])
    cola = deque()
    cola.append((fila_inicial, columna_inicial))
    visitados = set()
    while cola:
        f, c = cola.popleft()
        if (f, c) in visitados:
            continue
        visitados.add((f, c))
        celda = tablero[f][c]
        if celda['marcado'] or celda['revelado']:
            continue
        celda['revelado'] = True
        if celda['adyacentes'] == 0:
            for df in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    nf, nc = f + df, c + dc
                    if 0 <= nf < filas and 0 <= nc < columnas and (nf, nc) not in visitados:
                        cola.append((nf, nc))
        elif celda['adyacentes'] > 0:
            celda['revelado'] = True

def verificar_victoria(tablero, total_minas):
    """Verifica si el jugador ha ganado."""
    filas = len(tablero)
    columnas = len(tablero[0])
    celdas_reveladas = sum(celda['revelado'] for fila in tablero for celda in fila)
    total_celdas = filas * columnas
    return celdas_reveladas == total_celdas - total_minas

def guardar_puntuacion(nombre_jugador, nivel, resultado, tiempo_total, puntuacion):
    """Guarda la puntuación del jugador en un archivo de texto."""
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    linea = f"{fecha_hora} | Jugador: {nombre_jugador} | Nivel: {nivel} | Resultado: {resultado} | Tiempo: {tiempo_total}s | Puntuación: {puntuacion}\n"
    with open("PUNTUACIONES BUSCAMINAS.txt", "a", encoding='utf-8') as archivo:
        archivo.write(linea)

def calcular_puntuacion(resultado, tiempo_total, nivel):
    """Calcula la puntuación del jugador."""
    if resultado == 'Victoria':
        base_puntuacion = 1000
        factor_nivel = {'Fácil': 1, 'Medio': 2, 'Difícil': 3}
        puntuacion = base_puntuacion * factor_nivel[nivel] - tiempo_total * 10
        return max(puntuacion, 0)
    else:
        return 0

def jugar():
    """Función principal para jugar."""
    mostrar_tutorial()
    print("¡Bienvenido al Busca Minas!")
    nombre_jugador = input("Por favor, ingrese su nombre: ")
    nivel_info = seleccionar_nivel()
    filas, columnas, minas = nivel_info['filas'], nivel_info['columnas'], nivel_info['minas']
    nombre_nivel = nivel_info['nombre']
    tablero = crear_tablero(filas, columnas)
    primera_jugada = True
    inicio_tiempo = time.time()

    while True:
        imprimir_tablero(tablero)
        accion = input("Ingrese su acción (formato: 'fila columna' para descubrir, 'm fila columna' para marcar/desmarcar): ")
        partes = accion.strip().split()
        if len(partes) == 2:
            try:
                fila, columna = int(partes[0]), int(partes[1])
                marcar = False
            except ValueError:
                print("Entrada inválida. Por favor, intente de nuevo.")
                continue
        elif len(partes) == 3 and partes[0].lower() == 'm':
            try:
                fila, columna = int(partes[1]), int(partes[2])
                marcar = True
            except ValueError:
                print("Entrada inválida. Por favor, intente de nuevo.")
                continue
        else:
            print("Entrada inválida. Por favor, intente de nuevo.")
            continue

        if not (0 <= fila < filas and 0 <= columna < columnas):
            print("Coordenadas fuera de los límites. Por favor, intente de nuevo.")
            continue

        celda = tablero[fila][columna]

        if marcar:
            if celda['revelado']:
                print("No puede marcar una celda ya revelada.")
                continue
            celda['marcado'] = not celda['marcado']
            continue

        if celda['marcado']:
            print("Esta celda está marcada como mina. Desmarque antes de descubrir.")
            continue

        if celda['revelado']:
            print("Esta celda ya ha sido revelada.")
            continue

        if primera_jugada:
            colocar_minas(tablero, fila, columna, minas)
            calcular_adyacentes(tablero)
            primera_jugada = False

        if celda['mina']:
            celda['revelado'] = True
            imprimir_tablero(tablero, revelar_todo=True)
            tiempo_total = int(time.time() - inicio_tiempo)
            puntuacion = calcular_puntuacion('Derrota', tiempo_total, nombre_nivel)
            print(Fore.RED + "¡Perdiste! Has descubierto una mina.")
            print(f"Tiempo total de juego: {tiempo_total} segundos.")
            print(f"Puntuación obtenida: {puntuacion}")
            guardar_puntuacion(nombre_jugador, nombre_nivel, 'Derrota', tiempo_total, puntuacion)
            break

        if celda['adyacentes'] > 0:
            celda['revelado'] = True
        else:
            revelar_celdas(tablero, fila, columna)

        if verificar_victoria(tablero, minas):
            imprimir_tablero(tablero, revelar_todo=True)
            tiempo_total = int(time.time() - inicio_tiempo)
            puntuacion = calcular_puntuacion('Victoria', tiempo_total, nombre_nivel)
            print(Fore.GREEN + "¡Felicidades! ¡Has ganado!")
            print(f"Tiempo total de juego: {tiempo_total} segundos.")
            print(f"Puntuación obtenida: {puntuacion}")
            guardar_puntuacion(nombre_jugador, nombre_nivel, 'Victoria', tiempo_total, puntuacion)
            break

if __name__ == "__main__":
    jugar()
