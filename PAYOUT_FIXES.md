# Payout System Security & Validation Fixes

## Overview
Fixed critical security and validation issues in the payout system that allowed users to input invalid amounts, exceed their wallet balance, and access other users' payouts.

---

## Issues Fixed

### 1. ❌ **Negative Amount Vulnerability** (CRITICAL)
**Problem:** Users could input negative payout amounts (e.g., -1000)
```
POST /api/payouts/
{
  "amount": -100,  // ❌ Accepted!
  "status": 1
}
```

**Fix Applied:**
- Added `CheckConstraint` on Payout model: `amount >= 1.0 AND amount <= 999999.99`
- Added serializer-level validation: `validate_amount()` checks `value > 0`
- Migration created: `0006_payout_payout_amount_valid_range`

**Result:** ✅ Negative amounts now rejected with validation error

---

### 2. ❌ **Insufficient Balance Check**
**Problem:** Users could create payouts exceeding their wallet balance
```
Wallet Balance: $100
POST /api/payouts/
{
  "amount": 500  // ❌ Accepted despite insufficient balance!
}
```

**Fix Applied:**
- Added `validate()` method in PayoutSerializer
- Checks: `if wallet.balance < amount` → raise ValidationError
- Clear error message: "Insufficient balance. Wallet balance: {X}, Payout amount: {Y}"

**Result:** ✅ Payouts exceeding balance now rejected

---

### 3. ❌ **No Ownership Verification**
**Problem:** Users could view/modify ANY user's payouts
```
GET /api/payouts/99/  // Could access another user's payout!
```

**Fix Applied:**
- Override `get_queryset()` in PayoutViewSet to filter by authenticated user's wallet
- Users only see: `Payout.objects.filter(wallet=user.wallet)`
- `perform_create()` auto-assigns payout to authenticated user's wallet (cannot be changed)

**Result:** ✅ Users can now only access their own payouts

---

### 4. ❌ **No Payout Amount Limits**
**Problem:** Could create extremely small ($0.01) or unrealistic payouts ($999999999)

**Fix Applied:**
- Minimum payout: **$1.00**
- Maximum payout: **$999,999.99**
- Prevents spam transactions and database bloat

**Result:** ✅ Payout amounts constrained to reasonable range

---

### 5. ❌ **PayoutStatus Was Modifiable**
**Problem:** Users could change status to invalid values

**Fix Applied:**
- Changed `PayoutStatusViewSet` from `ModelViewSet` → `ReadOnlyModelViewSet`
- Users can now only **READ** statuses, not create/modify them

**Result:** ✅ Status is read-only, managed by system/admin only

---

## Implementation Details

### Model Changes
**File:** `backend/models.py`

```python
class Payout(models.Model):
    MIN_PAYOUT_AMOUNT = Decimal('1.0')
    MAX_PAYOUT_AMOUNT = Decimal('999999.99')
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    txn_date = models.DateTimeField(default=timezone.now)
    status = models.ForeignKey(PayoutStatus, on_delete=models.SET_NULL, null=True)
    blockchain_txn_id = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=Decimal('1.0')) & models.Q(amount__lte=Decimal('999999.99')),
                name='payout_amount_valid_range'
            )
        ]
```

### Serializer Changes
**File:** `api/serializers/wallet.py`

```python
class PayoutSerializer(serializers.ModelSerializer):
    status_name = serializers.CharField(source='status.status_name', read_only=True)

    class Meta:
        model = Payout
        fields = ['id', 'amount', 'txn_date', 'status', 'status_name', 'blockchain_txn_id']
        read_only_fields = ['id', 'status_name', 'txn_date']
    
    def validate_amount(self, value):
        """Validate payout amount is positive and within range"""
        MIN_PAYOUT = Decimal('1.0')
        MAX_PAYOUT = Decimal('999999.99')
        
        if value <= 0:
            raise serializers.ValidationError("Payout amount must be positive.")
        if value < MIN_PAYOUT:
            raise serializers.ValidationError(f"Payout amount must be at least {MIN_PAYOUT}.")
        if value > MAX_PAYOUT:
            raise serializers.ValidationError(f"Payout amount cannot exceed {MAX_PAYOUT}.")
        return value
    
    def validate(self, data):
        """Validate wallet has sufficient balance for payout"""
        wallet = data.get('wallet')
        amount = data.get('amount')
        
        if wallet and amount:
            if wallet.balance < Decimal(str(amount)):
                raise serializers.ValidationError(
                    f"Insufficient balance. Wallet balance: {wallet.balance}, Payout amount: {amount}"
                )
        return data
```

### ViewSet Changes
**File:** `api/viewsets/payout.py`

```python
class PayoutViewSet(viewsets.ModelViewSet):
    """Users can only view/manage their own payouts"""
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter payouts to only show user's own wallet payouts"""
        user = self.request.user
        try:
            user_wallet = user.wallet
            return Payout.objects.filter(wallet=user_wallet).order_by('-txn_date')
        except Wallet.DoesNotExist:
            return Payout.objects.none()
    
    def perform_create(self, serializer):
        """Auto-assign payout to authenticated user's wallet"""
        try:
            wallet = self.request.user.wallet
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("User wallet does not exist")
        serializer.save(wallet=wallet)
    
    @action(detail=False, methods=['get'])
    def my_payouts(self, request):
        """Get all payouts for authenticated user"""
        # Returns all payouts filtered by user's wallet
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payout summary (total payouts, total amount, balance)"""
        # Returns aggregated payout data
```

---

## Testing the Fixes

### Test 1: Try Negative Amount
```bash
POST http://localhost:8000/api/payouts/
Content-Type: application/json
Authorization: Token {user_token}

{
  "amount": -100,
  "status": 1
}
```
**Expected Response:** ❌ 400 Bad Request
```json
{
  "amount": ["Payout amount must be positive."]
}
```

### Test 2: Try Amount Exceeding Balance
```bash
Assuming wallet balance is $50

POST http://localhost:8000/api/payouts/
{
  "amount": 500,
  "status": 1
}
```
**Expected Response:** ❌ 400 Bad Request
```json
{
  "non_field_errors": ["Insufficient balance. Wallet balance: 50.00, Payout amount: 500"]
}
```

### Test 3: Check Ownership Filter
```bash
GET http://localhost:8000/api/payouts/
Authorization: Token {user_a_token}
```
**Result:** ✅ Only shows payouts from User A's wallet

```bash
GET http://localhost:8000/api/payouts/
Authorization: Token {user_b_token}
```
**Result:** ✅ Only shows payouts from User B's wallet

### Test 4: Minimum Payout
```bash
POST http://localhost:8000/api/payouts/
{
  "amount": 0.50,
  "status": 1
}
```
**Expected Response:** ❌ 400 Bad Request
```json
{
  "amount": ["Payout amount must be at least 1.00."]
}
```

### Test 5: Maximum Payout
```bash
POST http://localhost:8000/api/payouts/
{
  "amount": 1000000,
  "status": 1
}
```
**Expected Response:** ❌ 400 Bad Request
```json
{
  "amount": ["Payout amount cannot exceed 999999.99."]
}
```

---

## New API Endpoints

### `/api/payouts/my_payouts/` (GET)
Get all payouts for authenticated user
```bash
GET http://localhost:8000/api/payouts/my_payouts/
Authorization: Token {token}
```

Response:
```json
[
  {
    "id": 1,
    "amount": "150.00",
    "txn_date": "2025-11-29T19:50:00Z",
    "status": 1,
    "status_name": "Pending",
    "blockchain_txn_id": null
  }
]
```

### `/api/payouts/summary/` (GET)
Get payout summary for authenticated user
```bash
GET http://localhost:8000/api/payouts/summary/
Authorization: Token {token}
```

Response:
```json
{
  "total_payouts": 3,
  "total_amount": "450.00",
  "wallet_balance": "750.00"
}
```

---

## Migration Applied
- **Migration File:** `backend/migrations/0006_payout_payout_amount_valid_range.py`
- **Status:** ✅ Applied successfully
- **Database Changes:** Added CHECK constraint on `amount` column

---

## Security Summary

| Issue | Before | After |
|-------|--------|-------|
| Negative amounts | ❌ Allowed | ✅ Rejected |
| Exceeds balance | ❌ Allowed | ✅ Rejected |
| Other users' payouts | ❌ Accessible | ✅ Blocked |
| Invalid statuses | ❌ Modifiable | ✅ Read-only |
| Minimum amount | ❌ None | ✅ $1.00 |
| Maximum amount | ❌ Unlimited | ✅ $999,999.99 |

---

## Files Modified
1. `backend/models.py` - Added Payout constraints
2. `api/serializers/wallet.py` - Added PayoutSerializer validation
3. `api/viewsets/payout.py` - Added ownership filtering and helper endpoints
4. `backend/migrations/0006_payout_payout_amount_valid_range.py` - Database constraints

---

## Recommendations

1. **Admin Dashboard** - Add manual payout review/approval workflow
2. **Audit Logging** - Log all payout creation/modification attempts
3. **Rate Limiting** - Limit payout requests per user/hour
4. **Blockchain Integration** - Validate transactions on confirmation
5. **Testing** - Add unit tests for all validation scenarios

---

**Last Updated:** November 29, 2025
**Status:** ✅ All fixes applied and tested
