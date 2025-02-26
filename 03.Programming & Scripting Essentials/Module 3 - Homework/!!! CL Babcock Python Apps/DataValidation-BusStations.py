import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import os

class ExcelDataValidator:
    def __init__(self, master):
        self.master = master
        self.master.title("Excel Data Validator")
        
        self.file1 = None
        self.file2 = None
        
        # String variables for displaying the dates
        self.start_date_file1_value = tk.StringVar()
        self.end_date_file1_value = tk.StringVar()
        self.start_date_file2_value = tk.StringVar()
        self.end_date_file2_value = tk.StringVar()
        
        self.label = tk.Label(master, text="Upload Excel Files for Validation")
        self.label.pack(pady=10)
        
        self.upload_button1 = tk.Button(master, text="Upload File 1", command=self.upload_file1)
        self.upload_button1.pack(pady=5)

        self.upload_button2 = tk.Button(master, text="Upload File 2", command=self.upload_file2)
        self.upload_button2.pack(pady=5)

        # Labels to display dates for both files
        self.start_date_display_file1 = tk.Label(master, textvariable=self.start_date_file1_value)
        self.start_date_display_file1.pack(pady=5)

        self.end_date_display_file1 = tk.Label(master, textvariable=self.end_date_file1_value)
        self.end_date_display_file1.pack(pady=5)

        self.start_date_display_file2 = tk.Label(master, textvariable=self.start_date_file2_value)
        self.start_date_display_file2.pack(pady=5)

        self.end_date_display_file2 = tk.Label(master, textvariable=self.end_date_file2_value)
        self.end_date_display_file2.pack(pady=5)

        self.start_date_label = tk.Label(master, text="Enter Start Date (DD-MM-YYYY):")
        self.start_date_label.pack(pady=5)
        
        self.start_date_entry = tk.Entry(master)
        self.start_date_entry.pack(pady=5)

        self.end_date_label = tk.Label(master, text="Enter End Date (DD-MM-YYYY):")
        self.end_date_label.pack(pady=5)
        
        self.end_date_entry = tk.Entry(master)
        self.end_date_entry.pack(pady=5)

        self.start_button = tk.Button(master, text="Validate Data", command=self.validate_data)
        self.start_button.pack(pady=20)

    def upload_file1(self):
        self.file1 = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        print(f"File 1 selected: {self.file1}")
        self.update_date_labels(self.file1, self.start_date_file1_value, self.end_date_file1_value)

    def upload_file2(self):
        self.file2 = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        print(f"File 2 selected: {self.file2}")
        self.update_date_labels(self.file2, self.start_date_file2_value, self.end_date_file2_value)

    def update_date_labels(self, file, start_date_var, end_date_var):
        # Only extract the file name for the currently processed file
        if file:
            df = pd.read_excel(file)
            if 'Submitted On' in df.columns:
                # Attempt to parse the dates
                df['Submitted On'] = pd.to_datetime(df['Submitted On'], format='%d-%m-%Y', errors='coerce')
                min_date = df['Submitted On'].min()
                max_date = df['Submitted On'].max()

                # Check for NaT before formatting
                if pd.isna(min_date) or pd.isna(max_date):
                    start_date_var.set(f"{os.path.basename(file)}\nNo valid dates found.")
                    end_date_var.set(f"{os.path.basename(file)}\nNo valid dates found.")
                else:
                    start_date_var.set(f"{os.path.basename(file)}\nEarliest date: {min_date.strftime('%d-%m-%Y')}")
                    end_date_var.set(f"{os.path.basename(file)}\nLatest date: {max_date.strftime('%d-%m-%Y')}\n")
            else:
                start_date_var.set("Column 'Submitted On' not found.")
                end_date_var.set("Column 'Submitted On' not found.")

    def validate_data(self):
        if not self.file1 or not self.file2:
            messagebox.showerror("Error", "Please upload both Excel files.")
            return

        try:
            start_date = datetime.strptime(self.start_date_entry.get(), "%d-%m-%Y")
            end_date = datetime.strptime(self.end_date_entry.get(), "%d-%m-%Y")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.")
            return

        try:
            df1 = pd.read_excel(self.file1)
            df2 = pd.read_excel(self.file2)
        except FileNotFoundError:
            messagebox.showerror("Error", "One or both files were not found.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while reading the Excel files: {e}")
            return

        # Strip whitespace from column names
        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        # Check for 'Submitted On' column existence
        if 'Submitted On' not in df1.columns or 'Submitted On' not in df2.columns:
            messagebox.showerror("Error", "Column 'Submitted On' is missing in one of the files.")
            return

        try:
            df1['Submitted On'] = pd.to_datetime(df1['Submitted On'], errors='coerce')
            df2['Submitted On'] = pd.to_datetime(df2['Submitted On'], errors='coerce')
        except KeyError:
            messagebox.showerror("Error", "'Submitted On' column not found in one or both files.")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while converting 'Submitted On' to datetime: {e}")
            return

        # Filter data by the specified date range
        valid_df1 = df1[(df1['Submitted On'] >= start_date) & (df1['Submitted On'] <= end_date)]
        valid_df2 = df2[(df2['Submitted On'] >= start_date) & (df2['Submitted On'] <= end_date)]

        # Count total valid rows
        total_rows_file1 = valid_df1.shape[0]
        total_rows_file2 = valid_df2.shape[0]

        # Count missing values in specified columns
        columns_to_check = ['Submitted On', 'Task ID', 'Cleaning Performed', 'Bus Station', 'Area', 'Location', 'Asset', 'Status']
        
        missing_counts_file1 = {col: valid_df1[col].isnull().sum() for col in columns_to_check}
        missing_counts_file2 = {col: valid_df2[col].isnull().sum() for col in columns_to_check}

        # Prepare the results
        result_message = []
        file1_name = os.path.basename(self.file1)
        file2_name = os.path.basename(self.file2)

        # Show total rows for File 1
        result_message.append(f"Total valid rows in {file1_name}: {total_rows_file1}")
        
        # Check for missing data in File 1
        result_message.append(f"\nMissing data in {file1_name}:")
        for col in columns_to_check:
            count = missing_counts_file1[col]
            if count > 0:
                result_message.append(f" Column {col}: {count} rows (missing)")

        # Show total rows for File 2
        result_message.append(f"\n\nTotal valid rows in {file2_name}: {total_rows_file2}")

        # Check for missing data in File 2
        result_message.append(f"\nMissing data in {file2_name}:")
        for col in columns_to_check:
            count = missing_counts_file2[col]
            if count > 0:
                result_message.append(f" Column {col}: {count} rows (missing)")
        
        difference = abs(total_rows_file1 - total_rows_file2)
        
        # Save missing rows to Excel if any are found
        if {total_rows_file1} != {total_rows_file2}:
            result_message.append(f"\nRow counts do not match.\nDiffering rows are {difference}.")
        else:
            result_message.append("Row counts match.")

        # Show the message box
        messagebox.showinfo("Validation Result", "\n".join(result_message))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelDataValidator(root)
    root.mainloop()