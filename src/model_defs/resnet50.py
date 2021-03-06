num_chan_in = 3
height = 512
width = 512
num_classes = 6
bn_momentum = 0.99

inputs = K.layers.Input([height, width, num_chan_in], name="DICOM")

params = dict(kernel_size=(3, 3),
                activation="relu",
                padding="same",
                kernel_initializer="he_uniform")

img_1 = K.layers.BatchNormalization(momentum=bn_momentum)(inputs)
img_1 = K.layers.Conv2D(32, **params)(img_1)
img_1 = K.layers.MaxPooling2D(pool_size=(2,2))(img_1)

img_1 = K.layers.Conv2D(64, **params)((K.layers.BatchNormalization(momentum=bn_momentum))(img_1))
img_1 = K.layers.MaxPooling2D(name='skip1', pool_size=(2,2))(img_1)

# Residual block
img_2 = K.layers.Conv2D(128, **params) ((K.layers.BatchNormalization(momentum=bn_momentum))(img_1))
img_2 = K.layers.Conv2D(64, name='img2', **params) ((K.layers.BatchNormalization(momentum=bn_momentum))(img_2))
img_2 = K.layers.add( [img_1, img_2] )
img_2 = K.layers.MaxPooling2D(name='skip2', pool_size=(2,2))(img_2)

# Residual block
img_3 = K.layers.Conv2D(128, **params)((K.layers.BatchNormalization(momentum=bn_momentum))(img_2))
img_3 = K.layers.Conv2D(64, name='img3', **params)((K.layers.BatchNormalization(momentum=bn_momentum))(img_3))
img_res = K.layers.add( [img_2, img_3] )

# Filter residual output
img_res = K.layers.Conv2D(128, **params)((K.layers.BatchNormalization(momentum=bn_momentum))(img_res))

# Tendancy to flatten
img_res = K.layers.GlobalMaxPooling2D(name='global_pooling') ( img_res )

dense1 = K.layers.Dropout(0.5)(K.layers.Dense(256, activation = "relu")(img_res)) 
dense2 = K.layers.Dropout(0.5)(K.layers.Dense(64, activation = "relu")(dense1)) 
prediction = K.layers.Dense(num_classes, activation = 'sigmoid')(dense2)

model = K.models.Model(inputs=[inputs], outputs=[prediction])

opt = K.optimizers.Adam(lr = 1e-3, beta_1 = .9, beta_2 = .999, decay = 1e-3)

model.compile(loss=loss.weighted_log_loss(),
                optimizer=opt,
                metrics = [loss.weighted_loss()])