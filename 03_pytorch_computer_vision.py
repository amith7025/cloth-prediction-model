# -*- coding: utf-8 -*-
"""03_PyTorch_computer_vision.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19TGliXi5jFhdZ5wJImEhqg5AknZ4MvFP

**section 3**

Computer vision and convevolutional neural network

torch vision

List item
List item
torchvision.datasets-get datasets and data loading function for computer vision here torchvision.models-get pretrained computer vision models that can leverage your problem torchvision.transforms-functions for manipulating your vision data for ml model

torch.utils.data.dataset-base dataset for pytorch torch.util.data.dataloader-creates a python iterable over dataset
"""



"""# computer vison libraries

"""

import torch
from torch import nn

import torchvision
from torchvision import datasets
from torchvision import transforms
from torchvision.transforms import ToTensor

#we will be use FASIONMNIST

#setup training data
train_data = datasets.FashionMNIST(
    root="data",#where you want to download
    train=True,#do you want training dataset
    download=True,#do you eant to download
    transform=torchvision.transforms.ToTensor(),#do you want to convert to tensor
    target_transform=None #how do we transform label

)

test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=torchvision.transforms.ToTensor(),
    target_transform=None
)

#see the first training example

image,label = train_data[0]
image,label

class_names = train_data.classes
class_names

class_to_idx = train_data.class_to_idx
class_to_idx

image.shape #color_chanel,height,width

class_names[label],image.shape

import matplotlib.pyplot as plt

print(f"image shape: {image.shape}")
plt.imshow(image.squeeze())
plt.title(label)

plt.imshow(image.squeeze(),cmap="gray")
plt.title(class_names[label])
plt.axis(False)

#plot more images

torch.manual_seed(42)
fig = plt.figure(figsize=(9,9))
rows,cols = 4,4
for i in range(1,rows*cols+1):
  random_idx = torch.randint(0,len(train_data),size=[1]).item()
  img,label = train_data[random_idx]
  fig.add_subplot(rows,cols,i)
  plt.imshow(img.squeeze(),cmap="gray")
  plt.title(class_names[label])
  plt.axis(False)

train_data,test_data

"""right now our data is in the form of pytorch datasets


DAtaloader turns our dataset into a python iterable

more specifically we want to turn our data into batches or mini batches

we want to break 60000 images to batches

by creating batches it is more computable and hardware can look into it
"""

from torch.utils.data import DataLoader

#setup the batchsize hyperparameter

BATCH_SIZE = 32
train_loader = DataLoader(dataset=train_data,
                          batch_size=BATCH_SIZE,
                          shuffle=True)

Test_loader = DataLoader(dataset=test_data,
                         batch_size=BATCH_SIZE,
                         shuffle=False)

train_loader,Test_loader

train_features_batch,train_label_batch = next(iter(train_loader))
train_features_batch.shape,train_label_batch.shape

len(train_loader),len(Test_loader)

torch.manual_seed(42)
random_idx = torch.randint(0,len(train_features_batch),size=[1]).item()
img,label = train_features_batch[random_idx],train_label_batch[random_idx]
plt.imshow(img.squeeze(),cmap='gray')
plt.title(class_names[label])
plt.axis(False)

#start with a baseline model
#baseline model is simple model.....start with simple and add complexity


#creating a flatten layer

flatten_model = nn.Flatten()

#get a single data

x = train_features_batch[0]
x.shape

#lets flatten the sample

output = flatten_model(x)
print(x.shape,output.shape)#x.shape ->color chanel,height,width
#output.shape->color chanel,width * height

#linear layer cant handle multi dimensional so we need to convert them to single dimensional

from torch import nn

class FASIONMNISTMODEL(nn.Module):
  def __init__(self,input_shape:int,
               hidden_units:int,
               output_shape:int):
    super().__init__()

    self.layer_stack = nn.Sequential(
        nn.Flatten(),
        nn.Linear(in_features=input_shape,
                  out_features=hidden_units),
        nn.Linear(in_features=hidden_units,
                  out_features=output_shape)
    )
  def forward(self,x):
    return self.layer_stack(x)

torch.manual_seed(42)

model = FASIONMNISTMODEL(input_shape=784,#width * height 28*28
                         hidden_units=10,#no of hidden units
                         output_shape=len(class_names)#for every class
                         ).to("cpu")

model

dummy_x = torch.rand(1,1,28,28)
model(dummy_x)

model.state_dict()

#set loss optimizer evaluating function

#loss function will be crossEntropy
#optimizer-SGD
#evaluation metric-accuracy

from pathlib import Path
import requests


if Path("helper_function.py").is_file():
    print("file already exist")
else:
    print("downloading helper function")
    request = requests.get("https://raw.githubusercontent.com/mrdbourke/pytorch-deep-learning/main/helper_functions.py")
    with open("helper_function.py","wb") as f:
        f.write(request.content)

from helper_function import accuracy_fn

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(params=model.parameters(),
                            lr=0.1)

#to time our experiment

from timeit import default_timer as timer

def print_time(start:float,
               end:float,
               device:torch.device=None):

  """print difference"""

  total_time = end - start

  print(f"train time on {device}:{total_time:.3f} seconds")

start_time = timer()

####
###
##
end_time = timer()
print_time(start=start_time,
           end=end_time,
           device="cpu")

#creating a training loop
#loop through epoch
#loop through training batches calculate train loss per batch
#loop through test loss calculate test loss per batch
#print the result

from tqdm.auto import tqdm

torch.manual_seed(42)

train_time_start_on_cpu = timer()
epochs = 3

for epoch in tqdm(range(epochs)):
  print(f"epoch:{epoch}\n---------")
  train_loss = 0
  for batch, (X,y) in enumerate(train_loader):
    model.train()
    y_pred = model(X)
    loss = loss_fn(y_pred,y)
    train_loss += loss #acccumalate train loss
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if batch % 400 == 0:
      print(f"looked at{batch * len(X)} / {len(train_loader.dataset)} samples")

  #divide total train loss by length of train loader
  train_loss /= len(train_loader)

  #testing loop
  test_loss,test_acc = 0,0
  model.eval()
  with torch.inference_mode():
    for X_test,y_test in Test_loader:
      test_pred = model(X_test)
      test_loss += loss_fn(test_pred,y_test)
      test_acc += accuracy_fn(y_true=y_test,y_pred=test_pred.argmax(dim=1))

    #calculate the test loss
    test_loss /= len(Test_loader)
    test_acc /= len(Test_loader)
  print(f"\n trainloss:{train_loss:.4f} | testloss:{test_loss:.4f} | test acc:{test_acc:.4f}%")

train_time_end_cpu = timer()

total_cpu = print_time(start=train_time_start_on_cpu,
                       end=train_time_end_cpu,
                       device=str(next(model.parameters()).device))

torch.manual_seed(42)

def eval_model(model:torch.nn.Module,
               data_loader:torch.utils.data.DataLoader,
               loss_fn:torch.nn.Module,
               accuracy_fn):
  loss,acc = 0,0
  model.eval()
  with torch.inference_mode():
    for X_test,y_test in tqdm(data_loader):
      y_pred_new = model(X_test)

      loss += loss_fn(y_pred_new,y_test)
      acc += accuracy_fn(y_true=y_test,
                         y_pred=y_pred_new.argmax(dim=1))

    loss /= len(data_loader)
    acc /= len(data_loader)
  return {"model name":model.__class__.__name__,
          "model_loss":loss.item(),
          "model_acc":acc}

model_result = eval_model(model=model,
                          data_loader=Test_loader,
                          loss_fn=loss_fn,
                          accuracy_fn=accuracy_fn)

model_result

device = "cuda" if torch.cuda.is_available() else "cpu"
device

from torch.nn.modules.activation import ReLU
#building a better model with non-linearity
import torch.nn as nn

class FASIONMNISTMODELV1(nn.Module):
  def __init__(self,input_shape:int,
               hidden_units:int,
               output_shape:int):
    super().__init__()
    self.layer_stack = nn.Sequential(
        nn.Flatten(),
        nn.Linear(in_features=input_shape,
                  out_features=hidden_units),
        nn.ReLU(),
        nn.Linear(in_features=hidden_units,
                  out_features=hidden_units),
        nn.ReLU(),
        nn.Linear(in_features=hidden_units,
                  out_features=output_shape)
    )
  def forward(self,x:torch.tensor):
    return self.layer_stack(x)

torch.manual_seed(42)

model_1 = FASIONMNISTMODELV1(input_shape=784,
                             hidden_units=10,
                             output_shape=len(class_names)).to(device)

next(model_1.parameters()).device

optimizer = torch.optim.SGD(params=model_1.parameters(),
                            lr=0.1)
loss_fn = nn.CrossEntropyLoss()

train_loss = 0
test_loss = 0
test_acc = 0

#create training function

def train_step(model:torch.nn.Module,
               data_loader:torch.utils.data.DataLoader,
               loss_fn:torch.nn.Module,
               optimizer:torch.optim,
               accuracy_fn,
               device:torch.device=device):
  train_loss,train_acc = 0,0
  model.train()
  for batch,(X,y) in enumerate(data_loader):
    X,y = X.to(device),y.to(device)

    y_pred = model(X)
    loss = loss_fn(y_pred,y)
    train_loss += loss
    train_acc += accuracy_fn(y_true=y,
                             y_pred=y_pred.argmax(dim=1))

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

  train_loss /= len(data_loader)
  train_acc /= len(data_loader)
  print(f"train_loss:{train_loss:.5f} | train_acc:{train_acc:.2f}%")

def test_step(model:torch.nn.Module,
              data_loader:torch.utils.data.DataLoader,
              loss_fn:torch.nn.Module,
              accuracy_fn,
              device:torch.device=device):

  test_loss,test_acc=0,0
  model.eval()
  with torch.inference_mode():
    for X,y in data_loader:
      X,y = X.to(device),y.to(device)

      test_pred = model(X)
      test_loss += loss_fn(test_pred,y)
      test_acc += accuracy_fn(y_true=y,
                              y_pred=test_pred.argmax(dim=1))

    test_loss /= len(data_loader)
    test_acc /= len(data_loader)
    print(f"test_loss:{test_loss:.5f} | test_acc:{test_acc:.2f}%")

torch.manual_seed(42)

train_time_start_gpu = timer()
epochs = 3

for epoch in tqdm(range(epochs)):
  print(f"epoch:{epoch}\n-----------")
  train_step(model=model_1,
             data_loader=train_loader,
             loss_fn=loss_fn,
             optimizer=optimizer,
             accuracy_fn=accuracy_fn,
             device=device)
  test_step(model=model_1,
             data_loader=train_loader,
             loss_fn=loss_fn,
             accuracy_fn=accuracy_fn,
             device=device)
train_time_end_gpu = timer()

total_train_time = print_time(start=train_time_start_gpu,
                              end=train_time_end_gpu,
                              device=device)

!nvidia-smi

torch.manual_seed(42)

def eval_model(model:torch.nn.Module,
               data_loader:torch.utils.data.DataLoader,
               loss_fn:torch.nn.Module,
               accuracy_fn,
               device=device):
  loss,acc = 0,0
  model.eval()
  with torch.inference_mode():
    for X_test,y_test in tqdm(data_loader):
      X_test,y_test = X_test.to(device),y_test.to(device)
      y_pred_new = model(X_test)

      loss += loss_fn(y_pred_new,y_test)
      acc += accuracy_fn(y_true=y_test,
                         y_pred=y_pred_new.argmax(dim=1))

    loss /= len(data_loader)
    acc /= len(data_loader)
  return {"model name":model.__class__.__name__,
          "model_loss":loss.item(),
          "model_acc":acc}

model_results_1 = eval_model(model=model_1,
                             data_loader=Test_loader,
                             loss_fn=loss_fn,
                             accuracy_fn=accuracy_fn,
                             device=device)

model_results_1

#Building CNN(convolutional neural network)
class FASIONMNISTMODEL2(nn.Module):
  def __init__(self,
               input_shape:int,
               hidden_units:int,
               output_shape:int):
    super().__init__()
    #create a conv layer
    self.conv_blk1 = nn.Sequential(
        nn.Conv2d(in_channels=input_shape,
                  out_channels=hidden_units,
                  kernel_size=3,
                  stride=1,
                  padding=1),#value we can set in cnn kernalsize:
        nn.ReLU(),
        nn.Conv2d(in_channels=hidden_units,
                  out_channels=hidden_units,
                  kernel_size=3,
                  stride=1,
                  padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2)
    )
    self.conv_blk2 = nn.Sequential(
        nn.Conv2d(in_channels=hidden_units,
                  out_channels=hidden_units,
                  kernel_size=3,
                  stride=1,
                  padding=1),
        nn.ReLU(),
        nn.Conv2d(in_channels=hidden_units,
                  out_channels=hidden_units,
                  kernel_size=3,
                  stride=1,
                  padding=1),
        nn.ReLU(),
        nn.MaxPool2d(kernel_size=2)
    )
    self.classifier = nn.Sequential(
        nn.Flatten(),
        nn.Linear(in_features=(hidden_units * 49),#trick to calculate this
                  out_features=output_shape)
    )

  def forward(self,x):
    x = self.conv_blk1(x)
    #print(x.shape)
    x = self.conv_blk2(x)
    #print(x.shape)
    x = self.classifier(x)
    #print(x.shape)
    return x

torch.manual_seed(42)

model_3 = FASIONMNISTMODEL2(input_shape=1,
                            hidden_units=10,
                            output_shape=len(class_names)).to(device)

model_3.state_dict()

torch.manual_seed(42)

images = torch.randn(size=(32,3,64,64))
test_image = images[0]
print("images shape:",images.shape)
print("test images shape:",test_image.shape)
print("test image:\n",test_image)

#create single conv layer

conv_layer = nn.Conv2d(in_channels=3,
                       out_channels=10,
                       kernel_size=3,
                       stride=1,
                       padding=0)

#pass the data through this layer

conv_output = conv_layer(test_image)
conv_output.shape

#create a maxpool2d

print(f"test image shape:{test_image.shape}")
print(f"test image with unsqueezed dimension: {test_image.unsqueeze(0).shape}")
max_pool = nn.MaxPool2d(kernel_size=2)
max_output = max_pool(conv_output)

max_output.shape

rand_image = torch.randn(size=(1,28,28))
rand_image.shape

model_3(rand_image.unsqueeze(0).to(device))

model_3(image.unsqueeze(0).to(device))

#loss function and optimizer for cnn

loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(params=model_3.parameters(),
                            lr=0.1)

epochs = 3

torch.manual_seed(42)
torch.cuda.manual_seed(42)
start_time = timer()
for epoch in tqdm(range(epochs)):
  print(f"epoch:{epoch}\n----------")
  train_step(model=model_3,
             data_loader=train_loader,
             loss_fn=loss_fn,
             optimizer=optimizer,
             accuracy_fn=accuracy_fn,
             device=device)

  test_step(model=model_3,
            data_loader=Test_loader,
            loss_fn=loss_fn,
            accuracy_fn=accuracy_fn,
            device=device)
  end_time = timer()

  total_time = print_time(start=start_time,
                          end=end_time,
                          device=device)

model_3_results = eval_model(
    model=model_3,
    data_loader=Test_loader,
    loss_fn=loss_fn,
    accuracy_fn=accuracy_fn,
    device=device
)

model_3_results

import pandas as pd

compare_results = pd.DataFrame({
    "model_1_result":model_result,
    "model_2_result":model_results_1,
    "model_3_result":model_3_results
})

compare_results

def make_predictions(model:torch.nn.Module,
                     data:list,
                     devic:torch.device=device):
  pred_probs = []

  model.eval()
  with torch.inference_mode():
    for sample in data:
      sample = torch.unsqueeze(sample,dim=0).to(device)
      #forward pass
      pred_logit = model(sample)
      pred_prob = torch.softmax(pred_logit.squeeze(),dim=0)

      #matplotlib dont work on gpu

      pred_probs.append(pred_prob.cpu())
  return torch.stack(pred_probs)

import random
random.seed(42)
test_samples = []
test_labels = []
for sample,label in random.sample(list(test_data),k=9):
  test_samples.append(sample)
  test_labels.append(label)

test_samples[7]

plt.imshow(test_samples[0].squeeze(),cmap="gray")
plt.title(class_names[test_labels[0]])

#make predictions

pred_probs = make_predictions(model=model_3,
                              data=test_samples)

pred_probs[:2]

pred_classes = pred_probs.argmax(dim=1)

pred_classes

plt.figure(figsize=(9,9))
nrows = 3
ncols = 3
for i,sample in enumerate(test_samples):
  plt.subplot(nrows,ncols,i+1)
  plt.imshow(sample.squeeze(),cmap="gray")
  #find prediction (in text form)
  pred_label = class_names[pred_classes[i]]
  #get the truth label
  truth_label = class_names[test_labels[i]]

  #create title
  title_text = f"pred: {pred_label} | Truth:{truth_label}"

  if pred_label == truth_label:
    plt.title(title_text,fontsize=10,c="g")
  else:
    plt.title(title_text,fontsize=10,c="r")

  #plt.axis(False)

torch.save(model_3,'model_architecture.pth')
torch.save(model_3.state_dict(), 'model_parameters.pth')

from PIL import













