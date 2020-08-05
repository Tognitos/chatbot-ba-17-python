#!/bin/bash

echo "This script generates properties from mappings files in the mappings/ folder"
echo "Example usage: ./generate_properties.sh imdb"
echo "Generating property file for mapping"

db_name=$1

# use default name if param was not passed
if [ -z "$1" ]; then
  db_name="imdb"
  echo "WARNING: No db name supplied. Using default 'imdb'"
fi

# Todo add counter of how many files generated
i=$(date)
# For every file in mappings/ generate a properties file in properties/ with the same name
for mappath in mappings/*.ttl; do
  mapfile=$(basename "$mappath")
  mapfile_name=${mapfile%%.ttl} # removes extension
  echo "#Mappings
mapping.file=mappings/$mapfile
mapping.file.type=TTL

# Destinations
jena.destinationFileName=outputs/$mapfile
jena.destinationFileSyntax=TTL



# Mysql
db.url=jdbc:mysql://127.0.0.1:3306/$db_name
db.login=root
db.password=root
db.driver=com.mysql.jdbc.Driver

# You can leave these
default.namespace=http://chatbot-zhaw.com/base#
default.verbose=false
default.log=status.rdf
default.forceURI=true
default.incremental=false

# Jena settings
jena.storeOutputModelUsingTdb=false
jena.tdb.directory=outputs

jena.showXmlDeclaration=false
jena.encodeURLs=false" > properties/$mapfile_name.properties
done

echo "Generated files for $i mappings"
