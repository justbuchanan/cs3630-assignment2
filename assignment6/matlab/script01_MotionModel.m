% demo08_squareWorldMCL
% Demo generic Monte Carlo Localization

path(path,'threedee') 

%% Create a map
A = [
     12,0, 0.1,4
     ];
A = A./2;
map=SquareMap(A)

%% and a robot with noisy odometry
V=diag([0.01, 0.1*pi/180].^2)
startPos = [-20,-15,pi/2] / 10;
veh=Differential(V, 'x0', startPos);
veh.add_driver(DeterministicPath('log-1429239656.txt'));
veh.init(startPos);

%% and then a sensor with noisy readings
W=0.05^2;
sensor = RangeSensor(veh,map, W,'log-1429239656.txt')

%% define two covariances for random noise Q and L (hmmm!)
% For Q, use the uncertainly estimates from A2!
Q = diag([0.01,0.01,0.1*pi/180].^2);
L = diag(0.1); 

%% Finally, construct ParticleFilter
pf = GenericParticleFilter(veh, sensor, Q, L, 200);

%% and run for 1000 steps
pf.run(1000,'nouniform','nosense');

veh.plot_xy()
