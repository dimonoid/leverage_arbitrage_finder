class Model:

    def __init__(self, started_date):
        self.n = 5
        self.history = [self.n]

        self.started_date = started_date

    def simulate_one_step(self):
        self.n *= 1.1
        self.history.insert(0, self.n)

    def __str__(self):
        return str(self.history)


def main(name):
    l = []
    for i in range(100):
        m = Model(i)
        l.append(m)

        for j in l:
            j.simulate_one_step()

    for i in l:
        print(i)


if __name__ == '__main__':
    main('PyCharm')
