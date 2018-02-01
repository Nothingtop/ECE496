import chainer
import chainer.functions as F
import chainer.links as L


class VGG7(chainer.Chain):

    def __init__(self, ch):
        self.ch = ch
        self.offset = 0
        self.inner_scale = 1
        super(VGG7, self).__init__(
            conv0=L.Convolution2D(ch, 32, 3, pad=1),
            conv1=L.Convolution2D(32, 32, 3, pad=1),
            conv2=L.Convolution2D(32, 64, 3, pad=1),
            conv3=L.Convolution2D(64, 64, 3, pad=1),
            conv4=L.Convolution2D(64, 128, 3, pad=1),
            conv5=L.Convolution2D(128, 128, 3, pad=1),
            conv6=L.Convolution2D(128, 256, 3, pad=1),
            conv7=L.Convolution2D(256, 256, 3, pad=1),
            conv8=L.Convolution2D(256, ch, 3, pad=1),
        )

    def __call__(self, x):
        h = F.leaky_relu(self.conv0(x), 0.1)
        h = F.leaky_relu(self.conv1(h), 0.1)
        h = F.leaky_relu(self.conv2(h), 0.1)
        h = F.leaky_relu(self.conv3(h), 0.1)
        h = F.leaky_relu(self.conv4(h), 0.1)
        h = F.leaky_relu(self.conv5(h), 0.1)
        h = F.leaky_relu(self.conv6(h), 0.1)
        h = F.leaky_relu(self.conv7(h), 0.1)
        y = self.conv8(h)
        return y


class UpConv7(chainer.Chain):

    def __init__(self, ch):
        self.ch = ch
        self.offset = 14
        self.inner_scale = 2
        super(UpConv7, self).__init__(
            conv0=L.Convolution2D(ch, 16, 3),
            conv1=L.Convolution2D(16, 32, 3),
            conv2=L.Convolution2D(32, 64, 3),
            conv3=L.Convolution2D(64, 128, 3),
            conv4=L.Convolution2D(128, 256, 3),
            conv5=L.Convolution2D(256, 256, 3),
            conv6=L.Deconvolution2D(256, ch, 4, 2, 3, nobias=True),
        )

    def __call__(self, x):
        h = F.leaky_relu(self.conv0(x), 0.1)
        h = F.leaky_relu(self.conv1(h), 0.1)
        h = F.leaky_relu(self.conv2(h), 0.1)
        h = F.leaky_relu(self.conv3(h), 0.1)
        h = F.leaky_relu(self.conv4(h), 0.1)
        h = F.leaky_relu(self.conv5(h), 0.1)
        y = self.conv6(h)
        return y


class ResBlock(chainer.Chain):

    def __init__(self, in_channels, out_channels, slope=0.1):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.slope = slope
        super(ResBlock, self).__init__(
            conv1=L.Convolution2D(in_channels, out_channels, 3),
            conv2=L.Convolution2D(out_channels, out_channels, 3),
        )
        if in_channels != out_channels:
            conv_bridge = L.Convolution2D(in_channels, out_channels, 1)
            self.add_link('conv_bridge', conv_bridge)

    def __call__(self, x):
        h = F.leaky_relu(self.conv1(x), self.slope)
        h = F.leaky_relu(self.conv2(h), self.slope)
        if self.in_channels != self.out_channels:
            x = self.conv_bridge(x[:, :, 2:-2, 2:-2])
        else:
            x = x[:, :, 2:-2, 2:-2]
        return h + x


class ResNet10(chainer.Chain):

    """Note

    No batch-norm, no padding and relu to leaky_relu

    """

    def __init__(self, ch):
        self.ch = ch
        self.offset = 13
        self.inner_scale = 1
        super(ResNet10, self).__init__(
            conv_fe=L.Convolution2D(ch, 64, 3),
            res1=ResBlock(64, 64),
            res2=ResBlock(64, 64),
            res3=ResBlock(64, 64),
            res4=ResBlock(64, 64),
            res5=ResBlock(64, 64),
            conv6=L.Convolution2D(64, 64, 3),
            conv_be=L.Convolution2D(64, ch, 3),
        )

    def __call__(self, x):
        h = skip = F.leaky_relu(self.conv_fe(x), 0.1)
        h = self.res1(h)
        h = self.res2(h)
        h = self.res3(h)
        h = self.res4(h)
        h = self.res5(h)
        h = F.leaky_relu(self.conv6(h), 0.1)
        h = h + skip[:, :, 11:-11, 11:-11]
        h = self.conv_be(h)
        return h


archs = {
    'VGG7': VGG7,
    'UpConv7': UpConv7,
    'ResNet10': ResNet10,
}

table = {
    '0': 'VGG7',
    '1': 'UpConv7',
    '2': 'ResNet10',
}
