#mfcc_cnn_ps.py
#librosa.feature.mfcc(n_mfcc=20) 이용해서 저장한 데이터와 CNN을 이용하여 사운드 분류하는 코드입니다.
#데이터 프로세싱 코드는 mfcc_processing.py에 있습니다.

#모듈 임포트(numpy, tensorflow, math.ceil) 및 랜덤 지정
import numpy as np
import tensorflow as tf
from math import ceil
tf.set_random_seed(777) 

#트레이닝/테스트 셋 각각 데이터/라벨 임포트
trainData = np.genfromtxt('/home/paperspace/Downloads/trainData6.csv', delimiter=',')
trainData = trainData.reshape(-1, 20, 430)
testData = np.genfromtxt('/home/paperspace/Downloads/testData6.csv', delimiter=',')
testData = testData.reshape(-1, 20, 430)
trainLabel = np.genfromtxt('/home/paperspace/Downloads/trainLabel6.csv', delimiter=',')
testLabel = np.genfromtxt('/home/paperspace/Downloads/testLabel6.csv', delimiter=',')

#임포트한 데이터가 원하는 데이터가 맞는지 shape을 통해 확인
print(trainData.shape, testData.shape, trainLabel.shape, testLabel.shape)
# (6631, 20, 430) (2842, 20, 430) (6631,) (2842,)

#데이터 준비 끝.
#다시 돌릴때는 여기부터 
#그래프 초기화
tf.reset_default_graph()     

# hyper parameters
learning_rate = 0.0002
training_epochs = 300
batch_size = 200
steps_for_validate = 20

#placeholder
X = tf.placeholder(tf.float32, [None, 20, 430], name="X")
X_sound = tf.reshape(X, [-1, 20, 430, 1])          
Y = tf.placeholder(tf.int32, [None, 1], name="Y")
Y_onehot=tf.reshape(tf.one_hot(Y, 41), [-1, 41])
p_keep_conv = tf.placeholder(tf.float32, name="p_keep_conv")
p_keep_hidden = tf.placeholder(tf.float32, name="p_keep_hidden")


# L1 SoundIn shape=(?, 20, 430, 1)
W1 = tf.get_variable("W1", shape=[2, 21, 1, 32],initializer=tf.contrib.layers.xavier_initializer())
L1 = tf.nn.conv2d(X_sound, W1, strides=[1, 1, 1, 1], padding='SAME')
L1 = tf.nn.elu(L1)
L1 = tf.layers.batch_normalization(L1)
L1 = tf.nn.max_pool(L1, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='VALID') 
L1 = tf.nn.dropout(L1, p_keep_conv)

# L2 Input shape=(?,10,21,32)
W2 = tf.get_variable("W2", shape=[2, 21, 32, 32],initializer=tf.contrib.layers.xavier_initializer())
L2 = tf.nn.conv2d(L1, W2, strides=[1, 1, 1, 1], padding='SAME')
L2 = tf.nn.elu(L2)
L2 = tf.layers.batch_normalization(L2)
L2 = tf.nn.max_pool(L2, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='VALID') 
L2 = tf.nn.dropout(L2, p_keep_conv)

# L3 Input shape=(?,3,12,64)
W3 = tf.get_variable("W3", shape=[2, 21, 32, 32],initializer=tf.contrib.layers.xavier_initializer())
L3 = tf.nn.conv2d(L2, W3, strides=[1, 1, 1, 1], padding='SAME')
L3 = tf.nn.elu(L3)
L3 = tf.layers.batch_normalization(L3)
L3 = tf.nn.max_pool(L3, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='VALID') 
L3 = tf.nn.dropout(L3, p_keep_conv)

# L4 Input shape=(?,3,25,32)
W4 = tf.get_variable("W4", shape=[2, 21, 32, 32],initializer=tf.contrib.layers.xavier_initializer())
L4 = tf.nn.conv2d(L3, W4, strides=[1, 1, 1, 1], padding='SAME')
L4 = tf.nn.elu(L4)
L4 = tf.layers.batch_normalization(L4)
L4 = tf.nn.max_pool(L4, ksize=[1, 2, 2, 1],strides=[1, 2, 2, 1], padding='VALID') 
L4 = tf.nn.dropout(L4, p_keep_conv)
L4_flat= tf.reshape(L4, shape=[-1, 26*32])

# Final FC 2*3*128 inputs -> 41 outputs
W5 = tf.get_variable("W5", shape=[26*32, 185],initializer=tf.contrib.layers.xavier_initializer())
L5 = tf.nn.elu(tf.matmul(L4_flat, W5))
L5 = tf.layers.batch_normalization(L5)
L5 = tf.nn.dropout(L5, p_keep_hidden)
W_o = tf.get_variable("W_o", shape=[185,41],initializer=tf.contrib.layers.xavier_initializer())
b = tf.Variable(tf.random_normal([41]))
logits = tf.matmul(L5, W_o) + b
logits = tf.layers.batch_normalization(logits)
#logits shape=(?,41)

# define cost/loss & optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits,labels= Y_onehot))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost) # 아담버젼
predict_op = tf.argmax(logits, 1, name="pred")

# initialize
sess = tf.Session()
sess.run(tf.global_variables_initializer())
saver = tf.train.Saver()

# train my model
print('Learning started. It takes sometime.')
for epoch in range(training_epochs):
    avg_cost = 0
    total_batch = ceil(len(trainData) / batch_size)
    for i in range(total_batch):
        batch_xs = trainData[i*batch_size:(i+1)*batch_size]
        batch_ys = trainLabel[i*batch_size:(i+1)*batch_size].reshape(-1, 1)
        feed_dict = {X: batch_xs, Y: batch_ys, p_keep_conv: .8, p_keep_hidden: 0.7}
        c, _ = sess.run([cost, optimizer], feed_dict=feed_dict)
        avg_cost += c / total_batch
    if epoch % steps_for_validate == steps_for_validate-1:
        print('Epoch:', '%04d' % (epoch + 1), 'cost =', '{:.9f}'.format(avg_cost))
        correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(Y_onehot, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        x1=np.random.choice(testLabel.shape[0], 300, replace=False)
        print('TrainAccuracy:', sess.run(accuracy, feed_dict={
                X: trainData[x1], Y: trainLabel[x1].reshape(-1, 1), p_keep_conv: 1, p_keep_hidden: 1}))
        x2=np.random.choice(testLabel.shape[0], 300, replace=False)
        print('TestAccuracy:', sess.run(accuracy, feed_dict={
                X: testData[x2], Y: testLabel[x2].reshape(-1, 1), p_keep_conv: 1, p_keep_hidden: 1}))
        save_path = saver.save(sess, '/home/paperspace/Downloads/optx/optx')
print('Finished!')

