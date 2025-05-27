.PHONY: backend
backend:
	cd backend && adk api_server --allow_origins "http://localhost:3000"

.PHONY: web
web:
	cd web && npm run dev

.PHONY: renderer
renderer:
	cd renderer && uvicorn app:app --host 0.0.0.0 --port 8001 --reload

.PHONY: stop
stop:
	@echo "Stopping all services"
	@echo "Stopping backend"
	-pkill -f 'uvicorn.*8000'
	@echo "Stopping renderer"
	-pkill -f 'uvicorn.*8001'

	@echo "Stopping web"
	-pkill -f 'node.*web'
