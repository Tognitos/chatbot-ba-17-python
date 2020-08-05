#!/bin/sh
rm -f dump.out

# $abs_path = $1 = absolute path to ttl outputs
# $db_name = $2 = db name in jena
# $3, $4, $n = ttl dump files to import

abs_path=$1
db_name=$2

if test "$1" = '-h'; then
  echo "Usage"
  echo "sh ./import_ttl.sh /absolute/path/to/ttl/outputs/ db_name input1.ttl input2.ttl ..."
  echo ""
  echo "For example, in order to import 2 actor files and the movie triples:"
  echo "sh ./import_ttl.sh /home/tognitos/Documents/BA/chatbot-source/r2rml/outputs/ imdb actor1.ttl actor2.ttl movie.ttl"
  echo ""
  echo "Alternatively, everything *.ttl can be imported with NO file params"
  echo "sh ./import_ttl.sh /home/tognitos/Documents/BA/chatbot-source/r2rml/outputs/ imdb"
  exit 1
fi

files=''
#loop through additional files and append (>= index 2)
while [ $# -gt 2 ]
do
  files=$files' '$3 # start from the third arg
  shift
done

$(docker run --volumes-from fuseki -v $abs_path:/staging stain/jena-fuseki ./load.sh $db_name $files)
