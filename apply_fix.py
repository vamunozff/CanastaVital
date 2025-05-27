"""
Script para aplicar la corrección a la función registrar_direccion en views.py
"""
import re
import os

# Ruta al archivo views.py
views_path = os.path.join('myapp', 'views.py')

# Ruta al archivo con la función corregida
fix_path = os.path.join('myapp', 'registrar_direccion_fix.py')

# Leer la función corregida
with open(fix_path, 'r', encoding='utf-8') as file:
    # Saltar las primeras líneas de comentario
    lines = file.readlines()
    start_line = 0
    for i, line in enumerate(lines):
        if '@login_required' in line:
            start_line = i
            break
    
    # Obtener la función corregida
    fixed_function = ''.join(lines[start_line:])

# Leer el contenido del archivo views.py
with open(views_path, 'r', encoding='utf-8') as file:
    content = file.read()

# Patrón para encontrar la función registrar_direccion
pattern = r'@login_required\s+def registrar_direccion\(request\):.*?return render\(request, \'otros/direccion.html\', \{\'form\': form\}\)'

# Reemplazar la función
new_content = re.sub(pattern, fixed_function, content, flags=re.DOTALL)

# Escribir el contenido actualizado
with open(views_path, 'w', encoding='utf-8') as file:
    file.write(new_content)

print("La función registrar_direccion ha sido actualizada correctamente.")