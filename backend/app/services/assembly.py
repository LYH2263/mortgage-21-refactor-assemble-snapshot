"""组装步骤：输入校验后调用摊还引擎，得到未经裁剪的全表结果。"""
from app.engines.amortization import equal_payment_schedule


def assemble_schedule(principal: float, annual_rate: float, months: int) -> dict:
    if float(principal) <= 0:
        raise ValueError("principal")
    if float(annual_rate) < 0:
        raise ValueError("annual_rate")
    if int(months) <= 0:
        raise ValueError("months")
    return equal_payment_schedule(principal, annual_rate, months)
