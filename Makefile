PYTHON ?= python3
ENV_FILE ?= app/.env
ALEMBIC = $(PYTHON) -m alembic

define WITH_ENV
if [ -f $(ENV_FILE) ]; then \
	set -a; \
	. $(ENV_FILE); \
	set +a; \
fi; \
$(ALEMBIC) $(1)
endef

.PHONY: migrate downgrade revision history current heads stamp run

migrate:
	@$(call WITH_ENV,upgrade head)

downgrade:
	@$(call WITH_ENV,downgrade -1)

revision:
	@$(call WITH_ENV,revision --autogenerate -m "$(MESSAGE)")

history:
	@$(call WITH_ENV,history)

current:
	@$(call WITH_ENV,current)

heads:
	@$(call WITH_ENV,heads)

stamp:
	@$(call WITH_ENV,stamp $(if $(REVISION),$(REVISION),head))

run:
	@echo "Starting development server..."
	python app/main.py