# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import Warning

FORMAT_DATE = "%Y-%m-%d"
NO_VARIATION = "NO DIFFERENCE FOUND BETWEEN THE 2 PERIODS"


def format_amount(amount):
    return '{0:,}'.format(amount).replace(',', ' ')


class ComparePayslipEmployeeReport(models.AbstractModel):

    _name = 'report.hyd_hr_compare_payroll.compare_payslip_employee_template'

    @api.multi
    def _get_report_values(self, docids, data=None):

        if data and data['form']:
            formulaire = data['form']

            domain1 = [
                ('date_from', '>=', formulaire['date_start1']),
                ('date_to', '<=', formulaire['date_end1'])]

            domain2 = [
                ('date_from', '>=', formulaire['date_start2']),
                ('date_to', '<=', formulaire['date_end2'])]

            if not formulaire['all_employee']:
                domain1.append(
                    ('employee_id', 'in', formulaire['employees']))

                domain2.append(
                    ('employee_id', 'in', formulaire['employees']))

            bullpaie_obj = self.env['hr.payslip']
            bulletins_1 = bullpaie_obj.search(domain1)
            bulletins_2 = bullpaie_obj.search(domain2)

            datas = {}
            total = {}

            resultat_regles = []
            employees = bulletins_1.mapped('employee_id')
            employees |= bulletins_2.mapped('employee_id')

            if not employees:
                raise Warning('NO PAYSLIP FOUND')

            for employee in employees:

                employee_name = employee.name

                bulletin_1 = bulletins_1.filtered(
                    lambda r: r.employee_id.id == employee.id)

                bulletin_2 = bulletins_2.filtered(
                    lambda r: r.employee_id.id == employee.id)

                regles_1 = bulletin_1.mapped('line_ids')
                regles_2 = bulletin_2.mapped('line_ids')

                toutes_regles = regles_1.mapped("salary_rule_id")
                toutes_regles |= regles_2.mapped("salary_rule_id")

                if formulaire['select_rules'] == "appears":
                    toutes_regles = toutes_regles.filtered(
                        lambda x: x.appears_on_payslip)
                elif formulaire['select_rules'] == "select":
                    toutes_regles = toutes_regles.filtered(
                        lambda x: x.id in formulaire['rules'])

                if not toutes_regles:
                    raise Warning(u'NO SALARY RULE')

                ligne = {}
                ligne['colonnes'] = []
                for regle_id in toutes_regles:

                    reg1 = regles_1.filtered(
                            lambda r: r.salary_rule_id.id == regle_id.id)
                    reg2 = regles_2.filtered(
                        lambda r: r.salary_rule_id.id == regle_id.id)

                    val_reg1 = sum(reg1.mapped('total'))
                    val_reg2 = sum(reg2.mapped('total'))

                    if val_reg2 == val_reg1:
                        continue

                    nom_regle = regle_id.name
                    status = 'No' if val_reg2 == val_reg1 else 'Yes'
                    variation = val_reg2 - val_reg1

                    ligne['colonnes'].append({
                        'champ': nom_regle,
                        'val1': format_amount(val_reg1),
                        'val2': format_amount(val_reg2),
                        'status': status,
                        'variation': format_amount(variation)})

                    # compute total
                    key_tuple = (nom_regle, regle_id.sequence)  # awesome!!!
                    if nom_regle in total.keys():
                        total[key_tuple] += variation
                    else:
                        total[key_tuple] = variation

                if ligne['colonnes']:
                    resultat_regles.append((employee_name, ligne))

            if not resultat_regles:
                raise Warning(_(NO_VARIATION))

            datas['regles_valeurs'] = resultat_regles
            datas['date_start1'] = formulaire['date_start1']
            datas['date_end1'] = formulaire['date_end1']
            datas['date_start2'] = formulaire['date_start2']
            datas['date_end2'] = formulaire['date_end2']

            result_total = [(x, format_amount(y)) for x, y in total.items()]
            result_total.sort(key=lambda x: x[0][1])
            datas['total'] = [(x[0][0], x[1]) for x in result_total]

        return {'doc_ids': docids, 'data': datas}
