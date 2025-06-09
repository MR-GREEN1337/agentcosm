"""
Enhanced Streamlined In-Memory Renderer Backend
Now supports PDF storage and serving for startup pitch decks
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid
import base64
from datetime import datetime
from jinja2 import Environment, BaseLoader
from settings import settings

# Initialize FastAPI app
app = FastAPI(
    title="Landing Page Renderer + PDF Storage",
    description="Instant webpage deployment and PDF storage for startup validation",
    version="2.1.0",
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

# In-memory storage for PDFs
STORED_PDFS: Dict[str, Dict[str, Any]] = {}

# Basic analytics storage
SITE_METRICS: Dict[str, Dict[str, Any]] = {}

# PDF analytics storage
PDF_METRICS: Dict[str, Dict[str, Any]] = {}


# Enhanced Pydantic models
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


class PDFStorageRequest(BaseModel):
    pdf_name: str = Field(..., description="PDF filename")
    pdf_base64: str = Field(..., description="Base64 encoded PDF data")
    pdf_type: str = Field(
        default="pitch_deck", description="Type of PDF (pitch_deck, report, etc.)"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="PDF metadata")
    associated_site_id: Optional[str] = Field(
        default=None, description="Associated website ID"
    )


class PitchDeckRequest(BaseModel):
    pitch_name: str = Field(..., description="Pitch deck name")
    pdf_base64: str = Field(..., description="Base64 encoded PDF data")
    executive_summary: Dict[str, Any] = Field(..., description="Executive summary data")
    presentation_metadata: Dict[str, Any] = Field(
        ..., description="Presentation metadata"
    )
    create_landing_page: bool = Field(
        default=True, description="Also create a landing page"
    )
    landing_page_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Landing page content"
    )


# Jinja2 Environment setup
jinja_env = Environment(loader=BaseLoader())


def generate_id() -> str:
    """Generate a unique ID"""
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

        // Track CTA clicks and PDF downloads
        document.querySelectorAll('.btn-primary, .btn-cta, [data-track="cta"]').forEach(btn => {{
            btn.addEventListener('click', () => {{
                trackEvent('cta_click', {{
                    text: btn.textContent.trim(),
                    location: btn.dataset.location || 'unknown'
                }});
            }});
        }});

        document.querySelectorAll('[data-track="pdf-download"]').forEach(btn => {{
            btn.addEventListener('click', () => {{
                trackEvent('pdf_download', {{
                    pdf_id: btn.dataset.pdfId || 'unknown',
                    pdf_name: btn.dataset.pdfName || 'unknown'
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


def create_pitch_landing_page_template() -> str:
    """Create a professional template for pitch deck landing pages"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ pitch_name }} - Investment Opportunity</title>
    <meta name="description" content="{{ executive_summary.tagline }}">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            line-height: 1.6;
            color: #1a202c;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .hero {
            padding: 80px 20px;
            text-align: center;
            color: white;
            background: rgba(0,0,0,0.1);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .hero h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #fff, #e2e8f0);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 1.25rem;
            margin-bottom: 40px;
            opacity: 0.9;
        }

        .download-section {
            background: white;
            padding: 80px 20px;
            margin-top: -50px;
            border-radius: 30px 30px 0 0;
            position: relative;
            z-index: 10;
        }

        .download-card {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 50px;
            border-radius: 20px;
            text-align: center;
            border: 1px solid #e2e8f0;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }

        .pdf-icon {
            font-size: 4rem;
            margin-bottom: 20px;
            color: #dc2626;
        }

        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 20px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }

        .download-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin: 60px 0;
        }

        .stat-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            border: 1px solid #e2e8f0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }

        .stat-label {
            color: #64748b;
            font-weight: 500;
        }

        .highlights {
            background: #f8fafc;
            padding: 60px 20px;
        }

        .highlights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            max-width: 1000px;
            margin: 0 auto;
        }

        .highlight-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }

        .footer {
            background: #1a202c;
            color: white;
            padding: 40px 20px;
            text-align: center;
        }

        .footer p {
            opacity: 0.7;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }

            .download-card {
                padding: 30px 20px;
                margin: 0 10px;
            }

            .stats-grid {
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>{{ pitch_name }}</h1>
            <p>{{ executive_summary.tagline }}</p>
        </div>
    </section>

    <section class="download-section">
        <div class="container">
            <div class="download-card">
                <div class="pdf-icon">📊</div>
                <h2>Investor Pitch Deck</h2>
                <p style="margin: 20px 0; color: #64748b;">
                    Comprehensive {{ presentation_metadata.pages }}-page investment presentation
                    with market analysis, financial projections, and growth strategy.
                </p>

                <a href="/api/pdf/{{ pdf_id }}/download"
                   class="download-btn"
                   data-track="pdf-download"
                   data-pdf-id="{{ pdf_id }}"
                   data-pdf-name="{{ pdf_filename }}">
                    📥 Download Pitch Deck PDF
                </a>

                <p style="font-size: 0.9rem; color: #64748b; margin-top: 15px;">
                    File size: {{ file_size_mb }}MB | Generated: {{ generated_date }}
                </p>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{{ executive_summary.market_size or '$10M+' }}</div>
                    <div class="stat-label">Market Size</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ executive_summary.investment_ask or '$1M+' }}</div>
                    <div class="stat-label">Investment Ask</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ presentation_metadata.pages or '12' }}</div>
                    <div class="stat-label">Pages</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ executive_summary.projected_revenue.year_3 or '$5M+' }}</div>
                    <div class="stat-label">Year 3 Revenue</div>
                </div>
            </div>
        </div>
    </section>

    <section class="highlights">
        <div class="container">
            <h2 style="text-align: center; margin-bottom: 50px; color: #1a202c;">Key Investment Highlights</h2>
            <div class="highlights-grid">
                {% for highlight in executive_summary.key_highlights[:4] %}
                <div class="highlight-card">
                    <h3 style="color: #667eea; margin-bottom: 15px;">{{ loop.index }}.</h3>
                    <p>{{ highlight }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; {{ current_year }} {{ pitch_name }}. Investment opportunity generated by AI analysis.</p>
            <p style="margin-top: 10px;">Site ID: {{ site_id }} | PDF ID: {{ pdf_id }}</p>
        </div>
    </footer>
</body>
</html>
    """


# Original deployment endpoints (unchanged)
@app.post("/api/deploy")
async def deploy_website(deployment: DeploymentRequest):
    """Deploy a new website - Core endpoint used by builder agents"""

    try:
        # Generate unique site ID
        site_id = generate_id()

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
            "pdf_downloads": 0,
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


# NEW PDF STORAGE ENDPOINTS


@app.post("/api/pdf/store")
async def store_pdf(pdf_request: PDFStorageRequest):
    """Store a PDF file and return access details"""

    try:
        # Generate unique PDF ID
        pdf_id = generate_id()

        # Decode base64 to get actual PDF size
        try:
            pdf_bytes = base64.b64decode(pdf_request.pdf_base64)
            file_size_bytes = len(pdf_bytes)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Invalid base64 PDF data: {str(e)}"
            )

        # Store PDF data
        STORED_PDFS[pdf_id] = {
            "pdf_id": pdf_id,
            "pdf_name": pdf_request.pdf_name,
            "pdf_base64": pdf_request.pdf_base64,
            "pdf_type": pdf_request.pdf_type,
            "metadata": pdf_request.metadata,
            "associated_site_id": pdf_request.associated_site_id,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": file_size_mb,
            "created_at": datetime.now().isoformat(),
            "download_count": 0,
        }

        # Initialize PDF metrics
        PDF_METRICS[pdf_id] = {
            "downloads": 0,
            "views": 0,
            "unique_downloaders": set(),
            "last_accessed": None,
        }

        # Generate URLs
        base_url = "http://localhost:8001"
        download_url = f"{base_url}/api/pdf/{pdf_id}/download"
        view_url = f"{base_url}/api/pdf/{pdf_id}/view"

        return {
            "success": True,
            "pdf_id": pdf_id,
            "download_url": download_url,
            "view_url": view_url,
            "file_size_mb": file_size_mb,
            "storage_details": {
                "created_at": datetime.now().isoformat(),
                "pdf_name": pdf_request.pdf_name,
                "pdf_type": pdf_request.pdf_type,
                "associated_site": pdf_request.associated_site_id,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF storage failed: {str(e)}")


@app.post("/api/pitch/deploy")
async def deploy_pitch_deck(pitch_request: PitchDeckRequest):
    """Deploy a pitch deck PDF with optional landing page - Main endpoint for startup pitch agent"""

    try:
        # First, store the PDF
        pdf_storage_request = PDFStorageRequest(
            pdf_name=f"{pitch_request.pitch_name.lower().replace(' ', '_')}_pitch_deck.pdf",
            pdf_base64=pitch_request.pdf_base64,
            pdf_type="pitch_deck",
            metadata=pitch_request.presentation_metadata,
        )

        pdf_result = await store_pdf(pdf_storage_request)
        pdf_id = pdf_result["pdf_id"]

        response_data = {
            "success": True,
            "pdf_id": pdf_id,
            "pdf_download_url": pdf_result["download_url"],
            "pdf_view_url": pdf_result["view_url"],
            "file_size_mb": pdf_result["file_size_mb"],
            "pitch_deck_details": {
                "pitch_name": pitch_request.pitch_name,
                "pdf_filename": pdf_storage_request.pdf_name,
                "created_at": datetime.now().isoformat(),
                "presentation_pages": pitch_request.presentation_metadata.get(
                    "pages", 12
                ),
            },
        }

        # Optionally create landing page
        if pitch_request.create_landing_page:
            # Prepare landing page content
            landing_content = {
                "pitch_name": pitch_request.pitch_name,
                "executive_summary": pitch_request.executive_summary,
                "presentation_metadata": pitch_request.presentation_metadata,
                "pdf_id": pdf_id,
                "pdf_filename": pdf_storage_request.pdf_name,
                "file_size_mb": pdf_result["file_size_mb"],
                "generated_date": datetime.now().strftime("%B %d, %Y"),
                "current_year": datetime.now().year,
            }

            # Merge with any additional landing page data
            if pitch_request.landing_page_data:
                landing_content.update(pitch_request.landing_page_data)

            # Create landing page deployment
            landing_deployment = DeploymentRequest(
                site_name=f"{pitch_request.pitch_name} - Pitch Deck",
                assets=WebsiteAssets(
                    html_template=create_pitch_landing_page_template(),
                    css_styles="",  # Styles are embedded in template
                    javascript="",  # Basic analytics will be injected
                    config={"type": "pitch_landing", "pdf_integration": True},
                ),
                content_data=landing_content,
                seo_optimization={
                    "title": f"{pitch_request.pitch_name} - Investment Opportunity",
                    "description": pitch_request.executive_summary.get(
                        "tagline", "Investment opportunity"
                    ),
                    "keywords": ["investment", "pitch deck", "startup", "opportunity"],
                },
                conversion_elements={
                    "primary_cta": "Download Pitch Deck",
                    "cta_tracking": True,
                },
                premium_features={"pdf_integration": True, "analytics": True},
            )

            # Deploy the landing page
            site_result = await deploy_website(landing_deployment)

            # Link the PDF to the site
            STORED_PDFS[pdf_id]["associated_site_id"] = site_result["site_id"]

            response_data.update(
                {
                    "landing_page_created": True,
                    "site_id": site_result["site_id"],
                    "landing_page_url": site_result["live_url"],
                    "preview_url": site_result["preview_url"],
                    "integrated_solution": True,
                }
            )

        return response_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Pitch deck deployment failed: {str(e)}"
        )


@app.get("/api/pdf/{pdf_id}/download")
async def download_pdf(pdf_id: str, request: Request):
    """Download a stored PDF file"""

    if pdf_id not in STORED_PDFS:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        pdf_data = STORED_PDFS[pdf_id]

        # Update metrics
        pdf_data["download_count"] += 1
        PDF_METRICS[pdf_id]["downloads"] += 1
        PDF_METRICS[pdf_id]["last_accessed"] = datetime.now().isoformat()
        PDF_METRICS[pdf_id]["unique_downloaders"].add(request.client.host)

        # Track in associated site metrics if exists
        if (
            pdf_data.get("associated_site_id")
            and pdf_data["associated_site_id"] in SITE_METRICS
        ):
            SITE_METRICS[pdf_data["associated_site_id"]]["pdf_downloads"] += 1

        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_data["pdf_base64"])

        # Return PDF with proper headers
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{pdf_data["pdf_name"]}"',
                "Content-Length": str(len(pdf_bytes)),
                "Cache-Control": "no-cache",
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF download failed: {str(e)}")


@app.get("/api/pdf/{pdf_id}/view")
async def view_pdf_inline(pdf_id: str, request: Request):
    """View PDF inline in browser"""

    if pdf_id not in STORED_PDFS:
        raise HTTPException(status_code=404, detail="PDF not found")

    try:
        pdf_data = STORED_PDFS[pdf_id]

        # Update view metrics
        PDF_METRICS[pdf_id]["views"] += 1
        PDF_METRICS[pdf_id]["last_accessed"] = datetime.now().isoformat()

        # Decode base64 PDF
        pdf_bytes = base64.b64decode(pdf_data["pdf_base64"])

        # Return PDF for inline viewing
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{pdf_data["pdf_name"]}"',
                "Content-Length": str(len(pdf_bytes)),
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF view failed: {str(e)}")


@app.get("/api/pdf/{pdf_id}/info")
async def get_pdf_info(pdf_id: str):
    """Get PDF information and metrics"""

    if pdf_id not in STORED_PDFS:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_data = STORED_PDFS[pdf_id]
    pdf_metrics = PDF_METRICS.get(pdf_id, {})

    return {
        "pdf_id": pdf_id,
        "pdf_name": pdf_data["pdf_name"],
        "pdf_type": pdf_data["pdf_type"],
        "file_size_mb": pdf_data["file_size_mb"],
        "created_at": pdf_data["created_at"],
        "associated_site_id": pdf_data.get("associated_site_id"),
        "metadata": pdf_data.get("metadata", {}),
        "metrics": {
            "download_count": pdf_data["download_count"],
            "view_count": pdf_metrics.get("views", 0),
            "unique_downloaders": len(pdf_metrics.get("unique_downloaders", set())),
            "last_accessed": pdf_metrics.get("last_accessed"),
        },
        "urls": {
            "download": f"http://localhost:8001/api/pdf/{pdf_id}/download",
            "view": f"http://localhost:8001/api/pdf/{pdf_id}/view",
            "info": f"http://localhost:8001/api/pdf/{pdf_id}/info",
        },
    }


# Original website serving endpoints (enhanced with PDF tracking)
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
                        <small>Powered by Landing Page Renderer v2.1</small>
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
    """Enhanced event tracking endpoint with PDF tracking"""

    try:
        data = await request.json()
        site_id = data.get("site_id")
        event_type = data.get("event_type")

        if site_id in SITE_METRICS:
            if event_type == "cta_click":
                SITE_METRICS[site_id]["cta_clicks"] += 1
            elif event_type == "pdf_download":
                SITE_METRICS[site_id]["pdf_downloads"] += 1

            SITE_METRICS[site_id]["last_activity"] = datetime.now().isoformat()

        return {"success": True}

    except Exception:
        return {"success": False}


@app.get("/api/sites/{site_id}/metrics")
async def get_site_metrics(site_id: str):
    """Get enhanced site metrics including PDF data"""

    if site_id not in DEPLOYED_SITES:
        raise HTTPException(status_code=404, detail="Site not found")

    site_data = DEPLOYED_SITES[site_id]
    metrics = SITE_METRICS.get(site_id, {})

    # Find associated PDFs
    associated_pdfs = [
        {
            "pdf_id": pdf_id,
            "pdf_name": pdf_data["pdf_name"],
            "download_count": pdf_data["download_count"],
            "file_size_mb": pdf_data["file_size_mb"],
        }
        for pdf_id, pdf_data in STORED_PDFS.items()
        if pdf_data.get("associated_site_id") == site_id
    ]

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
            "pdf_downloads": metrics.get("pdf_downloads", 0),
            "unique_sessions": len(metrics.get("unique_sessions", set())),
            "last_activity": metrics.get("last_activity"),
        },
        "features": {
            "premium_features": bool(site_data.get("premium_features")),
            "conversion_optimized": bool(site_data.get("conversion_elements")),
            "seo_optimized": bool(site_data.get("seo_optimization")),
            "visual_assets": bool(site_data.get("visual_assets")),
            "pdf_integration": len(associated_pdfs) > 0,
        },
        "associated_pdfs": associated_pdfs,
    }


@app.get("/dashboard")
async def dashboard():
    """Enhanced dashboard with PDF management"""

    total_sites = len(DEPLOYED_SITES)
    total_pdfs = len(STORED_PDFS)
    total_views = sum(site["view_count"] for site in DEPLOYED_SITES.values())
    total_downloads = sum(pdf["download_count"] for pdf in STORED_PDFS.values())
    total_clicks = sum(
        metrics.get("cta_clicks", 0) for metrics in SITE_METRICS.values()
    )

    sites_html = ""
    for site_id, data in DEPLOYED_SITES.items():
        metrics = SITE_METRICS.get(site_id, {})
        pdf_count = len(
            [p for p in STORED_PDFS.values() if p.get("associated_site_id") == site_id]
        )

        sites_html += f"""
        <tr>
            <td><strong>{data['site_name']}</strong></td>
            <td><code>{site_id}</code></td>
            <td>{data['view_count']}</td>
            <td>{metrics.get('cta_clicks', 0)}</td>
            <td>{metrics.get('pdf_downloads', 0)}</td>
            <td>{pdf_count}</td>
            <td><span style="color: #28a745;">{data.get('performance_score', 90)}</span></td>
            <td>{data['created_at'][:16]}</td>
            <td>
                <a href="/site/{site_id}" target="_blank" style="color: #007bff;">View</a> |
                <a href="/preview/{site_id}" target="_blank" style="color: #28a745;">Preview</a>
            </td>
        </tr>
        """

    pdfs_html = ""
    for pdf_id, data in STORED_PDFS.items():
        site_link = ""
        if data.get("associated_site_id"):
            site_link = f'<a href="/site/{data["associated_site_id"]}" target="_blank" style="color: #007bff;">{data["associated_site_id"]}</a>'
        else:
            site_link = "None"

        pdfs_html += f"""
        <tr>
            <td><strong>{data['pdf_name']}</strong></td>
            <td><code>{pdf_id}</code></td>
            <td>{data['pdf_type']}</td>
            <td>{data['file_size_mb']}MB</td>
            <td>{data['download_count']}</td>
            <td>{site_link}</td>
            <td>{data['created_at'][:16]}</td>
            <td>
                <a href="/api/pdf/{pdf_id}/download" style="color: #dc2626;">Download</a> |
                <a href="/api/pdf/{pdf_id}/view" target="_blank" style="color: #059669;">View</a>
            </td>
        </tr>
        """

    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Landing Page Renderer + PDF Storage Dashboard</title>
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
            .container {{ max-width: 1400px; margin: 0 auto; padding: 30px; }}
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
                margin-bottom: 30px;
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
            .section-title {{
                font-size: 1.5rem;
                font-weight: 600;
                margin: 40px 0 20px 0;
                color: #1a202c;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 Landing Page Renderer + PDF Storage</h1>
            <p>Comprehensive deployment platform with PDF management for startup validation</p>
        </div>

        <div class="container">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_sites}</div>
                    <div class="stat-label">Active Sites</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_pdfs}</div>
                    <div class="stat-label">Stored PDFs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_views}</div>
                    <div class="stat-label">Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_downloads}</div>
                    <div class="stat-label">PDF Downloads</div>
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

            <h2 class="section-title">📋 Deployed Sites</h2>

            {f'''
            <table>
                <thead>
                    <tr>
                        <th>Site Name</th>
                        <th>Site ID</th>
                        <th>Views</th>
                        <th>Clicks</th>
                        <th>PDF Downloads</th>
                        <th>PDFs</th>
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
                <p>Deploy your first site using <code>POST /api/deploy</code> or <code>POST /api/pitch/deploy</code></p>
            </div>
            '''}

            <h2 class="section-title">📄 Stored PDFs</h2>

            {f'''
            <table>
                <thead>
                    <tr>
                        <th>PDF Name</th>
                        <th>PDF ID</th>
                        <th>Type</th>
                        <th>Size</th>
                        <th>Downloads</th>
                        <th>Associated Site</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {pdfs_html}
                </tbody>
            </table>
            ''' if total_pdfs > 0 else '''
            <div class="empty-state">
                <h3>No PDFs stored yet</h3>
                <p>Store your first PDF using <code>POST /api/pdf/store</code> or <code>POST /api/pitch/deploy</code></p>
            </div>
            '''}
        </div>
    </body>
    </html>
    """

    return HTMLResponse(content=dashboard_html)


@app.get("/")
async def root():
    """Root endpoint with enhanced API information"""
    return {
        "service": "Landing Page Renderer + PDF Storage",
        "version": "2.1.0",
        "status": "active",
        "deployed_sites": len(DEPLOYED_SITES),
        "stored_pdfs": len(STORED_PDFS),
        "core_endpoints": {
            "deploy_site": "POST /api/deploy",
            "deploy_pitch_deck": "POST /api/pitch/deploy",
            "store_pdf": "POST /api/pdf/store",
            "download_pdf": "GET /api/pdf/{pdf_id}/download",
            "view_pdf": "GET /api/pdf/{pdf_id}/view",
            "pdf_info": "GET /api/pdf/{pdf_id}/info",
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
            "pdf_storage",
            "pdf_download_tracking",
            "integrated_pitch_decks",
            "landing_page_generation",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Enhanced Landing Page Renderer + PDF Storage...")
    print("📊 Dashboard: http://localhost:8001/dashboard")
    print("🔧 API Docs: http://localhost:8001/docs")
    print("✨ Core Endpoints:")
    print("   - Deploy Site: POST /api/deploy")
    print("   - Deploy Pitch Deck: POST /api/pitch/deploy")
    print("   - Store PDF: POST /api/pdf/store")
    print("   - Download PDF: GET /api/pdf/{pdf_id}/download")
    print("   - View Site: GET /site/{site_id}")
    print("   - Dashboard: GET /dashboard")

    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
