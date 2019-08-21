# DEAP-dataset
using deep learnin

nn_net: 搭建了一个三层神经网络，神经元的个数分别是500，100，4
注意tf.nn.sparse_cross_entroy.logit()的sparse，预测值只能取一类的，Logits和target的维度不一致
一般无sparse用交叉熵，首先要将标签进行one_hot编码
注意padding='same'or'valid'是针对卷积层还是池化层的