import requests
base_url = "http://127.0.0.1:8000"
print(requests.get(f"{base_url}/").json())
print(requests.get(f"{base_url}/items/0").json())
print(requests.get(f"{base_url}/items/57").json())
print(requests.get(f"{base_url}/items/abc").json())
print()
print(requests.get(f"{base_url}/items?name=Nails").json())
print("\n POST an item")
print(
    requests.post(
        f"{base_url}",
        json={"name": "Screwdriver", "price": 3.99, "count": 10, "id": 4, "category": "tools"}
    ).json()
)
print(requests.get("http://127.0.0.1:8000/").json())

print("\n UPDATE an item")
print(requests.put(f"{base_url}/items/0?count=9001").json())
print(requests.get(f"{base_url}/items/0").json())

print("\n DELETE an item")
print(requests.delete(f"{base_url}/items/0").json())
print(requests.get(f"{base_url}/").json())

print("request fails because 'ingredient' is not a valid category")
print(requests.get(f"{base_url}/items?category=ingredient").json())

print("request fails because of the specified type hints on the endpoint")
print(requests.get(f"{base_url}/items/?count=Hello").json())

print("fails also on the specified type hints of the endpoint")
print(
    requests.post(
        base_url,
        json={"name": "ScrewDriver", "price": 3.99, "count": "Hello", "id": 4}
    ).json()
)