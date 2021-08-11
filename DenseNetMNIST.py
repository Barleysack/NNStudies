import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.utils import save_image
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import os
import glob
import PIL
from PIL import Image
from torch.utils import data as D
from torch.utils.data.sampler import SubsetRandomSampler
import random
import torchsummary
from torchvision import datasets
import matplotlib.pyplot as plt
print(torch.__version__)
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu") 
print(device)

batch_size = 64
validation_ratio = 0.1
random_seed = 7993
initial_lr = 0.01
num_epoch = 300

#데이터 어그멘테이션은 스킵합니다. MNIST는 그 자체로 충분할 터.

from torchvision import datasets
mnist_train = datasets.MNIST(root='./data/',train=True,transform=transforms.ToTensor(),download=True)
mnist_test = datasets.MNIST(root='./data/',train=False,transform=transforms.ToTensor(),download=True)
print ("mnist_train:\n",mnist_train,"\n")
print ("mnist_test:\n",mnist_test,"\n")
print ("Done.")
#마침 적당한 셀이 과제에 있어 뜯어왔다. 


class ConvReluBatch(nn.Module):                     #DenseNet에 이런 뭉태기가 많이 쓰인다고, 동시에 구현하면 좋다길래 해뒀습니다. 
    def __init__(self, nin, nout, kernel_size, stride, padding, bias = False):
        super(ConvReluBatch,self).__init__()
        self.batch_norm = nn.BatchNorm2d(nin)
        self.relu = nn.ReLU(True)
        self.conv = nn.Conv2d(nin,nout,kernel_size=kernel_size,stride=stride,padding=padding,bias=bias)
    def __forward__(self,x):
        output = self.batch_norm(x)
        output = self.relu(output)
        output = self.conv(output)

        return output

class bottleneck_layer(nn.Sequential): #일어나서 여기 리뷰 매우 필요
    def __init__(self, nin, growth_rate, drop_rate=0.2):    
      super(bottleneck_layer, self).__init__()
      
      self.add_module('conv_1x1', ConvReluBatch(nin=nin, nout=growth_rate*4, kernel_size=1, stride=1, padding=0, bias=False))
      self.add_module('conv_3x3', ConvReluBatch(nin=growth_rate*4, nout=growth_rate, kernel_size=3, stride=1, padding=1, bias=False))
      
      self.drop_rate = drop_rate
      
    def forward(self, x):
      bottleneck_output = super(bottleneck_layer, self).forward(x)
      if self.drop_rate > 0:
          bottleneck_output = F.dropout(bottleneck_output, p=self.drop_rate, training=self.training)
          
      bottleneck_output = torch.cat((x, bottleneck_output), 1)
      
      return bottleneck_output





#평가까지 해주는 편안한 셀이 있는데 안쓸 이유가 없죠
n_sample = 25
sample_indices = np.random.choice(len(mnist_test.targets),n_sample,replace=False)
test_x = mnist_test.data[sample_indices]
test_y = mnist_test.targets[sample_indices]
with torch.no_grad():
    C.eval() # to evaluation mode #put model name in
    y_pred = C.forward(test_x.view(-1,1,28,28).type(torch.float).to(device)/255.)
y_pred = y_pred.argmax(axis=1)
plt.figure(figsize=(10,10))
for idx in range(n_sample):
    plt.subplot(5, 5, idx+1)
    plt.imshow(test_x[idx], cmap='gray')
    plt.axis('off')
    plt.title("Pred:%d, Label:%d"%(y_pred[idx],test_y[idx]))
plt.show()    
print ("Done")
    