"""Replace this adapter when a payment and order provider is selected."""
class DemoPaymentProvider:
    def checkout(self, cart):
        return {'mode': 'demo', 'charged': False, 'order_submitted': False,
                'total': cart['total'], 'currency': 'SAR',
                'message': 'Demo checkout complete. No payment was taken and no order was submitted.'}
