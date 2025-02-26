import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

class ExcelDataValidator:
    def __init__(self, master):
        self.master = master
        self.master.title("Excel Data Validator")
        
        self.file1 = None
        self.file2 = None
        
        self.label = tk.Label(master, text="Upload Excel Files for Validation")
        self.label.pack(pady=10)
        
        self.upload_button1 = tk.Button(master, text="Upload File 1", command=self.upload_file1)
        self.upload_button1.pack(pady=5)

        self.upload_button2 = tk.Button(master, text="Upload File 2", command=self.upload_file2)
        self.upload_button2.pack(pady=5)

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

    def upload_file2(self):
        self.file2 = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        print(f"File 2 selected: {self.file2}")

    def validate_data(self):
        if not self.file1 or not self.file2:
            messagebox.showerror("Error", "Please upload both Excel files.")
            return
        
        try:
            start_date = datetime.strptime(self.start_date_entry.get(), "%d-%m-%Y")
            end_date = datetime.strptime(self.end_date_entry.get(), "%d-%m-%Y")
        except Exception:
            messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.")
            return
        
        df1 = pd.read_excel(self.file1)
        df2 = pd.read_excel(self.file2)

        # Check row counts
        inconsistent_rows = df1.shape[0] != df2.shape[0]

        # Check for 'Submitted On' column existence
        for column in ['Submitted On']:
            if column not in df1.columns or column not in df2.columns:
                messagebox.showerror("Error", f"Column '{column}' is missing in one of the files.")
                return
        
        df1['Submitted On'] = pd.to_datetime(df1['Submitted On'], errors='coerce')
        df2['Submitted On'] = pd.to_datetime(df2['Submitted On'], errors='coerce')

        # Filter data by the specified date range
        valid_df1 = df1[(df1['Submitted On'] >= start_date) & (df1['Submitted On'] <= end_date)]
        valid_df2 = df2[(df2['Submitted On'] >= start_date) & (df2['Submitted On'] <= end_date)]

        # Check for missing data, excluding certain columns under specific conditions
        def count_missing_data(df):
            count = df.isnull().sum()
            if 'Status' in df.columns:
                count.loc['Reason'] = count['Reason'] if not (df['Status'] == 'Not Completed').any() else 0
                count.loc['Reason Detail'] = count['Reason Detail'] if not (df['Status'] == 'Not Completed').any() else 0
            count.loc['Remarks'] = 0  # Exclude 'Remarks' column entirely
            return count

        missing_data_df1 = count_missing_data(valid_df1)
        missing_data_df2 = count_missing_data(valid_df2)

        # Prepare an inconsistencies summary
        inconsistencies_list = []
        detailed_inconsistencies = pd.DataFrame()  # DataFrame to store detailed inconsistencies

        for column in valid_df1.columns:
            if column in valid_df2.columns:
                if (missing_data_df1[column] > 0 or missing_data_df2[column] > 0) :
                    inconsistencies_list.append({
                        "Column": column,
                        "File 1 Missing": missing_data_df1[column],
                        "File 2 Missing": missing_data_df2[column],
                        "Row Count Mismatch": inconsistent_rows
                    })

                    # Add detailed data for the rows with inconsistencies
                    detail_df1 = valid_df1[valid_df1[column].isnull()]
                    detail_df2 = valid_df2[valid_df2[column].isnull()]

                    # Add the column name and source file to the details
                    detail_df1['Source File'] = 'File 1'
                    detail_df2['Source File'] = 'File 2'

                    # Combine the detailed information
                    detailed_inconsistencies = pd.concat([detailed_inconsistencies, detail_df1, detail_df2], ignore_index=True)

        # Create DataFrame from the inconsistencies summary list
        inconsistencies_df = pd.DataFrame(inconsistencies_list)

        # Generate CSV report for summary and detailed data
        summary_file = 'InconsistenciesReport.xlsx'
        with pd.ExcelWriter(summary_file) as writer:
            inconsistencies_df.to_excel(writer, sheet_name='Summary', index=False)
            detailed_inconsistencies.to_excel(writer, sheet_name='Details', index=False)

        # Count total rows without inconsistencies
        total_rows_file1 = valid_df1.shape[0]
        total_rows_file2 = valid_df2.shape[0]

        # Show the result in a message box
        result_message = f"Row Count Mismatch: {inconsistent_rows}\n\n" \
                         f"Missing Data in File 1:\n{missing_data_df1[missing_data_df1 > 0].to_dict()}\n\n" \
                         f"Missing Data in File 2:\n{missing_data_df2[missing_data_df2 > 0].to_dict()}\n\n" \
                         f"Total rows in File 1: {total_rows_file1}\n" \
                         f"Total rows in File 2: {total_rows_file2}\n" 

        if inconsistencies_df.empty:
            result_message += "No missing data found across the specified columns.\n"
        else:
            result_message += "\n Inconsistencies found.\n Please check 'InconsistenciesReport.xlsx' for details."

        # Show message box with results
        messagebox.showinfo("Validation Result", result_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelDataValidator(root)
    root.mainloop()