from pykat import finesse                  # Importing the pykat.finesse package
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
from scipy.stats import logistic
import random
import os
import tempfile
import time
import glob
import imageio
import numpy as np
from datetime import datetime, date

from geo_aLIGO12 import compute_strain, compute_baseline_aligo



def create_strains(target, best='', baseline='', curr_id=0, curr_loss=666):
    NUM_OF_SIMULATION_POINTS=1000
    freq_info_full=[5,6000,NUM_OF_SIMULATION_POINTS]
    use_classical_noise=True
    if target==0:
        freq_info_curr=[30,1000,NUM_OF_SIMULATION_POINTS] # normal BH
        pltname='normal BH'
        pltname=r"$\bf{"+"Broadband"+"}$\n 800Hz - 3kHz"
    elif target==1:
        freq_info_curr=[2700,3300,NUM_OF_SIMULATION_POINTS] # merger
        pltname='merger'
        pltname=r"$\bf{"+"Post-Merger"+"}$\n 800Hz - 3kHz"      
    elif target==2:
        freq_info_curr=[200,1000,NUM_OF_SIMULATION_POINTS] # supernova  
        pltname='Supernova: 200Hz - 1kHz'
        pltname=r"$\bf{"+"Supernova"+"}$\n 200Hz - 1kHz"
        
    elif target==3:
        freq_info_curr=[10,30,NUM_OF_SIMULATION_POINTS] # cosmology   
        pltname='cosmology'  
        pltname=r"$\bf{"+"Cosmology"+"}$\n 10Hz - 30Hz"        
    elif target==4:
        freq_info_curr=[20,5000,NUM_OF_SIMULATION_POINTS] # broad band   
        pltname='broad band'    
        pltname=r"$\bf{"+"Broadband"+"}$\n 20Hz - 5kHz"
        
    elif target==5:
        freq_info_curr=[20,5000,NUM_OF_SIMULATION_POINTS] # broad band   
        pltname='Broadband: 20Hz - 5kHz'    
        pltname=r"$\bf{"+"Broadband"+"}$\n 20Hz - 5kHz"
        use_classical_noise=False     

    elif target==6:
        freq_info_curr=[2000,3000,NUM_OF_SIMULATION_POINTS] # broad band   
        pltname='range: 2kHz - 3kHz'
        #use_classical_noise=True # (check whether thats true, probably false)
        pltname=r"$\bf{"+"Narrow Post-Merger"+"}$\n 800Hz - 3kHz"
        
    elif target==7:
        freq_info_curr=[800,3000,NUM_OF_SIMULATION_POINTS] # neutron star merger expanded     
        pltname='large range'  
        print("I DONT EXPECT EXAMPLES HERE")
        
    elif target==8:
        freq_info_curr=[800,3000,NUM_OF_SIMULATION_POINTS] # neutron star merger expanded     
        pltname='Post-Merger: 800Hz - 3kHz'  
        pltname=r"$\bf{"+"Post-Merger"+"}$\n 800Hz - 3kHz"
        use_classical_noise=False
        
    elif target==9:
        freq_info_curr=[10,30,NUM_OF_SIMULATION_POINTS] # cosmology   
        pltname=r"$\bf{"+"Cosmology"+"}$\n 10Hz - 30Hz"
        use_classical_noise=False   

    elif target==10:
        freq_info_curr=[20,5000,NUM_OF_SIMULATION_POINTS] # broad band   
        pltname='Broadband with short filters: 20Hz - 5kHz'
        pltname=r"$\bf{"+"Broadband (short)"+"}$\n 20Hz - 5kHz"
        use_classical_noise=False
    
    if use_classical_noise==True:
        pltname+='\n (with thermal&seismic noise)'
    
    
    print(best)
    v1=np.log10(freq_info_curr[0])
    v2=np.log10(freq_info_curr[1])
    range_log=v2-v1
    
    extra_space_log=range_log/2
    
    new_exponent_min=v1-extra_space_log
    new_exponent_max=v2+extra_space_log
    
    min_val=10**new_exponent_min
    max_val=10**new_exponent_max

    #min_val=freq_info_curr[0]*0.8
    #max_val=freq_info_curr[1]/0.8
    freq_info=[min_val,max_val,NUM_OF_SIMULATION_POINTS]
    
    did_succeed=False
    while not did_succeed:
        if True:
            freq_aligo, strain_aligo, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aligo, totalnoise_aligo, totalsignal_aligo = compute_baseline_aligo(freq_info, use_classical_noise=use_classical_noise)
            did_succeed=True
        else:
            time.sleep(0.1)
    
    # compute solution
    file1 = open(best, "r") 
    readfile = file1.read()
    file1.close()    
    if readfile[-1]=='\n':
        readfile=readfile[0:len(readfile)-1]
    did_succeed=False
    while not did_succeed:
        try:        
            freq_best, strain_best, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise_best, totalsignal_best = compute_strain(freq_info,readfile, use_classical_noise=use_classical_noise)
            did_succeed=True
        except:
            time.sleep(0.1)
                
            
    # compute baseline        
    file1 = open(baseline, "r") 
    readfile = file1.read()
    file1.close()    
    if readfile[-1]=='\n':
        readfile=readfile[0:len(readfile)-1]
    did_succeed=False
    while not did_succeed:
        try:    
            freq_baseline, strain_baseline, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise_baseline, totalsignal_baseline = compute_strain(freq_info,readfile, use_classical_noise=use_classical_noise)
            did_succeed=True
        except:
            time.sleep(0.1)

    # compute aLIGO    
    did_succeed=False
    while not did_succeed:
        try:
            freq_aligo_full, strain_aligo_full, lossPowerElements_aligo, lossPowerPD_aligo, lossPowerCoating_aligo, totalnoise_aligo_full, totalsignal_aligo_full = compute_baseline_aligo(freq_info_full, use_classical_noise=use_classical_noise)
            did_succeed=True
        except:
            time.sleep(0.1)

    file1 = open(best, "r") 
    readfile = file1.read()
    file1.close()    
    if readfile[-1]=='\n':
        readfile=readfile[0:len(readfile)-1]
        
    did_succeed=False
    while not did_succeed:
        try:        
            freq_best_full, strain_best_full, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise_best_full, totalsignal_best_full = compute_strain(freq_info_full,readfile, use_classical_noise=use_classical_noise)
            print(f'{lossPowerElements} {lossPowerPD} {lossPowerCoating}')
            did_succeed=True
        except:
            time.sleep(0.1)
            
    if len(baseline)>0:
        file1 = open(baseline, "r") 
        readfile = file1.read()
        file1.close()    
        if readfile[-1]=='\n':
            readfile=readfile[0:len(readfile)-1]
        did_succeed=False
        while not did_succeed:
            try:                    
                freq_baseline_full, strain_baseline_full, lossPowerElements, lossPowerPD, lossPowerCoating, totalnoise_baseline_full, totalsignal_baseline_full = compute_strain(freq_info_full, readfile, use_classical_noise=use_classical_noise)
                did_succeed=True
            except:
                time.sleep(0.1) 
    
    
    return freq_aligo, strain_aligo, strain_best, strain_baseline, freq_info_curr, freq_info, pltname, freq_aligo_full, strain_aligo_full, strain_best_full, strain_baseline_full, freq_info_full, totalnoise_aligo_full, totalsignal_aligo_full, totalnoise_best_full, totalsignal_best_full, totalnoise_baseline_full, totalsignal_baseline_full, totalnoise_aligo, totalsignal_aligo, totalnoise_best, totalsignal_best, totalnoise_baseline, totalsignal_baseline



def plot_strain_sensitivity(target, input_file, baseline, new_file_dir='.'):
    y_limit=[10**(-25), 10**(-22)]
    clinewidth=3
    
    freq_aligo, strain_aligo, strain_best, strain_baseline, freq_info_curr, freq_info, pltname, freq_aligo_full, strain_aligo_full, strain_best_full, strain_baseline_full, freq_info_full, totalnoise_aligo_full, totalsignal_aligo_full, totalnoise_best_full, totalsignal_best_full, totalnoise_baseline_full, totalsignal_baseline_full, totalnoise_aligo, totalsignal_aligo, totalnoise_best, totalsignal_best, totalnoise_baseline, totalsignal_baseline=create_strains(target=target, best=input_file, baseline=baseline)
    
    # plot
    plt.grid()
    plt.loglog(freq_aligo, strain_aligo, label='Voyager', linewidth=clinewidth)
    plt.loglog(freq_aligo, strain_baseline, label='Baseline', linewidth=clinewidth)
    plt.loglog(freq_aligo, strain_best, label='best UIFO', linewidth=clinewidth)
    plt.legend(loc="upper right", fontsize=11.5)
    ymin, ymax = y_limit
    plt.ylim(ymin, ymax)
    plt.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    plt.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    plt.axvspan(xmin=freq_info[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    plt.axvspan(xmin=freq_info[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)
    plt.xlabel(r'Frequency [Hz]', fontsize=14)
    plt.ylabel(r'Strain Sensitivity [/$\sqrt{Hz}$]', fontsize=14)
    plt.title(f"Strain: {pltname}", fontsize=18)
    
    # plot on the nested subplot
    #ax2 = plt.inset_axes([0.5, 0.5, 0.47, 0.47])  # adjust size and position as needed
    ax2 = inset_axes(plt.gca(), width="30%", height="30%", loc='upper center')  # adjust size and position as needed

    ax2.grid()
    ax2.loglog(freq_aligo_full, strain_aligo_full, linewidth=clinewidth)
    ax2.set_ylim(ymin, ymax)
    ax2.loglog(freq_aligo_full, strain_baseline_full, linewidth=clinewidth)
    ax2.loglog(freq_aligo_full, strain_best_full, linewidth=clinewidth)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    ax2.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    ax2.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    ax2.axvspan(xmin=freq_info_full[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    ax2.axvspan(xmin=freq_info_full[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)

    plt.tight_layout()
    output_file=os.path.join(new_file_dir, 'strain.png')
    plt.savefig(output_file, dpi=300)
    plt.show()
    
# ---------------------------------------------------------------    
    
    
    # plot
    plt.grid()
    plt.loglog(freq_aligo, totalnoise_aligo, label='Voyager', linewidth=clinewidth)
    plt.loglog(freq_aligo, totalnoise_baseline, label='Baseline', linewidth=clinewidth)
    plt.loglog(freq_aligo, totalnoise_best, label='best UIFO', linewidth=clinewidth)
    plt.legend(loc="upper right", fontsize=11.5)
    #ymin, ymax = y_limit
    #plt.ylim(ymin, ymax)
    plt.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    plt.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    plt.axvspan(xmin=freq_info[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    plt.axvspan(xmin=freq_info[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)
    plt.xlabel(r'Frequency [Hz]', fontsize=14)
    plt.ylabel(r'Quantum noise [W/$\sqrt{Hz}$]', fontsize=14)
    plt.title(f"Quantum Noise: {pltname}", fontsize=18)
    
    # plot on the nested subplot
    #ax2 = plt.inset_axes([0.5, 0.5, 0.47, 0.47])  # adjust size and position as needed
    ax2 = inset_axes(plt.gca(), width="30%", height="30%", loc='upper center')  # adjust size and position as needed

    ax2.grid()
    ax2.loglog(freq_aligo_full, totalnoise_aligo_full, linewidth=clinewidth)
    #ax2.set_ylim(ymin, ymax)
    ax2.loglog(freq_aligo_full, totalnoise_baseline_full, linewidth=clinewidth)
    ax2.loglog(freq_aligo_full, totalnoise_best_full, linewidth=clinewidth)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    ax2.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    ax2.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    ax2.axvspan(xmin=freq_info_full[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    ax2.axvspan(xmin=freq_info_full[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)

    plt.tight_layout()
    output_file=os.path.join(new_file_dir, 'noise.png')
    plt.savefig(output_file, dpi=300)
    plt.show()
    
# ---------------------------------------------------------------    
    
    # plot
    plt.grid()
    plt.loglog(freq_aligo, totalsignal_aligo, label='Voyager', linewidth=clinewidth)
    plt.loglog(freq_aligo, totalsignal_baseline, label='Baseline', linewidth=clinewidth)
    plt.loglog(freq_aligo, totalsignal_best, label='best UIFO', linewidth=clinewidth)
    plt.legend(loc="upper right", fontsize=11.5)
    #ymin, ymax = y_limit
    #plt.ylim(ymin, ymax)
    plt.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    plt.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    plt.axvspan(xmin=freq_info[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    plt.axvspan(xmin=freq_info[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)
    plt.xlabel(r'Frequency [Hz]', fontsize=14)
    plt.ylabel(r'Optical Response [W/Strain]', fontsize=14)
    plt.title(f"Optical Signal: {pltname}", fontsize=18)
    
    # plot on the nested subplot
    #ax2 = plt.inset_axes([0.5, 0.5, 0.47, 0.47])  # adjust size and position as needed
    ax2 = inset_axes(plt.gca(), width="30%", height="30%", loc='upper center')  # adjust size and position as needed

    ax2.grid()
    ax2.loglog(freq_aligo_full, totalsignal_aligo_full, linewidth=clinewidth)
    #ax2.set_ylim(ymin, ymax)
    ax2.loglog(freq_aligo_full, totalsignal_baseline_full, linewidth=clinewidth)
    ax2.loglog(freq_aligo_full, totalsignal_best_full, linewidth=clinewidth)
    ax2.set_yticklabels([])
    ax2.set_xticklabels([])
    ax2.axvline(x=freq_info_curr[0], linestyle='-', color='black')
    ax2.axvline(x=freq_info_curr[1], linestyle='-', color='black')
    ax2.axvspan(xmin=freq_info_full[0], xmax=freq_info_curr[0], color='gray', alpha=0.2)
    ax2.axvspan(xmin=freq_info_full[1], xmax=freq_info_curr[1], color='gray', alpha=0.2)

    plt.tight_layout()
    output_file=os.path.join(new_file_dir, 'signal.png')
    plt.savefig(output_file, dpi=300)
    plt.show()
    
# ---------------------------------------------------------------    
    
   
def get_baseline_filename(target):
    files = glob.glob(f'all_baselines/CFGS_{target}_*.txt')
    return files[0] if files else None
 

if __name__=='__main__':
    target=5     # in this example, target=5 (broadband)
    baseline=get_baseline_filename(target)
    plot_strain_sensitivity(target=target, input_file='example_setup_type5.kat', baseline=baseline)