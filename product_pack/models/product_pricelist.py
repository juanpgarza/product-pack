from odoo import models


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_product_price(self, product, *args, **kwargs):
        """Compute the pricelist price for the specified pack product, qty & uom.

        :returns: unit price of the pack product + components,
                  considering pricelist rules
        """
        self and self.ensure_one()
        if product._is_pack_to_be_handled():
            # NOTE: This exception is to avoid adding the list price of the packs
            # "totalized" and "non detailed". Should be removed to solve the issue #169.
            if (
                product.pack_type == "non_detailed"
                or product.pack_component_price == "totalized"
            ):
                pack_price = 0
            else:
                pack_price = self._compute_price_rule(product, *args, **kwargs)[
                    product.id
                ][0]

            for line in product.sudo().pack_line_ids:
                pack_price += line._get_pack_line_price(self, *args, **kwargs)
            return pack_price
        else:
            return super()._get_product_price(product, *args, **kwargs)

    def _get_products_price(self, products, *args, **kwargs):
        """Compute the pricelist price for the specified pack product, qty & uom.

        :returns: unit price of the pack product + components,
                  considering pricelist rules
        """
        packs, no_packs = products.split_pack_products()
        res = super()._get_products_price(no_packs, *args, **kwargs)
        for pack in packs:
            res[pack.id] = self._get_product_price(pack, *args, **kwargs)
        return res
