from fastapi import Request


def get_template_context(request: Request):
    #breakpoint()
    user_id = None
    restaurant_slug = None
    restaurant_id = None
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("sub")
        restaurant_slug = request.state.user.get("restaurant_slug")
        restaurant_id = request.state.user.get("restaurant_id")
    return {
        "request": request,
        "user_id": user_id,
        "restaurant_slug": restaurant_slug,
        "restaurant_id": restaurant_id
    }
