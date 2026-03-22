import json
import random

floors = 8
rooms_per_floor = 21

room_types = ["single", "double", "triple"]

base_facilities = [
    "Bed", "Mattress", "Pillow", "Wardrobe",
    "Study Table", "Chair", "Fan",
    "High-Speed WiFi"
]

extra_facilities = [
    "AC", "Geyser", "Balcony",
    "Co-living Space", "Common Lounge",
    "Daily Cleaning", "Laundry Service"
]

data = {
    "rooms": [],
    "mess": {
        "Monday": "Rice, Dal, Paneer, Roti",
        "Tuesday": "Fried Rice, Manchurian",
        "Wednesday": "Chapati, Sabzi, Curd",
        "Thursday": "Rajma, Rice, Salad",
        "Friday": "Pulao, Raita",
        "Saturday": "Noodles, Soup",
        "Sunday": "Special Meal (Chicken/Paneer)"
    },
    "rules": [
        "No smoking",
        "No loud music after 10 PM",
        "Visitors allowed till 8 PM",
        "Maintain cleanliness"
    ]
}

for floor in range(1, floors + 1):
    for room in range(1, rooms_per_floor + 1):

        room_type = random.choice(room_types)

        # 💰 Pricing logic
        if room_type == "single":
            price = random.randint(9000, 14000)
        elif room_type == "double":
            price = random.randint(6000, 9000)
        else:
            price = random.randint(4000, 6000)

        # 🏠 Facilities logic
        facilities = base_facilities.copy()

        # Bathroom type
        if room_type == "single":
            facilities.append("Attached Bathroom")
        else:
            if random.random() > 0.5:
                facilities.append("Attached Bathroom")
            else:
                facilities.append("Shared Bathroom")

        # Random extras
        facilities += random.sample(extra_facilities, k=random.randint(2, 5))

        # Ensure AC not everywhere
        if "AC" in facilities and random.random() > 0.6:
            facilities.remove("AC")

        room_data = {
            "room_id": f"F{floor}R{room:02}",
            "floor": floor,
            "type": room_type,
            "price": price,
            "facilities": facilities,
            "available": random.choice([True, False]),
            "rating": round(random.uniform(3.5, 5.0), 1)
        }

        data["rooms"].append(room_data)

# Save JSON
with open("data/hostel_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ Advanced dataset generated!")