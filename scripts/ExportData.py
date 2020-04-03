import csv
import datetime
import time
import logging
import configparser
from influxdb import InfluxDBClient


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class CsvExporter:

    def __init__(self):
        self.client = None
        self.is_connected = False
        self.retry = 1
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("config/application.ini")
        self.influx_address = self.config_parser.get("INFLUX", "address")
        self.influx_port = int(self.config_parser.get("INFLUX", "port"))
        self.db_name = self.config_parser.get("INFLUX", "db_name")
        self.measurement_name = self.config_parser.get("INFLUX", "measurement_name")
        self.csv_name = self.config_parser.get("CSV", "file_name")

    def init(self):
        self.connect()
        self.client.create_database(self.db_name)
        self.client.switch_database(self.db_name)

    def connect(self):
        self.client = InfluxDBClient(
            host=self.influx_address,
            port=self.influx_port)

        try:
            self.client.ping()
            self.is_connected = True
            return
        except Exception as e:
            self.reconnection_retry(connect_function=self.connect)

    def reconnection_retry(self, connect_function, backoff_factor=1, **kwargs):
        while not self.is_connected:
            LOGGER.info("Reconnection tentative [{}]..".format(self.retry))
            wait_time = backoff_factor * (2 ** (self.retry - 1))
            LOGGER.info("New reconnection tentative in {} second(s)..".format(wait_time))
            time.sleep(wait_time)
            self.retry += 1
            connect_function(**kwargs)

    def export(self):
        with open(self.csv_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            headers = next(csv_reader)
            headers = headers[1:]
            timestamp_list = []
            counter = 1

            for row in csv_reader:
                # Modify the date in unix format
                row[0] = row[0].split("T")[0]
                date_list = row[0].split("-")
                timestamp = datetime.datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]))
                timestamp = int(time.mktime(timestamp.timetuple()))
                row = row[1:]

                data_row = dict(zip(headers, row))

                for key, value in data_row.items():
                    try:
                        data_row[key] = int(value)
                    except Exception as e:
                        data_row[key] = value

                if timestamp not in timestamp_list:
                    timestamp_list.append(timestamp)
                    self.write_on_db(data_row, timestamp)
                else:
                    timestamp += counter
                    counter += 1
                    timestamp_list.append(timestamp)
                    self.write_on_db(data_row, timestamp)

    def write_on_db(self, row, ts):
        data_row = [dict(
            measurement=self.measurement_name,
            fields=row,
            time=ts)
        ]
        self.client.write_points(
            points=data_row,
            database=self.db_name,
            time_precision="s")


if __name__ == "__main__":
    csv_exporter = CsvExporter()

    csv_exporter.init()
    csv_exporter.export()
