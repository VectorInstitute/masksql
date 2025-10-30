import json


with open("data/dev.json", "r") as f:
    spider_dev = json.load(f)
with open("data/train_spider.json", "r") as f:
    spider_train = json.load(f)

with open("NatSQLv1_6/dev-natsql.json", "r") as f:
    natsql_dev = json.load(f)
with open("NatSQLv1_6/train_spider-natsql.json", "r") as f:
    natsql_train = json.load(f)


assert len(spider_dev) == len(natsql_dev)
assert len(spider_train) == len(natsql_train)

for se, ne in zip(spider_dev, natsql_dev):
    se["NatSQL"] = ne["NatSQL"]
    se["sql"] = ne["sql"]

for se, ne in zip(spider_train, natsql_train):
    se["NatSQL"] = ne["NatSQL"]
    se["sql"] = ne["sql"]


with open("NatSQLv1_6/dev.json", "w") as f:
    json.dump(spider_dev, f, indent=2)
with open("NatSQLv1_6/train_spider.json", "w") as f:
    json.dump(spider_train, f, indent=2)
