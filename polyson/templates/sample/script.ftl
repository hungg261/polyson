<#assign SMALL = 100>
<#assign BIG = 1000000000>

<#list 1..5 as i>
gen ${i} --min_val=-${SMALL} --max_val=${SMALL} > $
</#list>

<#list 6..10 as i>
gen ${i} --min_val=-${BIG} --max_val=${BIG} > $
</#list>
