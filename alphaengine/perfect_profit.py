import tensorflow as tf
import numpy as np
import progressbar


def tf_calculate_cost(rolling_positions, cost=0.01):
    return tf.abs(tf_diff_axis_0(rolling_positions)) * cost


def tf_sharpe_ratio(rolling_positions, rolling_volatility, cost=0.01):
    returns = rolling_positions * rolling_volatility

    returns -= tf_calculate_cost(rolling_positions, cost)

    risk_free_returns = tf.ones(rolling_positions.shape) * rolling_volatility

    sharpe_numerator = tf.reduce_mean(returns) - tf.reduce_mean(risk_free_returns)
    sharpe_denomenator = tf.math.reduce_std(returns)

    sharpe = tf.math.divide_no_nan(sharpe_numerator, sharpe_denomenator)

    return sharpe


def tf_diff_axis_0(a):
    _a = tf.concat(([a[0]], a), 0)
    return _a[1:] - _a[:-1]


def trading_loss(position, volatility, rolling_positions, rolling_volatility, loss_fn=tf_sharpe_ratio):
    current_loss = loss_fn(rolling_positions, rolling_volatility)

    next_positions = tf.concat([rolling_positions[1:], tf.cast(position, rolling_positions.dtype)], axis=0)
    next_volatility = tf.concat([rolling_volatility[1:], tf.cast(volatility, rolling_volatility.dtype)], axis=0)

    next_loss = loss_fn(next_positions, next_volatility)

    loss = tf.negative(next_loss - current_loss)

    return next_positions, next_volatility, loss


def returns_minus_cost(y, outputs, slippage=0.25, contract_cost=2.1, leverage=50):
    _outputs = (np.array(outputs) > 0).astype(int) * 2 - 1
    contracts_traded = np.abs(np.diff(_outputs, prepend=_outputs[0]))

    costs = contracts_traded * (contract_cost + slippage)

    returns = _outputs * (y * leverage)

    return returns - costs


def train_model_v1(model, optimizer, X, y, window_size=30, epochs=1):
    # Iterate over the batches of a dataset.
    for j in range(epochs):
        print(f'{j+1}/{epochs} epoch...')

        outputs = []
        losses = []

        rolling_positions = tf.zeros((window_size))
        rolling_volatility = tf.zeros((window_size))

        for i in progressbar.progressbar(range(len(X))):
            with tf.GradientTape() as tape:
                logits = model(np.expand_dims(X[i], axis=0))[0]

                # Compute the loss value for this batch.
                rolling_positions, rolling_volatility, loss_value = trading_loss(logits, np.expand_dims(y[i], axis=0),
                                                                                 rolling_positions, rolling_volatility)

                outputs.append(logits.numpy()[0])
                losses.append(loss_value)

            # Update the weights of the model to minimize the loss value.
            gradients = tape.gradient(loss_value, model.trainable_weights)
            optimizer.apply_gradients(zip(gradients, model.trainable_weights))

    return model, outputs, losses


def build_windowed_data(data, input_size=50, split=0.75):
    X_arr = []
    y_arr = []
    for i in range(len(data) - input_size):
        X_arr.append(data[i:i + input_size])
        y_arr.append(data[i + input_size])

    X = np.array(X_arr)
    y = np.array(y_arr)

    idx = int(len(X) * split)
    X_train = X[:idx]
    y_train = y[:idx]

    X_test = X[idx:]
    y_test = y[idx:]

    return np.nan_to_num(X_train), np.nan_to_num(y_train), np.nan_to_num(X_test), np.nan_to_num(y_test)


def build_batched_data(X, y, batch_size=100):
    X_arr = []
    y_arr = []
    for i in range(len(X) - batch_size):
        X_arr.append(X[i:i+batch_size])
        y_arr.append(y[i:i+batch_size])

    X_batches = np.array(X_arr)
    y_batches = np.expand_dims(np.array(y_arr), axis=-1).astype('float32')

    return X_batches, y_batches


def train_model_v3(X_batches, y_batches, model, epochs=10, optimizer=tf.keras.optimizers.Adam()):
    for j in range(epochs):
        print(f'{j + 1} / {epochs} epochs...')
        for i in progressbar.progressbar(range(len(X_batches))):
            with tf.GradientTape() as tape:
                logits = model(X_batches[i])
                loss = tf.cumsum(y_batches[i]) - tf.cumsum(logits * y_batches[i])

                # loss *= tf.cast(tf.range(1, len(y_batches[i]))[::1], tf.float32)

            gradients = tape.gradient(loss, model.trainable_weights)
            optimizer.apply_gradients(zip(gradients, model.trainable_weights))

        print(f'Loss: {np.average(loss)}')

    return model


def train_model_v4(model, X_train, y_train, X_test, y_test, epochs=10, optimizer=tf.keras.optimizers.Adam()):
    for i in progressbar.progressbar(range(epochs)):
        with tf.GradientTape() as tape:
            train_logits = model(X_train)
            train_loss = tf.cumsum(y_train) - tf.cumsum(train_logits * y_train)

            test_logits = model(X_test)
            test_loss = tf.cumsum(y_train) - tf.cumsum(test_logits * y_train)

        gradients = tape.gradient(train_loss, model.trainable_weights)
        optimizer.apply_gradients(zip(gradients, model.trainable_weights))

    print(f'Train loss: {np.average(train_loss)}\nTest loss: {np.average(test_loss)}')

    return model