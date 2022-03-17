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

* Inicjalizacja stanu 
* Okresowe pobieranie kursu 
    - USD_PLN -> Trigeruje ASK/BID 
    - DERIBIT_BTC_USD  -> Triggeruje ASK/BID 
* Pobieranie kursu z bitclude na Websocketach Realtime -> Triggeruje ASK/BID 
* Refleksja na temat uzywania LMAX vs cos innego 

# yahoo finance api
wget https://www.yahoofinanceapi.com/yahoo-finance-api-specification.json

datamodel-codegen --input example/finance_quote.json --input-file-type json --output model.py

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
## get_actions_ask
```mermaid
flowchart
    K[get_actions_ask] --> M{is asking profitable?}
    M -- YES --> N[create desirable ofer: rate, amount]
    M -- NO --> O[/cancel all ask offers/]
    N --> P{"len(ask_offers) > 0?"}
    P -- YES --> R[cancel all ask offers]
    P -- NO --> S[/push desirable offer to bitclude/]
    R --> S

```

## get_actions_bid
```mermaid
flowchart
    K[get_actions_bid] --> M{is biding profitable?}
    M -- YES --> N[create desirable ofer: rate, amount]
    M -- NO --> O[/cancel all bid offers/]
    N --> P{"len(bid_offers) > 0?"}
    P -- YES --> R[cancel all bid offers]
    P -- NO --> S[/push desirable offer to bitclude/]
    R --> S

```