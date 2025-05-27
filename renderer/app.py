"""
In-Memory Webpage Renderer Backend
Receives HTML/CSS/JS assets and serves them at dynamic URLs for instant validation
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uuid
import json
from datetime import datetime
from jinja2 import Environment, BaseLoader
from settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="In-Memory Landing Page Renderer",
    description="Instant webpage deployment for market validation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for deployed websites
DEPLOYED_SITES: Dict[str, Dict[str, Any]] = {}

# Analytics storage
SITE_ANALYTICS: Dict[str, List[Dict[str, Any]]] = {}


# Pydantic models
class WebsiteAssets(BaseModel):
    html_template: str = Field(..., description="Jinja2 HTML template")
    css_styles: str = Field(..., description="CSS styles")
    javascript: str = Field(default="", description="JavaScript code")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Site configuration"
    )


class ContentData(BaseModel):
    brand_name: str = Field(default="Demo Site")
    tagline: str = Field(default="Amazing Solution")
    headline: str = Field(default="Transform Your Workflow")
    description: str = Field(default="The best solution for your needs")
    features: List[Dict[str, Any]] = Field(default_factory=list)
    pricing_plans: List[Dict[str, Any]] = Field(default_factory=list)
    testimonials: List[Dict[str, Any]] = Field(default_factory=list)
    faqs: List[Dict[str, Any]] = Field(default_factory=list)


class DeploymentRequest(BaseModel):
    deployment_id: Optional[str] = Field(default=None)
    site_name: str = Field(..., description="Site identifier")
    assets: WebsiteAssets
    content_data: ContentData
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    analytics: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsEvent(BaseModel):
    site_id: str
    event_type: str  # 'page_view', 'click', 'form_submit', etc.
    event_data: Dict[str, Any] = Field(default_factory=dict)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


# Jinja2 Environment setup
jinja_env = Environment(loader=BaseLoader())


def generate_site_id() -> str:
    """Generate a unique site ID"""
    return str(uuid.uuid4())[:8]


def process_jinja_template(template_str: str, content_data: Dict[str, Any]) -> str:
    """Process Jinja2 template with content data"""
    try:
        template = jinja_env.from_string(template_str)
        return template.render(**content_data)
    except Exception as e:
        print(f"Template rendering error: {e}")
        return f"<html><body><h1>Template Error</h1><p>{str(e)}</p></body></html>"


def create_complete_html(
    assets: WebsiteAssets, content_data: Dict[str, Any], site_id: str
) -> str:
    """Create complete HTML with embedded CSS and JS"""

    # Process the Jinja template
    rendered_html = process_jinja_template(assets.html_template, content_data)

    # Inject CSS and JS directly into the HTML
    css_injection = f"""<style>
{assets.css_styles}
</style>"""

    js_injection = f"""<script>
// Site ID for analytics
window.SITE_ID = '{site_id}';

// Analytics tracking
function trackEvent(eventType, eventData = {{}}) {{
    fetch('/api/analytics/track', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            site_id: window.SITE_ID,
            event_type: eventType,
            event_data: eventData,
            timestamp: new Date().toISOString()
        }})
    }}).catch(console.error);
}}

// Track page view
trackEvent('page_view', {{
    url: window.location.href,
    title: document.title,
    referrer: document.referrer
}});

// Custom JavaScript
{assets.javascript}
</script>"""

    # Inject CSS before </head>
    if "</head>" in rendered_html:
        rendered_html = rendered_html.replace("</head>", f"{css_injection}\n</head>")
    else:
        rendered_html = css_injection + rendered_html

    # Inject JS before </body>
    if "</body>" in rendered_html:
        rendered_html = rendered_html.replace("</body>", f"{js_injection}\n</body>")
    else:
        rendered_html = rendered_html + js_injection

    return rendered_html


@app.post("/api/deploy")
async def deploy_website(deployment: DeploymentRequest):
    """Deploy a new website and return access URLs"""

    try:
        # Generate site ID if not provided
        site_id = deployment.deployment_id or generate_site_id()

        # Convert Pydantic models to dicts for template processing
        content_dict = deployment.content_data.dict()

        # Add some default values if missing
        content_dict.setdefault("current_year", datetime.now().year)
        content_dict.setdefault("site_url", f"http://localhost:8001/site/{site_id}")

        # Create complete HTML
        complete_html = create_complete_html(deployment.assets, content_dict, site_id)

        # Store in memory
        DEPLOYED_SITES[site_id] = {
            "site_id": site_id,
            "site_name": deployment.site_name,
            "html_content": complete_html,
            "content_data": content_dict,
            "meta_data": deployment.meta_data,
            "analytics": deployment.analytics,
            "created_at": datetime.now().isoformat(),
            "last_accessed": None,
            "view_count": 0,
        }

        # Initialize analytics storage
        SITE_ANALYTICS[site_id] = []

        # Generate URLs
        base_url = "http://localhost:8001"  # Configure as needed
        live_url = f"{base_url}/site/{site_id}"
        admin_url = f"{base_url}/admin/{site_id}"
        analytics_url = f"{base_url}/analytics/{site_id}"

        return {
            "success": True,
            "site_id": site_id,
            "live_url": live_url,
            "admin_url": admin_url,
            "analytics_url": analytics_url,
            "deployment_details": {
                "deployment_id": site_id,
                "status": "deployed",
                "created_at": datetime.now().isoformat(),
                "site_name": deployment.site_name,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@app.get("/site/{site_id}")
async def serve_website(site_id: str, request: Request):
    """Serve the deployed website"""

    if site_id not in DEPLOYED_SITES:
        return HTMLResponse(
            content="""
            <html>
                <head><title>Site Not Found</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1>🚫 Site Not Found</h1>
                    <p>The site you're looking for doesn't exist or has been removed.</p>
                    <p>Site ID: <code>{}</code></p>
                </body>
            </html>
            """.format(site_id),
            status_code=404,
        )

    # Update access tracking
    site_data = DEPLOYED_SITES[site_id]
    site_data["last_accessed"] = datetime.now().isoformat()
    site_data["view_count"] += 1

    # Track analytics
    SITE_ANALYTICS[site_id].append(
        {
            "event_type": "page_view",
            "timestamp": datetime.now().isoformat(),
            "user_agent": request.headers.get("user-agent"),
            "ip_address": request.client.host,
            "event_data": {"url": str(request.url), "method": request.method},
        }
    )

    return HTMLResponse(content=site_data["html_content"])


@app.get("/admin/{site_id}")
async def admin_panel(site_id: str):
    """Simple admin panel for site management"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    site_data = DEPLOYED_SITES[site_id]

    admin_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin - {site_data['site_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }}
            .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #007bff; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .actions {{ margin-top: 30px; }}
            .btn {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
            .btn-danger {{ background: #dc3545; }}
            .section {{ margin: 30px 0; }}
            .section h3 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
            pre {{ background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛠️ Admin Panel</h1>
                <p><strong>Site:</strong> {site_data['site_name']} | <strong>ID:</strong> {site_id}</p>
            </div>

            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-number">{site_data['view_count']}</div>
                    <div class="stat-label">Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(SITE_ANALYTICS.get(site_id, []))}</div>
                    <div class="stat-label">Analytics Events</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{site_data['created_at'][:10]}</div>
                    <div class="stat-label">Created Date</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{"✅ Active" if site_id in DEPLOYED_SITES else "❌ Inactive"}</div>
                    <div class="stat-label">Status</div>
                </div>
            </div>

            <div class="actions">
                <a href="/site/{site_id}" class="btn" target="_blank">👁️ View Live Site</a>
                <a href="/analytics/{site_id}" class="btn">📊 View Analytics</a>
                <a href="/api/sites/{site_id}/data" class="btn">📄 Export Data</a>
                <button onclick="deleteSite()" class="btn btn-danger">🗑️ Delete Site</button>
            </div>

            <div class="section">
                <h3>📋 Site Information</h3>
                <pre>{json.dumps({{
                    'site_name': site_data['site_name'],
                    'created_at': site_data['created_at'],
                    'last_accessed': site_data['last_accessed'],
                    'view_count': site_data['view_count'],
                    'content_summary': {{
                        'brand_name': site_data['content_data'].get('brand_name'),
                        'headline': site_data['content_data'].get('headline'),
                        'features_count': len(site_data['content_data'].get('features', [])),
                        'pricing_plans': len(site_data['content_data'].get('pricing_plans', []))
                    }}
                }}, indent=2)}</pre>
            </div>
        </div>

        <script>
            function deleteSite() {{
                if (confirm('Are you sure you want to delete this site? This action cannot be undone.')) {{
                    fetch('/api/sites/{site_id}', {{
                        method: 'DELETE'
                    }}).then(response => {{
                        if (response.ok) {{
                            alert('Site deleted successfully');
                            window.location.href = '/admin';
                        }} else {{
                            alert('Failed to delete site');
                        }}
                    }});
                }}
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=admin_html)


@app.get("/analytics/{site_id}")
async def analytics_dashboard(site_id: str):
    """Analytics dashboard for the site"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    analytics_data = SITE_ANALYTICS.get(site_id, [])
    site_data = DEPLOYED_SITES[site_id]

    # Process analytics data
    page_views = len([e for e in analytics_data if e["event_type"] == "page_view"])
    unique_ips = len(
        set(e.get("ip_address") for e in analytics_data if e.get("ip_address"))
    )

    analytics_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Analytics - {site_data['site_name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ border-bottom: 2px solid #28a745; padding-bottom: 20px; margin-bottom: 30px; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .metric-card {{ background: #f8f9fa; padding: 20px; border-radius: 6px; text-align: center; }}
            .metric-number {{ font-size: 2em; font-weight: bold; color: #28a745; }}
            .metric-label {{ color: #666; margin-top: 5px; }}
            .events-list {{ max-height: 400px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 4px; }}
            .event-item {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .event-item:last-child {{ border-bottom: none; }}
            .btn {{ background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Analytics Dashboard</h1>
                <p><strong>Site:</strong> {site_data['site_name']} | <strong>ID:</strong> {site_id}</p>
            </div>

            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-number">{page_views}</div>
                    <div class="metric-label">Page Views</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{unique_ips}</div>
                    <div class="metric-label">Unique Visitors</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{len(analytics_data)}</div>
                    <div class="metric-label">Total Events</div>
                </div>
                <div class="metric-card">
                    <div class="metric-number">{site_data['view_count']}</div>
                    <div class="metric-label">Site Views</div>
                </div>
            </div>

            <div style="margin: 30px 0;">
                <a href="/admin/{site_id}" class="btn">🛠️ Back to Admin</a>
                <a href="/site/{site_id}" class="btn" target="_blank">👁️ View Live Site</a>
            </div>

            <h3>📋 Recent Events</h3>
            <div class="events-list">
                {"".join([f'''
                <div class="event-item">
                    <strong>{event.get('event_type', 'unknown')}</strong> - {event.get('timestamp', 'no timestamp')}
                    <br><small>IP: {event.get('ip_address', 'unknown')} | UA: {(event.get('user_agent', 'unknown') or 'unknown')[:50]}...</small>
                </div>
                ''' for event in analytics_data[-20:]])}
            </div>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=analytics_html)


@app.post("/api/analytics/track")
async def track_analytics(event: AnalyticsEvent):
    """Track analytics events"""

    if event.site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    # Store the event
    SITE_ANALYTICS.setdefault(event.site_id, []).append(
        {
            "event_type": event.event_type,
            "event_data": event.event_data,
            "timestamp": datetime.now().isoformat(),
            "user_agent": event.user_agent,
            "ip_address": event.ip_address,
        }
    )

    return {"success": True}


@app.get("/api/sites")
async def list_sites():
    """List all deployed sites"""
    return {
        "sites": [
            {
                "site_id": site_id,
                "site_name": data["site_name"],
                "created_at": data["created_at"],
                "view_count": data["view_count"],
                "live_url": f"http://localhost:8001/site/{site_id}",
            }
            for site_id, data in DEPLOYED_SITES.items()
        ]
    }


@app.get("/api/sites/{site_id}/data")
async def get_site_data(site_id: str):
    """Get complete site data"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    return {
        "site_data": DEPLOYED_SITES[site_id],
        "analytics": SITE_ANALYTICS.get(site_id, []),
    }


@app.delete("/api/sites/{site_id}")
async def delete_site(site_id: str):
    """Delete a deployed site"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    # Remove from storage
    del DEPLOYED_SITES[site_id]
    if site_id in SITE_ANALYTICS:
        del SITE_ANALYTICS[site_id]

    return {"success": True, "message": "Site deleted successfully"}


@app.get("/admin")
async def admin_home():
    """Admin home page listing all sites"""

    sites_html = ""
    for site_id, data in DEPLOYED_SITES.items():
        sites_html += f"""
        <tr>
            <td>{data['site_name']}</td>
            <td><code>{site_id}</code></td>
            <td>{data['view_count']}</td>
            <td>{data['created_at'][:16]}</td>
            <td>
                <a href="/site/{site_id}" target="_blank">View</a> |
                <a href="/admin/{site_id}">Admin</a> |
                <a href="/analytics/{site_id}">Analytics</a>
            </td>
        </tr>
        """

    admin_home_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Site Management Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; border: 1px solid #ddd; text-align: left; }}
            th {{ background: #007bff; color: white; }}
            tr:nth-child(even) {{ background: #f8f9fa; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #007bff; color: white; padding: 20px; border-radius: 6px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Landing Page Renderer Dashboard</h1>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(DEPLOYED_SITES)}</div>
                    <div>Active Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(data['view_count'] for data in DEPLOYED_SITES.values())}</div>
                    <div>Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{sum(len(events) for events in SITE_ANALYTICS.values())}</div>
                    <div>Analytics Events</div>
                </div>
            </div>

            <h2>📋 Deployed Sites</h2>
            <table>
                <thead>
                    <tr>
                        <th>Site Name</th>
                        <th>Site ID</th>
                        <th>Views</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {sites_html or '<tr><td colspan="5" style="text-align: center; color: #666;">No sites deployed yet</td></tr>'}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=admin_home_html)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "In-Memory Landing Page Renderer",
        "version": "1.0.0",
        "status": "active",
        "deployed_sites": len(DEPLOYED_SITES),
        "endpoints": {
            "deploy": "POST /api/deploy",
            "view_site": "GET /site/{site_id}",
            "admin_panel": "GET /admin/{site_id}",
            "analytics": "GET /analytics/{site_id}",
            "list_sites": "GET /api/sites",
            "admin_home": "GET /admin",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting In-Memory Landing Page Renderer...")
    print("📊 Admin Dashboard: http://localhost:8001/admin")
    print("🔧 API Docs: http://localhost:8001/docs")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
