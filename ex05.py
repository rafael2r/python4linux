# geração baseada mo ano de nascimento

ano = int(input('entre com o ano de nascimento '))
if (ano < 1965):
    print('você pertence a geração BBoomer')
elif (ano > 1964 and ano < 1982):
    print('você pertence a geração X')
elif (ano > 1981 and ano < 1997):
    print('você pertence a geração Y')
elif (ano > 1996):
    print('você pertence a geração Z')        
