import asyncio
import os
import sys

from uvicorn import Config, Server

# Asegura que Python reconozca el paquete 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

config = Config("app.main:app", host="127.0.0.1", port=8080, reload=False)
server = Server(config)

if __name__ == "__main__":
    # Aquí puedes poner tu punto de interrupción
    breakpoint()  # ← Este sí se detendrá
    asyncio.run(server.serve())
