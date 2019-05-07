def daymet_download(Watershed_Raster,Start_year,End_year,R_EXE_Path,R_Code_Path):
    head,tail=os.path.split(str(Watershed_Raster))
    watershed_dir=str(head)
    wateshed_name=str(tail)
    daymet_download_script= os.path.join(R_Code_Path,'daymet_download.r')
    commands=[]
    commands.append(os.path.join(R_EXE_Path,"Rscript"));commands.append(daymet_download_script);commands.append(str(watershed_dir))
    commands.append(str(wateshed_name));commands.append(str(Start_year));commands.append(str(End_year));
    fused_command = ''.join(['"%s" ' % c for c in commands])
    subprocess.call(fused_command)
