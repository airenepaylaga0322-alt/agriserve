def calculate_priority_score(monthly_income, loss_percentage, is_primary_income, has_prior_aid):
    """
    Calculates the priority score based on the Phase 2 Rubric.
    Max score is 100.
    """
    # Criterion A: Household Economic Vulnerability (40%)
    # Logic: Lower income = Higher vulnerability score. 
    poverty_threshold = 12000
    if monthly_income <= 0:
        score_a = 100
    elif monthly_income >= poverty_threshold:
        score_a = 0
    else:
        score_a = 100 - ((monthly_income / poverty_threshold) * 100)

    # Criterion B: Severity of Agricultural Loss (30%)
    score_b = float(loss_percentage)

    # Criterion C: Dependence on Farming (20%)
    score_c = 100 if is_primary_income else 50

    # Criterion D: Previous Assistance Adjustment (10%)
    score_d = 0 if has_prior_aid else 100

    # Calculate Weighted Total
    weighted_total = (
        (score_a * 0.40) + 
        (score_b * 0.30) + 
        (score_c * 0.20) + 
        (score_d * 0.10)
    )
    
    recommendation = "APPROVED" if weighted_total >= 60 else "REJECTED"
    
    return {
        "score_a": round(score_a, 2),
        "score_b": round(score_b, 2),
        "score_c": round(score_c, 2),
        "score_d": round(score_d, 2),
        "total": round(weighted_total, 2),
        "recommendation": recommendation
    }