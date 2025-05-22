import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.signal import butter,filtfilt

def butter_lowpass_filter(data, cutoff, order):
    b, a = butter(order, cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y

# Specify the directory path
directory = Path('/Users/asharma/Library/CloudStorage/OneDrive-HewlettPackardEnterprise/codes/C_Code/currTests/LSMS/fept_16/power_mi250/logs')
power_pattern = r"(\S+)\s+(\w+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\w+)"
pdf_pages = PdfPages('/Users/asharma/Library/CloudStorage/OneDrive-HewlettPackardEnterprise/codes/C_Code/currTests/LSMS/fept_16/power_mi250/power_plots.pdf')

for file_path in directory.iterdir():
    # Check if the file starts with "frontier"
    if file_path.name.endswith('_power.log') and file_path.is_file():  
        file_name = file_path.name
        file_base = file_name.replace(".log", "")
        
        with open(file_path, 'r') as file:
            node_power = []
            gpu0_power = []
            cpu_power = []
            mem_power = []
            
            for line in file:
                if "power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'node_power': float(match[2]),
                    }
                    node_power.append(power_entry)

                if "accel0_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'gpu0_power': float(match[2]),
                    }
                    gpu0_power.append(power_entry)

                if "cpu_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'cpu_power': float(match[2]),
                    }
                    cpu_power.append(power_entry)

                if "memory_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'mem_power': float(match[2]),
                    }
                    mem_power.append(power_entry)                    

        node_power_df = pd.DataFrame(node_power)
        node_power_np = node_power_df['node_power'].to_numpy()
        node_power_filt = butter_lowpass_filter(node_power_np, cutoff=0.03, order=2)

        gpu0_power_df = pd.DataFrame(gpu0_power)
        gpu0_power_np = gpu0_power_df['gpu0_power'].to_numpy()
        gpu0_power_filt = butter_lowpass_filter(gpu0_power_np, cutoff=0.03, order=2)

        mem_power_df = pd.DataFrame(mem_power)
        mem_power_np = mem_power_df['mem_power'].to_numpy()

        # Plot power_array and sum_array
        plt.figure(figsize=(8, 6))

        plt.plot(node_power_np, label='Node power', color='darkgray',linewidth=1.0)
        plt.plot(node_power_filt, label='Filtered Node power', color='black',linewidth=2.0)

        plt.plot(gpu0_power_np, label='GPU 0 power', color='lightblue',linewidth=1.0)
        plt.plot(gpu0_power_filt, label='Filtered GPU 0 power', color='blue',linewidth=2.0)

        plt.plot(mem_power_np, label='MEM power', color='red',linewidth=1.0)
        plt.title(f'{file_base}')
        plt.ylabel('Power(W)')
        plt.xlabel('Sample number')
        plt.legend()

        pdf_pages.savefig()
        plt.show(block=True)
        # plt.close()

# Close the PDF after all pages are added
pdf_pages.close()