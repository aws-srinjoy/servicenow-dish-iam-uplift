#set -Eeuox pipefail
set -x

find . -name "guardrails.md" |  sort -t '\0' -n | while read filename; do
  p=$(dirname $filename)
  abbr=$(basename $p)

  pandoc -f markdown "$filename" > html/"$abbr".out.html
  #html2csv "$abbr".out.html -o csv/"$abbr".csv
  python3 html2csv.py html/"$abbr".out.html --output csv/"$abbr".csv
done
