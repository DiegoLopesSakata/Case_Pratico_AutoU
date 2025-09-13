from file_reader import read_file
from classifier import classify_email

texto = "Feliz Natal para todos da equipe!"
resultado = classify_email(texto)
print("Resultado:", resultado)
