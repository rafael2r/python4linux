#habilitaçao

#1 - verifica a idade
#2 - possui habilitacao

idade = int(input('Digite a sua idade'))
hab = input('Possui habilitaçao: ')

# verifica se a idade é maior ou igual a 18 anos

#if (idade >= 18):
#    if(hab == 'sim'):
if (idade >= 18 and hab == 'sim'):
        print('Pode dirigir')
else: 
    print('não pode dirigir')
