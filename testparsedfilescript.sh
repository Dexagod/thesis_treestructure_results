parsedstreets.json | sed "s/^.*userid.*$//g" | sed "s/^.*target.*$//g" | sed "s/^.*requests.*$//g" | sed "s/^.*[{}\[].*$//g" | sed "s/^.*].*$//g" | sed "s/\s*//g" | grep \" | wc -l
