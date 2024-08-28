import pandas as pd
import csv
import json
import os
import numpy as np
import sys

# read csv file to drop duplicates
filename=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] +".csv"
filename_without_duplicates=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_without_duplicates" +".csv"
combinedcolumnsfile=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_with_combined_columns" +".csv"
combinedcolumnsfilewithout_repeatedheaders=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_with_combined_unique_header" +".csv"
combined_shiftedcol=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_with_combined_shiftedcolumns" +".csv"
finalcombined=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "finalcombined" +".csv"

############# Merge columns for docker under repoKey#######
if sys.argv[1].lower() == "docker":
    colnames=['repoKey', 'filesCount', 'usedSpace', 'usedSpaceRaw','infoUpdatedold','infoUpdated']
    df = pd.read_csv(filename, names=colnames, header=None)
    result = df.columns
    print("result",result)
    df['repoKey_and_filesCount'] = df['repoKey'] +'-'+ df['filesCount'].map(str)
    print(df)
    print(df.columns.tolist())
    df.to_csv(combinedcolumnsfile, index=False)
    #######remove extra header########
    lines = list()
    rownumbers_to_remove= [2]
    with open(combinedcolumnsfile, 'r') as read_file:
        reader = csv.reader(read_file)
        for row_number, row in enumerate(reader, start=1):
            if(row_number not in rownumbers_to_remove):
                lines.append(row)
    with open(combinedcolumnsfilewithout_repeatedheaders, 'w') as write_file:
        writer = csv.writer(write_file)
        writer.writerows(lines)

    ########## remove repokey  from combined csv##########
    temp=pd.read_csv(combinedcolumnsfilewithout_repeatedheaders,index_col=False)
    temp.drop('repoKey',axis=1,inplace=True)
    temp.to_csv(combined_shiftedcol, index=False)
    ########shifting columns#########
    dfshift = pd.read_csv(combined_shiftedcol,index_col=False)
    df_1 = dfshift[['repoKey_and_filesCount', 'filesCount', 'usedSpace', 'usedSpaceRaw','infoUpdated']]
    print('\nPandas DataFrame with changed column order:\n')
    df_1.rename(columns=({'repoKey_and_filesCount':'repoKey'}),inplace=True)
    df_1.to_csv(finalcombined, index=False)
    df = pd.read_csv(finalcombined, usecols=['repoKey'],sep=',').drop_duplicates(keep='first')
    column_values = set()
    new_rows = []
    with open(finalcombined, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (row[0] in column_values):
                continue
            column_values.add(row[0])
            new_rows.append(row)
    with open(filename_without_duplicates, 'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_rows)
######read csv file to drop duplicates##############
else:
    df = pd.read_csv(filename, usecols=['repoKey'],sep=',').drop_duplicates(keep='first')
    column_values = set()
    new_rows = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if (row[0] in column_values):
                continue
            column_values.add(row[0])
            new_rows.append(row)
    with open(filename_without_duplicates, 'w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_rows)

########remove columns from non duplicated csv#######
selected_nonduplicate_columns=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_selectednonduplicate_columns" +".csv"
duplicate = pd.read_csv(filename_without_duplicates,index_col=False)
col=['infoUpdated','filesCount','usedSpaceRaw']
duplicate.drop(columns=col, axis = 1, inplace = True)
duplicate.to_csv(selected_nonduplicate_columns,sep=',',index=False)

### read column values of non duplicated csv into list#######
data = pd.read_csv(selected_nonduplicate_columns)
reponames = data['repoKey'].tolist()
print("reponames",reponames)
headers = ['repoKey','usedSpace']
search_for = reponames
print("filename",filename)
filename_with_selected_columns=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_selected_columns" +".csv"
#####if repo is docker#######
if sys.argv[1].lower() == "docker":
    with open(finalcombined) as inf, open(filename_with_selected_columns,'w',newline='') as outf:
        print("for docker specific repos")
        reader = csv.reader(inf)
        writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,)
        writer.writerow(headers)
        for row in reader:
            if row[0] in search_for:
                print('Found: {}'.format(row))
                writer.writerow((row[0],row[3]))
else:
    with open(filename) as inf, open(filename_with_selected_columns,'w',newline='') as outf:
        reader = csv.reader(inf)
        writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,)
        writer.writerow(headers)
        for row in reader:
            if row[0] in search_for:
                print('Found: {}'.format(row))
                writer.writerow((row[0],row[3]))

file = pd.read_csv(filename_with_selected_columns)
print("\nOriginal file:")
print(file)
data = pd.read_csv(filename_with_selected_columns)
df = pd.read_csv(filename_with_selected_columns)
# sort data frame
sorted_df = df.sort_values(by=["repoKey"],ascending=[False])
# displaying sorted data frame
print("\nAfter sorting:")
print(data)
sortedcsv=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] + "_sorted" +".csv"
sorted_df.to_csv(sortedcsv, index=False)

filenames=[]
# reading csv file
for repos in range(0, len(reponames)):
    df = pd.read_csv(sortedcsv, sep=",")
    new_file = f'artifactory_{reponames[repos]}.csv'
    filenames.append(new_file)
    output = df[df.repoKey == reponames[repos]].to_csv(f'.tmp/.usage-report/artifactory_{reponames[repos]}.csv', sep=',', index=False)
    print(output)

########read generated csv in current working directory into a list ########
print("filenames",filenames)
os.chdir(".tmp/.usage-report/")
print("cwr",os.getcwd())
filesnames1 = [f for f in filenames]
print("filesnames1",filesnames1)

########get repowise space usage in  repos csv#######
print("cwr1",os.getcwd())
for files in filesnames1:
    df = pd.read_csv(files,sep=',', header=0, usecols=[0,1])
    my_data=df['repoKey'].iloc[0]
    df.rename(columns={'usedSpace': my_data}, inplace=True)

    df.to_csv(f'artifactory_{files}', index=False,header=True)
    datadrop = pd.read_csv(f'artifactory_{files}')
    datadrop.drop('repoKey', inplace=True, axis=1)
    datadrop.to_csv(f'artifactoryrepos_{files}', index=False,header=True)
    print("repolist")
print("repos_list created")

#######get filenames in list#######
myfilenames=[]
searchstring = sys.argv[1]
directory_list = os.listdir()
for file in directory_list:
    for i in range(len(filenames)):
        if filenames[i] in file and file.startswith("artifactoryrepos_"):
            myfilenames.append(file)
            print("filemynames",file)
print("myfilenames",myfilenames)
li = []
for csvfilename in myfilenames:
    df = pd.read_csv(csvfilename,index_col=None)
    li.append(df)
print("li",li)

df = pd.concat(li,axis=1)
print("filename before concat",csvfilename)
concatfilename="artifactory_concat" + sys.argv[1] +".csv"
df.to_csv(concatfilename, sep=",", index = False)


####get and add  infoupdated column#####
headers = ['repoKey','usedSpace','infoUpdated']
print("search for")
headers = ['repoKey','usedSpace','infoUpdated']
search_for = reponames
finalcombined1="artifactory-repo-usage-report_" + sys.argv[1] + "finalcombined" +".csv"
relativefilename="artifactory-repo-usage-report_" + sys.argv[1] +".csv"
file_including_infoupdatedcol="artifactory-repo-usage-report_" + sys.argv[1] + "including_infoupdated" +".csv"
if sys.argv[1].lower() == "docker":
    with open(finalcombined1) as inf, open(file_including_infoupdatedcol,'w',newline='') as outf:
        print("for docker specific repos")
        reader = csv.reader(inf)
        writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,)
        writer.writerow(headers)
        for row in reader:
            if row[0] in search_for:
                print('Found: {}'.format(row))
                writer.writerow((row[0],row[3],row[4]))
else:
     with open(relativefilename) as inf, open(file_including_infoupdatedcol,'w',newline='') as outf:
          reader = csv.reader(inf)
          writer = csv.writer(outf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL,)
          writer.writerow(headers)
          for row in reader:
            if row[0] in search_for:
                print('Found: {}'.format(row))
                writer.writerow((row[0],row[3],row[5]))
print("filename",filename)

datanew = pd.read_csv(file_including_infoupdatedcol)
df = pd.read_csv(file_including_infoupdatedcol)
# sort data frame
sorted_df = df.sort_values(by=["repoKey"],ascending=[False])
# displaying sorted data frame
print("\nAfter sorting:")
print(datanew)
sorted_infoupdated_file="artifactory-repo-usage-report_" + sys.argv[1] + "_sortedinfoupdated" +".csv"
sorted_df.to_csv(sorted_infoupdated_file, index=False)
print("reponames",reponames[0])
df = pd.read_csv(sorted_infoupdated_file, sep=",")
finalinfoupdatedsortedfile="artifactory-repo-usage-report_" + sys.argv[1] + "_finalinfoupdatedsorted" +".csv"
output = df[df.repoKey == reponames[0]].to_csv(finalinfoupdatedsortedfile,sep=',',index=False)
print(output)

######sorting infoupdated#######
sorted_file="artifactory-repo-usage-report_" + sys.argv[1] + "_sorted" +".csv"
df = pd.read_csv(finalinfoupdatedsortedfile)
# sort data frame
sorted_df = df.sort_values(by=["infoUpdated"],ascending=[True])
sorted_df.to_csv(sorted_file, index=False)

########add new row to infoupdated csv#######
with open(sorted_file) as csvfile:
    readCSV = list(csv.reader(csvfile, delimiter=','))
    row_you_want = readCSV[-1]
print("row_you_want",row_you_want)

dfupdated = pd.read_csv(sorted_file)
length = len(df)
dfupdated.loc[length] = row_you_want
print("The dataframe after the append operation:")
filename_including_infoupdatedfinal="artifactory-repo-usage-report_" + sys.argv[1] + "_infoupdatedincludingfinal" +".csv"
dfupdated.to_csv(filename_including_infoupdatedfinal, index=False,na_rep='NULL')

###add blank values as Nan#######
nullconcatfilename="artifactoryconcatwithnull" + sys.argv[1] +".csv"
data_nan = pd.read_csv(concatfilename)
data_nan1 = data_nan.copy()
data_nan1 = data_nan1.replace(r'^s*$', float('NaN'), regex = True)  # Replace blanks by NaN
print("data_nan1",data_nan1)
data_nan1.to_csv(nullconcatfilename, index=False,na_rep='NULL')                                     # Print updated data
data = pd.read_csv(sorted_file)
new_col = list(data.infoUpdated)
data_new = pd.read_csv(nullconcatfilename)
print("data_new",new_col)
data_new['infoUpdated'] = new_col
finalconcatfilename="artifactory_final_concat_with_infoupdated" + sys.argv[1] +".csv"
data_new.to_csv(finalconcatfilename, index=False)

#######csv to html table#####
count=len(open(finalconcatfilename).readlines())
df=pd.read_csv(finalconcatfilename, skiprows=range(1,count-1), header=0)
latestusagefilename="artifactory_final_latest_usage" + sys.argv[1] +".csv"
df.to_csv(latestusagefilename, index=False)

######csv to html
a = pd.read_csv(latestusagefilename)
filename_last_usage_table="artifactory-repo-usage-report_" + sys.argv[1] + "_updatedusagetable" +".htm"
a.to_html(filename_last_usage_table)
html_file = a.to_html()
