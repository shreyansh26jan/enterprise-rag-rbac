from app.main import app
print('\n'.join(sorted(route.path for route in app.routes if hasattr(route, 'path'))))