# flowAroundTriangles
This is a small example project, that showcases the possibility of using a surrogate model to estimate the drag coefficient of arbitrary triangles.

The project is divided in four parts:
1. Mesh creation
2. CFD calculation
3. Neural network model training
4. Data exploration using Dash

The basic idea is to use OpenFOAM to calculate the flow around many differently shaped triangles at different Reynolds numbers and obtain the resulting drag coefficient. These results are then used to train a neural network. Finally the neural network can be used to estimate the drag coefficient for arbitrary triangles.

## Prerequisites
Tested with the following set-up:
* OpenFOAM-6
* Python 3.8
  * Tensorflow 2.5.0
  * Scikit-learn 0.23.1
  * Pandas 1.0.5
  * Numpy 1.19.5
  * Matplotlib 3.2.2
  * Plotly 4.14.1
  * Dash 1.18.1

## Quick start
To start the simulations simply navigate to the main folder, type
```
./runCases.sh
```
in a console that has access to OpenFOAM and hit enter.
## Mesh creation
The bash script `runCases.sh` first creates the required mesh for each case using the set-up in the `mesh` folder. By changing the `blockMeshDict` in the `mesh/system` folder meshes for a large number of triangles are craeted. `blockMesh` creates a structured mesh of hexahedral blocks. One resulting mesh is shown in the image below.

<img src="https://github.com/axelfiedler/flowAroundTriangles/blob/main/assets/mesh_example.PNG" alt="Example of an automatically generated hex mesh around a triangle" width="300"/>

## CFD calculation ##
After a mesh for one triangle is created, it will be copied from the `mesh` folder to the `simple_laminar` folder. There the inlet velocity in `0/U` as well as the velocity at infinity in `system/controlDict` will be updated according to the current Reynolds number. After that the case will be decomposed for parallel computing. The default number of processors in `runCases.sh` is 4, this can be changed in `line 101` and `line 104` if a system with more processors is used. The mesh is renumbered after decomposition for speed-up and a `simpleFoam` calculation is started. After the simulation is finished the resulting `forceCoeffs.dat` file, that contains the drag coefficient is copied to the results folder `C_D` and the next calculation is started by generating the next mesh. E.g. for the mesh that was shown above the resulting velocity field is shown below.

<img src="https://github.com/axelfiedler/flowAroundTriangles/blob/main/assets/flow_example.PNG" alt="Example of calculated velocity field" width="300"/>

## Neural network model training ##
First run `read_files.py` to store the simulation data in a Pandas DataFrame, that can easily be used in the further steps. The DataFrame will be saved in `tmp` folder. After that you can run `parameter_study.py` to perform a small parameter study, that will try to train neural networks with different width and depth (i.e. number of nodes per layer and number of layers). Some of the results of that parameter study are shown in the table below.

| No of layers  | No of nodes   | Loss  |
| ------------- |:-------------:| -----:|
1|1|6.184e-05|
1|2|0.00021|
1|4|1.064e-05|
...|...|...|
15|64|4.459e-08|
15|128|1.123e-06|
15|256|1.369e-07|

The parameter study is helpful and shows that a good set-up can be found using 8 layers and 32 nodes per layer. Therefore these parameters are used in `train_model.py` to train the model.

The mean squared error is used as loss function for the training. A plot of the loss on the training dataset and the validation dataset is shown below. It can be observed that additional training epochs would not lead to a better model fit.

<img src="https://github.com/axelfiedler/flowAroundTriangles/blob/main/assets/model_loss_32_nodes_8_layer.png" alt="Loss for model with 32 nodes per layer and 8 layer" width="500"/>

Finally the trained model can be used to predict values using the following structure
```
model.predict(x=[[x1,y1,x2,y2,x3,y3]])
```
and will return the drag coefficient for `Re=200`, `Re=400` and `Re=600`. The model is saved 

## Data exploration using Dash

To examine the simulation results and the `results_dash.py` Dash app can be used. This app allows the user to choose combinations of x and y coordinates for the triangle and observe the resulting drag coefficient as shown in the animation below. It can be observed that the neural network model is able to reflect some features very well, but fails to incorporate the influence of other paramaters correctly. Thus additional tweaking of the set-up might be necessary.

<img src="https://github.com/axelfiedler/flowAroundTriangles/blob/main/assets/Dash_Animation.gif" alt="Animation of Dash app" width="500"/>
