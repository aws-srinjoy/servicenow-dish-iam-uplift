import os
import json
import pandas

def generate_markdown_from_files(foldername):
  frames=[]
  for filename in os.listdir(foldername):
    print(filename)
    with open(f"{foldername}/{filename}") as json_file:
      data=json.load(json_file)
      del data["Authorized Principals"]
      print(len(data))
      frames.append(data)

  result=pandas.DataFrame(frames)
  print(result.shape)
  print(result.columns)
  md=result.to_markdown(showindex=False)
  prefix="../docs/guardrails"
  md_filename=f"{prefix}/{foldername}/guardrails.md"
  print(md_filename)
  with open(md_filename,'w') as out:
    out.write(md)

if __name__ == "__main__":
  files = os.listdir(os.curdir)
  for filename in files:
    if os.path.isdir(filename):
      generate_markdown_from_files(filename)
