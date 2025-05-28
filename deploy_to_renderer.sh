#!/bin/bash

# Deploy a simple landing page
curl -X POST "http://localhost:8001/api/deploy" \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "My Test Site",
    "assets": {
      "html_template": "<!DOCTYPE html><html><head><title>{{ brand_name }}</title></head><body><h1>{{ headline }}</h1><p>{{ description }}</p><ul>{% for feature in features %}<li>{{ feature.title }}: {{ feature.description }}</li>{% endfor %}</ul></body></html>",
      "css_styles": "body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; } h1 { color: #007bff; } ul { list-style-type: none; } li { padding: 10px; background: #f8f9fa; margin: 5px 0; border-radius: 4px; }",
      "javascript": "console.log(\"Site loaded!\"); document.addEventListener(\"DOMContentLoaded\", function() { console.log(\"DOM ready\"); });"
    },
    "content_data": {
      "brand_name": "TechStartup Pro",
      "tagline": "Innovation at Scale",
      "headline": "Sakina matota",
      "description": "Our cutting-edge solution helps businesses scale efficiently with modern technology.",
      "features": [
        {
          "title": "Fast Setup",
          "description": "Get started in minutes, not hours"
        },
        {
          "title": "Scalable",
          "description": "Grows with your business needs"
        },
        {
          "title": "24/7 Support",
          "description": "We are here when you need us"
        }
      ],
      "pricing_plans": [
        {
          "name": "Starter",
          "price": "$29/month",
          "features": ["Basic features", "Email support"]
        }
      ]
    },
    "meta_data": {
      "author": "Demo User",
      "purpose": "Testing deployment"
    }
  }'

echo -e "\n\n=== After running the above command, you'll get a response like: ==="
echo '{
  "success": true,
  "site_id": "abc12345",
  "live_url": "http://localhost:8001/site/abc12345",
  "admin_url": "http://localhost:8001/admin/abc12345",
  "analytics_url": "http://localhost:8001/analytics/abc12345",
  "deployment_details": {
    "deployment_id": "abc12345",
    "status": "deployed",
    "created_at": "2025-05-27T10:30:00",
    "site_name": "My Test Site"
  }
}'

echo -e "\n=== Then visit the live_url in your browser to see the deployed site! ==="

# Alternative: Minimal example
echo -e "\n\n=== MINIMAL EXAMPLE ==="
echo "curl -X POST \"http://localhost:8001/api/deploy\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{"
echo "    \"site_name\": \"Quick Test\","
echo "    \"assets\": {"
echo "      \"html_template\": \"<html><body><h1>{{ brand_name }}</h1><p>{{ description }}</p></body></html>\","
echo "      \"css_styles\": \"body { text-align: center; font-family: Arial; }\""
echo "    },"
echo "    \"content_data\": {"
echo "      \"brand_name\": \"Hello World\","
echo "      \"description\": \"This is a test site!\""
echo "    }"
echo "  }'"
