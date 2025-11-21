Asset Class Reference Guide
Complete guide to all 12 supported asset classes and their typical transaction patterns.

📊 Asset Classes Overview
Asset ClassCodeTransaction CostsRecurring EventsData SourceEquityEQUITYBrokerage feesDividendsyfinanceETFETFBrokerage fees, TERDividends, feesyfinanceBondBONDTransaction feesCouponsManualUnit TrustUNIT_TRUSTNo transaction feesDistributions, feesScrapingPropertyPROPERTYTransfer costsRental incomeManualCommodityCOMMODITYTransaction feesStorage feesyfinanceCryptoCRYPTOExchange feesStaking rewardsManualFXFXConversion spreadsInterest differentialyfinanceMoney MarketMONEY_MARKETNo feesDaily interestManualBank AccountBANK_ACCOUNTAccount feesInterest incomeManualIndexINDEXN/A (benchmark)N/AyfinanceOtherOTHERUser-definedUser-definedManual

1. 📈 Equity (Stocks)
Typical Transactions:
pythonBUY:
- quantity: 100 shares
- price: R50.00
- fees: R10.00 (brokerage)
- net_amount: R5,010.00

DIVIDEND:
- dividend_per_share: R2.50
- quantity: 100
- gross_amount: R250.00
- taxes: R50.00 (20% dividend tax)
- net_amount: R200.00

SELL:
- quantity: -50 shares
- price: R55.00
- fees: R5.00 (brokerage)
- net_amount: R2,745.00
Recurring Events:

Quarterly Dividends - PER_SHARE calculation
Special Dividends - One-time events

South African Examples:

Naspers (NPN.JO)
FirstRand (FSR.JO)
Shoprite (SHP.JO)
MTN (MTN.JO)


2. 📊 ETF (Exchange-Traded Funds)
Typical Transactions:
pythonBUY:
- quantity: 500 units
- price: R70.00
- fees: R15.00 (brokerage)
- net_amount: R35,015.00

DIVIDEND:
- dividend_per_share: R1.20
- frequency: SEMI_ANNUAL
- net_amount: R480.00 (after tax)

FEE (TER):
- calculation_method: PERCENTAGE_VALUE
- amount_value: 0.35 (0.35% TER)
- frequency: ANNUAL
- basis: market_value
Recurring Events:

Dividends - Semi-annual or annual
TER (Total Expense Ratio) - Annual management fee
Rebalancing costs - Varies

South African Examples:

Satrix 40 (STX40.JO)
Satrix MSCI World (STXWDM.JO)
CoreShares Top 50 (CSTOP50.JO)


3. 💰 Bond
Typical Transactions:
pythonBUY:
- quantity: 10 bonds (R1000 face value each)
- price: R950.00 (clean price)
- fees: R50.00
- net_amount: R9,550.00

COUPON:
- calculation_method: PER_UNIT
- coupon_rate: 8.0% (annual)
- face_value: R10,000
- frequency: SEMI_ANNUAL
- amount_per_payment: R400.00

MATURITY:
- Receive: R10,000 (face value)
- plus final coupon
Recurring Events:

Coupon Payments - Semi-annual or annual
Accrued Interest - Daily calculation

South African Examples:

Government bonds (R186, R2032)
Corporate bonds


4. 🏢 Unit Trust (Mutual Fund)
Typical Transactions:
pythonBUY:
- quantity: 1000 units
- price: R15.50 (NAV)
- fees: R0.00 (no transaction fee)
- net_amount: R15,500.00

DISTRIBUTION:
- dividend_per_share: R0.85
- frequency: ANNUAL
- reinvested: Yes → Creates BUY transaction

FEE (Management):
- calculation_method: PERCENTAGE_NAV
- amount_value: 1.5 (1.5% annual)
- frequency: ANNUAL
- deducted_from_NAV: Yes
Recurring Events:

Annual Distributions - Often reinvested
Management Fees - % of NAV (1-2% typical)
Performance Fees - If applicable

South African Examples:

Allan Gray Balanced Fund
Coronation Equity Fund
Foord Equity Fund


5. 💱 FX (Foreign Exchange) - NEW!
Typical Transactions:
pythonBUY (Convert ZAR to USD):
- quantity: $1,000 USD
- exchange_rate: 18.50
- gross_amount: R18,500.00
- fees: R185.00 (1% conversion spread)
- net_amount: R18,685.00
- foreign_currency: USD
- foreign_amount: $1,000

SELL (Convert USD back to ZAR):
- quantity: -$1,000
- exchange_rate: 19.00
- gross_amount: R19,000.00
- fees: R190.00 (1% spread)
- net_amount: R18,810.00

INTEREST (Carry Trade):
- interest_rate: 2.5% (differential)
- calculation_method: PERCENTAGE_VALUE
- frequency: MONTHLY
Recurring Events:

Interest Differential - For carry trades
Rolling Costs - For leveraged positions

Transaction Costs:

Conversion Spread - 0.5% - 2%
Wire Fees - R50 - R200
Platform Fees - Varies

Use Cases:
python1. Currency Holdings:
   - Hold USD for offshore investments
   - Track realized/unrealized FX gains
   
2. Carry Trades:
   - Earn interest differential
   - Track daily/monthly interest

3. Hedging:
   - Hedge offshore equity exposure
   - Track hedge effectiveness
Examples:

USD/ZAR (USDZAR=X)
EUR/ZAR (EURZAR=X)
GBP/ZAR (GBPZAR=X)


6. 🏦 Money Market - NEW!
Typical Transactions:
pythonDEPOSIT (Initial):
- transaction_type: BUY
- quantity: 10000 units
- price: R1.00 (NAV)
- fees: R0.00
- net_amount: R10,000.00

INTEREST (Daily Accrual):
- calculation_method: PERCENTAGE_NAV
- amount_value: 7.5 (7.5% annual)
- frequency: DAILY
- gross_amount: R2.05 (daily interest)
- net_amount: R2.05

FEE (Management):
- calculation_method: PERCENTAGE_NAV
- amount_value: 0.15 (0.15% annual)
- frequency: ANNUAL
- deducted_from_NAV: Yes

WITHDRAWAL:
- transaction_type: SELL
- quantity: -5000 units
- price: R1.001 (accumulated NAV)
- net_amount: R5,005.00
Recurring Events:

Daily Interest - Compounds daily
Management Fees - Very low (0.1% - 0.3%)

Transaction Costs:

No transaction fees
No entry/exit penalties
Instant liquidity

Use Cases:
python1. Emergency Fund:
   - Track daily interest
   - Instant access
   - Better than bank account

2. Cash Allocation:
   - Part of asset allocation
   - Track as separate asset class
   - Compare to other fixed income

3. Parking Cash:
   - Between investments
   - Earn interest while deciding
   - Full capital protection
Examples:

Allan Gray Money Market Fund (AGMMF)
Investec Money Market Fund (INVMMF)
Coronation Money Market Fund


7. 🏦 Bank Account - NEW!
Typical Transactions:
pythonDEPOSIT:
- transaction_type: DEPOSIT
- amount: R50,000.00
- notes: "Opening deposit"

INTEREST (Monthly):
- calculation_method: PERCENTAGE_COST
- interest_rate: 5.5% (annual)
- frequency: MONTHLY
- gross_amount: R229.17 (monthly)
- taxes: R68.75 (30% interest tax)
- net_amount: R160.42

FEE (Monthly):
- transaction_type: FEE
- calculation_method: FIXED_AMOUNT
- amount_value: R65.00
- frequency: MONTHLY
- notes: "Account maintenance fee"

WITHDRAWAL:
- transaction_type: WITHDRAWAL
- amount: R10,000.00
- fees: R0.00 (if within limits)
Account Types:
Savings Account:
python- Interest: 3% - 6% annual
- Fees: R50 - R100/month
- Withdrawals: Limited (6 per month typical)
- Interest Frequency: MONTHLY
Fixed Deposit:
python- Interest: 7% - 10% annual
- Fees: None
- Withdrawals: Locked period (penalties if early)
- Interest Frequency: MONTHLY or AT_MATURITY
- Term: 1, 3, 6, 12, 24 months

Example Fixed Deposit:
DEPOSIT:
- amount: R100,000
- term: 12 months
- interest_rate: 8.5%

INTEREST (At Maturity):
- calculation_method: FIXED_AMOUNT
- gross_amount: R8,500.00
- taxes: R2,550.00 (30%)
- net_amount: R5,950.00

MATURITY:
- principal: R100,000
- interest: R5,950 (after tax)
- total_received: R105,950
Transactional Account:
python- Interest: 0% - 1%
- Fees: R100 - R300/month
- Withdrawals: Unlimited
- Primary: Cash management, not investment
Recurring Events:

Monthly Interest - Taxed at 30%
Account Fees - Monthly or annual
Transaction Fees - Per withdrawal/transfer

Transaction Costs:

Account Fees: R50 - R300/month
Withdrawal Fees: R5 - R20 per transaction
Early Termination (Fixed Deposit): Interest penalty

Use Cases:
python1. Track All Bank Products:
   - Savings accounts
   - Fixed deposits
   - Notice deposits
   - Holistic view of all assets

2. Interest Income Tracking:
   - Auto-calculate monthly interest
   - Track after-tax returns
   - Compare to other investments

3. Fee Monitoring:
   - Track account fees
   - Compare bank accounts
   - Optimize banking costs

4. Emergency Fund:
   - Separate from investments
   - Track liquidity
   - Include in net worth
Examples:

FNB Savings Account
Capitec Global One (5.5% interest)
ABSA 12-Month Fixed Deposit (7.5%)
Nedbank Notice Deposit
TymeBank SaveGoal


8. 📦 Other - NEW!
Purpose:
User-defined asset class for unique investments not fitting standard categories.
Typical Transactions:
pythonCUSTOM_BUY:
- transaction_type: BUY or OTHER
- quantity: User-defined
- price: User-defined
- notes: "Describe your asset"

CUSTOM_INCOME:
- transaction_type: DIVIDEND or INTEREST or OTHER
- calculation_method: User choice
- frequency: Any
Use Cases:
Peer-to-Peer Lending:
pythonDEPOSIT:
- amount: R10,000
- notes: "RainFin loan portfolio"

INTEREST (Monthly):
- calculation_method: PERCENTAGE_COST
- interest_rate: 12% annual
- frequency: MONTHLY
- gross_amount: R100.00

DEFAULT (Loss):
- transaction_type: OTHER
- amount: -R1,000
- notes: "Loan default loss"
Art & Collectibles:
pythonBUY:
- quantity: 1
- price: R50,000
- notes: "Limited edition artwork"
- fees: R2,500 (auction fees)

VALUATION (Annual):
- Update manually
- Track appreciation
- No recurring events
Private Equity:
pythonINVESTMENT:
- amount: R100,000
- notes: "Startup XYZ - Series A"

DISTRIBUTION:
- transaction_type: DIVIDEND
- amount: R5,000
- frequency: ANNUAL
- notes: "Dividend distribution"

EXIT:
- transaction_type: SELL
- proceeds: R250,000
- notes: "Company acquired"
Royalty Income:
pythonINITIAL:
- amount: R0
- notes: "Book royalties"

INCOME (Quarterly):
- transaction_type: INCOME
- calculation_method: FIXED_AMOUNT
- amount_value: varies
- frequency: QUARTERLY
Transaction Costs:

User-defined - Whatever applies to your asset

Recurring Events:

Fully flexible - Create any recurring pattern you need


🎯 Quick Reference: When to Use Each Asset Class
If You Have...Use Asset ClassWhyJSE stocksEQUITYFull API support, dividends trackedETFsETFTracks TER, special dividend handlingGovernment bondsBONDCoupon calculationsAllan Gray fundUNIT_TRUSTManagement fee trackingInvestment propertyPROPERTYRental income trackingGold/OilCOMMODITYPrice trackingBitcoinCRYPTOSeparate from other assetsUSD cashFXExchange rate trackingAllan Gray MMMONEY_MARKETDaily interest compoundingFNB savingsBANK_ACCOUNTInterest + fee trackingPeer-to-peer lendingOTHERCustom income patternsArt collectionOTHERManual valuation

🔄 Asset Class Migration Paths
Moving Between Asset Classes:
Some assets can be tracked under multiple classes - choose what makes sense for you:
Example 1: ETF vs Equity
Satrix Top 40 ETF:
✅ Recommended: ETF (tracks TER, proper categorization)
⚠️ Alternative: EQUITY (works, but misses ETF-specific features)
Example 2: Money Market vs Bank Account
High-interest savings:
If < 1% interest → BANK_ACCOUNT
If > 5% interest → MONEY_MARKET (better tracking)
Example 3: Unit Trust vs Other
Standard mutual fund → UNIT_TRUST
Obscure hedge fund → OTHER (more flexibility)

📊 Asset Allocation Strategy
Recommended Portfolio Mix (Example):
Conservative:
- 20% Equity
- 10% ETF
- 30% Bond
- 20% Unit_Trust
- 10% Money_Market
- 10% Bank_Account (emergency fund)

Balanced:
- 40% Equity
- 20% ETF
- 15% Bond
- 15% Unit_Trust
- 5% FX (offshore exposure)
- 5% Money_Market

Aggressive:
- 50% Equity
- 25% ETF
- 10% Unit_Trust
- 10% Property
- 5% Commodity/Crypto

✅ Checklist: Setting Up New Asset
When adding any new asset:

 Choose correct asset class
 Enter all transaction costs
 Set up recurring events (if any)
 Link to cash pool (if relevant)
 Configure tax treatment
 Add to appropriate portfolio
 Test calculations


Last Updated: Phase 1.1 Complete
Next: Phase 1.2 - Build calculators to use these asset classes