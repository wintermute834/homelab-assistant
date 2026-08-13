
# replace 127.0.0.1 with the address of each machine
machine1 = "http://127.0.0.1" # has llama.cpp server
machine2 = "http://127.0.0.1"
machine3 = "http://127.0.0.1"
machine4 = "http://127.0.0.1"

LLAMA_URL = f"{machine1}:8080"

SHIM_URLS = [
    f"{machine1}:8765",
    f"{machine2}:8765",
    f"{machine3}:8765",
    f"{machine4}:8765"
]
