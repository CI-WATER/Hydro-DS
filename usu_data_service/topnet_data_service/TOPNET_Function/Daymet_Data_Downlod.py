import sys
import subprocess
import os
def create_rain_dat(climate_file_dir,Start_year, End_year,R_Code_Path):
    raindat_script= os.path.join(R_Code_Path,'create_rain.R')

    commands=[]
    commands.append('Rscript');commands.append(raindat_script)
    commands.append(str(climate_file_dir));commands.append(str(Start_year));commands.append(str(End_year))
    fused_command = ''.join(['"%s" ' % c for c in commands])
    print(fused_command)
    os.system(fused_command)

if __name__ == '__main__':
    climate_file_dir = sys.argv[1]
    Start_year = sys.argv[2]
    End_year=sys.argv[3]
    R_Code_Path=sys.argv[4]
    create_rain_dat(climate_file_dir,Start_year, End_year,R_Code_Path)