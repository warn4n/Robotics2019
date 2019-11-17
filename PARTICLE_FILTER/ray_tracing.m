% Copyright © 2019 Giovanni Miraglia
% 
% Permission is hereby granted, free of charge, to any person obtaining a 
% copy of this software and associated documentation files (the “Software”), 
% to deal in the Software without restriction, including without limitation 
% the rights to use, copy, modify, merge, publish, distribute, sublicense, 
% and/or sell copies of the Software, and to permit persons to whom the 
% Software is furnished to do so, subject to the following conditions: 
% The above copyright notice and this permission notice shall be included in 
% all copies or substantial portions of the Software. 
% THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS 
% OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
% THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
function [distance, end_point_x, end_point_y] = ray_tracing(x_pos,y_pos,direction,gridmap,cell_size)

    [max_row,max_col] = size(gridmap);
    
    start_row = floor(y_pos/cell_size)+1;
    start_col = floor(x_pos/cell_size)+1;
    % check for 90 270 180 0 360   
    direction = wrapTo360(direction);
    if direction == 90 || direction == 180 || direction == 0 ||...
            direction == 360 || direction == 270  
        direction = wrapTo360(direction+eps(1000));
    end
               
    % position out of map
    if start_row<1 || start_row>max_row || start_col<1 || start_col>max_col
        distance = NaN;
        end_point_x = NaN;
        end_point_y = NaN;
        return;
    end
        
    if gridmap(start_row,start_col)~=0 %inside obstacle
        distance = NaN;
        end_point_x = NaN;
        end_point_y = NaN;
        return;
    end
    
    inc_col = sign(cosd(direction));
    inc_row = sign(sind(direction));
    

    % horizontal scan
    
    if inc_row>0 %first delta y
        delta_y1 = cell_size*start_row - y_pos;
    else
        delta_y1 = cell_size*(start_row-1) - y_pos;
    end
    
    delta_x1 = delta_y1/tand(direction);  %first delta x  
    
    y_step = inc_row * cell_size; 
    x_step = y_step/tand(direction); %delta x for each horizontal line crossing
    
    current_x = x_pos + delta_x1;
    current_y = y_pos + delta_y1;
        
    current_row = start_row + inc_row;
    current_col = floor(current_x/cell_size)+1;
    
    while true
        if current_col<1 || current_col>max_col
            x_intersection_h = NaN;
            y_intersection_h = NaN;
            break;
        elseif current_row<1 || current_row>max_row
            x_intersection_h = current_x;
            y_intersection_h = current_y;
            break;
        elseif gridmap(current_row,current_col)~=0
            x_intersection_h = current_x;
            y_intersection_h = current_y;
            break;
        end

        current_x = current_x + x_step;
        current_y = current_y + y_step;
        current_col = floor(current_x/cell_size)+1;
        current_row = current_row + inc_row;        
    end

    % vertical scan
    
    if inc_col>0 %first delta x
        delta_x1 = cell_size*start_col - x_pos;
    else
        delta_x1 = cell_size*(start_col-1) - x_pos;
    end
    
    delta_y1 = delta_x1*tand(direction);  %first delta y  
    
    x_step = inc_col * cell_size; 
    y_step = x_step*tand(direction); %delta x for each horizontal line crossing
    
    current_x = x_pos + delta_x1;
    current_y = y_pos + delta_y1;
        
    current_col = start_col + inc_col;
    current_row = floor(current_y/cell_size)+1;
      
    while true
        if current_row<1 || current_row>max_row
            x_intersection_v = NaN;
            y_intersection_v = NaN;
            break;
        elseif current_col<1 || current_col>max_col
            x_intersection_v = current_x;
            y_intersection_v = current_y;
            break;
        elseif gridmap(current_row,current_col)~=0
            x_intersection_v = current_x;
            y_intersection_v = current_y;
            break;
        end

        current_x = current_x + x_step;
        current_y = current_y + y_step;
        current_row = floor(current_y/cell_size)+1;
        current_col = current_col + inc_col;        
    end
    
    %compute distances
    
    dist_h = norm([(x_pos-x_intersection_h) (y_pos-y_intersection_h)]); 
    dist_v = norm([(x_pos-x_intersection_v) (y_pos-y_intersection_v)]); 
    
    [~,index] = min([dist_h dist_v]);

    if index == 1
        distance = dist_h;
        end_point_x = x_intersection_h;
        end_point_y = y_intersection_h;
    else
        distance = dist_v;
        end_point_x = x_intersection_v;
        end_point_y = y_intersection_v;
    end
    