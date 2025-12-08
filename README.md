#  Text-to-Vector Embedding API

A simple and efficient FastAPI service for converting any length of text into a vector embedding.

---

##  Overview

This API allows you to convert arbitrary-length text into vector embeddings.
It is designed to be:

*  **Easy to use**
*  **Fast** (powered by FastAPI)
*  **Flexible** (no URL-length limits thanks to JSON body input)

Ideal for semantic search, or any workflow requiring text embeddings.

---

##  Base URL & Endpoint

Assuming your FastAPI server is running locally:

```
http://127.0.0.1:8000/
```

Main endpoint:

```
POST /convert-text
```

Example handler:

```python
@app.post("/convert-text")
def converter(input_data: TextInput):
    ...
```

---

##  How to Use the API

### 1️⃣ Create a JSON File Containing Your Text

Create a file such as `text.json` and include your text:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

JSON supports long or multiline strings as well.

---

### 2️⃣ Send a POST Request with cURL

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/json" \
     -d @text.json
```

`@text.json` tells `curl` to read the JSON body from the file `text.json`.

If your JSON file is located elsewhere, specify the full path:

```bash
-d @"/home/user/documents/text.json"
```

---

##  Using Postman to Call the `/convert-text` Endpoint

### Step 1: Open Postman

Download Postman: [https://www.postman.com/downloads/](https://www.postman.com/downloads/)

### Step 2: Create a New POST Request

1. Click **New → HTTP Request**
2. Set method: **POST**
3. URL: `http://127.0.0.1:8000/convert-text`

### Step 3: Configure Headers and Authorization 

1. Go to the **Headers** tab and set:

| Key           | Value              |
|---------------|------------------|
| Content-Type  | application/json |

2. Go to the **Authorization** tab (or alternatively, add a new header) and set:

| Key       | Value              |
|-----------|------------------|
| X-API-Key | your_api_key_here |

This ensures your request includes the correct content type and your API key for authentication.

### Step 4: Add JSON Body

Go to **Body → raw → JSON** and paste:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

### Step 5: Send Request

Click **Send**. You’ll receive a JSON response containing the vector embedding.

---

##  Logging

The API includes middleware that logs each request:

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Completed request: {request.method} {request.url} - Status {response.status_code}")
    return response
```

Logged data includes:

* HTTP method & URL
* Status code
* Timestamps

Useful for debugging and auditing.

---

##  Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Lesly4/Embeding_vector_API.git
cd Embeding_vector_API
```

### 2. Create & activate a virtual environment

```bash
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run FastAPI

```bash
uvicorn main:app --reload
```

Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

---

##  Architecture Diagram

```
+-------------------+
|  Client (curl /   |
|  Postman / Python)|
+---------+---------+
          |
          v
+-------------------+
|  FastAPI Server   |
|  (main.py)        |
+---------+---------+
          |
          v
+-------------------+
|  Tokenizer +      |
|  Embedding Model  |
+---------+---------+
          |
          v
+-------------------+
|  JSON Response    |
|  with Vector      |
+-------------------+
```

---

##  Workflow Diagram

```
[User sends text JSON] 
           |
           v
  [POST /convert-text endpoint]
           |
           v
 [FastAPI middleware logs request]
           |
           v
  [Text -> Tokenizer -> Model]
           |
           v
 [Embedding vector generated]
           |
           v
[FastAPI sends JSON response]
           |
           v
 [Middleware logs completion]
```

---

##  Contributing

Contributions, issues, and feature requests are welcome.

---

##  License

MIT License
