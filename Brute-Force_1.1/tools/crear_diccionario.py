import re

with open('cadenas.txt', 'r', encoding='utf-8', errors='ignore') as f_in, \
     open('diccionario_memoria.txt', 'w', encoding='utf-8') as f_out:
    for line in f_in:
        pwd = line.strip()
        if 8 <= len(pwd) <= 16 and re.match(r'^[A-Za-z0-9!@#$%^&*()_+=-]+$', pwd):
            if any(c.isdigit() for c in pwd) and any(c.isalpha() for c in pwd):
                f_out.write(pwd + "\n")
