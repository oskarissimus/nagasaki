# Dzień 2022-09-11

## godzina 11:09:12.875

```
nagasaki.clients.exchange_client:83 creating BID order_id=None symbol=ETH/PLN amount=0.53080000 price=7978.34 hidden=True post_only=True type=LIMIT
```

## godzina: 11:09:22.658 zfilowano order

```json
{
  "id": "6266557760221479314",
  "currency1": "eth",
  "currency2": "pln",
  "amount": "0.2350572000",
  "price": "7978.3400000000",
  "time_close": "2022-09-11 11:09:22.658",
  "fee_taker": 280,
  "fee_maker": 50,
  "type": "bid",
  "action": "open"
}
```

}

## godzina 11:09:22.735

```
nagasaki.clients.exchange_client:89 cancelling BID order_id=16571193 symbol=None amount=0.53080000 price=7978.34 hidden=None post_only=True type=LIMIT
```

## godzina 11:09:23.425

```
nagasaki.clients.exchange_client:83 creating BID order_id=None symbol=ETH/PLN amount=0.53080000 price=7978.34 hidden=True post_only=True type=LIMIT
```

## godzina: 11:09:23.619

Traceback:
"message": "Not enough money"
"code": 5051,
"timestamp": "0.56976100 1662894563",
"success": false,
Job "TraderApp.synchronize_state_and_execute_strategy (trigger: interval[0:00:10], next run at: 2022-09-11 11:09:32 UTC)" raised an exception

# jakieś query

```sql
SELECT
id,time,
(state->'exchange_states'->'bitclude'->'exchange_balance'->'used'->>'PLN')::DECIMAL as free_plns
FROM snapshot
WHERE (state->'exchange_states'->'bitclude'->'exchange_balance'->'used'->>'PLN')::DECIMAL < 0
ORDER BY time ASC


select * from order_maker WHERE time < '2022-09-11 11:09:42' and side = 'BID'
ORDER BY time DESC LIMIT 100


select * from my_trades where time_close < '2022-09-12 11:09:00' ORDER BY time_close DESC LIMIT 100

SELECT
id,time,state
FROM snapshot
WHERE id <= 267525
order by id desc
limit 10
```
