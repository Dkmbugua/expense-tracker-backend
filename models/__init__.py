# models/__init__.py
from app.db import db

# Import models in correct order (User must come first)
from models.user import User  
from models.expenses import Expense
from models.income import Income
from models.budget_goal import BudgetGoal
from models.subscription import Subscription  # ✅ Subscription comes last
