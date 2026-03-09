import numpy_financial as npf

def get_financial_metrics(income, expenses, debt):
    """Calculates Scenario 1: Budget Health."""
    surplus = income - expenses - debt
    savings_rate = (surplus / income * 100) if income > 0 else 0
    dti_ratio = (debt / income * 100) if income > 0 else 0
    return surplus, savings_rate, dti_ratio

def calculate_goal_roadmap(target, years, annual_return=0.08):
    """Calculates Scenario 2: Monthly savings needed for a goal."""
    months = years * 12
    monthly_rate = annual_return / 12
    # Returns the monthly payment needed to reach the future target
    required_monthly = abs(npf.pmt(monthly_rate, months, 0, target))
    return round(required_monthly, 2)

def create_ai_prompt(persona, income, expenses, debt, goal_name, target, years, surplus, s_rate, dti):
    """Structures the data for Gemini 2.0 Flash."""
    return f"""
    Act as a professional AI Financial Advisor. 
    USER PROFILE: {persona}
    
    FINANCIAL DATA:
    - Monthly Income: ₹{income}
    - Monthly Expenses: ₹{expenses}
    - Monthly Debt: ₹{debt}
    
    HEALTH METRICS:
    - Current Surplus: ₹{surplus}
    - Savings Rate: {s_rate:.1f}%
    - Debt-to-Income (DTI): {dti:.1f}%
    
    PRIMARY GOAL: Save ₹{target} for '{goal_name}' in {years} years.
    
    TASKS:
    1. Analyze budget health for a {persona}.
    2. Provide a 3-step action plan for the '{goal_name}'.
    3. Suggest an investment split (e.g., Mutual Funds vs. Gold).
    4. Provide one 'Money Nudge' to improve their surplus.
    """
