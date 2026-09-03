from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EquipmentLoan(models.Model):
    _name = 'equipment.loan'
    _description = 'Equipment Loan Tracker'

    # ERD Relations
    equipment_id = fields.Many2one('product.product', string='Barang', required=True)
    borrower_id = fields.Many2one('res.partner', string='Peminjam', required=True)
    
    borrower_email = fields.Char(related='borrower_id.email', string='Email', readonly=True)
    borrower_phone = fields.Char(related='borrower_id.phone', string='Telepon', readonly=True)
    
    loan_date = fields.Date(string='Tanggal Pinjam', default=fields.Date.context_today)
    due_date = fields.Date(string='Tenggat Waktu', required=True)
    return_date = fields.Date(string='Tanggal Kembali')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
        ('late', 'Late'),
        ('lost', 'Lost')
    ], string='Status', default='draft')
    
    line_notes = fields.Text(string='Catatan')

    # ERD Document Relations (Inventory & Invoicing)
    picking_ids = fields.Many2many('stock.picking', string='Riwayat Stok Stock Picking')
    invoice_id = fields.Many2one('account.move', string='Invoice Denda', readonly=True)

    def action_confirm(self):
        for record in self:
            location_src = self.env.ref('stock.stock_location_stock')
            location_dest = self.env.ref('stock.stock_location_customers')
            picking_type_out = self.env.ref('stock.picking_type_out')

            quant = self.env['stock.quant'].search([
                ('product_id', '=', record.equipment_id.id),
                ('location_id', '=', location_src.id)
            ], limit=1)
            
            if not quant or quant.quantity <= 0:
                raise UserError(f"Stok untuk {record.equipment_id.name} sedang kosong di gudang!")

            picking = self.env['stock.picking'].create({
                'partner_id': record.borrower_id.id,
                'picking_type_id': picking_type_out.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'origin': record.display_name or 'Peminjaman',
            })

            self.env['stock.move'].create({
                'name': record.equipment_id.name,
                'product_id': record.equipment_id.id,
                'product_uom_qty': 1,
                'product_uom': record.equipment_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
            })

            picking.action_confirm()
            record.picking_ids = [(4, picking.id)]
            record.state = 'ongoing'

    def action_return(self):
        for record in self:
            location_src = self.env.ref('stock.stock_location_customers')
            location_dest = self.env.ref('stock.stock_location_stock')
            picking_type_in = self.env.ref('stock.picking_type_in')

            picking = self.env['stock.picking'].create({
                'partner_id': record.borrower_id.id,
                'picking_type_id': picking_type_in.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'origin': record.display_name or 'Peminjaman',
            })

            self.env['stock.move'].create({
                'name': record.equipment_id.name,
                'product_id': record.equipment_id.id,
                'product_uom_qty': 1, 
                'product_uom': record.equipment_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
            })

            picking.action_confirm()
            record.picking_ids = [(4, picking.id)]
            record.state = 'returned'
            record.return_date = fields.Date.context_today(self)

    def action_lost_penalty(self):
        self.ensure_one()
        
        # Pastikan partner peminjam sudah dipilih
        if not self.borrower_id:
            raise UserError(_("Peminjam belum dipilih pada transaksi ini!"))
        
        # Cari produk denda atau gunakan produk alat yang dipinjam sebagai referensi item tagihan
        # (Pastikan kamu memiliki produk khusus denda atau menggunakan equipment_id)
        product = self.equipment_id
        if not product:
            raise UserError(_("Barang / alat tidak ditemukan dalam transaksi!"))

        # Buat data account.move (Invoice / Tagihan)
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.borrower_id.id,
            'invoice_origin': self.display_name or 'Peminjaman Alat',
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': product.id,
                    'name': f"Denda Kehilangan Alat: {product.name}",
                    'quantity': 1.0,
                    'price_unit': product.list_price * 1.5, # Contoh: Denda 1.5x harga normal atau sesuaikan
                })
            ],
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        
        # Ubah status transaksi atau catat referensi invoice jika ada field-nya
        self.write({'state': 'lost'}) # Sesuaikan dengan status di modulmu

        # Mengembalikan aksi agar langsung membuka halaman Invoice yang baru dibuat
        return {
            'name': _('Invoice Denda'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }