from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ✅ Load FLAN-T5 (instruction model)
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

# ✅ Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# ✅ Load data
with open("data/hostel_data.json") as f:
    data = json.load(f)

# ✅ Create documents (BETTER STRUCTURE)
documents = []

for room in data["rooms"]:
    text = f"""
Room {room['room_id']}:
Type: {room['type']}
Price: ₹{room['price']} per month
Facilities: {', '.join(room['facilities'])}
Available: {room['available']}
"""
    documents.append(text)

for day, menu in data["mess"].items():
    documents.append(f"{day} mess menu is {menu}")

for rule in data["rules"]:
    documents.append(f"Rule: {rule}")

# ✅ Create embeddings
embeddings = embed_model.encode(documents)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings))


# 🔍 Search
def search(query, k=3):
    query_vector = embed_model.encode([query])
    distances, indices = index.search(np.array(query_vector), k)
    return [documents[i] for i in indices[0]]


# 🧠 Generate better response
def generate_natural_response(context, query):
    prompt = f"""
You are a hostel assistant chatbot.

Your job is to give COMPLETE and FRIENDLY answers.

STRICT INSTRUCTIONS:
- Never give one-word answers
- Always explain properly
- Always include room price when relevant
- Always mention room type
- Write like you are talking to a student

Context:
{context}

User Question:
{query}

Final Answer (detailed and friendly):
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_length=200,   # 🔥 increased
        temperature=0.8,  # 🔥 more expressive
        do_sample=True    # 🔥 avoids short boring outputs
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()