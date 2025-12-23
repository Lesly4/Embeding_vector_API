#  Text-to-Vector Embedding API

A simple and efficient FastAPI service for converting any length of text into a vector embedding.

---

##  Overview

This API allows you to convert arbitrary-length text into vector embeddings.
It is designed to be:

*  **Easy to use**
*  **Fast** (powered by FastAPI)
*  **Flexible** (supports JSON, plain text, and PDF inputs)

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

---

<<<<<<< HEAD
## Docker Usage 
=======
##  Docker Usage 
>>>>>>> fd0e0813d7d4784a3718954a12dad6407ac4dbb0

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

### 4. Persistent Logs with a Bind Mount

To ensure API logs are **persisted outside the Docker container** and not lost when the container stops or is rebuilt, this project uses a **bind mount**.

A bind mount maps a directory on the host machine to a directory inside the container, allowing logs to be written directly to the host filesystem.

#### Why a Bind Mount?

- Logs remain available even if the container is stopped or deleted.
- Easy to inspect logs directly from the host machine.
- Ideal for development and debugging.
- No Docker-managed volumes required.


#### Run the Container with a Bind Mount

```bash
docker run -p 8000:8000 \
  -v $(pwd)/logs:/app/logs \
  text-to-vector-api
```

**Explanation:**

- /app/logs → directory inside the container where logs are written.

- ./logs → directory on the host where logs are persisted.


### 5. Stop the container
```bash
docker ps
docker stop <CONTAINER_ID>
```

##### Inspecting the Contents of a Running Container


You can inspect what is inside a running container by opening an interactive shell.

**Step 1**: List Running Containers

```bash
docker ps
```


**Step 2**: Open a Shell Inside the Container


```bash
docker exec -it <CONTAINER_ID> /bin/bash
```

If bash is not available, use:


```bash
docker exec -it <CONTAINER_ID> /bin/sh
```

**Step 3**: Explore the Container Filesystem

Once inside the container, you can inspect files normally:

```bash
ls
cd /app/logs
ls
cat api-YYYY-MM-DD.log
```


**Step 4**: Exit the Container

```bash
exit
```

---

##  How to Use the API

The API accepts text input in **JSON**, **plain text**, or **PDF**.


### Choose the API Interaction Methods

You can submit requests from the terminal using **`curl`**, use **Postman** for a graphical interface, or interact directly through the built-in **Swagger UI** provided by FastAPI.

## Calling the `/convert-text` Endpoint Using curl

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/json" \
     -H "My-API-Key: your-api-key-value-here" \
     -d @text.json
```



### JSON Input

Create `text.json`:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

Send with curl:

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/json" \
     -H "My-API-Key: your-api-key-value" \
     -d @text.json
```

`@text.json` tells `curl` to read the JSON body from the file `text.json` in the current working directory.

If your JSON file is located elsewhere, specify the full path:

```bash
-d @"/home/user/documents/text.json"
```


### Plain Text Input

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: text/plain" \
     -H "My-API-Key: your-api-key-value" \
     --data "This is my plain text input for embedding."
```

### PDF Input

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/pdf" \
     -H "My-API-Key: your-api-key-value" \
     --data-binary @ML.pdf
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

| Key           | Value                   |
|---------------|-------------------------|
| Content-Type  |application/json/text/pdf|

2. Go to the **Authorization** tab (or alternatively, add a new header) and set:

| Key       | Value                    |
|-----------|--------------------------|
| My-API-Key | your_api_key_value_here |

This ensures your request includes the correct content type and your API key for authentication.

### Step 4: Set body type


3. Set body type:

* **JSON** : *Body → raw → JSON*
* **Plain text** : *Body → raw → Text*
* **PDF** :  *Body →  binary → select PDF file*


### Step 5: Send Request

Click **Send**. You’ll receive a JSON response containing the vector embedding.


---


## Calling the `/convert-text` Endpoint Using Swagger UI (only for json body)


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
