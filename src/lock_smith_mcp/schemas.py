"""JSON Schemas for POST /v1/audit — copied verbatim from the
LockSmith service's own discovery document (/.well-known/x402
in QuincyGB/lock-smith), which is the service's published
contract. Keep these in sync with the service, never fork them.
"""


AUDIT_INPUT_SCHEMA = {'properties': {'endpoint_url': {'description': 'Full URL of the x402 endpoint (paid route) to '
                                                'audit, e.g. '
                                                'https://service.example.com/v1/endpoint',
                                 'type': 'string'}},
 'required': ['endpoint_url'],
 'type': 'object'}


AUDIT_OUTPUT_SCHEMA = {'properties': {'audit_version': {'type': 'string'},
                'checks': {'items': {'properties': {'detail': {'type': 'string'},
                                                    'fix': {'type': 'string'},
                                                    'id': {'type': 'string'},
                                                    'name': {'type': 'string'},
                                                    'severity': {'enum': ['low',
                                                                          'medium',
                                                                          'high',
                                                                          'critical'],
                                                                 'type': 'string'},
                                                    'status': {'enum': ['pass',
                                                                        'finding',
                                                                        'not_tested'],
                                                               'type': 'string'}},
                                     'required': ['id', 'name', 'status', 'detail'],
                                     'type': 'object'},
                           'type': 'array'},
                'ok': {'type': 'boolean'},
                'probes_used': {'type': 'integer'},
                'scope_note': {'type': 'string'},
                'service': {'type': 'string'},
                'summary': {'properties': {'findings': {'type': 'integer'},
                                           'not_tested': {'type': 'integer'},
                                           'passed': {'type': 'integer'},
                                           'worst_severity': {'type': ['string', 'null']}},
                            'type': 'object'},
                'target': {'type': 'string'},
                'terms_observed': {'properties': {'amount_units': {'type': ['string', 'null']},
                                                  'asset': {'type': ['string', 'null']},
                                                  'network': {'type': ['string', 'null']},
                                                  'pay_to': {'type': ['string', 'null']},
                                                  'price': {'type': ['string', 'null']}},
                                   'type': 'object'},
                'verdict': {'enum': ['SECURE', 'FINDINGS', 'EXPOSED'], 'type': 'string'}},
 'required': ['ok',
              'service',
              'audit_version',
              'target',
              'verdict',
              'summary',
              'terms_observed',
              'checks',
              'probes_used',
              'scope_note'],
 'type': 'object'}
