from pseudo_Ni_simulator import NIfromUnA
from pooledage_clc4pseudoEDM import calc_pooledage4pseudoEDM
# from single_grain_age_clc4LAICPMS import calc_singleage4LAICPMS
from pooledage_clc4LAICPMS import calc_pooledage4LAICPMS
# from central_clc import central
import numpy as np
import os
# os.environ['R_HOME'] = 'C:\Program Files\R\R-4.5.0'
import pandas as pd
import matplotlib.pyplot as plt
from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
isoplotR = importr('IsoplotR')

def read_csv_files_from_folder(folder_path):
    """
    Read all CSV files from the specified folder
    Parameters:
    folder_path -- folder path
    Returns:
    dict -- dictionary containing all CSV files, keys are filenames, values are DataFrames
    """
    csv_files = {}
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder {folder_path} does not exist")
    
    # Iterate through all files in the folder
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            try:
                # Read CSV file
                df = pd.read_csv(file_path)
                csv_files[file] = df
                # print(f"✓ Successfully read file: {file}")
            except Exception as e:
                print(f"✗ Error reading file {file}: {str(e)}")
    
    return csv_files


# Create custom dropdown selection window
def select_mineral():
    """Create dropdown selection window and return selected mineral type and parameters"""
    # Create a root window
    root = tk.Tk()
    root.title("Set parameters")
    
    # Force window to stay on top, ensure it appears in front of VSCode
    root.attributes('-topmost', True)
    
    # Set window size and center it on screen
    root.geometry("220x250")  # Increase window height to accommodate new options and progress label
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    # Create result variables
    result = {
        'folder': tk.StringVar(value=os.getcwd()),  # Default current directory
        'mineral': tk.StringVar(value="apatite"),
        'zeta': tk.StringVar(value="390"),
        'rho_d': tk.StringVar(value="1.322E6"),
        'la_vs_pedm': tk.StringVar(value="yes, plot"),  # New la_vs_pedm option
        'radial_plots': tk.StringVar(value="yes")  # New Radial plots option
    }
    
    # Create main frame - reduce padding to fit small window
    main_frame = ttk.Frame(root, padding="5")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Configure columns: make the first column as narrow as possible
    main_frame.columnconfigure(0, weight=0, minsize=60)
    main_frame.columnconfigure(1, weight=1)
    
    # Folder selection function - keep label short so first column stays narrow
    tk.Label(main_frame, text="Data folder:", 
             font=("Arial", 10)).grid(row=0, column=0, pady=(3, 0), sticky="e", padx=(28, 2))
    
    folder_var = tk.StringVar(value=os.getcwd())
    
    def browse_folder():
        """Browse and select folder"""
        folder_path = filedialog.askdirectory(initialdir=os.getcwd(), title="Select data folder")
        if folder_path:
            # Verify if folder exists and contains CSV files
            if os.path.exists(folder_path):
                csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
                if csv_files:
                    folder_var.set(folder_path)
                    print(f"\033[94m✓ Selected folder: {folder_path} (contains {len(csv_files)} CSV files)\033[0m")
                    status_label.config(text=f"✓ Selected folder with {len(csv_files)} CSV files", fg="green")
                else:
                    # If no CSV files in folder, ask user if they want to continue
                    import tkinter.messagebox as messagebox
                    response = messagebox.askyesno(
                        "No CSV Files Found", 
                        f"The selected folder does not contain any CSV files.\n\nFolder: {folder_path}\n\nDo you want to continue anyway?"
                    )
                    if response:
                        folder_var.set(folder_path)
                        print(f"\033[93m⚠ Selected folder: {folder_path} (no CSV files found)\033[0m")
                        status_label.config(text="⚠ Warning: No CSV files found", fg="orange")
                    else:
                        print("\033[95m✗ Folder selection cancelled\033[0m")
                        status_label.config(text="Please select a folder with CSV files", fg="magenta", font=("Arial", 10))
            else:
                folder_var.set(folder_path)
                print(f"\033[94mBrowse selected folder: {folder_path}\033[0m")  # Blue output
    
    browse_button = tk.Button(main_frame, text="Browse", command=browse_folder, width=9, font=("Arial", 10))
    browse_button.grid(row=0, column=1, pady=(3, 0), sticky="w", padx=(0, 20))
    
    # Center address display box
    folder_entry = ttk.Entry(main_frame, textvariable=folder_var, font=("Arial", 10), width=65)
    # folder_entry.grid(row=1, column=0, columnspan=2, pady=(0, 5), padx=(10, 10))padx=(5, 0), sticky="ew"
    folder_entry.grid(row=1, column=0, columnspan=2, pady=(0, 2), padx=(5, 5), sticky="ew")
    
    # Parameter rows: shift label + input further left
    tk.Label(main_frame, text="Mineral:", 
             font=("Arial", 10)).grid(row=2, column=0, pady=(1, 0), sticky="e", padx=(0, 2))
    
    mineral_var = tk.StringVar(value="apatite")
    mineral_menu = ttk.Combobox(main_frame, textvariable=mineral_var, 
                               values=["apatite", "zircon"], 
                               state="readonly", font=("Arial", 10), width=12, justify="center")
    # Move mineral combobox further left
    mineral_menu.grid(row=2, column=1, pady=(1, 0), sticky="w", padx=(0, 0))
    
    # zeta parameter input - shift right slightly
    tk.Label(main_frame, text="Zeta:", 
             font=("Arial", 10)).grid(row=3, column=0, pady=(0, 0), sticky="e", padx=(0, 2))
    
    zeta_var = tk.StringVar(value="390")
    zeta_entry = ttk.Entry(main_frame, textvariable=zeta_var, font=("Arial", 10), width=12, justify="center")
    # Move zeta entry further left
    zeta_entry.grid(row=3, column=1, pady=(0, 0), sticky="w", padx=(0, 0))
    
    # rho-d parameter input - shift right slightly
    tk.Label(main_frame, text="Rho-d:", 
             font=("Arial", 10)).grid(row=4, column=0, pady=(0, 1), sticky="e", padx=(0, 2))
    
    rho_d_var = tk.StringVar(value="1.322E6")
    rho_d_entry = ttk.Entry(main_frame, textvariable=rho_d_var, font=("Arial", 10), width=12, justify="center")
    # Move rho-d entry further left
    rho_d_entry.grid(row=4, column=1, pady=(0, 1), sticky="w", padx=(0, 0))
    
    # Radial plots option - newly added
    tk.Label(main_frame, text="Radial plots:", 
             font=("Arial", 10)).grid(row=5, column=0, pady=(1, 2), sticky="e", padx=(0, 2))
    
    radial_plots_var = tk.StringVar(value="yes, in pdf")
    radial_plots_menu = ttk.Combobox(main_frame, textvariable=radial_plots_var, 
                             values=["yes, in pdf", "yes, in png", "no"], 
                             state="readonly", font=("Arial", 10), width=12, justify="center")
    # Move radial plots combobox further left
    radial_plots_menu.grid(row=5, column=1, pady=(1, 2), sticky="w", padx=(0, 0))
    
    # Plots option - newly added
    tk.Label(main_frame, text="LA vs PEDM:", 
             font=("Arial", 10)).grid(row=6, column=0, pady=(2, 2), sticky="e", padx=(0, 2))
    
    la_vs_pedm_var = tk.StringVar(value="yes, plot")
    la_vs_pedm_menu = ttk.Combobox(main_frame, textvariable=la_vs_pedm_var, 
                             values=["yes, plot", "ignore"], 
                             state="readonly", font=("Arial", 10), width=12, justify="center")
    # Move plots combobox further left
    la_vs_pedm_menu.grid(row=6, column=1, pady=(2, 2), sticky="w", padx=(0, 0))
    
    # Status label - reduce spacing
    status_label = tk.Label(main_frame, text="", font=("Arial", 10), fg="red")
    status_label.grid(row=7, column=0, columnspan=2, pady=(0, 0), padx=(5, 5))
    
    # Progress label - shows which file is being processed
    progress_label = tk.Label(main_frame, text="", font=("Arial", 10), fg="blue")
    progress_label.grid(row=8, column=0, columnspan=2, pady=(0, 0), padx=(5, 5))
    
    def update_defaults(*args):
        """Update defaults based on mineral type"""
        mineral_type = mineral_var.get()
        if mineral_type == "zircon":
            zeta_var.set("112")
            rho_d_var.set("0.45E6")
        else:  # apatite
            zeta_var.set("390")
            rho_d_var.set("1.322E6")
    
    # Bind mineral type change event
    mineral_var.trace('w', update_defaults)
    
    def validate_parameters():
        """Validate parameter ranges"""
        mineral_type = mineral_var.get()
        zeta_value = zeta_var.get()
        rho_d_value = rho_d_var.get()
        folder_path = folder_var.get()
        
        # Check if folder exists
        if not os.path.exists(folder_path):
            status_label.config(text="Selected folder does not exist", fg="magenta", font=("Arial", 10))
            return False
        
        # Check if folder contains CSV files
        try:
            csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
            if not csv_files:
                status_label.config(text="No CSV file in the selected folder", fg="magenta", font=("Arial", 10))
                return False
        except (PermissionError, OSError) as e:
            status_label.config(text=f"Cannot access folder: {str(e)}", fg="magenta", font=("Arial", 10))
            return False
        
        try:
            zeta = float(zeta_value)
            rho_d = float(rho_d_value.replace('E', 'e'))
            
            if mineral_type == "zircon":
                if zeta < 100 or zeta > 130:
                    status_label.config(text="Please use a valid zeta (100-130)", fg="magenta", font=("Arial", 10))
                    return False
                if rho_d < 0.1e6 or rho_d > 1e6:
                    status_label.config(text="Please use a valid rho-d (0.1E6 - 1E6)", fg="magenta", font=("Arial", 10))
                    return False
            else:  # apatite
                if zeta < 340 or zeta > 400:
                    status_label.config(text="Please use a valid zeta (340-400)", fg="magenta", font=("Arial", 10))
                    return False
                if rho_d < 0.8e6 or rho_d > 1.8e6:
                    status_label.config(text="Please use a valid rho-d (0.8E6 - 1.8E6)", fg="magenta", font=("Arial", 10))
                    return False
            
            status_label.config(text="✓ Parameters validated successfully", fg="green", font=("Arial", 10))
            return True
        except ValueError:
            status_label.config(text="Please enter valid numeric values", fg="magenta", font=("Arial", 10))
            return False
    
    def confirm_selection():
        """Confirm selection and disable all input controls"""
        if validate_parameters():
            result['folder'].set(folder_var.get())
            result['mineral'].set(mineral_var.get())
            result['zeta'].set(zeta_var.get())
            result['rho_d'].set(rho_d_var.get())
            result['la_vs_pedm'].set(la_vs_pedm_var.get())
            result['radial_plots'].set(radial_plots_var.get())
              
            # Exit main loop to continue program execution
            root.quit()
    
    def cancel_selection():
        """Cancel selection and force close window"""
        print("\033[95m✗ Dialog cancelled by user\033[0m")
        result['folder'].set("")
        result['mineral'].set("")
        result['zeta'].set("")
        result['rho_d'].set("")
        result['la_vs_pedm'].set("")
        result['radial_plots'].set("")
        root.quit()
        root.destroy()
    
    # Create button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=9, column=0, columnspan=2, pady=(0, 20), padx=(20, 20), sticky="ew")
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)
    
    # Create OK button
    ok_button = ttk.Button(button_frame, text="OK", command=confirm_selection)
    ok_button.grid(row=0, column=0, pady=(0, 0), padx=(0, 3), sticky="ew")
    
    # Create Cancel button
    cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel_selection)
    cancel_button.grid(row=0, column=1, pady=(0, 0), padx=(3, 0), sticky="ew")
    
    def disable_ui():
        """Disable all UI controls"""
        browse_button.config(state=tk.DISABLED)
        folder_entry.config(state=tk.DISABLED)
        mineral_menu.config(state=tk.DISABLED)
        zeta_entry.config(state=tk.DISABLED)
        rho_d_entry.config(state=tk.DISABLED)
        la_vs_pedm_menu.config(state=tk.DISABLED)
        radial_plots_menu.config(state=tk.DISABLED)
        ok_button.config(state=tk.DISABLED)
        cancel_button.config(state=tk.DISABLED)
    
    # Set focus to dropdown menu
    mineral_menu.focus_set()
    
    # Bind Enter key to confirm button
    root.bind('<Return>', lambda event: confirm_selection())
    
    # Bind window close event
    root.protocol("WM_DELETE_WINDOW", cancel_selection)
    
    # Bind ESC key to cancel button
    root.bind('<Escape>', lambda event: cancel_selection())
    
    # Initial validation of current folder
    if os.path.exists(folder_var.get()):
        csv_files = [f for f in os.listdir(folder_var.get()) if f.endswith('.csv')]
        if csv_files:
            status_label.config(text=f"✓ Current folder has {len(csv_files)} CSV files", fg="green")
        # else:
            # status_label.config(text="⚠ Current folder has no CSV files", fg="orange")
    
    # Start main loop
    root.mainloop()
    
    folder_value = result['folder'].get()
    mineral_value = result['mineral'].get()
    zeta_value = result['zeta'].get()
    rho_d_value = result['rho_d'].get()
    
    return {
        'folder': folder_value,
        'mineral': mineral_value,
        'zeta': float(zeta_value) if zeta_value else None,
        'rho_d': float(rho_d_value.replace('E', 'e')) if rho_d_value else None,
        'la_vs_pedm': result['la_vs_pedm'].get(),  # Return la_vs_pedm option
        'radial_plots': result['radial_plots'].get(),  # Return Radial plots option
        'root': root,  # Return the window object
        'disable_ui': disable_ui,  # Return the disable_ui function
        'status_label': status_label,  # Return the status label
        'progress_label': progress_label  # Return the progress label
    }

# Main processing function
def main_processing(foldername1, mineral, zeta, rho_d, la_vs_pedm, radial_plots, progress_label=None, cairo_available=False):
    """Main processing function to run in a separate thread"""
    print(f"\033[94m✓ Selected mineral type: {mineral}\033[0m") 
    print(f"\033[94m✓ Zeta value: {zeta}\033[0m")
    print(f"\033[94m✓ Rho-d value: {rho_d}\033[0m")
    print(f"\033[94m✓ Plot LA vs PEDM option: {la_vs_pedm}\033[0m")  # Print la_vs_pedm option
    print(f"\033[94m✓ Radial plots option: {radial_plots}\033[0m")  # Print Radial plots option
    print(f"\033[94m✓ Cairo PDF support: {cairo_available}\033[0m")  # Print Cairo availability

    # read data from selected folder
    spotsize = 25
    radialplot_width = 300
    radialplot_height = 300
    radialplot_res = 100
    csv_files1 = read_csv_files_from_folder(foldername1)
    file_count = len(csv_files1)
    print(f"✓ Total {file_count} CSV files read")

    # Initialize parameters with NaN values
    nan_array = [np.nan] * file_count
    mediumNS = nan_array.copy()
    totalNS = nan_array.copy()
    ngrains = nan_array.copy()
    pooledage4LAICPMS = nan_array.copy()
    pooledage_err4LAICPMS = nan_array.copy()
    pooledU4LAICPMS = nan_array.copy()
    pooledU_err4LAICPMS = nan_array.copy()
    U_mean4LAICPMS = nan_array.copy()
    U_std4LAICPMS = nan_array.copy()
    pooledage4pseudoEDM = nan_array.copy()
    pooledage_err4pseudoEDM = nan_array.copy()
    pooledage4pseudoEDM_wighted = nan_array.copy()
    pooledage_err4pseudoEDM_wighted = nan_array.copy()
    Samples = [None] * file_count

    dispers = nan_array.copy()
    dispers_se = nan_array.copy()
    mswds = nan_array.copy()
    centerages = nan_array.copy()
    centerages_se = nan_array.copy()
    pooled_age = nan_array.copy()
    pooled_age_se = nan_array.copy()
    pvalues = nan_array.copy()
    BH_used = [None] * file_count

    pooled_age2 = nan_array.copy()
    pooled_age_se2 = nan_array.copy()
    dispers2 = nan_array.copy()
    dispers_se2 = nan_array.copy()
    mswds2 = nan_array.copy()
    centerages2 = nan_array.copy()
    centerages_se2 = nan_array.copy()
    pvalues2 = nan_array.copy()
    BH_used2 = [None] * file_count
    minerals = nan_array.copy()

    i=0
    for j in csv_files1:
        print(f"processing file: {j}")
        # Update progress label if provided
        if progress_label:
            progress_label.config(text=f"Processing file: {j}", fg="blue")
            progress_label.update()  # Force UI update
        minerals[i] = mineral
        df = csv_files1[j]
        if 'Area' in df.columns:
            df = df.rename(columns={'Area': 'A'})
        u_cols = [col for col in df.columns if (col.startswith('U') and 
                                              col[1:].isdigit() and 
                                              not any(s in col.lower() for s in ['err']))]
        if u_cols:
            df['U_log_mean'] = df[u_cols].apply(lambda x: np.log(x.dropna())).mean(axis=1)
            df['U_log_std'] = df[u_cols].apply(lambda x: np.log(x.dropna())).std(axis=1)
            df['U_mean'] = np.exp(df['U_log_mean'])
            df['U_std'] = np.exp(df['U_log_std'])
            # print(df['U_mean'])
        df['U_std'] = df['U_std'].fillna(df['U1err'])
        df['U_mean'] = df['U_mean']
        df['U_std'] = df['U_std']
        df['A'] = df['A']  # in micrometer square
        # Remove Sample column
        if 'GrainID' in df.columns:
            df = df.drop(columns=['GrainID'])
        df = df[['Ns', 'A', 'U_mean', 'U_std']]
        df.columns = ['Ns', 'A', 'U1', 'U1err']
        mediumNS[i] = np.median(df['Ns'])
        totalNS[i] = np.sum(df['Ns'])
        ngrains[i] = len(df)
        pooledage4LAICPMS_i, pooledage_err4LAICPMS_i, pooled_U_i, pooled_U_err_i, U_mean_i, U_std_i = calc_pooledage4LAICPMS(df, mineral_type=mineral)
        # print(pooledage4LAICPMS_i, pooledage_err4LAICPMS_i)
        # single_ages, single_error = calc_singleage4LAICPMS(df, mineral_type=mineral)
        # print(single_ages, single_error)
        pooledage4LAICPMS[i] = pooledage4LAICPMS_i
        pooledage_err4LAICPMS[i] = pooledage_err4LAICPMS_i
        pooledU4LAICPMS[i] = pooled_U_i
        pooledU_err4LAICPMS[i] = pooled_U_err_i
        U_mean4LAICPMS[i] = U_mean_i
        U_std4LAICPMS[i] = U_std_i    
        df2 = df.copy()
        df2['Ni'] = NIfromUnA(df2['U1'].values, df2['A'].values, mineral_type=mineral,Zeta=zeta,RhoD=rho_d)
        # Remove Sample column
        df2 = df2.drop(columns=['U1','U1err'])
        # print(df2)
        pooledage4pseudoEDM_i, pooledage_err4pseudoEDM_i, pooledage4pseudoEDM_wighted_i, pooledage_err4pseudoEDM_wighted_i = calc_pooledage4pseudoEDM(df2, mineral_type=mineral,Zeta=zeta,RhoD=rho_d)
        pooledage4pseudoEDM[i] = pooledage4pseudoEDM_i
        pooledage_err4pseudoEDM[i] = pooledage_err4pseudoEDM_i
        pooledage4pseudoEDM_wighted[i] = pooledage4pseudoEDM_wighted_i
        pooledage_err4pseudoEDM_wighted[i] = pooledage_err4pseudoEDM_wighted_i
        Samples[i] = j

        csv_file = 'temp.csv'
                    # Write header data
        with open(csv_file, 'w') as f:
            # Write header
            f.write(f"mineral,,,\n")
            f.write(f"{mineral},,,\n")
            f.write(f"spotsize,,,\n")
            f.write(f"{spotsize},,,\n")
            f.write(f"Ns,A,U1,U1err\n")
            # Write data rows
            for _, row in df.iterrows():
                f.write(f"{row['Ns']},{row['A']},{row['U1']},{row['U1err']}\n")
        # Read data and generate centralages regardless of radial_plots option
        data = isoplotR.read_data(csv_file,method='fissiontracks',format=3)
        centralages = isoplotR.central(x=data,oerr = 1)
        
        # Generate radial plot based on user selection
        if radial_plots == 'yes, in png':
            # Save as PNG
            radiaplot_pic_name = f'{foldername1}/{j}.png'
            # Use png device with specified resolution
            ro.r(f'png(file = "{radiaplot_pic_name}", width = {radialplot_width}, height = {radialplot_height}, res = {radialplot_res})')
            # Set smaller font size for better readability
            ro.r('par(cex = 0.8)')  # Reduce font size by 20%
            isoplotR.radialplot(x=data,oerr = 1)
            # Close R graphics device
            ro.r('dev.off()')
        elif radial_plots == 'yes, in pdf':
            # Save as PDF
            radiaplot_pic_name = f'{foldername1}/{j}.pdf'
            # Use cairo_pdf for better font support if available
            if cairo_available:
                # Use cairo_pdf with points as units (1 point = 1/72 inch)
                ro.r(f'cairo_pdf(file = "{radiaplot_pic_name}", width = {radialplot_width/72}, height = {radialplot_height/72})')
            else:
                # Fall back to standard pdf device if Cairo is not available
                ro.r(f'pdf(file = "{radiaplot_pic_name}", width = {radialplot_width/72}, height = {radialplot_height/72})')
            # Set smaller font size for better readability in PDF
            ro.r('par(cex = 0.8)')  # Reduce font size by 20%
            isoplotR.radialplot(x=data,oerr = 1)
            # Close R graphics device
            ro.r('dev.off()')
        
        # Delete temporary file csv_file
        if os.path.exists(csv_file):
            os.remove(csv_file)
            # print(f"Temporary file deleted: {csv_file}")

        # print(df)
        # data22 = np.column_stack((single_ages, single_error))
        # print(data22)
        # centralages3 = central(x=data22,oerr = 1)
        # print("this is the centralage2: ",centralages3)
        mswd = centralages[1][0]
        pvalue = centralages[2][0]
        centerage = centralages[3][0]
        centerage_se = centralages[3][1]
        disper = centralages[-1][0]*100
        disper_se = centralages[-1][1]*100
        dispers[i] = disper
        dispers_se[i] = disper_se
        mswds[i] = mswd
        centerages[i] = centerage
        centerages_se[i] = centerage_se
        pvalues[i] = pvalue
        BH_used[i] = Samples

        csv_file2 = 'temp2.csv'
                    # Write header data
        with open(csv_file2, 'w') as f:
            if mineral == 'apatite':
                # Write header
                f.write(f"zeta,err\n")
                f.write(f"{zeta},{0.0001}\n")
                f.write(f"rhoD,err\n")
                f.write(f"{rho_d},{10000}\n")
                f.write(f"Ns,Ni\n")
            elif mineral == 'zircon':
                 # Write header
                f.write(f"zeta,err\n")
                f.write(f"{zeta},{2.5}\n")
                f.write(f"rhoD,err\n")
                f.write(f"{rho_d},{1000}\n")
                f.write(f"Ns,Ni\n")
            # Write data rows
            for _, row in df2.iterrows():
                f.write(f"{row['Ns']},{row['Ni']}\n")
        # Generate radial plot PNG only if radial_plots option is yes
        radiaplot_pic_name2 = f'{foldername1}/{j}_pseudoEDM.pdf'
        try:
            data2 = isoplotR.read_data(csv_file2,method='fissiontracks',format=1)
            centralages2 = isoplotR.central(x=data2,oerr = 1)
            
            # Generate radial plot based on user selection
            if radial_plots == 'yes, in png':
                # Save as PNG
                radiaplot_pic_name2 = f'{foldername1}/{j}_pseudoEDM.png'
                # Use png device with specified resolution
                ro.r(f'png(file = "{radiaplot_pic_name2}", width = {radialplot_width}, height = {radialplot_height}, res = {radialplot_res})')
                # Set smaller font size for better readability
                ro.r('par(cex = 0.8)')  # Reduce font size by 20%
                isoplotR.radialplot(x=data2,oerr = 1)
                # Close R graphics device
                ro.r('dev.off()')
            elif radial_plots == 'yes, in pdf':
                # Save as PDF
                radiaplot_pic_name2 = f'{foldername1}/{j}_pseudoEDM.pdf'
                # Use cairo_pdf for better font support if available
                if cairo_available:
                    # Use cairo_pdf with points as units (1 point = 1/72 inch)
                    ro.r(f'cairo_pdf(file = "{radiaplot_pic_name2}", width = {radialplot_width/72}, height = {radialplot_height/72})')
                else:
                    # Fall back to standard pdf device if Cairo is not available
                    ro.r(f'pdf(file = "{radiaplot_pic_name2}", width = {radialplot_width/72}, height = {radialplot_height/72})')
                # Set smaller font size for better readability in PDF
                ro.r('par(cex = 0.8)')  # Reduce font size by 20%
                isoplotR.radialplot(x=data2,oerr = 1)
                # Close R graphics device
                ro.r('dev.off()')
            
            mswd2 = centralages2[1][0]
            pvalue2 = centralages2[2][0]
            centerage2 = centralages2[3][0]
            centerage_se2 = centralages2[3][1]
            disper2 = centralages2[-1][0]*100
            disper_se2 = centralages2[-1][1]*100
            # pooled_age2[i] = pooled2)  # Modified to use pooled2
            # pooled_age_se2[i] = pooledsigma2)  # Modified to use pooledsigma2
            dispers2[i] = disper2
            dispers_se2[i] = disper_se2
            mswds2[i] = mswd2
            centerages2[i] = centerage2
            centerages_se2[i] = centerage_se2
            pvalues2[i] = pvalue2
            # BH_used2[i] = item)
            i = i +1
            # Delete temporary file csv_file2
            if os.path.exists(csv_file2):
                os.remove(csv_file2)
                # print(f"Temporary file deleted: {csv_file2}")
        except Exception as e:
            print(f"✗ Error processing file {i}: {str(e)}")
            i = i +1
            continue  # Skip current loop and proceed to next
    age_results = pd.DataFrame({'ID':Samples,'Pooled_ICPMS_age':pooledage4LAICPMS,'Pooled_ICPMS_age_1se':pooledage_err4LAICPMS,
                                'pooledU4LAICPMS':pooledU4LAICPMS, 'pooledU_err4LAICPMS':pooledU_err4LAICPMS,'U_mean4LAICPMS':U_mean4LAICPMS,
                                'U_std4LAICPMS':U_std4LAICPMS,
                                'pooledage4pseudoEDM':pooledage4pseudoEDM,'pooledage_err4pseudoEDM':pooledage_err4pseudoEDM,
                                'central_ICPMSage':centerages,'central_ICPMSage_err':centerages_se,
                                'central_pseudoEDMage':centerages2,'central_pseudoEDMage_err':centerages_se2,
                                'p_value_ICPMS':pvalues,'Dispersion_ICPMS %':dispers,'Dispersion_1se_ICPMS %':dispers_se,
                                'p_value_pseudoEDM':pvalues2,'Dispersion_pseudoEDM %':dispers2,'Dispersion_1se_pseudoEDM %':dispers_se2,'mediumNS':mediumNS,'totalNS':totalNS,'ngrains':ngrains,'mineral':minerals})

    # Only export results if the DataFrame is not empty
    if age_results.empty:
        print("\033[94m✓ No valid age results to export.\033[0m")
    else:
        age_results.to_excel(f'{foldername1}/ages_results.xlsx',index=False)
        print(f"\033[94m✓ Export ages_results.xlsx\033[0m")

    if la_vs_pedm == 'yes, plot':
        print(f"\033[94m✓ Plot a figure comparing LA-ICPMS vs pseudo-EDM results and statistics\033[0m")
        # Plot LA-ICPMS vs pseudo-EDM method comparison
        plt.figure(figsize=(6.5, 6))
        plt.subplot(2, 2, 1)
        plt.text(0.0, 1.01, '(a)', transform=plt.gca().transAxes,
                 ha='left', va='bottom', fontsize=11, clip_on=False)

        # Plot scatter chart
        plt.errorbar(pooledage4LAICPMS,np.array(pooledage4LAICPMS)/np.array(pooledage4pseudoEDM), 
                    xerr=pooledage_err4LAICPMS, yerr=0,
                    fmt='o', color='blue', ecolor='lightgray',
                    capsize=0, alpha=0.5)

        # Add 1:1 reference line
        max_age = max(max(pooledage4LAICPMS), max(pooledage4pseudoEDM)) * 1.1
        plt.plot([0, max_age], [1, 1], 'r--')

        # Chart decoration
        plt.xlabel('LA-ICPMS pooled age (Ma)',fontsize=9)
        plt.ylabel('pooled age ratio: \n pseudo-EDM / LA-ICPMS',fontsize=9)
        # plt.legend()
        plt.grid(True, linestyle='--', alpha=0.5)
        # Set axis tick labels font size
        plt.tick_params(axis='both', which='major', labelsize=9)
        # plt.ylim(0.95, 1.05)
        plt.minorticks_on()

        differences = 100*(np.array(centerages) - np.array(pooledage4LAICPMS))/np.array(pooledage4LAICPMS)
        differences2 = 100*(np.array(centerages2) - np.array(pooledage4pseudoEDM))/np.array(pooledage4pseudoEDM)
        max_disp = max(dispers)

        plt.subplot(2, 2, 3)
        plt.text(0.0, 1.01, '(b)', transform=plt.gca().transAxes,
                 ha='left', va='bottom', fontsize=11, clip_on=False)
        plt.scatter(dispers, differences, color='blue', alpha=0.5,label='LA-ICPMS')
        plt.scatter(dispers2, differences2, color='red', alpha=0.5,label='pseudo-EDM')
        # Add gray polygon background for x-axis > 20 range
        # x_min, x_max = plt.xlim()
        # y_min, y_max = plt.ylim()
        # plt.fill_betweenx([y_min, y_max], 20, x_max, color='gray', alpha=0.2)
        plt.xlabel('Dispersion (%)',fontsize=8.5)
        plt.ylabel('age difference: \n(central-pooled)/pooled age (%)',fontsize=9)
        plt.legend(fontsize=8.5)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.plot([0, max_disp], [0, 0], 'r--')
        # Set axis tick labels font size
        plt.tick_params(axis='both', which='major', labelsize=9)
        plt.minorticks_on()

        plt.subplot(2, 2, 4)
        plt.text(0.0, 1.01, '(c)', transform=plt.gca().transAxes,
                 ha='left', va='bottom', fontsize=11, clip_on=False)
        plt.scatter(pvalues, differences, color='blue', alpha=0.5,label='LA-ICPMS')
        plt.scatter(pvalues2, differences2, color='red', alpha=0.5,label='pseudo-EDM')
        # Add gray polygon background for x-axis 0-0.05 range
        # x_min, x_max = plt.xlim()
        # y_min, y_max = plt.ylim()
        # plt.fill_betweenx([y_min, y_max], 0, 0.05, color='gray', alpha=0.2)
        plt.xlabel('p-value (*100)',fontsize=9)
        # plt.ylabel('(Central-Pooled)/Pooled Age (%)',fontsize=9)
        plt.legend(fontsize=8.5)
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.plot([0, 1], [0, 0], 'r--')
        # Set axis tick labels font size
        plt.tick_params(axis='both', which='major', labelsize=9)
        plt.minorticks_on()

        plt.tight_layout(pad=2.0, w_pad=1.5, h_pad=1.0)
        # Save the figure
        image_path = f'{foldername1}/LAICPMS_vs_pseudoEDM_comparison.pdf'
        plt.savefig(image_path, dpi=300, bbox_inches='tight')

        # Open the saved PDF for review
        import subprocess
        if os.path.exists(image_path):
            subprocess.call(['open', image_path])  # macOS default PDF viewer
            print(f"\033[94m✓ Figure opened for review: {image_path}\033[0m")
        else:
            print(f"\033[95m✗ Figure file not found: {image_path}\033[0m")
        # plt.show()
    
    print("\033[94m✓ Processing completed successfully!\033[0m")

# Call dropdown selection window
mineral_params = select_mineral()

# Check if user cancelled
if not mineral_params['folder']:
    print("\033[95m✗ Operation cancelled by user\033[0m")
else:
    # Get the window object, disable function, status label, and progress label
    root_window = mineral_params['root']
    disable_ui = mineral_params['disable_ui']
    status_label = mineral_params['status_label']
    progress_label = mineral_params['progress_label']
    
    # Disable all UI controls
    disable_ui()
    
    # Start main processing in a separate thread
    foldername1 = mineral_params['folder']
    mineral = mineral_params['mineral']
    zeta = mineral_params['zeta']
    rho_d = mineral_params['rho_d']
    la_vs_pedm = mineral_params['la_vs_pedm']  # Get la_vs_pedm option
    radial_plots = mineral_params['radial_plots']  # Get Radial plots option
    
    # Update status label to indicate processing started
    status_label.config(text="Processing started...", fg="blue")
    
    # Check if Cairo package is available in R
    try:
        ro.r('library(Cairo)')
        cairo_available = True
    except Exception:
        cairo_available = False
        print("\033[93m⚠ Cairo package not available in R, will use standard pdf device\033[0m")
    
    # Start main processing in the main thread (rpy2 has issues with threading)
    main_processing(foldername1, mineral, zeta, rho_d, la_vs_pedm, radial_plots, progress_label, cairo_available)
    
    # Update status label with success message
    status_label.config(text="✓ Processing completed successfully!", fg="green")
    progress_label.config(text="", fg="blue")  # Clear progress label
    
    # Restart the main loop to keep the parameter UI window open
    root_window.mainloop()
