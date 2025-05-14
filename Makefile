.PHONY: backend
backend:
	cd backend && adk api_server --allow_origins "http://localhost:3000"

.PHONY: web
web:
	cd web && npm run dev

.PHONY: deploy
deploy:
	@echo "Deploying agent to Google Cloud Run..."
	@export $(shell cat .env | xargs) && \
	adk deploy cloud_run \
		--project=$$GOOGLE_CLOUD_PROJECT \
		--region=$$GOOGLE_CLOUD_LOCATION \
		--service_name=$$SERVICE_NAME \
		--app_name=$$APP_NAME \
		--with_ui \
		$$AGENT_PATH