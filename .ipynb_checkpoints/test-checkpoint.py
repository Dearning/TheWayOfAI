{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "bec4cf14",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import os\n",
    "import argparse\n",
    "from mindspore import context\n",
    "\n",
    "parser = argparse.ArgumentParser(description='MindSpore LeNet Example')\n",
    "parser.add_argument('--device_target', type=str, default=\"CPU\", choices=['Ascend', 'GPU', 'CPU'])\n",
    "\n",
    "args = parser.parse_known_args()[0]\n",
    "context.set_context(mode=context.GRAPH_MODE, device_target=args.device_target)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "7f22d28d",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import mindspore.dataset as ds\n",
    "import mindspore.dataset.transforms.c_transforms as C\n",
    "import mindspore.dataset.vision.c_transforms as CV\n",
    "from mindspore.dataset.vision import Inter\n",
    "from mindspore import dtype as mstype\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "5e54cb98",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "def create_dataset(data_path, batch_size=32, repeat_size=1,\n",
    "                   num_parallel_workers=1):\n",
    "    # 定义数据集\n",
    "    mnist_ds = ds.MnistDataset(data_path)\n",
    "    resize_height, resize_width = 32, 32\n",
    "    rescale = 1.0 / 255.0\n",
    "    shift = 0.0\n",
    "    rescale_nml = 1 / 0.3081\n",
    "    shift_nml = -1 * 0.1307 / 0.3081\n",
    "\n",
    "    # 定义所需要操作的map映射\n",
    "    resize_op = CV.Resize((resize_height, resize_width), interpolation=Inter.LINEAR)\n",
    "    rescale_nml_op = CV.Rescale(rescale_nml, shift_nml)\n",
    "    rescale_op = CV.Rescale(rescale, shift)\n",
    "    hwc2chw_op = CV.HWC2CHW()\n",
    "    type_cast_op = C.TypeCast(mstype.int32)\n",
    "\n",
    "    # 使用map映射函数，将数据操作应用到数据集\n",
    "    mnist_ds = mnist_ds.map(operations=type_cast_op, input_columns=\"label\", num_parallel_workers=num_parallel_workers)\n",
    "    mnist_ds = mnist_ds.map(operations=resize_op, input_columns=\"image\", num_parallel_workers=num_parallel_workers)\n",
    "    mnist_ds = mnist_ds.map(operations=rescale_op, input_columns=\"image\", num_parallel_workers=num_parallel_workers)\n",
    "    mnist_ds = mnist_ds.map(operations=rescale_nml_op, input_columns=\"image\", num_parallel_workers=num_parallel_workers)\n",
    "    mnist_ds = mnist_ds.map(operations=hwc2chw_op, input_columns=\"image\", num_parallel_workers=num_parallel_workers)\n",
    "\n",
    "    # 进行shuffle、batch操作\n",
    "    buffer_size = 10000\n",
    "    mnist_ds = mnist_ds.shuffle(buffer_size=buffer_size)\n",
    "    mnist_ds = mnist_ds.batch(batch_size, drop_remainder=True)\n",
    "\n",
    "    return mnist_ds\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "id": "542b0c26",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import mindspore.nn as nn\n",
    "from mindspore.common.initializer import Normal\n",
    "\n",
    "class LeNet5(nn.Cell):\n",
    "    \"\"\"\n",
    "    Lenet网络结构\n",
    "    \"\"\"\n",
    "    def __init__(self, num_class=10, num_channel=1):\n",
    "        super(LeNet5, self).__init__()\n",
    "        # 定义所需要的运算\n",
    "        self.conv1 = nn.Conv2d(num_channel, 6, 5, pad_mode='valid')\n",
    "        self.conv2 = nn.Conv2d(6, 16, 5, pad_mode='valid')\n",
    "        self.fc1 = nn.Dense(16 * 5 * 5, 120, weight_init=Normal(0.02))\n",
    "        self.fc2 = nn.Dense(120, 84, weight_init=Normal(0.02))\n",
    "        self.fc3 = nn.Dense(84, num_class, weight_init=Normal(0.02))\n",
    "        self.relu = nn.ReLU()\n",
    "        self.max_pool2d = nn.MaxPool2d(kernel_size=2, stride=2)\n",
    "        self.flatten = nn.Flatten()\n",
    "\n",
    "    def construct(self, x):\n",
    "        # 使用定义好的运算构建前向网络\n",
    "        x = self.conv1(x)\n",
    "        x = self.relu(x)\n",
    "        x = self.max_pool2d(x)\n",
    "        x = self.conv2(x)\n",
    "        x = self.relu(x)\n",
    "        x = self.max_pool2d(x)\n",
    "        x = self.flatten(x)\n",
    "        x = self.fc1(x)\n",
    "        x = self.relu(x)\n",
    "        x = self.fc2(x)\n",
    "        x = self.relu(x)\n",
    "        x = self.fc3(x)\n",
    "        return x\n",
    "\n",
    "# 实例化网络\n",
    "net = LeNet5()\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "fa9daf08",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# 定义损失函数\n",
    "net_loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "id": "826fed4c",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# 定义优化器\n",
    "net_opt = nn.Momentum(net.trainable_params(), learning_rate=0.01, momentum=0.9)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "id": "6b9b3155",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "from mindspore.train.callback import ModelCheckpoint, CheckpointConfig\n",
    "# 设置模型保存参数\n",
    "config_ck = CheckpointConfig(save_checkpoint_steps=1875, keep_checkpoint_max=10)\n",
    "# 应用模型保存参数\n",
    "ckpoint = ModelCheckpoint(prefix=\"checkpoint_lenet\", config=config_ck)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "id": "a724bf6b",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "# 导入模型训练需要的库\n",
    "from mindspore.nn import Accuracy\n",
    "from mindspore.train.callback import LossMonitor\n",
    "from mindspore import Model\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "id": "679f901f",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "def train_net(args, model, epoch_size, data_path, repeat_size, ckpoint_cb, sink_mode):\n",
    "    \"\"\"定义训练的方法\"\"\"\n",
    "    # 加载训练数据集\n",
    "    ds_train = create_dataset(os.path.join(data_path, \"train\"), 32, repeat_size)\n",
    "    model.train(epoch_size, ds_train, callbacks=[ckpoint_cb, LossMonitor(125)], dataset_sink_mode=sink_mode)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "id": "0a80c812",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "def test_net(network, model, data_path):\n",
    "    \"\"\"定义验证的方法\"\"\"\n",
    "    ds_eval = create_dataset(os.path.join(data_path, \"test\"))\n",
    "    acc = model.eval(ds_eval, dataset_sink_mode=False)\n",
    "    print(\"{}\".format(acc))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "id": "24894d53",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "epoch: 1 step: 125, loss is 2.2816765\n",
      "epoch: 1 step: 250, loss is 2.2997642\n",
      "epoch: 1 step: 375, loss is 2.2928383\n",
      "epoch: 1 step: 500, loss is 2.2595525\n",
      "epoch: 1 step: 625, loss is 2.0352666\n",
      "epoch: 1 step: 750, loss is 0.5036373\n",
      "epoch: 1 step: 875, loss is 0.37264502\n",
      "epoch: 1 step: 1000, loss is 0.20490006\n",
      "epoch: 1 step: 1125, loss is 0.5872599\n",
      "epoch: 1 step: 1250, loss is 0.10938759\n",
      "epoch: 1 step: 1375, loss is 0.050717365\n",
      "epoch: 1 step: 1500, loss is 0.009906869\n",
      "epoch: 1 step: 1625, loss is 0.038485724\n",
      "epoch: 1 step: 1750, loss is 0.059718803\n",
      "epoch: 1 step: 1875, loss is 0.40282312\n",
      "{'Accuracy': 0.9644431089743589}\n"
     ]
    }
   ],
   "source": [
    "\n",
    "train_epoch = 1\n",
    "mnist_path = \"./datasets/MNIST_Data\"\n",
    "dataset_size = 1\n",
    "model = Model(net, net_loss, net_opt, metrics={\"Accuracy\": Accuracy()})\n",
    "train_net(args, model, train_epoch, mnist_path, dataset_size, ckpoint, False)\n",
    "test_net(net, model, mnist_path)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "id": "14eaae27",
   "metadata": {},
   "outputs": [
    {
     "ename": "SyntaxError",
     "evalue": "invalid syntax (Temp/ipykernel_21928/3982065139.py, line 1)",
     "output_type": "error",
     "traceback": [
      "\u001b[1;36m  File \u001b[1;32m\"C:\\Users\\sjc\\AppData\\Local\\Temp/ipykernel_21928/3982065139.py\"\u001b[1;36m, line \u001b[1;32m1\u001b[0m\n\u001b[1;33m    python mindsporetest.ipynb --device_target=CPU\u001b[0m\n\u001b[1;37m                       ^\u001b[0m\n\u001b[1;31mSyntaxError\u001b[0m\u001b[1;31m:\u001b[0m invalid syntax\n"
     ]
    }
   ],
   "source": [
    "\n",
    "python mindsporetest.ipynb --device_target=CPU\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "56a7dc17",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "from mindspore import load_checkpoint, load_param_into_net\n",
    "# 加载已经保存的用于测试的模型\n",
    "param_dict = load_checkpoint(\"checkpoint_lenet-1_1875.ckpt\")\n",
    "# 加载参数到网络中\n",
    "load_param_into_net(net, param_dict)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0a2e6e77",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import numpy as np\n",
    "from mindspore import Tensor\n",
    "\n",
    "# 定义测试数据集，batch_size设置为1，则取出一张图片\n",
    "ds_test = create_dataset(os.path.join(mnist_path, \"test\"), batch_size=1).create_dict_iterator()\n",
    "data = next(ds_test)\n",
    "\n",
    "# images为测试图片，labels为测试图片的实际分类\n",
    "images = data[\"image\"].asnumpy()\n",
    "labels = data[\"label\"].asnumpy()\n",
    "\n",
    "# 使用函数model.predict预测image对应分类\n",
    "output = model.predict(Tensor(data['image']))\n",
    "predicted = np.argmax(output.asnumpy(), axis=1)\n",
    "\n",
    "# 输出预测分类与实际分类\n",
    "print(f'Predicted: \"{predicted[0]}\", Actual: \"{labels[0]}\"')\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "23ab4735",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "mindspore1.3",
   "language": "python",
   "name": "mindspore"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
