from graph import craft, calculate_price

data = {
  "key": "1234577",
  "parents": {
    "1234573": 2,
    "1234572": 2,
  },
  "plus_5_percent": False
}

data2 = {
  "key": "1234574",
  "parents": {
    "1234577": 1,
    "1234580": 1,
  },
  "plus_5_percent": True
}

data3 = {
  "key": "1234574",
  "parents": {
    "1234575": 1,
    "1234578": 1,
    "1234574": 1,
  },
  "plus_5_percent": True
}


# craft(data)
# craft(data2)
craft(data3)
# calculate_price()