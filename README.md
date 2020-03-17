# How to
 - In order to build the exporter image:
 
        docker image build -t script .
        
 - In order to run Grafana, Influxdb and Script images
 
        docker-compose -f docker-compose-all up
 
 If you don't need to export the data that you already have in your own influxdb instance,
 just run the docker-compose.yml file with

        docker-compose -f docker-compose up
      
# Configuration
 Modify the application.ini file in the config directory.