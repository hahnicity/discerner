require(its)
require(tseries)


get.quotes <- function(symbol, start, end, quote, retclass="zoo", compression="d", quiet=T) {
    #Get price data for a selected stock
    return(get.hist.quote(instrument=symbol,
                          start=start,
                          end=end,
                          quote=quote,
                          retclass=retclass,
                          compression=compression,
                          quiet=quiet))
}
