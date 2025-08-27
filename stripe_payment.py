import stripe
import os
from flask import jsonify

# Seting up Stripe API auth
stripe.api_key = os.environ["STRIPE_TEST_API_KEY"]


def create_payment_intent(amount, currency="usd"):

    """
    Takes an amount and currency (currently only supports USD) and
    returns a response object with a client secret to be used in the front end payment processing integration.
    """

    # Convert the dollar amount to cents
    amount = amount * 100
    
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        payment_method_types=['card']
    )

    return jsonify({
        'clientSecret': payment_intent['client_secret']
    })