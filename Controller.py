from flask import Flask, jsonify, request, Response
from pydantic import ValidationError
from Database import init_db, mongo
from Repo import ItemRepository
from Service import ItemService
from Schema import ItemCreate, ItemUpdate, ItemResponse

app = Flask(__name__)
init_db(app)

item_repository = ItemRepository(mongo.db)
item_service = ItemService(item_repository)


# 1. POST
@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = ItemCreate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    new_item = item_service.add_item(data)
    return jsonify(ItemResponse(**new_item).model_dump(by_alias=True)), 201


@app.route('/items', methods=['GET'])
def get_all_items():
    items = item_service.list_items()
    response_data = [ItemResponse(**i).model_dump(by_alias=True) for i in items]
    return jsonify(response_data), 200


@app.route('/items/<string:item_id>', methods=['GET'])
def get_single_item(item_id):
    try:
        item = item_service.get_item(item_id)
        return jsonify(ItemResponse(**item).model_dump(by_alias=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/items/<string:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        data = ItemUpdate(**request.json)
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    try:
        updated_item = item_service.update_item(item_id, data)
        return jsonify(ItemResponse(**updated_item).model_dump(by_alias=True)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/items/<string:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        item_service.remove_item(item_id)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/items', methods=['HEAD'])
def read_items_head():
    items = item_service.list_items()
    res = Response()
    res.headers["X-Total-Count"] = str(len(items))
    return res

@app.route('/items', methods=['OPTIONS'])
def options_items():
    res = Response()
    res.headers["Allow"] = "GET, POST, PUT, DELETE, HEAD, OPTIONS, TRACE"
    return res

@app.route('/items', methods=['TRACE'])
def trace_items():
    headers_str = "\n".join(f"{k}: {v}" for k, v in request.headers.items())
    trace_content = f"TRACE Request Received\nHeaders:\n{headers_str}\nBody: {request.data.decode()}"
    return Response(trace_content, mimetype="message/http")


if __name__ == "__main__":
    app.run(debug=True)