import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from apps.forms import PaymentForm


class WithdrawView(LoginRequiredMixin, UpdateView):
    template_name = 'apps/auth/withdraw.html'
    context_object_name = 'user'
    fields = '__all__'
    login_url = reverse_lazy('admin_page')

    def post(self, request, *args, **kwargs):
        user = request.user
        data = json.loads(request.body)
        # coin exchange
        if data.get('action') == 'coin_exchange':
            amount = int(data.get('amount'))
            if amount < 50:
                return JsonResponse({'type': 'error', 'message': "Sorov miqdori 50 COIN dan kam bo'lmasligi shart!"})
            if user.bonus > amount:
                user.balance += (1000 * amount)
                user.bonus -= amount
                user.save()
                return JsonResponse({
                    'message': "So'rov muvaffaqiyatli bajarildi",
                    'balance': user.balance
                })
            else:
                return JsonResponse({'type': 'error', 'message': "Sizda COIN yetarli emas!"})

            # withdraw to card
        if data.get('action') == 'card_withdraw':
            amount = int(data.get('amount'))
            if amount > 50000:
                form = PaymentForm(data)
                form.instance.user = user
                if form.is_valid() and user.balance > amount:
                    payment = form.save()
                    user.balance -= amount
                    user.save()
                    return JsonResponse({
                        'message': "So'rov muvaffaqiyatli bajarildi, admin javobini kuting!",
                        'balance': user.balance,
                        'created_at': payment.created_at.strftime("%Y-%m-%d %H:%M"),
                        # 'payment': serialize('json', payment)
                    })
                else:
                    return JsonResponse({'type': 'error', 'message': "Sizda mablag' yetarli emas!"})
            else:
                return JsonResponse({'type': 'error', 'message': "Sorov miqdori 50 000 so'mdan kam bo'lmasligi shart!"})
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user
