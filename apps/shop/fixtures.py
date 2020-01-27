SHIPPING_OPTIONS = {
    'domestic': {
        'lte5': {
            'usps': {
                'flat_rate': {
                    'price': 15,
                    'days': '1-3'
                },
                'express': {
                    'price': 60,
                    'days': '1-2'
                }
            },
            'fedex': {
                'express': {
                    'price': 100,
                    'days': '1-2'
                }
            }
        },
        'gt5': {
            'usps': {
                'flat_rate': {
                    'price': 30,
                    'days': '1-3'
                },
                'express': {
                    'price': 60,
                    'days': '1-2'
                }
            },
            'fedex': {
                'express': {
                    'price': 100,
                    'days': '1-2'
                }
            }
        }
    },
    'canada': {
        'lte5': {
            'usps': {
                'flat_rate': {
                    'price': 32,
                    'days': '5-7'
                },
                'express': {
                    'price': 80,
                    'days': '5-7'
                }
            },
            'fedex': {
                'express': {
                    'price': 100,
                    'days': '2-4'
                }
            }
        },
        'gt5': {
            'usps': {
                'flat_rate': {
                    'price': 40,
                    'days': '5-7'
                },
                'express': {

                }
            }
        }
    },
    'international': {

    }
}
