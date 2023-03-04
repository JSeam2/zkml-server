# ZKML Server

## Quickstart (WIP)
1. ~~[Install EZKL](https://github.com/zkonduit/ezkl)~~ It's not that straightforward
2. Install python packages using pipenv
3. Run the server `python app.py`

## Endpoints

- `/` [GET]

**Description:**
Index page and liveness check

**Returns**
```
Extend your smart contracts with Gelkin
```

-----

- `/upload/inputdata` [POST]

**Description**
Uploads the input.json into the server and stores as some uuid4

**Params**
Provide file via `inputdata` as a form

**Returns**
Json from server
```json
{
    "file": "uuid4value.json"
}
```

-----

- `/list/inputdata` [GET]

**Description**
Lists all the input data stored on the server

**Returns**
Json from server
```json
{
    "list": ["uuid4value.json", "uuid4value.json"]
}
```

-----

- `/upload/onnxmodel` [POST]

**Description**
Uploads the network.onnx into the server and stores as some uuid4

**Params**
Provide file via `onnxmodel` as a form

**Returns**
Json from server
```json
{
    "file": "uuid4value.onnx"
}
```

-----

- `/list/onnxmodel` [GET]

**Description**
Lists all the onnx model data stored on the server

**Returns**
Json from server
```json
{
    "list": ["uuid4value.onnx", "uuid4value.onnx"]
}
```