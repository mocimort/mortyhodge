"""MCP server — the universal connector.

Exposes the knowledge base over the Model Context Protocol so Claude,
ChatGPT, Gemini, and any future Hodge project can query the same brain.

Run locally on morty-mini:
    python mcp_server/server.py

Claude Desktop / Claude Code: add as a stdio MCP server.
ChatGPT / Gemini connectors need an HTTP transport — expose via
`mcp` streamable-http and (only when ready) publish through the
Cloudflare Tunnel on hodgeindustrial.ai with auth in front.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mcp.server.fastmcp import FastMCP

from knowledge_engine import db

mcp = FastMCP("hodge-knowledge")


@mcp.tool()
def search_knowledge(query: str, limit: int = 10) -> str:
    """Search Hodge's real-world compressor service knowledge base.

    Query with symptoms, equipment names, or part names, e.g.
    'rotary screw overheating' or 'pressure switch short cycling'.
    """
    conn = db.connect()
    results = db.search(conn, query, limit=limit)
    return json.dumps(results, indent=2)


@mcp.tool()
def knowledge_stats() -> str:
    """Counts and coverage of the knowledge base."""
    conn = db.connect()
    total = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    by_conf = conn.execute(
        "SELECT confidence, COUNT(*) FROM knowledge GROUP BY confidence"
    ).fetchall()
    return json.dumps({"total": total, "by_confidence": dict(by_conf)})


if __name__ == "__main__":
    mcp.run()
