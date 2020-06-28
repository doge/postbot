import pymongo


class Database:
    def __init__(self, ip, port, db_name, collection_name):
        client = pymongo.MongoClient(ip, port)
        self.db = client[db_name]
        self.collection = self.db[collection_name]

    def insert_event(self, tracking_number, channel_id, events):
        found = self.collection.find_one({"channelId": channel_id})

        if found is None:
            self.collection.insert_one({
                "channelId": channel_id,
                "trackingNumber": tracking_number,
                "events": events
            })
        else:
            # get previous items and add them to the object
            for key in found['events']:
                events[key] = {
                    "description": found['events'][key]['description'],
                    "time": found['events'][key]['time']
                }

            # update the field
            self.collection.update_one({"channelId": channel_id}, {"$set": {
                "events": events
            }})

    def get_tracking_number(self, channel_id=None):
        if channel_id is not None:
            return self.collection.find_one({"channelId": channel_id})['trackingNumber']
        return None

    def get_events(self, channel_id=None):

        if channel_id is not None:
            events = self.collection.find({
                "channelId": channel_id
            })

        try:
            return events[0]['events']
        except Exception as e:
            return []

    def get_tracking_numbers(self):
        # group these by distinct pairs
        query = self.collection.aggregate([
            {
                "$group": {
                    "_id": {
                        "trackingNumber": "$trackingNumber",
                        "channelId": "$channelId"
                    }
                }
            }
        ])
        return query
