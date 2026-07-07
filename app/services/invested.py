from datetime import datetime


def investment_process(invest_obj, lis_donations_obj):
    """Функция запускающая инвестиционный процесс по распределению
    полученных пожертвований на незакрытые проекты.
    """
    for donaion_obj in lis_donations_obj:
        needed_money = invest_obj.full_amount - invest_obj.invested_amount
        remaining_money = donaion_obj.full_amount - donaion_obj.invested_amount
        if needed_money <= remaining_money:
            invest_obj.invested_amount += needed_money
            donaion_obj.invested_amount += needed_money
        else:
            invest_obj.invested_amount += remaining_money
            donaion_obj.invested_amount += remaining_money
        if donaion_obj.invested_amount == donaion_obj.full_amount:
            donaion_obj.fully_invested = True
            donaion_obj.close_date = datetime.now()
        if invest_obj.invested_amount == invest_obj.full_amount:
            invest_obj.fully_invested = True
            invest_obj.close_date = datetime.now()
            break
