# Leemos los datos de entrada
n, a, b, c = map(int, input().split())
 
# Inicializamos dp con un valor muy bajo (-inf) porque queremos el máximo
dp = [-4001] * (n + 1)
dp[0] = 0  # Con longitud 0, el máximo número de piezas es 0
 
# Recorremos cada longitud desde 1 hasta n
for i in range(1, n + 1):
    # Intentamos cortar de tamaño a
    if i >= a:
        dp[i] = max(dp[i], dp[i - a] + 1)
    # Intentamos cortar de tamaño b
    if i >= b:
        dp[i] = max(dp[i], dp[i - b] + 1)
    # Intentamos cortar de tamaño c
    if i >= c:
        dp[i] = max(dp[i], dp[i - c] + 1)
 
# Imprimimos el máximo número de piezas para longitud n
print(dp[n])