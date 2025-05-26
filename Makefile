.PHONY: backend
backend:
	cd backend && adk api_server --allow_origins "http://localhost:3000"

.PHONY: web
web:
	cd web && npm run dev

.PHONY: renderer
renderer:
	cd renderer && uvicorn app.main:app --host 0.0.0.0 --port 8001 --allow_origins "http://localhost:8000" --reload

.PHONY: deploy
deploy:
	@echo "Deploying agent to Google Cloud Run..."
	@export $(shell cat backend/multi_agent_tool/.env | xargs) && \
	cd backend && adk deploy cloud_run \
		--project=$$GOOGLE_CLOUD_PROJECT \
		--region=$$GOOGLE_CLOUD_LOCATION \
		--service_name=$$SERVICE_NAME \
		--app_name=$$APP_NAME \
		--with_ui \
		$$AGENT_PATH
	
.PHONY: stop
stop:
	@echo "Stopping all services"
	@echo "Stopping backend"
	-pkill -f 'uvicorn.*8000'
	@echo "Stopping renderer"
	-pkill -f 'uvicorn.*8001'

	@echo "Stopping web"
	-pkill -f 'node.*web'