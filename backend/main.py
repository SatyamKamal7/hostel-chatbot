from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import json
import re
from typing import List

# 🧠 Chat memory
chat_history: List[dict] = []

app = FastAPI()

# ✅ CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Request body model
class ChatRequest(BaseModel):
    user_query: str

# 📂 Load data
with open("data/hostel_data.json") as f:
    data = json.load(f)


@app.get("/")
def home():
    return {"message": "Hostel Chatbot API running 🚀"}


@app.get("/rooms")
def get_rooms():
    return data["rooms"]


@app.get("/available-rooms")
def available_rooms():
    return [room for room in data["rooms"] if room["available"]]


@app.get("/mess-menu")
def mess_menu():
    return data["mess"]


# 🤖 CHAT API
@app.post("/chat")
def chat(request: ChatRequest):
    user_query = request.user_query
    query = user_query.lower()

    response = ""

    # 🧠 Save user message
    chat_history.append({"role": "user", "content": user_query})

    # 🔹 Handle greetings
    if query in ["hi", "hello", "hey"]:
        response = "Hi! 😊 How can I help you with hostel rooms today?"

        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 💰 Cheapest room
    if "cheap" in query or "cheaper" in query:
        available_rooms = [r for r in data["rooms"] if r["available"]]

        if not available_rooms:
            response = "No rooms available right now."
        else:
            cheapest = min(available_rooms, key=lambda x: x["price"])
            response = f"The cheapest available room is 🏠 {cheapest['room_id']} costing ₹{cheapest['price']}."

        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # ❄️ AC follow-up
    if "ac" in query:
        last_rooms = [msg["content"] for msg in chat_history if "Room" in msg["content"]]

        if last_rooms:
            ac_rooms = []
            for room in data["rooms"]:
                if room["room_id"] in last_rooms[-1] and "AC" in room["facilities"]:
                    ac_rooms.append(room["room_id"])

            if ac_rooms:
                response = f"Yes ❄️, these rooms have AC: {', '.join(ac_rooms)}."
            else:
                response = "No ❌, those rooms do not have AC."
        else:
            response = "Please ask about rooms first 😊."

        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 🎯 FILTER LOGIC
    price_match = re.search(r'\d+', query)
    max_price = int(price_match.group()) if price_match else None

    room_type = None
    if "single" in query:
        room_type = "single"
    elif "double" in query:
        room_type = "double"
    elif "triple" in query:
        room_type = "triple"

    filtered_rooms = data["rooms"]

    if "available" in query:
        filtered_rooms = [r for r in filtered_rooms if r["available"]]

    if room_type:
        filtered_rooms = [r for r in filtered_rooms if r["type"] == room_type]

    if max_price:
        filtered_rooms = [r for r in filtered_rooms if r["price"] <= max_price]

    # 🎯 IF FILTER APPLIED
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

    # 🍽 Mess menu
    if "mess" in query:
        response = "Here is the weekly mess menu:\n\n"

        for day, menu in data["mess"].items():
            response += f"📅 {day}: {menu}\n"

        chat_history.append({"role": "assistant", "content": response})
        return {"response": response}

    # 🤖 Default fallback
    response = "I'm here to help! 😊 You can ask me about rooms, prices, availability, or facilities."

    chat_history.append({"role": "assistant", "content": response})
    return {"response": response}