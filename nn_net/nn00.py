import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from sklearn.model_selection import train_test_split
from tensorflow.python.framework import ops
ops.reset_default_graph()

# Start a graph session
sess = tf.Session()

x = np.load('E:/py/DEAP/x_data2.npy')
x = x[:12000, :]
x = np.reshape(x, (-1,640))
#标准化
for i in range(12000):
    x[i, :] = (x[i,:] - np.mean(x[i,:]))/np.std(x[i,:])
x = np.reshape(x,(-1,640))
y = np.load('E:/py/DEAP/label_y60.npy')
y = y[:24000]

for i in range(10):
    test_xdata = x[i*2400:(i+1)*2400,:]
    test_labels = y[i*2400:(i+1)*2400]
    train_xdata1  = x[0:i*2400,:]
    train_xdata2 = x[(i+1)*2400:,:]
    train_labels1 = y[0:i*2400]
    train_labels2 = y[(i+1)*2400:]
    if i < 1:
        train_xdata = train_xdata2
        train_labels = train_labels2
    elif  i>0 and i<9:
        train_xdata = np.row_stack((train_xdata1, train_xdata2))
        train_labels = np.hstack((train_labels1,train_labels2))    # 将Vstack改成hstack
    else:
        train_xdata = train_xdata1
        train_labels = train_labels1


# Set model parameters
    batch_size = 200
    learning_rate = 0.005
    evaluation_size = 200
    target_size = np.max(train_labels) + 1
    generations = 2000
    eval_every = 5
    fully_connected_size1 = 100

# Declare model placeholders
    x_input = tf.placeholder(tf.float32, (batch_size,640))
    y_target = tf.placeholder(tf.int32, shape=(batch_size))
    eval_input = tf.placeholder(tf.float32, (evaluation_size,640))
    eval_target = tf.placeholder(tf.int32, shape=(evaluation_size))

# fully connected variables
    resulting_width = 25
    resulting_height = 20
    full1_input_size = resulting_width * resulting_height
    full1_weight = tf.Variable(tf.truncated_normal([640,full1_input_size],stddev=0.1, dtype=tf.float32))
    full1_bias = tf.Variable(tf.truncated_normal([full1_input_size], stddev=0.1, dtype=tf.float32))
    full2_weight = tf.Variable(tf.truncated_normal([full1_input_size, fully_connected_size1], stddev=0.1, dtype=tf.float32))
    full2_bias = tf.Variable(tf.truncated_normal([fully_connected_size1], stddev=0.1, dtype=tf.float32))
    full3_weight = tf.Variable(tf.truncated_normal([fully_connected_size1, target_size],stddev=0.1, dtype=tf.float32))
    full3_bias = tf.Variable(tf.truncated_normal([target_size], stddev=0.1, dtype=tf.float32))

# Initialize Model Operations
    def my_nn_net(nn_input_data):
        # First Fully Connected Layer
        fully_connected1 = tf.nn.relu(tf.add(tf.matmul(nn_input_data, full1_weight), full1_bias))
     # Second Fully Connected Layer
        fully_connected2 = tf.nn.relu(tf.add(tf.matmul(fully_connected1, full2_weight), full2_bias))
        final_model_output = tf.add(tf.matmul(fully_connected2, full3_weight), full3_bias)
        return final_model_output

    model_output = my_nn_net(x_input)
    test_model_output = my_nn_net(eval_input)

    # Declare Loss Function (softmax cross entropy)
    loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=model_output, labels=y_target))

    # Create a prediction function
    prediction = tf.nn.softmax(model_output)
    test_prediction = tf.nn.softmax(test_model_output)

    # Create accuracy function
    def get_accuracy(logits, targets):
        batch_predictions = np.argmax(logits, axis=1)    # 返回类别
        num_correct = np.sum(np.equal(batch_predictions, targets))
        return 100. * num_correct / batch_predictions.shape[0]

    # Create an optimizer
    my_optimizer = tf.train.MomentumOptimizer(learning_rate, 0.9)
    train_step = my_optimizer.minimize(loss)

    # Initialize Variables
    init = tf.global_variables_initializer()
    sess.run(init)

    # Start training loop
    train_loss = []
    train_acc = []
    test_acc = []
    for i in range(generations):
        rand_index = np.random.choice(len(train_xdata), size=batch_size)
        rand_x = train_xdata[rand_index]
        rand_y = train_labels[rand_index]
        train_dict = {x_input: rand_x, y_target: rand_y}
        sess.run(train_step, feed_dict=train_dict)
        temp_train_loss, temp_train_preds = sess.run([loss, prediction], feed_dict=train_dict)
        temp_train_acc = get_accuracy(temp_train_preds, rand_y)
        if (i + 1) % eval_every == 0:
            eval_index = np.random.choice(len(test_xdata), size=evaluation_size)
            eval_x = test_xdata[eval_index]
            eval_y = test_labels[eval_index]
            test_dict = {eval_input: eval_x, eval_target: eval_y}
            test_preds = sess.run(test_prediction, feed_dict=test_dict)
            temp_test_acc = get_accuracy(test_preds, eval_y)

            # Record and print results
            train_loss.append(temp_train_loss)
            train_acc.append(temp_train_acc)
            test_acc.append(temp_test_acc)
            acc_and_loss = [(i + 1), temp_train_loss, temp_train_acc, temp_test_acc]
            acc_and_loss = [np.round(x, 2) for x in acc_and_loss]
            print('第' + str(i+1) + 'Generation # {}. Train Loss: {:.2f}. Train Acc (Test Acc): {:.2f} ({:.2f})'.format(*acc_and_loss))


    # Matlotlib code to plot the loss and accuracies
    eval_indices = range(0, generations, eval_every)
    # Plot loss over time
    plt.plot(eval_indices, train_loss, 'k-')
    plt.title('Softmax Loss per Generation')
    plt.xlabel('Generation')
    plt.ylabel('Softmax Loss')
    plt.show()

    # Plot train and test accuracy
    plt.plot(eval_indices, train_acc, 'k-', label='Train Set Accuracy')
    plt.plot(eval_indices, test_acc, 'r--', label='Test Set Accuracy')
    plt.title('Train and Test Accuracy')
    plt.xlabel('Generation')
    plt.ylabel('Accuracy')
    plt.legend(loc='lower right')
    plt.show()


