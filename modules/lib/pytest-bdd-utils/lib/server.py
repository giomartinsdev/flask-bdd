import socket
import threading

from flask import Flask
from werkzeug.serving import make_server


class LiveServer:
    """Flask app wrapped in a real Werkzeug TCP server running in a daemon thread.

    Uses ThreadedWSGIServer (threaded=True) so each k6 VU request runs in its
    own thread with an isolated Flask request context — g is thread-local.
    """

    def __init__(self, app: Flask, host: str = "127.0.0.1") -> None:
        self._port = self._free_port()
        self._server = make_server(host, self._port, app, threaded=True)
        self._thread = threading.Thread(
            target=self._server.serve_forever, daemon=True, name="LiveServer"
        )

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self._port}"

    def start(self) -> "LiveServer":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._server.shutdown()

    @staticmethod
    def _free_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]
