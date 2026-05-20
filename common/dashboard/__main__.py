"""Punto de entrada para `python -m common.dashboard`.

Lo invoca el spawn detached del lifecycle y también el modo dev cuando se
ejecuta en foreground.
"""
import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Arkanum Dashboard server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "common.dashboard.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
