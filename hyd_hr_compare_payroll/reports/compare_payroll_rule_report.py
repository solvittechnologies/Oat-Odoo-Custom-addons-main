# -*- coding: utf-8 -*-
from datetime import datetime

from openerp import api, models
from openerp.exceptions import Warning

from dateutil import relativedelta

FORMAT_DATE = "%Y-%m-%d"


def format_amount_to_integer(amount):
    """
    Convertit un nombre decimal en un entier.

    fonction qui formate un entier et le convertit en entier
    l'entier utilise est celui le plus proche du nombre decimal.
    """
    amount = round(amount, 2)
    return '{0:,}'.format(amount).replace(',', ' ')


class ComparePayrollRuleReport(models.AbstractModel):

    _name = 'report.hyd_hr_compare_payroll.compare_payroll_rule_template'

    @api.multi
    def _get_report_values(self, docids, data=None):

        if not data and not data['form']:
            raise Warning('No data')

        formulaire = data['form']

        domain1 = [
            ('date_from', '>=', formulaire['date_start1']),
            ('date_to', '<=', formulaire['date_end1'])]

        domain2 = [
            ('date_from', '>=', formulaire['date_start2']),
            ('date_to', '<=', formulaire['date_end2'])]

        bullpaie_obj = self.env['hr.payslip']
        bulletins_1 = bullpaie_obj.search(domain1)
        bulletins_2 = bullpaie_obj.search(domain2)

        datas = {}
        resultat_regles = []

        total_1 = 0
        total_2 = 0
        total_diff = 0

        select_rules = formulaire['select_rules']
        lignes_bull1 = bulletins_1.mapped("line_ids")
        lignes_bull2 = bulletins_2.mapped("line_ids")

        toutes_regles = lignes_bull1.mapped("salary_rule_id")
        toutes_regles |= lignes_bull2.mapped("salary_rule_id")

        if select_rules == "appears":
            toutes_regles = toutes_regles.filtered(
                lambda x: x.appears_on_payslip)

        if select_rules == "select":
            rules = formulaire['rules']
            toutes_regles = toutes_regles.filtered(
                lambda x: x.id in rules)

        for regle in toutes_regles:

            l_regles1 = [x for x in lignes_bull1 if x.code == regle.code]
            l_regles2 = [x for x in lignes_bull2 if x.code == regle.code]

            somme1 = sum([elt.total for elt in l_regles1])
            somme2 = sum([elt.total for elt in l_regles2])

            variation = somme2 - somme1

            total_1 += somme1
            total_2 += somme2
            total_diff += variation

            resultat_regles.append((
                regle.code,
                format_amount_to_integer(somme1),
                format_amount_to_integer(somme2),
                format_amount_to_integer(variation)))

        datas['regles_valeurs'] = resultat_regles
        datas['total_1'] = format_amount_to_integer(total_1)
        datas['total_2'] = format_amount_to_integer(total_2)
        datas['total_diff'] = format_amount_to_integer(total_diff)
        datas['date_start1'] = formulaire['date_start1']
        datas['date_end1'] = formulaire['date_end1']
        datas['date_start2'] = formulaire['date_start2']
        datas['date_end2'] = formulaire['date_end2']

        return {'doc_ids': docids, 'data': datas}
