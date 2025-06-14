
# stock-processing
For stock and etf data.

## Setup
    docker compose up -d


### docker-compose.yml maps container port 80 to localhost (127.0.0.1) port 8000 by default.

## Use
    # Using curl

    curl localhost:8000/<asset_type>/<ticker>/<data_type>

    # Returns JSON
    {...}

## Example
    curl localhost:8000/stocks/aapl/quote

    # Returns quote data in JSON
    {...}

## Suggestions
Format JSON output with python module `json`.

### Example
    curl localhost:8000/stocks/apple/quote | python -m json.tool

---

May put API documentation. Look at `main.py` for available routes and data.
