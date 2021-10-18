import os
import pandas

def create_markdown(filename,prefix):
  dataframe = pandas.read_csv(filename)
  rows=dataframe.shape[0]

  dataframe.insert(0,'Identifier','')
  ids=[]
  actions=[]
  for i in range(1,rows+1):
    ids.append(f"IAM-{prefix}-{i}")
    actions.append("")
  print(ids)  
  dataframe['Identifier']=ids

  dataframe["IAM Actions"]=actions

  md=dataframe.to_markdown(showindex=False)
  print(md)
  md_filename=f"{prefix}/guardrails.md"
  with open(md_filename,'w') as out:
    out.write(md)

if __name__ == "__main__":
  files = os.listdir(os.curdir)
  for filename in files:
    if filename.endswith(".csv"):
      prefix=os.path.splitext(filename)[0]
      create_markdown(filename,prefix)
