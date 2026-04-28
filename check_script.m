% Run this in MATLAB
conn_dir = 'C:\Users\Aditi\ds005613\derivatives\conn_restfc';
d = dir(fullfile(conn_dir, '**', '*.mat'));
disp(length(d))
d2 = dir(fullfile(conn_dir, 'preprocessing', '*'));
disp({d2.name})