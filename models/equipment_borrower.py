from odoo import models, fields

class EquipmentBorrower(models.Model):
    _name = 'equipment.borrower'
    _description = 'Data Peminjam Alat'

    # Data Peminjam
    name = fields.Char(string='Nama Lengkap', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Nomor Telepon')
