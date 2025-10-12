cdv backend#!/usr/bin/env python3
"""
Simple test server for AI Scheduler
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Server is working"}

if __name__ == "__main__":
    print("🚀 Starting simple test server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
