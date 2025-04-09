import csv
import os
import tkinter as tk
from tkinter import filedialog

CHUNK_SIZE = 1000  # Number of rows to process at once

# Prompt user for column names and delimiter
code_column_a = 'codcli'
date_column_a = 'data'
code_column_b = 'cod'
correct_date_column_b = 'datacorreta'

delimiter_a = ';'
delimiter_b = ';'

def selecionar_arquivo_prompt(window_title="Selecionar arquivo para abrir", starting_folder=None):
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

# Encontrar filepath dos arquivos
file_b_path = selecionar_arquivo_prompt(window_title='Selecionar CSV referência')
file_a_path = selecionar_arquivo_prompt(window_title='Selecionar CSV DADCAD')

# Load file B into memory
code_date_map = {}
with open(file_b_path, newline='', encoding='utf-8-sig') as b_file:
    reader = csv.reader(b_file, delimiter=delimiter_b)
    header_b = [h.strip() for h in next(reader)]
    try:
        code_idx_b = header_b.index(code_column_b)
        date_idx_b = header_b.index(correct_date_column_b)
    except ValueError:
        print(f"❌ Column not found in file B: {header_b}")
        exit(1)

    for row in reader:
        if len(row) <= max(code_idx_b, date_idx_b):
            continue
        code = row[code_idx_b].strip()
        correct_date = row[date_idx_b].strip()
        code_date_map[code] = correct_date

# Count rows in file A (excluding header)
with open(file_a_path, newline='', encoding='utf-8-sig') as a_file:
    total_rows = sum(1 for _ in a_file) - 1  # subtract header
print(f"\n📊 file_a.csv contains {total_rows:,} data rows.\n")

# Process file A in chunks
with open(file_a_path, newline='', encoding='utf-8-sig') as a_file, \
     open('updated_file.csv', 'w', newline='', encoding='utf-8-sig') as output_file:

    reader = csv.reader(a_file, delimiter=delimiter_a)
    writer = csv.writer(output_file, delimiter=delimiter_a)

    header_a = [h.strip() for h in next(reader)]
    writer.writerow(header_a)

    try:
        code_idx_a = header_a.index(code_column_a)
        date_idx_a = header_a.index(date_column_a)
    except ValueError:
        print(f"❌ Column not found in file A: {header_a}")
        exit(1)

    line_number = 2  # Because header is line 1
    buffer = []
    chunk_count = 1

    for row in reader:
        if len(row) <= max(code_idx_a, date_idx_a):
            line_number += 1
            continue  # skip malformed lines

        code = row[code_idx_a].strip()
        old_date = row[date_idx_a].strip()

        if code in code_date_map:
            new_date = code_date_map[code]
            if old_date != new_date:
                print(f"Line {line_number}: code {code} — {old_date} → {new_date}")
                row[date_idx_a] = new_date

        buffer.append(row)

        # Write buffer when full
        if len(buffer) >= CHUNK_SIZE:
            writer.writerows(buffer)
            print(f"🧩 Processed chunk {chunk_count} ({CHUNK_SIZE} rows)")
            buffer = []

        line_number += 1
        chunk_count += 1

    # Write any remaining rows
    if buffer:
        writer.writerows(buffer)

print("\n✅ file_a.csv has been updated and saved as updated_file.csv")
