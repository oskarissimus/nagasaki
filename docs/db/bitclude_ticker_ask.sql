-- View: public.bitclude_ticker_ask

-- DROP VIEW public.bitclude_ticker_ask;

CREATE OR REPLACE VIEW public.bitclude_ticker_ask
 AS
 SELECT snapshot.id,
    snapshot."time",
    min(ask.price) AS min_ask_price
   FROM snapshot
     CROSS JOIN LATERAL jsonb_to_recordset(((((snapshot.state -> 'exchange_states') -> 'bitclude') -> 'orderbooks') -> 'ETH/PLN') -> 'asks') ask(price numeric, amount numeric)
  GROUP BY snapshot.id, snapshot."time";

ALTER TABLE public.bitclude_ticker_ask
    OWNER TO postgres;

