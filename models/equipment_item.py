from odoo import models, fields

class EquipmentItem(models.Model):
    _name = 'equipment.item'
    _description = 'Data Inventaris Alat'

    name = fields.Char(string='Nama Alat', required=True)
    code = fields.Char(string='Kode Inventaris', required=True)
    
    category = fields.Selection([
        ('laptop', 'Laptop'),
        ('proyektor', 'Proyektor'),
        ('kabel', 'Kabel'),
        ('lainnya', 'Lainnya')
    ], string='Kategori', required=True)
    
    state = fields.Selection([
        ('available', 'Available'),
        ('on_loan', 'On Loan'),
        ('damaged', 'Damaged')
    ], string='Status Alat', default='available')
    
    notes = fields.Text(string='Catatan')

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Kode inventaris (Barcode) harus unik dan tidak boleh sama!')
    ]