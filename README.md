# Algo_Test

#### python3 -m tests.test_candle_data > results/test_candle_data_results.txt


##### ***TODO*** 

>Breaking up of EMA:
The previous close has to be below EMA and the close of this candle has to be above EMA.
So we take bullish trade on the open of the new candle


> Get current data. Also,
> * For a ONE_DAY interval , current data becomes history after 3:30 pm of current day
> * For a ONE_MINUTE interval, current data becomes history after a minute and likewise for ONE_HOUR and so on
> * All history is uploaded to database on cloud
> * * So Find a cloud which allows to host database for free
> * * What does work, docker and database as a microservice
