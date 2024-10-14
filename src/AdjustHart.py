import numpy as np
from scipy.optimize import curve_fit

# Função de Steinhart-Hart


def steinhart_hart(R, A, B, C):
    return 1 / (A + B * np.ln(R) + C * np.ln(R)**3)


# Solicitar ao user os valores de resistências e temperaturas
n = int(input("Quantos pontos de calibração? "))

resistances = []
temperatures_C = []

for i in range(n):
    R = float(input(f"Introduza a resistência {i+1} em ohms: "))
    T = float(input(f"Introduza a temperatura {i+1} em °C: "))
    resistances.append(R)
    temperatures_C.append(T)

# Converter listas para arrays NumPy
resistances = np.array(resistances)
temperatures_C = np.array(temperatures_C)

# Converter temperaturas de Celsius para Kelvin
temperatures_K = temperatures_C + 273.15

# Ajuste dos coeficientes A, B e C usando a curva de Steinhart-Hart
popt, _ = curve_fit(steinhart_hart, resistances, 1 / temperatures_K)

# Coeficientes A, B e C
A, B, C = popt
print(f"\nCoeficiente A: {A}")
print(f"Coeficiente B: {B}")
print(f"Coeficiente C: {C}")
