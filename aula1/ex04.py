#calculadora

n1 = int(input('entre com o primeiro numero: '))
n2 = int(input('entre com o segundo numero: '))
op = int(input('escola a operação desejada, 1 - soma, 2 - subtração, 3 - divisão, 4 - multiplicação'))
if (op == 1):
    print('o resultado é: {}'.format(n1+n2))
if (op == 2):
    print('o resultado é: {}'.format(n1-n2))
if (op == 3):
    print('o resultado é: {}'.format(n1/n2))
if (op == 4):
    print('o resultado é: {}'.format(n1*n2))
