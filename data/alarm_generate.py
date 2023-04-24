from data.kafka_producer import PyProducer

BASE_DATA = {
    "dataReport": {
        "siteId": 1,
        "timestamp": 1679504236246,
        "type": "report",
        "version": 1,
        "status": 0,
        "data": {
            "tmp": 88.8,
            "lx": 168.66,
            "hmt": 0.42
        }
    },
    "monitorItem": {
        "type": "tmp",
        "open": 1,
        "max": 22.2,
        "min": 0.0
    }
}

def gen_alarm(n=1, site_id=1):
    send_date = BASE_DATA
    send_date['dataReport']['siteId'] = site_id
    producer = PyProducer(topic='alarm')
    for i in range(n):
        producer.send_data(BASE_DATA)

if __name__ == '__main__':
    gen_alarm()
