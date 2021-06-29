name = 'Flutterwave payment acquirer'
config = {
    # PAY_ON_CHECKOUT
    # - checkout: Immediately an online payment is made, store are paid their entitlement
    #   as specified by the payout value of FM model.
    # - None: Payment will have to be made maually
    'PAY_ON_CHECKOUT': True,

    # WHEN_TO_PAY_STORES
    # - checkout: Immediately an online payment is made, store are paid their entitlement
    #   as specified by the payout value of FM model.
    # - None: Payment will have to be made maually
    'WHEN_TO_PAY_STORES': 'checkout',

    # WHEN_TO_PAY_DISPATCHERS
    # - checkout: Immediately an online payment is made, store are paid their entitlement
    #   as specified by the payout value of FM model.
    # - None: Payment will have to be made maually
    'WHEN_TO_PAY_DISPATCHERS': 'checkout',

    # PAY_FOR_STORE_REGISTERATION
    # - None: Users won't be prompted to pay for registeration
    # - amount+space+currency_code (e.g 1000 NGN): Users must pay to register store
    'PAY_FOR_STORE_REGISTERATION': '10 USD',

    # FLW_PUB_KEY
    # Flutterwave's public key for integrating frontend payments.
    'FLW_PUB_KEY': 'FLWPUBK_TEST-4b5acac8e21aceb3fc87f634a846c001-X',

    # FLW_SEC_KEY
    # Flutterwave's secret key for backend communications with your flutterwave's account
    'FLW_SEC_KEY': 'FLWSECK_TEST-604a7225885949af8eded44c605deb0c-X',
}
