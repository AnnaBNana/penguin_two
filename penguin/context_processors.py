from datetime import (datetime, timedelta)
from apps.shop.models import VacationSettings

def cart_count(request): 
    cart = request.session.get('cart', [])
    return {'cart': len(cart)}

def vacation_settings(request):
   vc_settings = VacationSettings.load()
   today = datetime.now().date()
   end = vc_settings.end_date
   delay_weeks = (end-today).days//7
   return {'vacation_settings': vc_settings, 'delay_weeks': delay_weeks}
