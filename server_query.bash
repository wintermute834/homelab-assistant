
curl -s http://192.168.0.210:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "LFM2.5-2.6B",
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "python",
                    "description": "Runs code in an ipython interpreter and returns the result of the execution after 60 seconds.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "The code to run in the ipython interpreter."
                            }
                        },
                        "required": ["code"]
                    }
                }
            }
        ],
        "messages": [
            {
                "role": "system",
                "content": "You are an AI assistant. Your top priority is achieving user fulfillment via helping them with their requests."
            },
            {
                "role": "user",
                "content": "Call a python script to print hello world"
            }
        ]
    }'
