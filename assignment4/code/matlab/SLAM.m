% Simultaneous Localization and Mapping

path(path, 'aprilTag');

% Specify the locations of the April tags in the Map

dummy = [1, 1];

% tag coords in inches
% A[tagID] = loc
A = [58,122; % 1
    40,98;  % 2
    70,98;  % 3
    dummy;  % 4
    dummy;  % 5
    dummy;  % 6
    dummy;  % 7
    dummy;  % 8
    dummy;  % 9
    dummy;  % 10
    36,0;  % 11
    84,0;  % 12
    0,32;  % 13
    0,84;  % 14
    120,18;  % 15
    40,88;    % 16
    100,102;  % 17
    120,78;  % 18
    dummy]; % 19
    
% convert inches to meters
A = A * 0.0254;


%% and a robot with noisy odometry
initPos = [36 * 0.0254, 60 * 0.0254, -pi/4];
V=diag([0.1, 1.1*pi/180].^2);
veh=GenericVehicle(V,'dt',0.3, 'x0', initPos);
veh.add_driver(DeterministicPath('data/log-1424819946-open.txt'));

% Creating the map. It places landmarks according to 'A' matrix.
map = LandmarkMap(19, A, 5);

% Creating the sensor.  We firstly define the covariance of the sensor measurements
% which report distance and bearing angle
W = diag([0.1, 1*pi/180].^2);

% and then use this to create an instance of the Sensor class.
sensor = GenericRangeBearingSensor(veh, map, W, 'animate');
% Note that the sensor is mounted on the moving robot and observes the features
% in the world so it is connected to the already created Vehicle and Map objects.

% Create the filter.  First we need to determine the initial covariance of the
% vehicle, this is our uncertainty about its pose (x, y, theta)
P0 = diag([0.005, 0.005, 0.001].^2);

% Now we create an instance of the EKF filter class
ekf = GenericEKF(veh, V, P0, sensor, W, []);
% and connect it to the vehicle and the sensor and give estimates of the vehicle
% and sensor covariance (we never know this is practice).

% Now we will run the filter for 1000 time steps.  At each step the vehicle
% moves, reports its odometry and the sensor measurements and the filter updates
% its estimate of the vehicle's pose
ekf.run(1000);
% all the results of the simulation are stored within the EKF object

% First let's plot the map
clf; map.plot()
% and then overlay the path actually taken by the vehicle
veh.plot_xy('b');
% and then overlay the path estimated by the filter
ekf.plot_xy('r');
% which we see are pretty close

% Now let's plot the error in estimating the pose
ekf.plot_error()
% and this is overlaid with the estimated covariance of the error.

% Remember that the SLAM filter has not only estimated the robot's pose, it has
% simultaneously estimated the positions of the landmarks as well.  How well did it
% do at that task?  We will show the landmarks in the map again
map.plot();
% and this time overlay the estimated landmark (with a +) and the 3sigma 
% uncertainty bounds as green ellipses
ekf.plot_map(3,'g');
