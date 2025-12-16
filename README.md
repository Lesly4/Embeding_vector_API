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

This API includes middleware that logs each request.

Logged data includes:

* HTTP method & URL
* Status code
* Timestamps
* Client IP address 

Useful for debugging and auditing.

---

##  Base URL & Endpoint

This FastAPI server is running locally at :

```
http://127.0.0.1:8000/
```

Main endpoint:

```
POST /convert-text
```

---

##  Local Setup (Development)

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

#### Open your browser and go to: 

```
http://127.0.0.1:8000/
```

#### Swagger UI is available at:

```
http://127.0.0.1:8000/docs
```

---

## 🐳 Docker Usage 

Docker allows you to run the API without installing Python or dependencies locally.

### Prerequisites

- Docker installed: https://docs.docker.com/get-docker/

### 1. Clone the repository

```bash
git clone https://github.com/Lesly4/Embeding_vector_API.git
cd Embeding_vector_API
```

### 2. Build the Docker image
```bash
docker build -t text-to-vector-api .
```

### 3. Run the container
```bash
docker run -p 8000:8000 text-to-vector-api
```

API available at:
```
http://127.0.0.1:8000
```

### 4. Persist model cache (Optional)
```bash
docker run -p 8000:8000 -v hf_models:/models text-to-vector-api
```

### 5. Stop the container
```bash
docker ps
docker stop <CONTAINER_ID>
```

---

##  How to Use the API


### 1. Create a JSON File Containing Your Text

Create a file such as `text.json` and include your text:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

JSON supports long or multiline strings as well.

After creating the JSON file, choose how you want to interact with the API.  


---

### 2. Choose the API Interaction Methods

You can submit requests from the terminal using **`curl`**, use **Postman** for a graphical interface, or interact directly through the built-in **Swagger UI** provided by FastAPI.



## Calling the `/convert-text` Endpoint Using curl

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

## Calling the `/convert-text` Endpoint Using Postman


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

Go to **Body → raw → JSON** and paste your text:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

### Step 5: Send Request

Click **Send**. You’ll receive a JSON response containing the vector embedding.


---


## Calling the `/convert-text` Endpoint Using Swagger UI


FastAPI automatically provides a **Swagger web interface** to explore and test an API.  Swagger UI is a simple way to interact with an API without using `curl` or Post

1. Open your browser and go to:  
```
http://127.0.0.1:8000/docs
```

2. Find the endpoint you want to use (e.g., `/convert-text` in this case) and click **Try it out**.  

3. Enter your input in the JSON body, for example:  
```json
{
  "text": "Your text to convert into a vector"
}
```

4. Click **Execute**. The API response, including the generated embedding vector, will appear below.  



---



##  Architecture Diagram

```
+-------------------+
|  Client (curl /   |
| Postman /         |
| Swagger UI )      |
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
