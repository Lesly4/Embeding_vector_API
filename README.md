# Text-to-Vector Embedding API

This API allows you to convert **any length of text** into a vector embedding.
It uses a clean and universal JSON-based POST request approach, avoiding URL length limits and inconvenient encoding issues.

##  Running the API

Assuming your FastAPI application is running at:

```
http://127.0.0.1:8000/
```

and the embedding endpoint is defined as:

```python
@app.post("/convert-text")
def converter(input_data: TextInput):
    ...
```

---

## 📄 1. Prepare Your Input Text (JSON)

Create a JSON file containing the text you want to convert.

Example: create **text.json** with your content:

```json
{
  "text": "This is the text I want to convert into a vector embedding."
}
```

You can include **very long text**—JSON fully supports multiline strings.

---

## 📤 2. Send a POST Request Using curl

Use `curl` to send the JSON file to your FastAPI endpoint:

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/json" \
     -d @text.json
```

The `@text.json` syntax tells `curl`:

> “Read the file *text.json* from the current working directory and send it as the request body.”

If your JSON file is stored elsewhere, specify the full path:

```bash
curl -X POST "http://127.0.0.1:8000/convert-text" \
     -H "Content-Type: application/json" \
     -d @"/home/user/myfiles/text.json"
```

---

## ✅ Response

The API will return the vector embedding as a JSON array.

---


## 📌 Notes

* There is **no text size limit** because data is passed in the body, not the URL.
* Ideal for long documents, research papers, logs, or streaming text.

