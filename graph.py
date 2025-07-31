from arango import ArangoClient

# Підключення до ArangoDB
client = ArangoClient()
db = client.db('test', username='root', password='')  # або без пароля

# Створення графа (якщо ще не існує)
if not db.has_graph('graphs'):
    graph = db.create_graph('graphs')
else:
    graph = db.graph('graphs')

# Створення вершини (vertex collection)
if not graph.has_vertex_collection('items'):
    graph.create_vertex_collection('items')

# Створення реберної колекції (edge definition)
if not graph.has_edge_definition('items_edge'):
    edge_definition = {
        'edge_collection': 'items_edge',
        'from_vertex_collections': ['items'],
        'to_vertex_collections': ['items'],
    }
    graph.create_edge_definition(**edge_definition)



def create_nodes(fields):
    items = graph.vertex_collection('items')
    items.insert(fields)

def craft(fields):
    node = fields.pop('key')
    parents = fields.pop('parents')
    plus_5_percent = fields.pop('plus_5_percent')

    print(node, parents, plus_5_percent)

    js_code = """
        function (params) {
            const db = require('@arangodb').db;

            const node = params.key;
            const parents = params.parents
            const edges = db._collection('items_edge')

            db.items.update(node, {"price": "None"} );
            
    
            for (const itemKey in parents) {
                // if (!Object.hasOwn(parents, itemKey)) continue;

                const edge = {
                    _from: `items/${itemKey}`,
                    _to: `${node}`,
                    plus_5_percent: params.plus_5_percent,
                    count: parents[itemKey]
                };

                db.items_edge.save(edge);
            }
        }
    """

    query = """

        FOR v IN 1..10000 INBOUND @key items_edge
            UPDATE v WITH {
                childNodes: APPEND(
                    HAS(v, "childNodes") ? v.childNodes : [],
                    [@key],
                    true
                )
            } IN items

    """


    bind_vars = {
        "key": f"items/{node}",
        "parents": parents,
        "plus_5_percent": plus_5_percent
    }


    db.execute_transaction(
        js_code,
        write=['items', 'items_edge'],  # колекції для запису
        read=[],                  # колекції для читання
        params=bind_vars,
    )

    db.aql.execute(query, bind_vars={"key": f"items/{node}",})
    

def calculate_price():
    get_elementary_items = """

        FOR v, node_edges, p IN 1..10000 INBOUND 'items/1234576' items_edge
            FILTER LENGTH(
                FOR e IN items_edge
                    FILTER e._to == v._id
                    LIMIT 1
                    RETURN 1
                ) <= 0

            RETURN {"_id" : v._id, "price" : v.price, "name" : v.name}

    """

    sum_price = """

        FOR item IN @parents

            FOR node, edge IN 1..1 OUTBOUND item GRAPH "graphs"
                FILTER @key IN node.childNodes OR node._id == @key

                LET new_price = edge.plus_5_percent ? item.price * 1.05 : item.price

                RETURN node._id == @key OR item.end == "true" ? 
                { "_id": item._id, "price": item.price, "end": "true" } : 
                { "_id": node._id, "price": new_price }



    """

    check_plus_5_percent = """
        FOR node, edge IN 1..1 INBOUND @key GRAPH "graphs"
            LIMIT 1

            RETURN edge.plus_5_percent ? true : false

    """


    elementary_items = db.aql.execute(get_elementary_items)

    data = []

    for item in elementary_items: data.append(item)
    

    def recursive_calc(data):
        bind_vars = {
            "key": f"items/{1234576}", 
            "parents": data
        }
        result = db.aql.execute(sum_price, bind_vars=bind_vars)
        
        # Преберання дублікатів
        combined = {}

        for item in result:
            item_id = item["_id"]
            price = item["price"]
            name = item.get("name")
            has_end = item.get("end") == "true"

            if item_id in combined:
                combined[item_id]["price"] += price
                if has_end:
                    combined[item_id]["end"] = "true"
            else:
                combined[item_id] = {
                    "_id": item_id,
                    "name": name,
                    "price": price
                }
                if has_end:
                    combined[item_id]["end"] = "true"

        final_result = list(combined.values())

        calc = 0
        sum_value = 0

        for item in final_result:
            if not "end" in item:
                calc += 1


        if calc == 0:
            check_plus = db.aql.execute(check_plus_5_percent, bind_vars={"key": f"items/{1234576}"})
            for i in final_result:
                sum_value += i['price']
            for i in check_plus:
                if i == True: sum_value = sum_value * 1.05 
            print(sum_value)
            return sum_value

        bind_vars['parents'] = final_result

        recursive_calc(final_result)


    recursive_calc(data)

        
