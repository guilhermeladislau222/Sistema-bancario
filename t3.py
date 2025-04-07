import textwrap
from datetime import datetime
from abc import ABC, abstractmethod

class Transacao(ABC):
    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self.valor = valor
        self.data = datetime.now()

    def registrar(self, conta):
        if conta.sacar(self.valor):
            return True
        return False

class Deposito(Transacao):
    def __init__(self, valor):
        self.valor = valor
        self.data = datetime.now()

    def registrar(self, conta):
        if conta.depositar(self.valor):
            return True
        return False

class Historico:
    def __init__(self):
        self.transacoes = []
    
    def adicionar_transacao(self, transacao):
        self.transacoes.append(transacao)

class PessoaFisica:
    def __init__(self, cpf, nome, data_nascimento):
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Cliente:
    def __init__(self, endereco, pessoa_fisica):
        self.endereco = endereco
        self.contas = []
        self.pessoa_fisica = pessoa_fisica
    
    def realizar_transacao(self, conta, transacao):
        return transacao.registrar(conta)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class Conta:
    def __init__(self, numero, agencia, cliente):
        self.saldo = 0
        self.numero = numero
        self.agencia = agencia
        self.cliente = cliente
        self.historico = Historico()
    
    def saldo(self):
        return self.saldo
    
    @classmethod
    def nova_conta(cls, cliente, numero, agencia):
        return cls(numero, agencia, cliente)
    
    def sacar(self, valor):
        if valor > 0 and self.saldo >= valor:
            self.saldo -= valor
            self.historico.adicionar_transacao(Saque(valor))
            return True
        return False
    
    def depositar(self, valor):
        if valor > 0:
            self.saldo += valor
            self.historico.adicionar_transacao(Deposito(valor))
            return True
        return False

class ContaCorrente(Conta):
    def __init__(self, numero, agencia, cliente, limite=500, limite_saques=3):
        super().__init__(numero, agencia, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0
    
    def sacar(self, valor):
        if valor > self.limite:
            print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
            return False
            
        if self.saques_realizados >= self.limite_saques:
            print("\n@@@ Operação falhou! Número máximo de saques excedido. @@@")
            return False
            
        if self.saldo < valor:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False
            
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
            
        self.saldo -= valor
        self.saques_realizados += 1
        self.historico.adicionar_transacao(Saque(valor))
        print("\n=== Saque realizado com sucesso! ===")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
            return False
            
        self.saldo += valor
        self.historico.adicionar_transacao(Deposito(valor))
        print("\n=== Depósito realizado com sucesso! ===")
        return True


def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.pessoa_fisica.cpf == cpf:
            return cliente
    return None


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    
    if filtrar_cliente(cpf, clientes):
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return None
    
    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    
    pessoa_fisica = PessoaFisica(cpf, nome, data_nascimento)
    cliente = Cliente(endereco, pessoa_fisica)
    clientes.append(cliente)
    
    print("\n=== Cliente criado com sucesso! ===")
    return cliente


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return None
    
    conta = ContaCorrente.nova_conta(cliente, numero_conta, "0001")
    cliente.adicionar_conta(conta)
    contas.append(conta)
    
    print("\n=== Conta criada com sucesso! ===")
    return conta


def listar_contas(contas):
    if not contas:
        print("\n@@@ Não há contas cadastradas! @@@")
        return
    
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(f"""
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero}
            Titular:\t{conta.cliente.pessoa_fisica.nome}
        """))


def exibir_extrato(conta):
    if not conta:
        print("\n@@@ Conta não selecionada! @@@")
        return
        
    print("\n================ EXTRATO ================")
    if not conta.historico.transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in conta.historico.transacoes:
            if isinstance(transacao, Deposito):
                print(f"Depósito:\tR$ {transacao.valor:.2f}")
            elif isinstance(transacao, Saque):
                print(f"Saque:\t\tR$ {transacao.valor:.2f}")
    
    print(f"\nSaldo:\t\tR$ {conta.saldo:.2f}")
    print("==========================================")


def main():
    clientes = []
    contas = []
    conta_atual = None
    
    while True:
        opcao = menu()
        
        if opcao == "d":
            if not conta_atual:
                print("\n@@@ Selecione uma conta primeiro! @@@")
                continue
                
            valor = float(input("Informe o valor do depósito: "))
            transacao = Deposito(valor)
            conta_atual.cliente.realizar_transacao(conta_atual, transacao)
        
        elif opcao == "s":
            if not conta_atual:
                print("\n@@@ Selecione uma conta primeiro! @@@")
                continue
                
            valor = float(input("Informe o valor do saque: "))
            transacao = Saque(valor)
            conta_atual.cliente.realizar_transacao(conta_atual, transacao)
        
        elif opcao == "e":
            exibir_extrato(conta_atual)
        
        elif opcao == "nu":
            criar_cliente(clientes)
        
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            conta = criar_conta(numero_conta, clientes, contas)
            if conta:
                conta_atual = conta
        
        elif opcao == "lc":
            listar_contas(contas)
            if contas:
                try:
                    numero_conta = int(input("\nSelecione uma conta (número): "))
                    for conta in contas:
                        if conta.numero == numero_conta:
                            conta_atual = conta
                            print(f"\n=== Conta {numero_conta} selecionada! ===")
                            break
                    else:
                        print("\n@@@ Conta não encontrada! @@@")
                except ValueError:
                    print("\n@@@ Entrada inválida! @@@")
        
        elif opcao == "q":
            print("\n=== Saindo do sistema... ===")
            break
        
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


if __name__ == "__main__":
    main()
