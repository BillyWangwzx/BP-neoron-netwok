import numpy as np
def reLU(x):
    x = np.maximum(x, 0)
    return x


def dreLU(x):
    return np.sign(x)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def dsigmoid(x):
    z = sigmoid(x)
    return z * (1 - z)


class Neuoron_layer:
    def __init__(self, initial_w=None, initial_b=None, input_varnum=100, output_varnum=10):
        self.input_varnum = input_varnum
        self.output_varnum = output_varnum
        if initial_w:
            self.w = initial_w
        else:
            self.w = np.random.randn(input_varnum, output_varnum) * 0.01
        if initial_b:
            self.b = initial_b
        else:
            self.b = np.random.randn(1, output_varnum) * 0.01
        self.delta = np.ones(output_varnum)
        self.last_w_add = np.zeros((input_varnum, output_varnum))
        self.last_b_add = np.zeros((1, output_varnum))

    def calc(self, x):
        self.input = x
        self.a = np.dot(self.input, self.w) + np.dot(np.ones((self.input.shape[0], 1)), self.b)
        self.output = sigmoid(self.a)
        return self.output

    def update_param(self, y, layer='output', back_delta=None, back_weights=None, learning_rate=0.01, momentum=0):
        if layer == 'output':
            self.delta = (y - self.output)
        else:
            self.delta = np.dot(back_delta, back_weights.T) * dsigmoid(self.a)
        b_add = learning_rate * np.average(self.delta, axis=0)
        self.b = self.b + b_add + momentum * self.last_b_add
        self.last_b_add = b_add
        w_add = learning_rate * \
                np.average(np.array([self.input[i][:, None]@self.delta[i][None, :] for i in range(self.input.shape[0])]),axis=0)
        self.w += w_add + momentum * self.last_w_add
        self.last_w_add = w_add
        return self.w-w_add, self.delta


class Neuoron_network:
    def __init__(self, sizes):
        self.network = [Neuoron_layer(input_varnum=i, output_varnum=j) for (i, j) in zip(sizes[:-1], sizes[1:])]
        self.num_layer = len(sizes)

    def forward(self, x, y):
        result = x
        for i in range(len(self.network)):
            result = self.network[i].calc(result)

    def backward(self, x, y, learning_rate, momentum):
        back_weights, back_delta = self.network[-1].update_param(y, momentum=momentum)
        for i in range(2, self.num_layer):
            back_weights, back_delta = self.network[-i].update_param(y, layer='hidden', back_delta=back_delta,
                                                                     back_weights=back_weights,
                                                                     learning_rate=learning_rate,
                                                                     momentum=momentum)

    def fit(self, x, y, epoch_num):
        for j in range(epoch_num):
            self.forward(x, y)
            self.backward(x, y)

    def fit_SGD(self, train_data, train_target, learning_rate, min_batch_size=100, epoch_num=10,
                momentum=0):
        shuffle = np.random.choice(train_data.shape[0], train_data.shape[0], replace=False)
        train_data = train_data[shuffle]
        train_target = train_target[shuffle]
        for i in range(epoch_num):
            for j in range(train_target.shape[0] // min_batch_size):
                self.forward(train_data[j:j + min_batch_size], train_target[j:j + min_batch_size])
                self.backward(train_data[j:j + min_batch_size], train_target[j:j + min_batch_size],
                              learning_rate=learning_rate, momentum=momentum)
            #self.emulate(test_data, test_target)

    def predict(self, x):
        result = x
        for i in range(len(self.network)):
            result = self.network[i].calc(result)
        return result

    def emulate(self, test_data, test_target):
        z = [(x, int(y1)) for x, y1 in zip(np.argmax(self.predict(x=test_data), axis=1), test_target)]
        zs = np.sum(int(a == b) for a, b in z)
        print(zs)


