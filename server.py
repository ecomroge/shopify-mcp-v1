import os
import json
import requests
from typing import Any
from mcp.server.fastmcp import FastMCP

SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "")
SHOPIFY_ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = "2024-10"

BASE_URL = f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{API_VERSION}"

HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json",
}

mcp = FastMCP("iHELFY Shopify MCP")

def shopify_get(endpoint: str, params: dict = None):
    r = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

def shopify_put(endpoint: str, data: dict):
    r = requests.put(f"{BASE_URL}{endpoint}", headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def shopify_post(endpoint: str, data: dict):
    r = requests.post(f"{BASE_URL}{endpoint}", headers=HEADERS, json=data)
    r.raise_for_status()
    return r.json()

def shopify_delete(endpoint: str):
    r = requests.delete(f"{BASE_URL}{endpoint}", headers=HEADERS)
    r.raise_for_status()
    return {"success": True}

# ─── PRODUCTS ────────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_list_products(limit: int = 50, status: str = None) -> str:
    """List products from the Shopify store."""
    params = {"limit": limit}
    if status:
        params["status"] = status
    return json.dumps(shopify_get("/products.json", params))

@mcp.tool()
def shopify_get_product(product_id: int) -> str:
    """Get a single product by ID."""
    return json.dumps(shopify_get(f"/products/{product_id}.json"))

@mcp.tool()
def shopify_update_product(product_id: int, title: str = None, body_html: str = None,
                           status: str = None, tags: str = None, vendor: str = None) -> str:
    """Update a product. Only provided fields are changed."""
    product = {}
    if title: product["title"] = title
    if body_html is not None: product["body_html"] = body_html
    if status: product["status"] = status
    if tags is not None: product["tags"] = tags
    if vendor: product["vendor"] = vendor
    return json.dumps(shopify_put(f"/products/{product_id}.json", {"product": product}))

@mcp.tool()
def shopify_create_product(title: str, body_html: str = None, status: str = "draft",
                           vendor: str = None, tags: str = None,
                           variants: list = None) -> str:
    """Create a new product."""
    product = {"title": title, "status": status}
    if body_html: product["body_html"] = body_html
    if vendor: product["vendor"] = vendor
    if tags: product["tags"] = tags
    if variants: product["variants"] = variants
    return json.dumps(shopify_post("/products.json", {"product": product}))

# ─── METAFIELDS ──────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_get_product_metafields(product_id: int) -> str:
    """Get all metafields for a product."""
    return json.dumps(shopify_get(f"/products/{product_id}/metafields.json"))

@mcp.tool()
def shopify_set_product_metafield(product_id: int, namespace: str, key: str,
                                   value: str, type: str = "single_line_text_field") -> str:
    """Create or update a metafield on a product."""
    data = {"metafield": {"namespace": namespace, "key": key, "value": value, "type": type}}
    return json.dumps(shopify_post(f"/products/{product_id}/metafields.json", data))

# ─── THEMES ──────────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_list_themes() -> str:
    """List all themes in the store with their IDs, names, and roles."""
    return json.dumps(shopify_get("/themes.json"))

@mcp.tool()
def shopify_get_theme_files(theme_id: int) -> str:
    """List all files/assets in a theme."""
    return json.dumps(shopify_get(f"/themes/{theme_id}/assets.json"))

@mcp.tool()
def shopify_get_theme_file(theme_id: int, file_key: str) -> str:
    """Get the content of a specific theme file. 
    Example file_key: 'templates/product.lp-gummys.liquid' or 'sections/hero-banner.liquid'"""
    return json.dumps(shopify_get(f"/themes/{theme_id}/assets.json",
                                   params={"asset[key]": file_key}))

@mcp.tool()
def shopify_update_theme_file(theme_id: int, file_key: str, content: str) -> str:
    """Update the content of a theme file (Liquid, CSS, JS, JSON sections).
    Example file_key: 'sections/product-hero.liquid'"""
    data = {"asset": {"key": file_key, "value": content}}
    return json.dumps(shopify_put(f"/themes/{theme_id}/assets.json", data))

@mcp.tool()
def shopify_get_section_data(theme_id: int, template: str = "product.lp-gummys") -> str:
    """Get the JSON data/settings for a specific template (sections and their content).
    Example template: 'product.lp-gummys'"""
    file_key = f"templates/{template}.json"
    try:
        return json.dumps(shopify_get(f"/themes/{theme_id}/assets.json",
                                       params={"asset[key]": file_key}))
    except:
        file_key = f"templates/{template}.liquid"
        return json.dumps(shopify_get(f"/themes/{theme_id}/assets.json",
                                       params={"asset[key]": file_key}))

@mcp.tool()
def shopify_update_section_data(theme_id: int, template: str, json_content: str) -> str:
    """Update the JSON data of a template (controls which sections appear and their settings).
    Example template: 'product.lp-gummys'"""
    file_key = f"templates/{template}.json"
    data = {"asset": {"key": file_key, "value": json_content}}
    return json.dumps(shopify_put(f"/themes/{theme_id}/assets.json", data))

# ─── ORDERS ──────────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_list_orders(limit: int = 50, status: str = "any",
                         financial_status: str = None) -> str:
    """List orders with optional filters."""
    params = {"limit": limit, "status": status}
    if financial_status: params["financial_status"] = financial_status
    return json.dumps(shopify_get("/orders.json", params))

@mcp.tool()
def shopify_get_order(order_id: int) -> str:
    """Get a single order by ID."""
    return json.dumps(shopify_get(f"/orders/{order_id}.json"))

# ─── CUSTOMERS ───────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_list_customers(limit: int = 50) -> str:
    """List customers."""
    return json.dumps(shopify_get("/customers.json", {"limit": limit}))

@mcp.tool()
def shopify_search_customers(query: str) -> str:
    """Search customers by name, email, etc."""
    return json.dumps(shopify_get("/customers/search.json", {"query": query}))

# ─── COLLECTIONS ─────────────────────────────────────────────────────────────

@mcp.tool()
def shopify_list_collections() -> str:
    """List all collections (smart and custom)."""
    customs = shopify_get("/custom_collections.json")
    smarts = shopify_get("/smart_collections.json")
    return json.dumps({"custom": customs, "smart": smarts})

if __name__ == "__main__":
    transport = os.environ.get("TRANSPORT", "http")
    port = int(os.environ.get("PORT", 3000))
    if transport == "http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
    else:
        mcp.run(transport="stdio")
