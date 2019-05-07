args<-commandArgs(TRUE)
repos=args[1]
lib=args[2]
package_list=as.matrix(read.table('Rpackage_list_to_Install.txt'))
for (i in 1:length(package_list)){
  install.packages(package_list[i],repos=repos,lib=lib)
}

