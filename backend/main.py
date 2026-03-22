from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import json
import re
from rag import search, generate_natural_response
from typing import List

# 🧠 Chat memory
chat_history: List[dict] = []

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow frontend on any host
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
with open("data/hostel_data.json") as f:
    data = json.load(f)

@app.get("/")
def home():
    return {"message": "Hostel Chatbot API running"}

@app.get("/rooms")
def get_rooms():
    return data["rooms"]

@app.get("/available-rooms")
def available_rooms():
    return [room for room in data["rooms"] if room["available"]]

@app.get("/mess-menu")
def mess_menu():
    return data["mess"]

# 🤖 Chat endpoint
@app.post("/chat")
def chat(user_query: str):
    query = user_query.lower()
    # 🖐 Handle greetings
    greetings = ["hi", "hello", "hey", "good morning", "good evening"]

    if any(word in query for word in greetings):
        response = "Hello! 👋 Ask me about hostel rooms or mess menu."
        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}
    response = ""
    context = ""

    # 🧠 Save user message
    chat_history.append({"role": "user", "content": user_query})

    # 🧠 Build last 3 messages context for RAG
    history_context = ""
    for msg in chat_history[-3:]:
        history_context += f"{msg['role']}: {msg['content']}\n"

    # 🔥 CHEAPEST ROOM
    if "cheap" in query or "cheaper" in query:
        available_rooms = [r for r in data["rooms"] if r["available"]]
        if not available_rooms:
            response = "No rooms available right now."
        else:
            cheapest = min(available_rooms, key=lambda x: x["price"])
            response = f"The cheapest available room is {cheapest['room_id']} costing ₹{cheapest['price']}."
        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # ❄️ AC follow-up
    if "ac" in query:
        last_rooms = [msg["content"] for msg in chat_history if "Room" in msg["content"]]
        if last_rooms:
            # Extract room IDs from last room suggestion
            last_room_ids = re.findall(r"\bF\dR\d{2}\b", last_rooms[-1])
            ac_rooms = [r['room_id'] for r in data["rooms"] if r['room_id'] in last_room_ids and "AC" in r["facilities"]]
            response = f"Yes, these rooms have AC: {', '.join(ac_rooms)}." if ac_rooms else "No, those rooms do not have AC."
        else:
            response = "Please ask about rooms first."
        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 🏨 FILTER ROOMS BASED ON TYPE / PRICE / AVAILABILITY / FACILITIES
    price_match = re.search(r'\d+', query)
    max_price = int(price_match.group()) if price_match else None

    room_type = None
    if "single" in query:
        room_type = "single"
    elif "double" in query:
        room_type = "double"
    elif "triple" in query:
        room_type = "triple"

    need_ac = "ac" in query
    need_wifi = "wifi" in query

    filtered_rooms = data["rooms"]

    if "available" in query:
        filtered_rooms = [r for r in filtered_rooms if r["available"]]

    if room_type:
        filtered_rooms = [r for r in filtered_rooms if r["type"] == room_type]

    if max_price:
        filtered_rooms = [r for r in filtered_rooms if r["price"] <= max_price]

    if need_ac:
        filtered_rooms = [r for r in filtered_rooms if "AC" in r["facilities"]]

    if need_wifi:
        filtered_rooms = [r for r in filtered_rooms if "WiFi" in r["facilities"]]

    # 🎯 IF FILTERED ROOMS ARE FOUND
    if filtered_rooms != data["rooms"]:
        if not filtered_rooms:
            response = "No rooms match your criteria."
        else:
            response = "Here are some rooms you might like:\n\n"

            for room in filtered_rooms:
                response += f"🏠 Room {room['room_id']} ({room['type']})\n"
                response += f"💰 Price: ₹{room['price']}\n"
                response += f"🛠 Facilities: {', '.join(room['facilities'])}\n\n"

        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 🍛 MESS MENU
    if "mess" in query or "food" in query:
        context = ""
        for day, menu in data["mess"].items():
            context += f"{day}: {menu}. "

        response = generate_natural_response(history_context + context, user_query)
        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 🔍 DEFAULT RAG
    results = search(user_query)
    context = " ".join(results)

    response = context
    chat_history.append({"role": "assistant", "content": response})

    return {"response": response}