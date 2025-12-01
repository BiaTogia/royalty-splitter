from decimal import Decimal
from django.utils import timezone

from .models import Royalty, Split, Wallet, Payout, PayoutStatus

ROYALTY_RATE_PER_MINUTE = Decimal("10.0")      # 1 dəqiqə üçün 10$
PLATFORM_FEE_PERCENT = Decimal("2.0")          # 2% platform fee


def distribute_royalty_for_track(track):
    """
    Uses track.payout_amount as the total earning to distribute.
    Split-lərə görə user-lərə bölür,
    Wallet balanslarını artırır,
    hər user üçün Payout (status=Pending) yaradır,
    eyni zamanda Royalty qeydini yaradır.
    """
    # Use uploader-defined payout amount
    total_earning = Decimal(str(track.payout_amount or 0))
    
    if total_earning <= 0:
        raise ValueError(f"Track payout_amount must be > 0, got {total_earning}")

    # Royalty qeydini yaradaq (audit üçün)
    royalty = Royalty.objects.create(
        track=track,
        total_earning=total_earning,
        distribution_date=timezone.now().date()
    )

    # Status
    pending_status, _ = PayoutStatus.objects.get_or_create(status_name="Pending")

    payouts_created = []

    for split in track.splits.all():
        # Brüt pay
        gross_share = (total_earning * Decimal(str(split.percentage))) / Decimal("100")

        # Platform fee çıxıldıqdan sonra
        net_share = gross_share * (Decimal("100") - PLATFORM_FEE_PERCENT) / Decimal("100")

        # Wallet tap / yarat
        wallet, _ = Wallet.objects.get_or_create(user=split.user)
        wallet.balance += net_share
        wallet.last_updated = timezone.now()
        wallet.save()

        # Pending payout yarat
        payout = Payout.objects.create(
            wallet=wallet,
            amount=net_share,
            status=pending_status,
            txn_date=timezone.now()
        )
        payouts_created.append(payout)

    return {
        "royalty_id": royalty.id,
        "track_id": track.id,
        "total_earning": total_earning,
        "payouts_count": len(payouts_created),
    }
