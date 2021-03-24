This is a meant to serve as a website for the Seediq dictionary.

# Setup
1. Run `docker-compose up -d`
2. Enter `web` container: `docker-compose exec web bash`
3. Input initial files

   ```python
   from core.utils import load
   load()
   ```
# Troubleshooting

## `AppRegistryNotReady` error
```python
import django
django.setup()
```