using Eirene
rv = [1, 2, 1, 3, 2, 4, 3, 4, 1, 4, 5, 7, 9, 5, 6, 7, 8]
cp = [1, 1, 1, 1, 1, 3, 5, 7, 9, 11, 14, 18]
dv = [0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2]
fv = [0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 1]
C = eirene(rv=rv,cp=cp,dv=dv,fv=fv,model="complex")
C_barcode = barcode(C, dim=1)
