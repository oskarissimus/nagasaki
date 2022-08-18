-- View: public.bitclude_ticker_bid

-- DROP VIEW public.bitclude_ticker_bid;

CREATE OR REPLACE VIEW public.bitclude_ticker_bid
 AS
 SELECT snapshot.id,
    snapshot."time",
    max(bid.price) AS max_bid_price
   FROM snapshot
     CROSS JOIN LATERAL jsonb_to_recordset(((((snapshot.state -> 'exchange_states') -> 'bitclude') -> 'orderbooks') -> 'ETH/PLN') -> 'bids') bid(price numeric, amount numeric)
  GROUP BY snapshot.id, snapshot."time";

ALTER TABLE public.bitclude_ticker_bid
    OWNER TO postgres;

