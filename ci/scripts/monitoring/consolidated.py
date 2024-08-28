import os
import pandas as pd


######generate consolidated report#####
#######get filenames in list#######
myfilenames=[]
directory_list = os.listdir(".tmp/.usage-report")
print("directory list",directory_list)
for file in directory_list:
        if file.startswith("artifactory_final_concat_with_infoupdated"):
            myfilenames.append(file)
            print("filemynames",file)
print("myfilenames",myfilenames)

li = []
for csvfilename in myfilenames:
    df = pd.read_csv(f'.tmp/.usage-report/{csvfilename}',index_col=None)
    li.append(df)

print("li",li)
df = pd.concat(li,axis=1)
concatfilename="consolidated.csv"
print(df.max())
df.to_csv(concatfilename, sep=",", index = False)
print("end")


#######combine html files##########
#######get filenames in list#######
filenames=[]
for file in os.listdir(".tmp/.usage-report/"):
        if file.endswith(".htm"):
            filenames.append(file)
            print("filemynames",file)
print("filenames",filenames)

li = []
with open('.tmp/.usage-report/final_usage.htm', 'w') as outfile:
    for htmlfilename in filenames:
        with open(f'.tmp/.usage-report/{htmlfilename}') as infile:
                outfile.write(infile.read()+"\n")