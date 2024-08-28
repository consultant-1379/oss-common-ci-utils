import json
import csv
import sys
import os.path

filename=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] +".json"
final_filename=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] +"-final.json"

try:
    print("filename")
    with open(filename, 'r') as fr:
        lines = fr.readlines()
        with open(final_filename, 'a') as fw:
            for line in lines:
                if 'Report' not in line:
                   fw.write(line)
    print("Deleted")
except:
    print("Oops!something error")

with open(final_filename) as json_file:
    jsondata = json.load(json_file)

csvfilename=".tmp/.usage-report/artifactory-repo-usage-report_" + sys.argv[1] +".csv"
file_exists = os.path.isfile(csvfilename)
data_file = open(csvfilename, 'a+', encoding='UTF8')
csv_writer = csv.writer(data_file,delimiter=',')

count = 0
for data in jsondata:
    if count == 0:
        header = ['repoKey', 'filesCount', 'usedSpace', 'usedSpaceRaw','infoUpdated']
        if not file_exists:
           csv_writer.writerow(header)
        count += 1
        print(data)
    csv_writer.writerow(data.values())

data_file.close()
