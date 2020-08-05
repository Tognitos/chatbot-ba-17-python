echo "This is R2RML Parser 0.8-alpha. Run with -h for help on options."
echo ""
echo "Dumping from property file $2 ..."
java -Xms2048m -Xmx6144m -cp "./*;./lib/*;" -jar lib/r2rml-parser-0.8.jar $1 $2
echo ""
echo "R2RML Parser 0.8-alpha. Done dumping $2."
