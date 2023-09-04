# photomanage
Scripts and ideas to manage tons and tons of images and movies


sort unique exclusions file
cat exclusions.csv | awk -F '.' '{print $NF}' | sort | uniq

