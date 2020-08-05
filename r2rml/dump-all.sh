#!/bin/sh
rm -f dump.out

if test "$1" = '-h'; then
  echo "Call with --genprop to generate new properties files automatically (calls generate_properties.sh)"
fi

# if --genprop exists, then regenerate properties files automatically
if test "$1" = '--genprop'; then
  echo "Calling generate_properties.sh"
  sh ./generate_properties.sh $2
fi

# For each file in properties/ execute the r2rml parse
for proppath in properties/*.properties; do
  propfile=$(basename "$proppath")
  property_filename=${propfile%%.properties} # removes extension
  echo "Dumping based on $propfile..."
  sh ./r2rml-parser.sh -p properties/$propfile #>> dump_result.out
  echo "Done dumping $property_filename"

done
