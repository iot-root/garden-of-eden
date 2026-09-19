"""Optional external integrations.

Each integration is gated by a config flag and is a no-op until enabled and
configured. See docs/integrations/ for setup instructions. These are
intentionally thin scaffolds (issues #82 Alexa, #24 ThingsBoard, #16 Telegraf)
so the rest of the system stays shippable without external accounts/keys.
"""
