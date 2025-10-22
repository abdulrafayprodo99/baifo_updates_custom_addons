from . import models




#   ARRAY_AGG(DISTINCT COALESCE(move.invoice_date, move.invoice_date)) AS invoice_date,
#                 ARRAY_AGG(DISTINCT COALESCE(CURRENT_DATE - move.invoice_date, CURRENT_DATE - move.invoice_date)) AS exact_days,
#                 ARRAY_AGG(DISTINCT payment_term_line.days) AS payment_term_days,
#                 ARRAY_AGG(DISTINCT COALESCE((CURRENT_DATE - move.invoice_date) - payment_term_line.days, (CURRENT_DATE - move.invoice_date) - payment_term_line.days)) AS over_due,
                
                
                
                
#              # custom fields start
#                     'invoice_date': query_res['invoice_date'][0] if len(query_res['invoice_date']) == 1 else None,
#                     'exact_days': query_res['exact_days'][0] if len(query_res['exact_days']) == 1 else None,
#                     'payment_term_days': query_res['payment_term_days'][0] if len(query_res['payment_term_days']) == 1 else None,
#                     'over_due': query_res['over_due'][0] if len(query_res['over_due']) == 1 else None,
#                     # custom fields end
                    
                    
#                      # custom fields start
#                     'invoice_date': None,
#                     'exact_days': None,
#                     'payment_term_days': None,
#                     'over_due': None,
#                     # custom fields end