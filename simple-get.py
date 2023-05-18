import datetime
import math

import matplotlib.pyplot as plt
import polygon

client = RESTClient()


def candles(symbol="AAPL"):
    return client.get_aggs(
        symbol,
        1,
        "minute",  # nanos
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
            print(ret)
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


buff_time = []
buff_a = []
buff_b = []

try:
    for i in get_synchronized_candles(g_a, g_b):
        print(i)
        buff_time.append(i[0])
        buff_a.append(i[1])
        buff_b.append(i[2])
except StopIteration as e:
    print(e)

candles_buff1 = []
candles_buff2 = []
candles_buff3 = []
last = (buff_time[0], buff_a[0], buff_b[0])
for n, current in enumerate(zip(buff_time, buff_a, buff_b)):
    if current[1] == None or current[2] == None:
        continue

    rebalancing_time = current[0]
    rebalancing_n = n
    while True:
        rebalancing_time = buff_time[rebalancing_n]
        if (rebalancing_time + datetime.timedelta(hours=72)) < current[0]:
            print('Rebalancing time not found')
            exit()
            break
        if rebalancing_time.time().hour == 10 and \
                rebalancing_time.time().minute == 0 and \
                rebalancing_time.time().second == 0 and \
                rebalancing_time.time().microsecond == 0:
            print('Rebalancing time found', rebalancing_time, current[0])
            break
        rebalancing_n -= 1

    try:
        # ret1 = (math.log(current[1] / last[1]))
        ret1 = (current[1] - last[1]) / buff_a[rebalancing_n]

    except ZeroDivisionError:
        ret1 = 0

    try:
        # ret2 = (math.log(current[2] / last[2]))
        ret2 = (current[2] - last[2]) / buff_b[rebalancing_n]
    except ZeroDivisionError:
        ret2 = 0

    try:
        ret3 = ret2 / ret1
    except ZeroDivisionError:
        print('ZeroDivisionError')
        ret3 = 3.0  # TODO, or 3

    print(current, last, ret1, ret2, ret3)
    candles_buff1.append(ret1)
    candles_buff2.append(ret2)
    candles_buff3.append(ret3)

    last = current

# candles_buff4 = []
# last = candles_buff[0]
# for i in candles_buff:
#    last = last * 0.999 + i * 0.001
#    candles_buff4.append(last)

# candles_buff7 = []
# last = 3  # any value without error
# for n, i in enumerate(candles_buff6):
#    if i != 'error':
#        last = last * (0.999 - candles_buff3[n]) + i * (0.001 + candles_buff3[n])

#    candles_buff7.append(last)

magnitude_buff = []
angle_buff = []
count_sum = 0
count1 = 0
count2 = 0

avg1 = 0
avg2 = 0

for n, (x, y, z) in enumerate(zip(candles_buff1, candles_buff2, candles_buff3)):

    magnitude = math.sqrt(x ** 2 + y ** 2)

    # angle = math.degrees(math.atan2(y, x))
    try:
        angle = y / x
    except ZeroDivisionError:
        angle = 0

    if y < 0:
        magnitude = -magnitude
        # angle = -angle # TODO use for more intuitive placement of bottom 3rd and 4th quadrants

    try:
        if angle < 0:
            angle = -math.log(-angle)  # TODO check if this is correct
            angle = 0
        else:
            angle = math.log(angle)
            # angle=0
    except ValueError:
        angle = 0

    count_sum += 1
    if 1 <= z <= 5 and 0.005 <= math.sqrt((x * 3) ** 2 + y ** 2) and x > 0:
        count1 += 1
        avg1 += z
    if 1 <= z <= 5 and 0.005 <= math.sqrt((x * 3) ** 2 + y ** 2) and x < 0:
        count2 += 1
        avg2 += z

    magnitude_buff.append(magnitude)
    angle_buff.append(angle)

    print(x, y, magnitude, angle)

# print("count1 / count_sum", count1 / count_sum, count1, count_sum, avg1 / count1)
# print("count2 / count_sum", count2 / count_sum, count2, count_sum, avg2 / count2)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

x = candles_buff1
y = candles_buff2
z = candles_buff3

# z = candles_buff1[1:] + [0.0]  # TODO

ax.scatter(x, y, z, c='b', marker='x', label='QQQ/TQQQ/QQQ[t+1]')

# x = angle_buff
# y = magnitude_buff
# z = angle_buff[1:] + [0.0]

# ax.scatter(x, y, z, c='r', marker='x', label='Angle/Magnitude/Magnitude[t+1]')

ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# ax.set_xlim(min(candles_buff1), max(candles_buff1))
# ax.set_ylim(min(candles_buff2), max(candles_buff2))
# ax.set_zlim(min(candles_buff2[1:] + [0.0]), max(candles_buff2[1:] + [0.0]))

# ax.set_xlim(-0.005, 0.005)
# ax.set_ylim(-0.01, 0.01)
# ax.set_zlim(-0.01, 0.01)

plt.legend()
plt.grid()
fig.tight_layout()
plt.autoscale()

ax.set_xlim(-0.02, 0.02)
ax.set_ylim(-0.02, 0.02)
# ax.set_zlim(-0.02, 0.02)
ax.set_zlim(1., 5)

ax.set_proj_type('ortho')

wm = plt.get_current_fig_manager()
wm.window.state('zoomed')
plt.show()

fig = plt.figure()
ax = fig.add_subplot()

ax.plot(buff_time, buff_a, label="QQQ")
ax.plot(buff_time, buff_b, label="TQQQ")
ax.plot(buff_time, candles_buff1, label="ln(dQQQ)")
ax.plot(buff_time, candles_buff2, label="ln(dTQQQ)")
# ax.plot(buff_time, candles_buff1, label="filtered(ln(dQQQ))")
# ax.plot(buff_time, candles_buff2, label="filtered(ln(dTQQQ))")
ax.plot(buff_time, candles_buff3, label="ln(dTQQQ)/ln(dQQQ)")
# ax.plot(buff_time, candles_buff7, label="filtered(ln(dTQQQ)/ln(dQQQ))")

ax.legend()
plt.grid()
plt.show()
