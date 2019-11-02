
import os

files_to_keep=5000
path="/mnt/disk1/"
counter=0

files=sorted(os.listdir(path), key=lambda x: os.path.getctime(path+x))
files_counter=len(files)
print files
print files_counter

if files_counter > files_to_keep:

  while files_counter!=files_to_keep:
    
    file_name=files[counter]
    file_to_remove=path+file_name
    print file_to_remove+" deleted"
    os.remove(file_to_remove)
    counter=counter+1
    files_counter=len(os.listdir(path))
  
  print "deleted "+str(counter)+" files"
else:
  print "file counter <= file_to_keep aborting"
