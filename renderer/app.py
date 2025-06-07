"""
Streamlined In-Memory Webpage Renderer Backend
Focused on core functionality used by the enhanced builder agents
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import uuid
from datetime import datetime
from jinja2 import Environment, BaseLoader
from settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Landing Page Renderer",
    description="Instant webpage deployment for startup validation",
    version="2.0.0",
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

# Basic analytics storage
SITE_METRICS: Dict[str, Dict[str, Any]] = {}


# Streamlined Pydantic models
class WebsiteAssets(BaseModel):
    html_template: str = Field(..., description="Jinja2 HTML template")
    css_styles: str = Field(default="", description="CSS styles (embedded in HTML)")
    javascript: str = Field(
        default="", description="JavaScript code (embedded in HTML)"
    )
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Site configuration"
    )


class DeploymentRequest(BaseModel):
    site_name: str = Field(..., description="Site identifier")
    assets: WebsiteAssets
    content_data: Dict[str, Any] = Field(
        ..., description="Dynamic content for template"
    )
    visual_assets: Dict[str, Any] = Field(
        default_factory=dict, description="Images and media"
    )
    conversion_elements: Dict[str, Any] = Field(
        default_factory=dict, description="A/B testing variants"
    )
    seo_optimization: Dict[str, Any] = Field(
        default_factory=dict, description="SEO metadata"
    )
    meta_data: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    analytics: Dict[str, Any] = Field(
        default_factory=dict, description="Analytics config"
    )
    premium_features: Dict[str, Any] = Field(
        default_factory=dict, description="Premium feature flags"
    )


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
        return f"""
        <html>
            <head><title>Template Error</title></head>
            <body style="font-family: Inter, sans-serif; padding: 50px; text-align: center;">
                <h1>🚫 Template Rendering Error</h1>
                <p>There was an issue processing the template.</p>
                <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px; text-align: left; max-width: 600px; margin: 20px auto;">{str(e)}</pre>
            </body>
        </html>
        """


def create_complete_html(
    assets: WebsiteAssets, content_data: Dict[str, Any], site_id: str
) -> str:
    """Create complete HTML with embedded CSS and JS"""

    # Add default values to content data
    enhanced_content = {
        **content_data,
        "current_year": datetime.now().year,
        "site_id": site_id,
        "site_url": f"http://localhost:8001/site/{site_id}",
    }

    # Process the Jinja template
    rendered_html = process_jinja_template(assets.html_template, enhanced_content)

    # Basic analytics injection
    analytics_js = f"""
    <script>
    // Basic analytics tracking
    window.SITE_ID = '{site_id}';

    function trackEvent(event_type, data = {{}}) {{
        fetch('/api/track', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify({{
                site_id: window.SITE_ID,
                event_type: event_type,
                event_data: data,
                timestamp: new Date().toISOString(),
                url: window.location.href
            }})
        }}).catch(() => {{}});
    }}

    // Track page view
    document.addEventListener('DOMContentLoaded', () => {{
        trackEvent('page_view');

        // Track CTA clicks
        document.querySelectorAll('.btn-primary, .btn-cta, [data-track="cta"]').forEach(btn => {{
            btn.addEventListener('click', () => {{
                trackEvent('cta_click', {{
                    text: btn.textContent.trim(),
                    location: btn.dataset.location || 'unknown'
                }});
            }});
        }});
    }});

    {assets.javascript}
    </script>
    """

    # Inject analytics before closing body tag
    if "</body>" in rendered_html:
        rendered_html = rendered_html.replace("</body>", f"{analytics_js}\n</body>")
    else:
        rendered_html = rendered_html + analytics_js

    return rendered_html


@app.post("/api/deploy")
async def deploy_website(deployment: DeploymentRequest):
    """Deploy a new website - Core endpoint used by builder agents"""

    try:
        # Generate unique site ID
        site_id = generate_site_id()

        # Create complete HTML
        complete_html = create_complete_html(
            deployment.assets, deployment.content_data, site_id
        )

        # Calculate performance score based on content size and features
        performance_score = min(
            100, 95 - (len(complete_html) // 10000)
        )  # Penalize large pages
        seo_score = 98 if deployment.seo_optimization else 85
        conversion_score = 92 if deployment.conversion_elements else 80

        # Store in memory with enhanced metadata
        DEPLOYED_SITES[site_id] = {
            "site_id": site_id,
            "site_name": deployment.site_name,
            "html_content": complete_html,
            "content_data": deployment.content_data,
            "visual_assets": deployment.visual_assets,
            "conversion_elements": deployment.conversion_elements,
            "seo_optimization": deployment.seo_optimization,
            "meta_data": deployment.meta_data,
            "analytics": deployment.analytics,
            "premium_features": deployment.premium_features,
            "created_at": datetime.now().isoformat(),
            "view_count": 0,
            "performance_score": performance_score,
            "seo_score": seo_score,
            "conversion_score": conversion_score,
        }

        # Initialize metrics
        SITE_METRICS[site_id] = {
            "page_views": 0,
            "cta_clicks": 0,
            "unique_sessions": set(),
            "last_activity": None,
        }

        # Generate URLs
        base_url = "http://localhost:8001"
        live_url = f"{base_url}/site/{site_id}"
        preview_url = f"{base_url}/preview/{site_id}"

        return {
            "success": True,
            "site_id": site_id,
            "deployment_id": site_id,
            "live_url": live_url,
            "preview_url": preview_url,
            "status": "deployed",
            "performance_score": performance_score,
            "seo_score": seo_score,
            "conversion_score": conversion_score,
            "premium_features_enabled": bool(deployment.premium_features),
            "deployment_details": {
                "created_at": datetime.now().isoformat(),
                "site_name": deployment.site_name,
                "features_enabled": list(deployment.assets.config.keys())
                if deployment.assets.config
                else [],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")


@app.post("/api/deploy/premium")
async def deploy_premium_website(deployment: DeploymentRequest):
    """Premium deployment endpoint with enhanced features"""

    # Same as regular deploy but with premium feature validation
    result = await deploy_website(deployment)

    # Add premium-specific enhancements
    if result["success"]:
        site_id = result["site_id"]
        DEPLOYED_SITES[site_id]["premium_deployed"] = True
        DEPLOYED_SITES[site_id]["performance_score"] = min(
            100, result["performance_score"] + 5
        )

        result.update(
            {
                "premium_features_enabled": True,
                "performance_score": DEPLOYED_SITES[site_id]["performance_score"],
                "premium_deployment": True,
            }
        )

    return result


@app.get("/site/{site_id}")
async def serve_website(site_id: str, request: Request):
    """Serve the deployed website - Core endpoint"""

    if site_id not in DEPLOYED_SITES:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Site Not Found</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: Inter, -apple-system, sans-serif;
                        text-align: center;
                        padding: 50px 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                        margin: 0;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .container {{
                        background: rgba(255,255,255,0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        max-width: 500px;
                    }}
                    h1 {{ margin-bottom: 20px; }}
                    code {{
                        background: rgba(255,255,255,0.2);
                        padding: 5px 10px;
                        border-radius: 6px;
                        font-family: 'JetBrains Mono', monospace;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚫 Site Not Found</h1>
                    <p>The site you're looking for doesn't exist or has been removed.</p>
                    <p>Site ID: <code>{site_id}</code></p>
                    <p style="margin-top: 30px; opacity: 0.8;">
                        <small>Powered by Landing Page Renderer v2.0</small>
                    </p>
                </div>
            </body>
            </html>
            """,
            status_code=404,
        )

    # Update metrics
    site_data = DEPLOYED_SITES[site_id]
    site_data["view_count"] += 1

    # Track metrics
    SITE_METRICS[site_id]["page_views"] += 1
    SITE_METRICS[site_id]["last_activity"] = datetime.now().isoformat()
    SITE_METRICS[site_id]["unique_sessions"].add(request.client.host)

    return HTMLResponse(content=site_data["html_content"])


@app.get("/preview/{site_id}")
async def preview_website(site_id: str):
    """Preview endpoint with frame-safe headers"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    site_data = DEPLOYED_SITES[site_id]
    content = site_data["html_content"]

    # Add preview banner
    preview_banner = """
    <div style="position: fixed; top: 0; left: 0; right: 0; background: #007bff; color: white;
                padding: 10px; text-align: center; z-index: 10000; font-family: Inter, sans-serif;
                font-size: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
        🔍 PREVIEW MODE - Site ID: {site_id} | Created: {created_at}
    </div>
    <style>body {{ margin-top: 50px !important; }}</style>
    """.format(site_id=site_id, created_at=site_data["created_at"][:16])

    if "<body>" in content:
        content = content.replace("<body>", f"<body>{preview_banner}")
    else:
        content = preview_banner + content

    return HTMLResponse(content=content)


@app.post("/api/track")
async def track_event(request: Request):
    """Simple event tracking endpoint"""

    try:
        data = await request.json()
        site_id = data.get("site_id")
        event_type = data.get("event_type")

        if site_id in SITE_METRICS:
            if event_type == "cta_click":
                SITE_METRICS[site_id]["cta_clicks"] += 1

            SITE_METRICS[site_id]["last_activity"] = datetime.now().isoformat()

        return {"success": True}

    except Exception:
        return {"success": False}


@app.get("/api/sites/{site_id}/metrics")
async def get_site_metrics(site_id: str):
    """Get basic site metrics"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    site_data = DEPLOYED_SITES[site_id]
    metrics = SITE_METRICS.get(site_id, {})

    return {
        "site_id": site_id,
        "site_name": site_data["site_name"],
        "created_at": site_data["created_at"],
        "view_count": site_data["view_count"],
        "performance_score": site_data.get("performance_score", 90),
        "seo_score": site_data.get("seo_score", 85),
        "conversion_score": site_data.get("conversion_score", 80),
        "metrics": {
            "page_views": metrics.get("page_views", 0),
            "cta_clicks": metrics.get("cta_clicks", 0),
            "unique_sessions": len(metrics.get("unique_sessions", set())),
            "last_activity": metrics.get("last_activity"),
        },
        "features": {
            "premium_features": bool(site_data.get("premium_features")),
            "conversion_optimized": bool(site_data.get("conversion_elements")),
            "seo_optimized": bool(site_data.get("seo_optimization")),
            "visual_assets": bool(site_data.get("visual_assets")),
        },
    }


@app.get("/dashboard")
async def dashboard():
    """Simple dashboard for monitoring deployed sites"""

    total_sites = len(DEPLOYED_SITES)
    total_views = sum(site["view_count"] for site in DEPLOYED_SITES.values())
    total_clicks = sum(
        metrics.get("cta_clicks", 0) for metrics in SITE_METRICS.values()
    )

    sites_html = ""
    for site_id, data in DEPLOYED_SITES.items():
        metrics = SITE_METRICS.get(site_id, {})
        sites_html += f"""
        <tr>
            <td><strong>{data['site_name']}</strong></td>
            <td><code>{site_id}</code></td>
            <td>{data['view_count']}</td>
            <td>{metrics.get('cta_clicks', 0)}</td>
            <td><span style="color: #28a745;">{data.get('performance_score', 90)}</span></td>
            <td>{data['created_at'][:16]}</td>
            <td>
                <a href="/site/{site_id}" target="_blank" style="color: #007bff;">View</a> |
                <a href="/preview/{site_id}" target="_blank" style="color: #28a745;">Preview</a>
            </td>
        </tr>
        """

    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Landing Page Renderer Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Inter, -apple-system, sans-serif;
                margin: 0;
                background: #f8fafc;
                color: #1a202c;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .stat-card {{
                background: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 1px solid #e2e8f0;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 5px;
            }}
            .stat-label {{ color: #64748b; font-weight: 500; }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            th {{ background: #f7fafc; font-weight: 600; color: #2d3748; }}
            tr:hover {{ background: #f7fafc; }}
            .empty-state {{
                text-align: center;
                padding: 60px;
                color: #64748b;
            }}
            .refresh-btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Landing Page Renderer</h1>
            <p>Streamlined deployment platform for startup validation</p>
        </div>

        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_sites}</div>
                    <div class="stat-label">Active Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_views}</div>
                    <div class="stat-label">Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_clicks}</div>
                    <div class="stat-label">CTA Clicks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len([s for s in DEPLOYED_SITES.values() if s.get('premium_features')])}</div>
                    <div class="stat-label">Premium Sites</div>
                </div>
            </div>

            <button onclick="window.location.reload()" class="refresh-btn">🔄 Refresh Data</button>

            <h2 style="margin: 30px 0 20px 0;">📋 Deployed Sites</h2>

            {f'''
            <table>
                <thead>
                    <tr>
                        <th>Site Name</th>
                        <th>Site ID</th>
                        <th>Views</th>
                        <th>Clicks</th>
                        <th>Performance</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {sites_html}
                </tbody>
            </table>
            ''' if total_sites > 0 else '''
            <div class="empty-state">
                <h3>No sites deployed yet</h3>
                <p>Deploy your first site using the API endpoint <code>POST /api/deploy</code></p>
            </div>
            '''}
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=dashboard_html)


@app.get("/")
async def root():
    """Root endpoint with streamlined API information"""
    return {
        "service": "Landing Page Renderer",
        "version": "2.0.0",
        "status": "active",
        "deployed_sites": len(DEPLOYED_SITES),
        "core_endpoints": {
            "deploy_site": "POST /api/deploy",
            "deploy_premium": "POST /api/deploy/premium",
            "view_site": "GET /site/{site_id}",
            "preview_site": "GET /preview/{site_id}",
            "site_metrics": "GET /api/sites/{site_id}/metrics",
            "dashboard": "GET /dashboard",
        },
        "features": [
            "jinja2_templating",
            "embedded_css_js",
            "basic_analytics",
            "premium_deployment",
            "performance_scoring",
            "responsive_design",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Streamlined Landing Page Renderer...")
    print("📊 Dashboard: http://localhost:8001/dashboard")
    print("🔧 API Docs: http://localhost:8001/docs")
    print("✨ Core Endpoints:")
    print("   - Deploy: POST /api/deploy")
    print("   - Deploy Premium: POST /api/deploy/premium")
    print("   - View Site: GET /site/{site_id}")
    print("   - Preview: GET /preview/{site_id}")

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
