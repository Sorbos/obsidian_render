import sys
import json
import asyncio
from typing import Any, Callable, Dict
from fastapi import FastAPI


class FastMCP:
    """A minimal reference MCP helper providing simple decorators and transports.

    - Use `@mcp.prompt()`, `@mcp.resource(name)`, `@mcp.tool()` to register handlers.
    - Call `mcp.run(transport='stdio')` to run a minimal stdio loop for local testing,
      or `mcp.run(transport='http')` to serve an HTTP endpoint at /mcp/message.
    """

    def __init__(self, name: str):
        self.name = name
        self.prompts: Dict[str, Callable] = {}
        self.resources: Dict[str, Callable] = {}
        self.tools: Dict[str, Callable] = {}
        self.app = FastAPI()

        @self.app.post("/mcp/message")
        async def handle_message(message: Dict[str, Any]):
            return await self._dispatch(message)

    def prompt(self, name: str = None):
        def decorator(fn: Callable):
            key = name or fn.__name__
            self.prompts[key] = fn
            return fn

        return decorator

    def resource(self, name: str):
        def decorator(fn: Callable):
            self.resources[name] = fn
            return fn

        return decorator

    def tool(self, name: str = None):
        def decorator(fn: Callable):
            key = name or fn.__name__
            self.tools[key] = fn
            return fn

        return decorator

    async def _dispatch(self, message: Dict[str, Any]):
        t = message.get("type")
        payload = message.get("payload", {}) or {}
        name = payload.get("name")
        args = payload.get("args", {}) or {}

        if t == "prompt":
            fn = self.prompts.get(name)
        elif t == "resource":
            fn = self.resources.get(name)
        elif t == "tool":
            fn = self.tools.get(name)
        else:
            return {"error": "unknown message type"}

        if fn is None:
            return {"error": f"no handler registered for {t}:{name}"}

        try:
            if asyncio.iscoroutinefunction(fn):
                result = await fn(**args)
            else:
                result = fn(**args)
            return {"result": result}
        except Exception as exc:
            return {"error": str(exc)}

    def run(self, transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000):
        if transport == "http":
            import uvicorn

            uvicorn.run(self.app, host=host, port=port)
        elif transport == "stdio":
            # Simple stdio loop: read JSON per-line, write JSON per-line
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                try:
                    message = json.loads(line)
                    res = asyncio.run(self._dispatch(message))
                    print(json.dumps(res), flush=True)
                except Exception as exc:
                    print(json.dumps({"error": str(exc)}), flush=True)
        else:
            raise ValueError("unknown transport")
