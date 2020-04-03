# Download the updated csv from the git repo
curl https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv > ./scripts/csv/dpc-covid19-ita-regioni.csv

# Run docker-compose file
docker-compose up -d