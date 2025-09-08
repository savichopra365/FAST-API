import asyncio
from fastapi import FastAPI, Response
from fastapi. responses import HTMLResponse
from starlette.responses import StreamingResponse
import uvicorn
import os

app = FastAPI()
TEXT_FILE_PATH = "sample.txt"

async def read_file_in_realtime(file_path: str):
    """
    An async generator that reads new lines from a file as they are appended.
    Simulates 'tail -f'.:
    """
    with open(file_path, "r") as f:
        # Seek to the end of the file initially
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                # No new line, wait a bit and try again
                await asyncio.sleep(0.1)
                continue
            yield line

@app.get("/stream-log")
async def stream_log_file():
    """
    Endpoint to stream the log file content via Server-Sent Events.
    """
    async def event_generator():
        async for line in read_file_in_realtime(TEXT_FILE_PATH):
            # SSE format: data: <your_data>\n\n
            yield f"data: {line}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Serves the HTML page to display the streamed log.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Realtime Log Viewer</title>
        <style>
            body { font-family: monospace; background-color: #1e1e1e; color: #d4d4d4; }
            #log-container { 
                background-color: #000; 
                padding: 10px; 
                border-radius: 5px; 
                max-height: 80vh; 
                overflow-y: auto; 
                margin: 20px;
                white-space: pre-wrap; /* Preserves whitespace and wraps long lines */
            }
            .log-line { border-bottom: 1px dotted #333; padding: 2px 0; }
        </style>
    </head>
    <body>
        <h1>Realtime Log Stream (FastAPI SSE)</h1>
        <div id="log-container">
            Loading log...
        </div>

        <script>
            const logContainer = document.getElementById('log-container');
            const eventSource = new EventSource('/stream-log');

            eventSource.onopen = function(event) {
                console.log('SSE connection opened.');
                logContainer.innerHTML = ''; // Clear "Loading log..."
            };

            eventSource.onmessage = function(event) {
                // Each event.data is a new log line
                const line = document.createElement('div');
                line.classList.add('log-line');
                line.textContent = event.data;
                logContainer.appendChild(line);
                // Scroll to the bottom to see the latest log entries
                logContainer.scrollTop = logContainer.scrollHeight;
            };

            eventSource.onerror = function(error) {
                console.error('SSE Error:', error);
                logContainer.innerHTML += '<div style="color: red;">Connection lost. Trying to reconnect...</div>';
                // EventSource will automatically try to reconnect by default
            };

            eventSource.onclose = function() {
                console.log('SSE connection closed.');
                logContainer.innerHTML += '<div style="color: orange;">Connection closed.</div>';
            };
        </script>
    </body>
    </html>
    """



