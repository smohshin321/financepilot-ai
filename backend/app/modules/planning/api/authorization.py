from app.modules.identity.api.authorization import RequirePermission

require_budget_read = RequirePermission("budget.read")
require_budget_write = RequirePermission("budget.write")
require_budget_manage = RequirePermission("budget.manage")

__all__ = [
    "require_budget_manage",
    "require_budget_read",
    "require_budget_write",
]
