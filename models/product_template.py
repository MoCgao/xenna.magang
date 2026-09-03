from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    loan_fine_fee = fields.Float(
        string='Nominal Denda Hilang', 
        help='Basis nominal denda jika barang hilang.'
    )