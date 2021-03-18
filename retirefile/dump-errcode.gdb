set height unlimited
set $i=0
while ($i<=GFARM_ERR_NUMBER)
p (enum gfarm_errcode)$i
p (int)$i
set $i=$i+1
end
