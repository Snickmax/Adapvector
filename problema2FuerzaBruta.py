# Leemos los datos de entrada: longitud total y los tamaños de los cortes posibles
longitud_total, corte_a, corte_b, corte_c = map(int, input("Ingrese: longitud_total corte_a corte_b corte_c: ").split())

# Variable para guardar el mayor número de piezas posibles
maximo_num_piezas = 0

# Recorremos todas las combinaciones posibles de piezas de tamaño 'corte_a'
for cantidad_a in range(longitud_total // corte_a + 1):
    
    # Para cada combinación de piezas de 'corte_a', probamos distintas cantidades de piezas de 'corte_b'
    for cantidad_b in range(longitud_total // corte_b + 1):
        
        # Calculamos la longitud restante después de usar piezas de 'corte_a' y 'corte_b'
        longitud_restante = longitud_total - (cantidad_a * corte_a + cantidad_b * corte_b)
        
        # Verificamos si podemos llenar el restante con piezas de 'corte_c'
        if longitud_restante >= 0 and longitud_restante % corte_c == 0:
            
            # Calculamos cuántas piezas de 'corte_c' necesitamos
            cantidad_c = longitud_restante // corte_c
            
            # Calculamos el total de piezas usadas en esta combinación
            total_piezas = cantidad_a + cantidad_b + cantidad_c
            
            # Actualizamos el máximo si esta combinación usa más piezas
            if total_piezas > maximo_num_piezas:
                maximo_num_piezas = total_piezas

# Mostramos el resultado final: el mayor número de piezas que se puede obtener
print(f"El máximo número de piezas posibles es: {maximo_num_piezas}")
