from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender='purchases.Purchase')
def registrar_compra_en_caja(sender, instance, **kwargs):
    """Cuando una compra cambia su estado a 'received', registrarla como egreso en caja."""
    if not instance.pk:
        return  # Es creación, no actualización
    try:
        anterior = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    if anterior.status != 'received' and instance.status == 'received':
        try:
            from apps.modules.cash_management.models import CashMovement
            CashMovement.objects.create(
                type='expense',
                category='purchase',
                description=f'Compra #{instance.id} — {instance.supplier.name}',
                amount=instance.total,
                date=instance.date,
            )
        except Exception:
            pass  # No bloquear el cambio de estado si falla el registro
