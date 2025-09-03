from graph import craft, calculate_price, get_all_nodes_from_graph

data = {
  "key": "1234574",
  "parents": {
    "1234573": 1,
    "1234572": 1,
  },
  "plus_5_percent": False
}

data2 = {
  "key": "1234576",
  "parents": {
    "1234574": 1,
    "1234578": 1,
    "1234575": 1,
  },
  "plus_5_percent": False
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

# print(get_all_nodes_from_graph(graph_name="graphs", field='mod', text="d"))
# craft(data)
# craft(data2)
# craft(data3)
calculate_price(object_id="test_items/365268", graph="test")