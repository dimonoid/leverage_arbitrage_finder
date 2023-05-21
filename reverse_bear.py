import datetime
import math

import matplotlib.pyplot as plt
from polygon import RESTClient

client = RESTClient()


def download_candles():
    def candles(symbol="AAPL"):
        return client.get_aggs(
            symbol,
            1,
            "minute",  # minute
            "2022-01-01",
            "2022-01-14",
            limit=50000
        )

    # count1 / count_sum 0.30663030509630135 3598 11734 2.8794043110373444
    # count2 / count_sum 0.30603374808249534 3591 11734 2.893220656688251

    # count1 / count_sum 0.3112403735867606 3799 12206 2.8743597813952846
    # count2 / count_sum 0.30493200065541537 3722 12206 2.8701974104270107

    def get_next_cadle(list_of_candles):
        for candle in list_of_candles:
            yield (datetime.datetime.fromtimestamp(candle.timestamp / 1000.0), candle.vwap)

    a = candles("QQQ")
    g_a = get_next_cadle(a)

    b = candles("TQQQ")
    g_b = get_next_cadle(b)

    def get_synchronized_candles(g_a, g_b):
        e_a = g_a.__next__()
        e_b = g_b.__next__()
        while 1:
            if e_a == None or e_b == None:
                break

            if e_a[0] == e_b[0]:
                ret = (e_a[0], e_a[1], e_b[1])
                # print(ret)
                yield ret

                try:
                    e_a = g_a.__next__()
                    e_b = g_b.__next__()
                except StopIteration:
                    break

                continue

            if e_a[0] < e_b[0]:
                print(e_a[0], e_b[0], e_a[1], e_b[1], "e")
                e_a = g_a.__next__()

                print("skip a")

                continue

            if e_a[0] > e_b[0]:
                print(e_a[0], e_b[0], e_a[1], e_b[1], "e")
                e_b = g_b.__next__()

                print("skip b")

                continue

    # Consolidate candles. Maybe use pandas?
    buff_time = []
    buff_a = []
    buff_b = []

    try:
        g = get_synchronized_candles(g_a, g_b)
        i = g.__next__()
        first_a = i[1]
        first_b = i[2]

        buff_time.append(i[0])
        buff_a.append(1)
        buff_b.append(1)
        for i in g:
            print(i)
            buff_time.append(i[0])
            buff_a.append(i[1] / first_a)
            buff_b.append(i[2] / first_b)
    except StopIteration as e:
        print(e)

    return buff_time, buff_a, buff_b


def plot(buff_time, buff_a, buff_b, buff_model):
    fig = plt.figure()
    ax = fig.add_subplot()

    ax.plot(buff_time, buff_a, label="QQQ")
    ax.plot(buff_time, buff_b, label="TQQQ")
    ax.plot(buff_time, buff_model, label="model")

    # ax.plot(buff_time, candles_buff1, label="ln(dQQQ)")
    # ax.plot(buff_time, candles_buff2, label="ln(dTQQQ)")
    # # ax.plot(buff_time, candles_buff1, label="filtered(ln(dQQQ))")
    # # ax.plot(buff_time, candles_buff2, label="filtered(ln(dTQQQ))")
    # ax.plot(buff_time, candles_buff3, label="ln(dTQQQ)/ln(dQQQ)")
    # # ax.plot(buff_time, candles_buff7, label="filtered(ln(dTQQQ)/ln(dQQQ))")

    ax.legend()
    plt.grid()
    plt.show()


class Model:
    def __init__(self, initial_time):
        self.time = initial_time
        self.non_leveraged_price = 1.0

        self.leveraged_price = 1.0

        self.rebalancing_time_of_the_day = datetime.timedelta(hours=9, minutes=30, seconds=2)
        self.rebalancing_price = None

    def simulate_one_step(self, time_step, new_non_leveraged_price):
        self.leveraged_price *= (new_non_leveraged_price / self.non_leveraged_price) * 3  # TODO

        # self.time = time_step
        self.non_leveraged_price = new_non_leveraged_price

    def simulate(self, last_time, non_leveraged_prices):
        ret = []
        while self.time <= last_time:
            # for i in range(len(time)+1):
            self.simulate_one_step(self.time, non_leveraged_prices[i])  # TODO
            if self.rebalancing_price == None:
                ret.append(1)
                continue
            ret.append(self.leveraged_price)
            self.time += datetime.timedelta(minutes=1)
        return ret


def main():
    buff_time, buff_a, buff_b = download_candles()

    model = Model(buff_time[0])
    buff_model = model.simulate(buff_time[0:-1], buff_a[0:-1])

    plot(buff_time, buff_a, buff_b, buff_model)


if __name__ == '__main__':
    main()
