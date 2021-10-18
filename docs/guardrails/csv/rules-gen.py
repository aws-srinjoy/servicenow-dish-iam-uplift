import os
import csv
import json

def create_rule(filename,prefix):
  print(filename,prefix)
  with open(filename,'r') as csvfile:
    iam=csv.DictReader(csvfile)
    for row in iam:
      row["Identifier"]=row["Identifier"].upper()
      id=row["Identifier"]
      row["Authorized Principals"]=""
      with open(f"../../../guardrails/{id}.json", 'w') as fp:
        json.dump(row,fp) 

 
if __name__ == "__main__":
  files = os.listdir(os.curdir)
  for filename in files:
    if filename.endswith(".csv"):
      prefix=os.path.splitext(filename)[0]
      create_rule(filename,prefix)  
