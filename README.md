# nagasaki

```
poetry shell
poetry install
pylint --errors-only $(git ls-files '*.py')
```

[] Bidding ASK
[] Hedging
[x] Added Hypothesis property based testing

Czy naprawiamy testy?
[]

Flow rzeczy

- Inicjalizacja stanu
- Okresowe pobieranie kursu
  - USD_PLN -> Trigeruje ASK/BID
  - DERIBIT_BTC_USD -> Triggeruje ASK/BID
- Pobieranie kursu z bitclude na Websocketach Realtime -> Triggeruje ASK/BID
- Refleksja na temat uzywania LMAX vs cos innego

# yahoo finance api

wget https://www.yahoofinanceapi.com/yahoo-finance-api-specification.json

datamodel-codegen --input example/finance_quote.json --input-file-type json --output model.py
datamodel-codegen --input orderbook_btcpln.json --input-file-type json --output model.py

# strategy execution flow

```mermaid
flowchart
classDef green fill:darkgreen;
classDef blue fill:darkblue;
A[Websocket client] --> B([event orderbook_changed is posted to EventManager])
B:::green --> C{{EventManager triggers attached handlers}}
C:::green --> D[/strategy_executor.on_orderbook_changed is triggered\]
D:::green --> E([event execute_strategy_requested is posted to EventManager])
E:::blue --> F{{EventManager triggers attached handlers}}
F:::blue --> G[/strategy_executor.on_execute_strategy_requested is triggered\]
G:::blue --> H[fetch AccountInfo and ActiveOffers]
H --> I{side}
I -- ASK --> K[get_actions_ask]
I -- BID --> L[get_actions_bid]
```

# strategy

![img](docs/img/strategy.jpg)

## get_actions_ask

- **REF** - cena referencyjna `USD_MARK_BTC * USD_PLN`
- **&Delta;** - arbitralny profit margin = `0.5%`
- **&epsilon;** - arbitralna wartość do przebijania TOP ASK = `0.01`
- **TOP_ASK** = `min(ask_orderbook)`
- **TOTAL_BTC** = BTC active + BTC inactive in Bitclude wallet

---

- **delta_price** = REF \* (1+&Delta;)
- **epsilon_price** = TOP_ASK - &epsilon;
- **desirable_price** = `max(delta_price,epsilon_price)`
- **desirable_amount** = TOTAL_BTC

---

### v1

```mermaid
flowchart
    N["desirable_order
    - desirable_price
    - desirable_amount"]
    N --> P{"len(ask_offers) > 0?"}
    P -- YES --> R[cancel all ask offers]
    P -- NO --> S[/push desirable offer to bitclude/]
    R --> S
```

---

### v2

```mermaid
flowchart
    N["desirable_order
    - desirable_price
    - desirable_amount"]
    N --> LEN{"len(ask_offers) == ?"}
    LEN -- ==0 --> PUSH[/push desirable offer to bitclude/]
    LEN -- ==1 --> TOLERANCE{"is
                    offer within
                    tolerance?"}
    TOLERANCE -- YES --> NOOP[/NOOP/]
    TOLERANCE -- NO --> CANCEL_ALL
    LEN -- >1 --> CANCEL_ALL[cancel all ask offers]


    CANCEL_ALL --> PUSH
```

# TODO 21.04.2022

- [x] databse module in nagasaki (sqlite) [done]
- [ ] create models for
  - [ ] bitlcude_ticker (timestamp, bid, ask)
  - [x] actions (mapping from Action class) [done]
  - [ ] inventory (timestamp, bitclude_balances pln_active, pln_inactive, btc_active, btc_inactive)
- [ ] create handlers for writing above data to db
  - [x] actions
- [ ] switch to postgres
- [ ] dry run

# TODO 02.06.2022

- [x] use api key scraper for yahoo
- [x] runtime config
- [x] delta adjusted for inventory
- [x] delta calculator
- [ ] pylint + black + isort pre-commit hook

# TODO 08.06.2022

- [ ] refactor trader/main.py
  - move clients init to another module and use as singelton
  - create strategy on demand
- [ ] rename `bitclude_id` in `Settings` and in `.env` files to `bitclude_client_id`
- [ ] rename `bitclude_key` in `Settings` and in `.env` files to `bitclude_client_key`

# TODO 6/9/22

- [x] Modify strategy tests to use granular states
- [x] Modify calculator tests to use granular states
- [x] Remove state object
- [x] Move strategy creation to containers
- [x] Clean up states' init/sync

# kimsufi housekeeping

```crontab
0 0 * * * docker image prune -a --force --filter "until=240h" > /root/crontab.log
```

# TODO 15.06.2022

- [x] make adapter class for `ccxt_exchange` client

# reinstall ccxt-unmerged after pushing to fork

```
pip uninstall ccxt-unmerged && poetry update ccxt-unmerged && poetry install
```

# TODO 27.07.2022

1. nagasaki/runtime_config.py zrobić żeby pod spodem była baza a reszta tak samo
2. change update_runtime_config api/main.py

# zajebiste query

```sql
select id, time, asks.min_ask, bids.max_bid
from snapshot
cross join lateral (
	select min(price) as min_ask
	from json_to_recordset
		( state::json->'exchange_states'->'bitclude'->'orderbooks'->'ETH/PLN'->'asks' )
	as ask(price decimal,amount decimal)
) asks
cross join lateral (
	select max(price) as max_bid
	from json_to_recordset
		( state::json->'exchange_states'->'bitclude'->'orderbooks'->'ETH/PLN'->'bids' )
	as bid(price decimal,amount decimal)
) bids
order by id desc
```

# one-liner to make tag and trigger deployment in actions

```
TAG=0.7.1; git tag $TAG && git push origin $TAG
```

# backup postgres

https://stackoverflow.com/questions/24718706/backup-restore-a-dockerized-postgresql-database

## Backup your databases

```
docker exec -t your-db-container pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql
```

## Restore your databases

```
cat your_dump.sql | docker exec -i your-db-container psql -U postgres
```
