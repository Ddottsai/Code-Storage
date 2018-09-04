function results = findAllWingCombosForTakeoff(minSstep,ARinterval,fileName,varargin)
%   Finds all combinations of wing area and aspect ratio that allow the 
%   plane to take off, given constraining inputs. Calls findWingCombosForTakeoff.
%   Assumptions include flat runway and no wind. findWingCombosForTakeoff
%   depends on function m, so parameters given must be within the bounds 
%   for which the estimate of mass given by m is accurate. Also, the
%   aspect ratio must have a strictly nonpositive relationship with the
%   wing area at all points in the range specified by ARinterval and 
%   between minS and maxS.
%      
%   Inputs:
%       minSstep: the desired area step (i.e., a smaller minSstep will
%           yield data points that are closer together)
%      
%       ARinterval: 
%           range of AR vals that you want to allow, written in the form
%           [minimum AR, AR step, maximum AR]
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
%       minS (optional): The minimum wing area allowed, in m^2. Defaults to 
%           0.
%      
%       maxS (optional): The maximum wing area allowed, in m^2. Defaults to 
%           one-tenth of the power.
%      
%       P (optional): Propulsive power of the plane, in watts.
%      
%       col1 (optional): String to change what values will be in the first 
%           column in output.
%               'area' (default): wing area in m^2.
%           	'mass': mass of plane in kg.
%               'span': wingspan in meters, as measured in AR = b^2/s
%      
%       col2 (optional):
%               'AR' (default): aspect ratio.
%           	'mass': mass of plane in kg.
%               'span': wingspan in meters, as measured in AR = b^2/s
%      
%       silent (optional): Boolean. If true, will not print progress and
%           will not generate graph.
%      
%   Output:
%       results: A 2-column array with each row corresponding to a wing 
%           area that allows the plane to take off with an AR in the 
%           range specified by ARinterval. See documentation of 
%           findWingCombosForTakeoff for more specifications.

p = inputParser;

p.addParameter('minS',0);
p.addParameter('maxS',-1); % default is set later in code
p.addParameter('P', PTO_const);
p.addParameter('col1','area');
p.addParameter('col2','AR');
p.addParameter('silent',false);
p.parse(varargin{:});

minS = p.Results.minS;
maxS = p.Results.maxS;
P = p.Results.P;
col1 = p.Results.col1;
col2 = p.Results.col2;
silent = p.Results.silent;
if maxS == -1
    maxS = P/10; % uses P as estimate of aircraft size
end

buffer = realmin('double');
ARsurvey = [ARinterval(1),2,ARinterval(3) + buffer];

% binary search for a point with AR in ARinterval, using the fact that 
% findWingCombosForTakeoff returns a list with AR in strictly descending order
left = minS+buffer;
right = maxS;
mid = (left + right) / 2;
arr = findWingCombosForTakeoff([mid, 1, mid], ARsurvey,'','P',P);
if arr(1,2) == 0
    found = false;
    while ~found
        if right - left < minSstep
            if mid < maxS/2
                disp(['Maximum wing area for this system approaches 0.'...
                    ' Output will be meaningless.']);
            else
                disp(['Minimum wing area for this system approaches'...
                    ' the set max area. Output will be meaningless.']);
             end
            disp('findAllWingCombosForTakeoff will now terminate.');
            return;
        end
        arr = findWingCombosForTakeoff([mid, 1, mid], ARsurvey,'search','P',P);
        if  arr(1,2) < ARinterval(1) 
            right = mid;
        elseif arr(1,2) > ARinterval(3)
            left = mid;
        else
            found = true;
        end
        mid = (left + right) / 2;
    end
end


%determine bounds

tempArr = findWingCombosForTakeoff([left, 10, right], ARsurvey,'','P',P);

step = maxS/10;
upperMindex = find(tempArr(:,2),1);
upperMin = tempArr(upperMindex, 1); %upper bound of min area
lowerMin = max(upperMin - step,0);
lowerMax = tempArr(find(tempArr(:,2),1,'last') , 1); %lower bound of max area
upperMax = min(lowerMax + step,maxS);

if upperMin == lowerMax
    if tempArr(upperMindex + 1,2) == 0 
    % then there's an upper bound, but no lower bound
        minS = findTightMinBound(0,step,minSstep,ARsurvey,P);
        maxS = findTightMaxBound(lowerMax,upperMax,minSstep,ARsurvey,P);
    else
    % then there's a lower bound, but no upper bound
        minS = findTightMinBound(lowerMin,upperMin,minSstep,ARsurvey,P);
        maxS = findTightMaxBound(maxS - step,maxS,minSstep,ARsurvey,P);
    end
else
    if isscalar(upperMin)
        minS = findTightMinBound(lowerMin,upperMin,minSstep,ARsurvey,P);
    else
        minS = findTightMinBound(minSstep,step,minSstep,ARsurvey,P);
    end

    if isscalar(lowerMax)
        maxS = findTightMaxBound(lowerMax,upperMax,minSstep,ARsurvey,P);
    else
        maxS = findTightMaxBound(maxS - step,maxS,minSstep,ARsurvey,P);
    end
end

if ~silent
    fprintf('Min Area: %d\n',minS)
    fprintf('Max Area: %d\n',maxS)
    disp('-----------------------------');
    disp('finding minimum AR for each wings area...');
end

% determine output

results = findWingCombosForTakeoff([minS,floor((maxS-minS)/minSstep),maxS], ...
        ARinterval,fileName,'P',P,'col1',col1,'col2',col2,'silent',silent);

end



function tightestMin = findTightMinBound(min0, max0, absMinStep, ARvals, P)
%   Returns a span that is close to the smallest possible span for which
%   the AR needed is within the range given by ARvals. Closeness to actual
%   minimum possible span is limited by absMinStep.
%   Inputs:
%       min0: Lower bound of wing areas to search in. 
%
%       max0: Upper bound of wing areas to search in. max0 holds the value
%             returned by this function.
%
%       absMinStep: Smallest step for wing area desired.
%
%       ARvals: Array representing AR limits, in the format
%               [minimum AR, points, maximum AR], where (points >= 2).
%               For maximum efficiency, have points = 2.
%       P: Propulsive power of plane.
    step = (max0-min0)/10;
    if step*10 <= absMinStep
        tightestMin = max0;
    else
        tempArr = findWingCombosForTakeoff([min0, 10, max0],ARvals,'','P',P);
        upperMin = tempArr(find(tempArr(:,2),1) , 1);
        if ~isscalar(upperMin)
            upperMin = step;
        end
        lowerMin = upperMin - step;
        tightestMin = findTightMinBound(lowerMin, upperMin, absMinStep, ARvals,P);
    end
end



function tightestMax = findTightMaxBound(min0, max0, absMinStep, ARvals, P)
%   Returns a span that is close to the largest possible span for which the
%   AR needed is within the range given by ARvals. Closeness to actual
%   maximum possible span is limited by absMinStep.
%   Inputs:
%       min0: Lower bound of wing areas to search in. min0 holds the value
%             returned by this function.
%
%       max0: Upper bound of wing areas to search in.
%
%       absMinStep: Smallest step in wing area wanted.
%
%       ARvals: Array representing AR limits, in the format
%               [minimum AR, points, maximum AR], where (points >= 2).
%               For maximum efficiency, have points = 2.
%
%       P: Propulsive power of plane.
    step = (max0-min0)/10;
    if step*10 <= absMinStep
        tightestMax = min0;
    else
        tempArr = findWingCombosForTakeoff([min0, 10, max0],ARvals,'','P',P);
        lowerMax = tempArr(find(tempArr(:,2),1,'last') , 1);
        if ~isscalar(lowerMax)
            lowerMax = max0-step;
        end
        upperMax = lowerMax + step;
        tightestMax = findTightMaxBound(lowerMax, upperMax, absMinStep, ARvals,P);
    end
    
end