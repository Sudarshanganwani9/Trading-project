import numpy as np


def robustness_score(
    percentage_return,
    max_drawdown,
    wfa_score,
    consistency_score,
    parameter_stability
):

    return_score = min(percentage_return / 2, 25)

    drawdown_score = max(0, 25 - max_drawdown)

    wfa_component = min(wfa_score / 4, 25)

    consistency_component = consistency_score * 15

    stability_component = parameter_stability * 10

    total = (
        return_score
        + drawdown_score
        + wfa_component
        + consistency_component
        + stability_component
    )

    return round(total, 2)


score = robustness_score(
    percentage_return=62,
    max_drawdown=11,
    wfa_score=82,
    consistency_score=0.9,
    parameter_stability=0.85
)

print('Robustness Score:', score)
