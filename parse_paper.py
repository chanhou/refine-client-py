

with open('/tmp2/MicrosoftAcademicGraph/Papers.txt', 'r') as f, open('/tmp2/MicrosoftAcademicGraph_refine/papers_1_column.txt','w') as b:
    for line in f:
        a = line.split('\t')
        #a = a[1].split('\r')
        #b.write(a[0]+a[1])
        b.write(a[2]+'\n')
        #break

