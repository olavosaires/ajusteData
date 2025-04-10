import tkinter as tk
from tkinter import ttk
import csv
import datetime
import threading

# === CONFIGURATION ===
file_a_path = 'file_a.csv'
file_b_path = 'file_b.csv'
log_path = 'update_audit_log.csv'
delimiter = ';'
code_column_a = 'codcli'
date_column_a = 'data'
code_column_b = 'cod'
date_column_b = 'datacorreta'


def process_file():
    # Step 1: Load corrections from file_b into a dictionary.
    code_date_map = {}
    with open(file_b_path, newline='', encoding='utf-8') as b_file:
        reader_b = csv.DictReader(b_file, delimiter=delimiter)
        for row in reader_b:
            code = row[code_column_b].strip()
            date = row[date_column_b].strip()
            if code:
                code_date_map[code] = date

    # Step 2: Count total data rows in file_a (exclude header).
    with open(file_a_path, 'rb') as f:
        total_lines = sum(1 for _ in f) - 1  # minus header
    progress_bar['maximum'] = total_lines

    log_entries = []
    processed = 0  # processed data rows count

    # Step 3: In-place update file_a:
    with open(file_a_path, 'r+b') as a_file:
        header_line = a_file.readline()
        header = header_line.decode('utf-8').strip().split(delimiter)
        try:
            code_idx = header.index(code_column_a)
            date_idx = header.index(date_column_a)
        except ValueError as e:
            print(f"❌ Column not found in file A: {e}")
            status_label.config(text=f"Error: {e}")
            return

        # Remember current file position after header.
        pos = a_file.tell()
        line_num = 2  # starting from the second line

        while True:
            line_start_pos = pos
            line_bytes = a_file.readline()
            if not line_bytes:
                break  # EOF reached
            pos = a_file.tell()
            line_str = line_bytes.decode('utf-8', errors='ignore').rstrip('\r\n')
            parts = line_str.split(delimiter)
            if len(parts) <= max(code_idx, date_idx):
                line_num += 1
                processed += 1
                if processed % 100 == 0:
                    progress_bar['value'] = processed
                    root.update_idletasks()
                continue

            code = parts[code_idx].strip()
            old_date = parts[date_idx].strip()

            if code in code_date_map:
                new_date = code_date_map[code]
                if old_date != new_date:
                    if len(old_date) == len(new_date):
                        # Replace the date in the line.
                        parts[date_idx] = new_date
                        new_line = delimiter.join(parts) + '\n'
                        new_line_bytes = new_line.encode('utf-8')
                        # If the new line is shorter than the original, pad with spaces.
                        if len(new_line_bytes) < len(line_bytes):
                            padding = b' ' * (len(line_bytes) - len(new_line_bytes))
                            new_line_bytes += padding
                        # Seek back to the beginning of the line and overwrite.
                        a_file.seek(line_start_pos)
                        a_file.write(new_line_bytes)
                        # Move the pointer back to our previously recorded position.
                        a_file.seek(pos)
                        log_entries.append({
                            'line_number': line_num,
                            'code': code,
                            'old_date': old_date,
                            'new_date': new_date,
                            'timestamp': datetime.datetime.now().isoformat()
                        })
                        print(f"✔ Line {line_num}: code {code} — {old_date} → {new_date}")
                    else:
                        print(f"⚠️ Skipped line {line_num}: new date length differs")
            line_num += 1
            processed += 1
            # Update the progress bar every 100 lines.
            if processed % 100 == 0:
                progress_bar['value'] = processed
                root.update_idletasks()

    # Write the audit log.
    # if log_entries:
    #     with open(log_path, 'w', newline='', encoding='utf-8') as log_file:
    #         fieldnames = ['line_number', 'code', 'old_date', 'new_date', 'timestamp']
    #         writer = csv.DictWriter(log_file, fieldnames=fieldnames, delimiter=delimiter)
    #         writer.writeheader()
    #         writer.writerows(log_entries)
    #     print(f"\n📝 Audit log written to {log_path}")
    # else:
    #     print("\nℹ️ No changes were made.")

    # Finalize progress and status.
    progress_bar['value'] = total_lines
    status_label.config(text="Completed")


# --- Tkinter GUI setup ---
root = tk.Tk()
root.title("In-Place CSV Update Progress")

# Create a progress bar widget.
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)

# A status label to show messages.
status_label = tk.Label(root, text="Processing...")
status_label.pack()

# Run the processing function in a separate thread to keep the GUI responsive.
threading.Thread(target=process_file, daemon=True).start()

root.mainloop()