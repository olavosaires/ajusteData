import csv
import os
import tkinter as tk
from tkinter import filedialog


def selecionar_arquivo_prompt(window_title="Selecionar arquivo para abrir)", starting_folder=None):
    # Retorna filepath do arquivo indicado
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    initial_dir = starting_folder or os.getcwd()

    file_path = filedialog.askopenfilename(
        title=window_title,
        initialdir=initial_dir,
        filetypes=[("Arquivos CSV", "*.csv")]
    )

    if file_path:
        print(f"Arquivo selecionado: {file_path}")
        return file_path
    else:
        print("Nenhum arquivo selecionado")
        return None

# Constantes
csv_delimiter = ';'

code_column_a = 'codcli'
date_column_a = 'data'
code_column_b = 'cod'
correct_date_column_b = 'datacorreta'

# Encontrar filepath dos arquivos
file_b_path = selecionar_arquivo_prompt(window_title='Selecionar CSV referência')
file_a_path = selecionar_arquivo_prompt(window_title='Selecionar CSV DADCAD')

# Leitura e gravação dos dados corretos da planilha B
code_date_map = {}
with open(file_b_path, newline='', encoding='utf-8-sig') as b_file:
    reader = csv.reader(b_file, delimiter=csv_delimiter)
    header_b = next(reader)
    print(f"Headers do arquivo ref.: {header_b}")
    code_idx_b = header_b.index(code_column_b)
    date_idx_b = header_b.index(correct_date_column_b)

    for row in reader:
        code = row[code_idx_b]
        correct_date = row[date_idx_b]
        code_date_map[code] = correct_date

# Ler e atualizar arquivo A
updated_rows = []
with open(file_a_path, newline='', encoding='utf-8-sig') as a_file:
    reader = csv.reader(a_file, delimiter=csv_delimiter)
    header_a = next(reader)
    print(f"Headers do arquivo dadcad.: {header_a}")
    code_idx_a = header_a.index(code_column_a)
    date_idx_a = header_a.index(date_column_a)
    updated_rows.append(header_a)

    for line_number, row in enumerate(reader, start=2):  # start=2 because of header
        code = row[code_idx_a]
        old_date = row[date_idx_a]
        if code in code_date_map:
            new_date = code_date_map[code]
            if old_date != new_date:
                print(f"Linha {line_number}: código {code} — {old_date} → {new_date}")
                row[date_idx_a] = new_date
        updated_rows.append(row)

# Write the updated data to a new file
with open('updated_file.csv', 'w', newline='', encoding='utf-8') as output_file:
    writer = csv.writer(output_file, delimiter=';')
    writer.writerows(updated_rows)

print(f"✅ f{file_a_path} foi atualizado e salvo como updated_file.csv")