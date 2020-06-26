import json
import urllib.request
from datetime import datetime
import bs4 as bs
from threading import Thread
from time import sleep
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import pgeocode
import time


class Kafka:
    def __init__(self, bootstrap_servers, topic_name=str):
        self.bootstrap_servers = bootstrap_servers
        #self.kafka_version = (0, 1, 0) # (0, 10)?
        self.topic_name = topic_name

    def kafka_producer(self, json):

        producer = KafkaProducer (
            bootstrap_servers   =   self.bootstrap_servers,
            #api_version         =   self.kafka_version
        )
        #print(producer.bootstrap_connected())
        #print(producer.partitions_for("haus-kaufen"))

        ack = producer.send(self.topic_name, json.encode('utf-8'))
        metadata = ack.get()

        #print(metadata.topic)
        #print(metadata.partition)


class WebScraper:
    def __init__(self, postleitzahl=int, radius=int, buy_or_rent=str):
        self.start_time = datetime.now()
        self.radius = radius  # Suchradius um Stuttgart
        self.plz = postleitzahl  # Postleitzahl um Suchradius
        self.buy_or_rent = buy_or_rent
        self.anzahl_haeuser = 0

    def zip_to_geo_conversion(self, seite):
        laendercode = pgeocode.Nominatim('de')
        latitude = str(laendercode.query_postal_code(str(self.plz)).latitude)
        longitude = str(laendercode.query_postal_code(str(self.plz)).longitude)
        self.suchlink = str("https://www.immobilienscout24.de/Suche/radius/haus-{0:s}?geocoordinates={1:s};"
                            "{2:s};{3:s}.0&sorting=2&pagenumber={4:s}".format(
            self.buy_or_rent, latitude, longitude, str(self.radius), str(seite)))

    def scrape_one_page(self, seite):
        self.l = []

        try:
            self.page_request(seite)

            for paragraph in self.soup.find_all("a"):
                if r"/expose/" in str(paragraph.get("href")):
                    self.l.append(paragraph.get("href").split("#")[0])
                self.l = list(set(self.l))

            for i in range(1, len(self.l) + 1):
                self.anzahl_haeuser += 1
                expose = self.l[i-1]
                Thread(target=self.single_object_on_page, kwargs={"expose": expose}).start()

        except Exception as e:
            print(str(datetime.now()) + ": " + str(e))

    def page_request(self, seite):
        self.zip_to_geo_conversion(seite)
        self.soup = bs.BeautifulSoup(
            urllib.request.urlopen(self.suchlink).read(), 'lxml')

    def single_object_on_page(self, expose):
        item = expose
        try:
            soup = bs.BeautifulSoup(urllib.request.urlopen('https://www.immobilienscout24.de' + item).read(),
                                    'lxml')
            data = (str(soup.find_all("script")).split("keyValues = ")[1].split("}")[0] + str("}"))
            data = data[:1] + "\"URL\":" + "\"" "https://www.immobilienscout24.de" + str(item) + "\"," + data[1:]
            data = data[:1] + "\"timestamp\":" + "\"" + str(datetime.now()) + "\"," + data[1:]
            self.data = eval(data)
            self.data_to_json()

        except Exception as e:
            empty_value = (str(e))[1:-1]
            if self.data.get(e) is None:  # adding "no_information" instead of None to keep the dataset
                self.data[str(empty_value)] = "no_information"
                self.data_to_json()

            # removes a faulty dataset
            else:
                print(str(datetime.now()) + ": " + str(e))
                self.l = list(filter(lambda x: x != item, self.l))
                print("ID " + str(item) + " entfernt.")

    def data_to_json(self):
        # Haus-Kaufen
        elements_in_json_kaufen = (
            'timestamp',
            'URL',
            'obj_scoutId',
            'obj_regio3',
            'geo_krs',
            'geo_land',
            'obj_zipCode',
            'obj_heatingType',
            'obj_cellar',
            'obj_picture',
            'obj_lotArea',
            'obj_buildingType',
            'obj_barrierFree',
            'obj_purchasePrice',
            'obj_purchasePriceRange',
            'obj_pricetrendbuy',
            'obj_livingSpace',
            'obj_livingSpaceRange',
            'obj_condition',
            'obj_constructionPhase',
            'obj_immotype',
            'obj_rented',
            'obj_noRooms',
            'obj_noRoomsRange',
            'obj_yearConstructed',)

        # Haus_Mieten
        elements_in_json_mieten = (
            'timestamp',
            'URL',
            'obj_scoutId',
            'obj_regio3',
            'geo_krs',
            'geo_land',
            'obj_zipCode',
            'obj_heatingType',
            'obj_cellar',
            'obj_picture',
            'obj_lotArea',
            'obj_buildingType',
            'obj_barrierFree',
            'obj_baseRent',
            'obj_baseRentRange',
            'obj_pricetrendrent',
            'obj_serviceCharge',
            'obj_totalRent',
            'obj_hasKitchen',
            'obj_petsAllowed',
            'obj_livingSpace',
            'obj_livingSpaceRange',
            'obj_condition',
            'obj_interiorQual',
            'obj_immotype',
            'obj_noRooms',
            'obj_noRoomsRange',
            'obj_lotArea',
            'obj_numberOfFloors',
            'obj_noParkSpaces',
            'obj_yearConstructed',
        )
        single_dict = {}
        if self.buy_or_rent == "mieten":
            for (key, value) in self.data.items():
                # Check if key is even then add pair to new dictionary
                if key in elements_in_json_mieten:
                    try:
                        single_dict[key] = int(value)
                    except ValueError:
                        try:
                            single_dict[key] = float(value)
                        except ValueError:
                            single_dict[key] = value

        else:
            for (key, value) in self.data.items():
                # Check if key is even then add pair to new dictionary
                if key in elements_in_json_kaufen:
                    try:
                        single_dict[key] = int(value)
                    except ValueError:
                        try:
                            single_dict[key] = float(value)
                        except ValueError:
                            single_dict[key] = value

        single_json = json.dumps(single_dict, ensure_ascii=False)  # converting dict to json, this goes to kafka
        ApacheKafka.kafka_producer(single_json)
        parsed = json.loads(single_json) #only for printing
        single_readable_json = (json.dumps(parsed, indent=4, sort_keys=True, ensure_ascii=False))
        #print(single_readable_json)  # from here sent jsons to kafka
        #print(datetime.now(), self.anzahl_haeuser)
        #print(self.anzahl_haeuser)

    def get_number_of_pages(self):
        self.zip_to_geo_conversion(1) #hier wird die Seite 1 gewählt
        soup = bs.BeautifulSoup(
            urllib.request.urlopen(self.suchlink).read(), 'lxml')
        self.numberofallpages = (str((soup.find_all("option"))[-1])[15:17])
        
        # hier wird geprüft, ob die maximale Seitenanzahl zweistelling ist
        if "\"" in self.numberofallpages:
            self.numberofallpages = int(self.numberofallpages[0:1])
        else:
            self.numberofallpages = int(self.numberofallpages)
        #print("Hier wird gescraped:")
        #print(self.suchlink)
        #print(str(self.numberofallpages) + " Seiten to scrape")


if __name__ == "__main__":
    #ApacheKafka = Kafka(bootstrap_servers=['34.107.21.187:9092'], topic_name="haus-kaufen")  # instanziiert Kafka
    Scraper = WebScraper(postleitzahl=70563, radius=30, buy_or_rent="kaufen")
    # Radius um Postleitzahl und kaufen oder mieten werden übergeben

    while True:  # wenn alle Seiten gescraped wurden fängt das Skriptt wieder von vorne an
        Scraper.get_number_of_pages()
        for seite in range(1, Scraper.numberofallpages +1):  # scrapes all pages
            Scraper.scrape_one_page(seite)
            sleep(3600)  # 5 Sekunden Verzögerung verhindert, dass sich die Threads überlagern
    end_time = datetime.now()
    #print("Es wurden Daten von ", Scraper.anzahl_haeuser, " Häusern gescraped")
