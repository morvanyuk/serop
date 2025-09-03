from arango import ArangoClient
from fastapi import HTTPException
from typing import Literal, Optional

# Підключення до ArangoDB
client = ArangoClient()
db = client.db('test', username='root', password='')  # або без пароля


def all_graphs():
    result = []
    graph_manager = db.graphs()
    for i in graph_manager: result.append(i['name'])
    return result
    

def get_all_nodes_from_graph(graph_name: str,
    text: Optional[str] = None,
    field: Optional[Literal["mod", "name"]] = None,
    limit: int = 20
):
    try: 
        graph = db.graph(graph_name)
    except:
        return f"{graph_name} graph not found"
    vertex_collections = graph.vertex_collections()

    all_nodes = []

    # Пройтись по всіх колекціях вузлів
    for vc_name in vertex_collections:
        vertex_collection = graph.vertex_collection(vc_name)
        nodes = list(vertex_collection.all())
        print(vc_name, graph_name)
        for node in nodes:
            # Пошук
            if text is not None:
                if field == "name":
                    if str(text).lower() not in node["name"].lower():
                        continue
                else:
                    if str(text).lower() not in node["mod"].lower():
                        continue
            node["is_elementar"] = "Так"
            # Знайти ціну,якщо предмет не елементарний
            if not isinstance(node["price"], (int, float)):
                print(node["name"], node["price"])
                node["price"] = calculate_price(object_id=node["_id"], graph=graph_name)
                node["is_elementar"] = "Ні"

            all_nodes.append({"id" : node["_id"], "name" : node["name"], "mod" : node["mod"],  
                               "price" : node["price"], "is_elementar" : node["is_elementar"]})
    return all_nodes[0:limit]


def create_graph(graph_name):
    if not db.has_graph(graph_name):
        graph = db.create_graph(graph_name)
    else:
        graph = db.graph(graph_name)

    vertex_collection = f"{graph_name}_items"
    edge_collection = f"{graph_name}_edges"

    # Створення вершини (vertex collection)
    if not graph.has_vertex_collection(vertex_collection):
        graph.create_vertex_collection(vertex_collection)

    # Створення реберної колекції (edge definition)
    if not graph.has_edge_definition(edge_collection):
        edge_definition = {
            'edge_collection': edge_collection,
            'from_vertex_collections': [vertex_collection],
            'to_vertex_collections': [vertex_collection],
        }
        graph.create_edge_definition(**edge_definition)


def create_node(fields):
    graph_name = fields.pop("graph")

    graph = db.graph(graph_name)
    items = graph.vertex_collection(f"{graph_name}_items")
    items.insert(fields)

def delete_node(fields):
    id_element = fields["id_element"]
    graph_name = fields["graph"]

    aql = """
    RETURN LENGTH(
        FOR v, e IN 1..1 OUTBOUND @id_element GRAPH @graph
            LIMIT 1
            RETURN 1
    ) > 0
    """

    bind_vars = {
        "id_element": id_element,
        "graph": graph_name
    }

    # Виконати AQL
    cursor = db.aql.execute(aql, bind_vars=bind_vars)
    has_edges = list(cursor)[0]

    if has_edges:
        raise HTTPException(status_code=400, detail=f"Вузол {id_element} має вихідні ребра і не може бути видалений.")

    # Інакше — видалити вузол
    collection_name = id_element.split('/')[0]
    collection = db.collection(collection_name)

    if collection.has(id_element):
        collection.delete(id_element)
        delete_edges_query = """
        FOR edge IN @@edge_collection
            FILTER edge._to == @id_element
            REMOVE edge IN @@edge_collection
        """


        db.aql.execute(
            delete_edges_query,
            bind_vars={
                "id_element": id_element,
                "@edge_collection": collection_name
            }
        )
    else:
        raise HTTPException(status_code=404, detail=f"Вузол {id_element} не знайдено.")

def update_node(fields):
    collection = fields.pop("graph")
    graph = db.graph(collection)

    vertex_collection = graph.vertex_collection(collection + "_items")
    vertex = vertex_collection.get(fields["id_element"].split("/")[1])

    if not isinstance(vertex["price"], (int, float)):
        fields.pop("price")

    fields['_id'] = fields['id_element']
    del fields['id_element']

    vertex_collection.update(fields)

def craft(fields):
    node = fields.pop('key')
    parents = fields.pop('parents')
    plus_5_percent = fields.pop('plus5')
    graph = fields.pop('graph')

    vertex_collection = f"{graph}_items"
    edge_collection = f"{graph}_edges"

    checkEdges = """
    FOR edge IN @@edge
        FILTER edge._to == @key
        LIMIT 1
        RETURN edge
    """

    bind_vars = {
        "@edge": edge_collection,
        "key": node
    }

    cursor = db.aql.execute(checkEdges, bind_vars=bind_vars)
    edges = list(cursor)
    
    if edges:
        raise HTTPException(
            status_code=409,
            detail={
                "status": "error",
                "message": f"{node} Вже має попередній крафт.",
            }
        )
    
    js_code = """
        function (params) {
            const db = require('@arangodb').db;

            const node = params.key;
            const parents = params.parents;
            const edgeCollection = db._collection(params.edge_collection);
            const vertexCollection = db._collection(params.vertex_collection);

            // Оновлюємо вузол
            vertexCollection.update(node, { price: "None" });

            // Додаємо ребра
            for (const parentKey in parents) {
                // if (!Object.prototype.hasOwnProperty.call(parents, parentKey)) continue;

                const edge = {
                    _from: parentKey,
                    _to: node,
                    plus_5_percent: params.plus_5_percent,
                    number: parents[parentKey]
                };

                edgeCollection.save(edge);
            }

            return { success: true };
        }
    """

    bind_vars = {
        "key": node,
        "parents": parents,
        "plus_5_percent": plus_5_percent,
        "vertex_collection": vertex_collection,
        "edge_collection": edge_collection
    }


    db.execute_transaction(
        js_code,
        write=[vertex_collection, edge_collection],  # колекції для запису
        read=[],                  # колекції для читання
        params=bind_vars,
    )

    query = """
    FOR v IN 1..10000 INBOUND @key @@edge
        UPDATE v WITH {
            childNodes: APPEND(
                HAS(v, "childNodes") ? v.childNodes : [],
                [@key],
                true
            )
        } IN @@vertex
    """

    bind_vars = {
        "key": node,
        "@edge": edge_collection,
        "@vertex": vertex_collection
    }

    db.aql.execute(query, bind_vars=bind_vars)


def calculate_price(object_id, graph):
    get_elementary_items = """

    FOR v IN @@vertex_collection
    FILTER LENGTH(
        FOR e IN @@edge_collection
        FILTER e._to == v._id
        LIMIT 1
        RETURN 1
    ) == 0
    AND @key IN v.childNodes

    RETURN {
        _id: v._id,
        price: v.price,
        name: v.name
    }

    """

    bind_data1 = {
        "key": object_id,
        "@edge_collection": f"{graph}_edges", 
        "@vertex_collection": f"{graph}_items"   
    }

    sum_price = """
        FOR item IN @parents
            FOR node, edge IN 1..1 OUTBOUND item GRAPH @graph
                FILTER @key IN node.childNodes OR node._id == @key

                LET number = HAS(edge, "number") && IS_NUMBER(edge.number) ? edge.number : 1

                // Додаємо +5% тільки за умов:
                // - plus_5_percent == true
                // - item не є кінцевим (end != "true")
                // - node не є шуканим (node._id != @key)
                LET add_bonus = edge.plus_5_percent 
                                && item.end != "true" 
                                && node._id != @key

                LET base_price = add_bonus ? item.price * 1.05 : item.price
                 LET new_price = item.end != "true" ? base_price * number : base_price

                RETURN 
                    node._id == @key || item.end == "true"
                        ? { "_id": item._id, "name": item.name, "price": new_price, "end": "true" }
                        : { "_id": node._id, "name": node.name, "price": new_price }




    """

    check_plus_5_percent = f"""
        FOR node, edge IN 1..1 INBOUND @key GRAPH {graph}
            LIMIT 1

            RETURN edge.plus_5_percent ? true : false

    """


    elementary_items_query = db.aql.execute(get_elementary_items, bind_vars=bind_data1)

    elementary_items = []

    for item in elementary_items_query: elementary_items.append(item)

    print(elementary_items)
    

    def recursive_calc(data):
        bind_vars = {
            "key": object_id, 
            "parents": data,
            "graph" : graph
        }
        result = db.aql.execute(sum_price, bind_vars=bind_vars)

        # for i in result: print(i)
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

        print(final_result)

        
        # print(final_result)

        calc = 0
        sum_value = 0

        for item in final_result:
            if not "end" in item:
                calc += 1


        if calc == 0:
            
            check_plus = db.aql.execute(check_plus_5_percent, bind_vars={"key": object_id})
            for i in final_result:
                sum_value += i['price']
            for i in check_plus:
                if i == True: sum_value = sum_value * 1.05
            print(sum_value)
            return sum_value

        bind_vars['parents'] = final_result

        return recursive_calc(final_result)


    return recursive_calc(elementary_items)

        
