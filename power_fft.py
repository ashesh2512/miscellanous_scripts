import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from pathlib import Path
import re
from scipy.signal import butter,filtfilt
from scipy import fftpack

# Specify the directory path
directory = '/Users/asharma/Library/CloudStorage/OneDrive-HewlettPackardEnterprise/codes/C_Code/currTests/LSMS/fept_16/power_mi250/1_atom_per_gpu/lmax_14_liz_6'
logs = Path(directory + '/logs')
pdf_pages = PdfPages(directory + '/power_' + Path(directory).name + '.pdf')

# pattern to capture
power_pattern = r"(\S+)\s+(\w+)\s+(\d+)\s+(\w+)\s+(\d+)\s+(\w+)"

# run time of simulation
log_file = logs.joinpath("lsms.log")
with open(log_file, 'r') as file:
    for line in file:
        match = re.search(r"LSMS Runtime\s*=\s*([0-9.]+)", line)
        if match:
            runtime = float(match.group(1))
            print("LSMS Runtime:", runtime)
            break  # Stop after the first match
        

def get_frequencies(signal):
    sig_noise_fft = fftpack.fft(signal)
    num_samples = sig_noise_fft.size

    # in the FFT of a sine wave with 1.0 amplitude, we get two non-zero components, at +f and –f; each of those has an amplitude of 0.5, because they share the original amplitude of 1.0 from the sine wave. Hence the use of 2, because we care only about the +ve f because value at -ve f is just the complex conjugate of the positive frequency.

    # sig_noise_amp = 2 / num_samples * np.abs(sig_noise_fft)

    sig_noise_freq = np.abs(fftpack.fftfreq(num_samples, runtime/num_samples))
    sig_noise_freq = np.sort(np.unique(sig_noise_freq))
    return sig_noise_freq

def butter_lowpass_filter(data, cutoff, order):
    b, a = butter(order, cutoff, btype='low', analog=False)
    y = filtfilt(b, a, data)
    return y


for file_path in logs.iterdir():
    # Check if the file starts with "frontier"
    if file_path.name.endswith('_power.log') and file_path.is_file():  
        file_name = file_path.name
        file_base = file_name.replace(".log", "")
        
        with open(file_path, 'r') as file:
            node_power = []
            gpu0_power = []
            gpu1_power = []
            gpu2_power = []
            gpu3_power = []
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

                if "accel1_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'gpu1_power': float(match[2]),
                    }
                    gpu1_power.append(power_entry)

                if "accel2_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'gpu2_power': float(match[2]),
                    }
                    gpu2_power.append(power_entry)                    

                if "accel3_power" in line.split():
                  matches = re.findall(power_pattern, line)
                  if matches:
                    match=matches[0]
                    power_entry = {
                      'gpu3_power': float(match[2]),
                    }
                    gpu3_power.append(power_entry)                    

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
        sig_noise_freq = get_frequencies(node_power_np)
        node_power_filt = butter_lowpass_filter(node_power_np, cutoff=sig_noise_freq[4], order=2)

        gpu0_power_df = pd.DataFrame(gpu0_power)
        gpu0_power_np = gpu0_power_df['gpu0_power'].to_numpy()
        sig_noise_freq = get_frequencies(gpu0_power_np)
        gpu0_power_filt = butter_lowpass_filter(gpu0_power_np, cutoff=sig_noise_freq[4], order=2)

        gpu1_power_df = pd.DataFrame(gpu1_power)
        gpu1_power_np = gpu1_power_df['gpu1_power'].to_numpy()
        sig_noise_freq = get_frequencies(gpu1_power_np)
        gpu1_power_filt = butter_lowpass_filter(gpu1_power_np, cutoff=sig_noise_freq[4], order=2)

        gpu2_power_df = pd.DataFrame(gpu2_power)
        gpu2_power_np = gpu2_power_df['gpu2_power'].to_numpy()
        sig_noise_freq = get_frequencies(gpu2_power_np)
        gpu2_power_filt = butter_lowpass_filter(gpu2_power_np, cutoff=sig_noise_freq[4], order=2)

        gpu3_power_df = pd.DataFrame(gpu3_power)
        gpu3_power_np = gpu3_power_df['gpu3_power'].to_numpy()
        sig_noise_freq = get_frequencies(gpu3_power_np)
        gpu3_power_filt = butter_lowpass_filter(gpu3_power_np, cutoff=sig_noise_freq[4], order=2)

        mem_power_df = pd.DataFrame(mem_power)
        mem_power_np = mem_power_df['mem_power'].to_numpy()

        # Plot power_array and sum_array
        fig, axs = plt.subplots(2, 2, figsize=(8, 10))

        axs[0, 0].plot(gpu0_power_np, label='GPU 0 power', color='lightblue',linewidth=0.5)
        axs[0, 0].plot(gpu0_power_filt, label='Filtered GPU 0 power', color='blue',linewidth=1.0)
        axs[0, 0].plot(mem_power_np, label='MEM power', color='red',linewidth=0.5)
        axs[0, 0].plot(node_power_np, label='Node power', color='darkgray',linewidth=0.5)
        axs[0, 0].plot(node_power_filt, label='Filtered Node power', color='black',linewidth=1.0)
        axs[0, 0].set_ylabel('Power(W)')
        # axs[0, 0].set_xlabel('Sample number')
        axs[0, 0].legend()

        axs[0, 1].plot(gpu1_power_np, label='GPU 1 power', color='lightblue',linewidth=0.5)
        axs[0, 1].plot(gpu1_power_filt, label='Filtered GPU 1 power', color='blue',linewidth=1.0)
        axs[0, 1].plot(mem_power_np, label='MEM power', color='red',linewidth=0.5)
        # axs[0, 1].set_ylabel('Power(W)')
        # axs[0, 1].set_xlabel('Sample number')
        axs[0, 1].legend()

        axs[1, 0].plot(gpu2_power_np, label='GPU 2 power', color='lightblue',linewidth=0.5)
        axs[1, 0].plot(gpu2_power_filt, label='Filtered GPU 2 power', color='blue',linewidth=1.0)
        axs[1, 0].plot(mem_power_np, label='MEM power', color='red',linewidth=0.5)
        axs[1, 0].set_ylabel('Power(W)')
        axs[1, 0].set_xlabel('Sample number')
        axs[1, 0].legend()

        axs[1, 1].plot(gpu3_power_np, label='GPU 3 power', color='lightblue',linewidth=0.5)
        axs[1, 1].plot(gpu3_power_filt, label='Filtered GPU 3 power', color='blue',linewidth=1.0)
        axs[1, 1].plot(mem_power_np, label='MEM power', color='red',linewidth=0.5)
        # axs[1, 1].set_ylabel('Power(W)')
        axs[1, 1].set_xlabel('Sample number')
        axs[1, 1].legend()

        # plt.plot(sig_noise_freq, sig_noise_amp, label='FFT', color='black',linewidth=0.5)

        # plt.plot(node_power_np, label='Node power', color='darkgray',linewidth=0.5)
        # plt.plot(node_power_filt, label='Filtered Node power', color='black',linewidth=1.0)

        fig.suptitle(f'{file_base}')

        pdf_pages.savefig()
        # plt.show(block=True)
        # plt.close()

# Close the PDF after all pages are added
pdf_pages.close()