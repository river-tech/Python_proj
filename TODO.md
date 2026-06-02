# Debugging TODO

## Plan items
- [x] Add `faulthandler` enablement at the very top of `manage.py`.
- [x] Add `LOGGING` in `config/settings.py` to output `django.db.backends` and `django.request` logs to the console at DEBUG level.
- [x] Inspect `settings.py` and `config/urls.py` for async monkeypatching; specifically remove/disable `import config.monkeypatch` if present.

- [ ] (After edits) run the server and confirm that C-level tracebacks/logs appear on crash.


