function results = findWingCombosForTakeoff(SRange,ARRange,fileName,varargin)

%   For each wing area (as specified by input SRange), finds the lowest 
%   aspect ratio that allows the plane to take off. Calls findMinAreaAndAR.
%   Assumptions include flat runway and no wind.Parameters given must be 
%   within the bounds for which the estimate of mass given by m is accurate.
%      
%   Inputs:
%       SRange: a length-3 array of the form 
%           [min area,n, max area], where n is the number of sample points
%           desired. min area must be greater than 0. 
%      
%       ARange: a length-3 array of the form 
%           [min AR, n, max AR], where n is the number of sample points 
%           desired. min AR and max AR must both be nonnegative.n must be 
%           greater than 1. If n is a float, it will be rounded down to an
%           integer.
%      
%       fileName: Filepath for excel file that results will be saved to.
%           If fileName is the empty char ('') or 'search', then results 
%           will not be saved to a file and the percentage progress will 
%           not be  displayed. to the command window. Also, if the fileName
%           is 'search', then when the AR needed for takeoff is greater
%           than ARmax, the column 2 value for that row in results 
%           will be a number larger than the bounds.
%      
%       P (optional): Propulsive power of plane, in watts.
%      
%       col1 (optional): String to change what values will be in the first 
%           column in results.
%               'area' (default): wing area in m^2.
%           	'mass': mass of plane in kg.
%               'span': wingspan in meters, as measured in AR = b^2/s
%      
%       col2 (optional):
%               'AR' (default): aspect ratio.
%           	'mass': mass of plane in kg.
%               'span': wingspan in meters, as measured in AR = b^2/s
%      
%       silent (optional): Boolean. If true, will not diplay progress and
%           will not generate graph.
%      
%   Output:
%       results: A 2-column array with one row for each area. So, results
%       is an array of size SRRange(2) x 2. By default, results(i,1) is a
%       wing area value and results(i,2) is the corresponding smallest 
%       possible AR that allows for takeoff with that area.

p = inputParser;
p.addParameter('P',PTO_const);
p.addParameter('col1','area');
p.addParameter('col2','AR');
p.addParameter('silent',false);
p.parse(varargin{:});
P = p.Results.P;
col1 = p.Results.col1;
col2 = p.Results.col2;
silent = p.Results.silent;

SVals = linspace(SRange(1),SRange(3),SRange(2));
ARmin = ARRange(1);
ARmax = ARRange(3);
if ARmin ~= ARmax
    ARstep = (ARmax - ARmin)/(ARRange(2)-1);
else
    ARstep = 1; %arbritrary positive number
end

len = length(SVals);
results = zeros(len,2);
row = 1;

for s = SVals
    AR = ARmin - ARstep;
    takesOff = false;
    while (AR < ARmax && ~takesOff)
        AR = AR + ARstep;
        takesOff = doesTakeoff(s,AR,P);
    end
    
    switch col1
        case 'mass'
            val1 = m('P',P,'s',s);
        case 'span'
            val1 = AR*s^2;
        case 'area'
            val1 = s;
    end
    
    if (takesOff)
        if AR <= ARmin
        	val2 = 0;
        else
            switch col2
                case 'mass'
                    val2 = m('P',P,'s',s);
                case 'span'
                    val2 = AR*s^2;
                case 'AR'
                    val2 = AR;
            end
        end
    else
        if strcmpi(fileName, 'search')
            switch col2
                case 'mass'
                    val2 = m(SRange(3) + 1,P);
                case 'span'
                    val2 = (ARmax+1)* (SRange(3)+1)^2;
                case 'AR'
                    val2 = ARmax+1;
            end
        else
            val2 = 0;
        end
    end

    if ~(strcmp(fileName,'') || strcmpi(fileName,'search') || silent)
        fprintf('%.1f%% done\n', row/SRange(2) * 100);
    end
    
    results(row,1) = val1;
    results(row,2) = val2;
    row = row + 1;
end

if ~(strcmp(fileName,'') || strcmpi(fileName,'search'))
    xlswrite(fileName,results);
    if ~silent
        figure;
        x = results(:,1);
        y = results(:,2);
        plot(x,y,'oc');
        title(sprintf('%s vs. %s',col2,col1));
        xlabel(col1);
        ylabel(col2);
    end
end

end


function doesTakeoff = doesTakeoff(s,AR,P)
%   Returns true if a plane with input paramemeters can take off in the set
%   runway distance. s = wing area (m^2), AR = aspect ratio, P = propulsive
%   power (W). 
%   NOTE: Upper bound of tInterval must be changed if runway distance 
%   or plane specifications are drastically changed.
    tInterval = linspace(0,10,1000);
    x0 = 0;
    v0 = 0.00001;
    z0 = [x0;v0];
    
    K = 1/(pi*e_const*AR);
    CDG = CD0 + K * CLmax^2 - mu_const * CLmax;
    mass = m('P',P,'S',s);
    function dz = odefun(~,z)
        a = P/z(2);
        a = a - 0.5 * 1.18 * (z(2))^2 * s * CDG;
        a = a/mass;
        dz = [z(2); a];
    end
 
    [~,Z] = ode45(@odefun,tInterval,z0);
    
    i = 0;
    [lenZ,~] = size(Z);
    takenOff = false;
    vTakeoff = VTO(mass,s);
    
    while i < lenZ && ~takenOff
        i = i + 1;
        if Z(i,2) > vTakeoff
            takenOff = true;
        end
    end
    
    if takenOff && (Z(i,1) <= runwayDist_const)
        doesTakeoff = true;
    else
        doesTakeoff = false;
    end
    
end
