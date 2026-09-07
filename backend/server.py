import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add parent path to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.rag.retriever import Retriever
from backend.rag.answer_engine import AnswerEngine

retriever = None
answer_engine = None

def init_components():
    global retriever, answer_engine
    if retriever is None:
        retriever = Retriever()
        answer_engine = AnswerEngine()

class RuleGuardHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            init_components()
            self.send_response(200)
            self._set_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response_data = {
                "status": "ok",
                "service": "RuleGuard AI Backend Server",
                "index_loaded": retriever.loaded if retriever else False
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/ask":
            init_components()
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode("utf-8"))
                question = payload.get("question", "").strip()

                if not question:
                    self.send_response(400)
                    self._set_cors_headers()
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "Question string cannot be empty."}).encode("utf-8"))
                    return

                # Retrieve & process
                sources = retriever.retrieve(question, top_k=6)
                res = answer_engine.process_query(question, sources)
                
                # Convert response objects & nested SourcePassage objects to plain dicts
                sources_list = []
                for s in res.sources:
                    if hasattr(s, "dict") and callable(getattr(s, "dict")):
                        sources_list.append(s.dict())
                    elif hasattr(s, "__dict__"):
                        sources_list.append(s.__dict__)
                    else:
                        sources_list.append(dict(s))

                res_dict = {
                    "status": res.status,
                    "answer": res.answer,
                    "sources": sources_list
                }

                self.send_response(200)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(res_dict, indent=2).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"detail": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    init_components()
    server_address = ("", port)
    httpd = HTTPServer(server_address, RuleGuardHandler)
    print(f"RuleGuard AI Backend Server running at http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
