from brownie import (
    network, accounts, config, MockV3Aggregator, LinkToken, VRFCoordinatorMock, Contract)

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "local-ganache"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork"]

DECIMALS = 8
STARTING_PRICE = 200000000000


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    # The default account will be the network account.
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator" : VRFCoordinatorMock,
    "link_token" : LinkToken
}

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    # The contract mock will be deployed if none, if there is, it will be used
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        
        contract = contract_type[-1]

    # The contract will be deployed by the address from config based on the network we are using.
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        ) 
    
    return contract
    
DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from" : account})
    VRFCoordinatorMock.deploy(link_token.address, {"from" : account})
    print("Mocks deployed!")
    
def fund_with_link(contract_address, account = None, link_token = None, amount = 280000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from":account})
    tx.wait(1)
    print("Contract funded!")
    return tx