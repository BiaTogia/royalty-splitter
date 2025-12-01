from rest_framework import viewsets, permissions
from backend.models import Wallet
from api.serializers.wallet import WalletSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class WalletViewSet(viewsets.ModelViewSet):
    """
    CRUD + list for Wallets
    """
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Normal user yalnız öz wallet-ini görsün
        user = self.request.user
        if user.is_staff:  # admin bütün wallet-ləri görə bilir
            return Wallet.objects.all()
        return Wallet.objects.filter(user=user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Return the current user's primary wallet (or first wallet)."""
        user = request.user
        wallets = Wallet.objects.filter(user=user)
        if not wallets.exists():
            return Response({'detail': 'Wallet not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(wallets.first())
        return Response(serializer.data)
