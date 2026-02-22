from fastapi.templating import Jinja2Templates

from app.utils.jinja_filters import from_json

# Single, shared Jinja environment for the whole frontend app.
templates = Jinja2Templates(directory="app/templates")
templates.env.filters["from_json"] = from_json
