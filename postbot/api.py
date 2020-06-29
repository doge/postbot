import requests

API_URL = "https://www.canadapost.ca/trackweb/rs/track/json/package/%s/detail"


class ValidationError(ValueError):
    def __str__(self):
        return "The tracking number provided was invalid."


class CanadaPostPackage(object):
    def __init__(self, tracking_num):
        self.tracking_num = tracking_num
        self.data = self.__validate_data()

    def get_all_data(self):
        with requests.Session() as sess:
            data = sess.get(API_URL % self.tracking_num).json()
            return data

    def __validate_data(self):
        data = self.get_all_data()
        if "error" in str(data):
            raise ValidationError()
        return data

    def get_events(self):
        return self.data['events']

    def get_package_info(self):
        # return most relevant package information
        package_info = []
        for event in self.get_events():
            package_info.append(
                {
                    "date":         event['datetime']['date'],
                    "time":         event['datetime']['time'],
                    "location":     event['locationAddr'],
                    "activityScan": event['type'],
                    "descriptions": {
                        # english and french
                        'descEn': event['descEn'],
                        'descFr': event['descFr']
                    }
                }
            )
        return package_info
