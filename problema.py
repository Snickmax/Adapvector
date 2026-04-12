numeroNinos, tiempos = map(int, input().split())
fila = list(input())

for tiempo in range(tiempos):
    
    posicionNino = 0  # comienza desde el primer niño
    while posicionNino < numeroNinos - 1:  # recorre hasta el penúltimo niño
        
        # si es un niño 'B' y el siguiente es una niña 'G', los intercambia
        if fila[posicionNino] == 'B' and  fila[posicionNino + 1] == 'G':
            # intercambia los niños
            fila[posicionNino], fila[posicionNino + 1] = fila[posicionNino + 1], fila[posicionNino]
            
            # avanza la posición del niño porque ya no puede moverse (por cada tiempo un niño puede moverse una vez)
            posicionNino += 1 # simula el salto del niño
        # avanza a la siguiente posición
        posicionNino += 1

print(''.join(fila))  # imprime la fila final de niños y niñas