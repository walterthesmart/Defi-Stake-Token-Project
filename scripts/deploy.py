from scripts.helpful_scripts import get_account
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3
import yaml
import json
import os
import shutil



KEPT_BALANCE = Web3.toWei(100, "ether")
def deploy_token_farm_and_dapp_token(front_end_update=False):
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account}, 
        # publish_source=config["networks"][network.show_active()]["verify"]
        )
    tx = dapp_token.transfer(token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account})
    tx.wait(1)
    # dapp_token, weth_token, kerry_token/dai
    weth_token = config["networks"][network.show_active()]["weth_token"]
    kerry_token = config["networks"][network.show_active()]["kerry_token"]
    dict_of_allowed_tokens = {
        dapp_token: config["networks"][network.show_active()]["dai_usd_price_feed"],
        kerry_token: config["networks"][network.show_active()]["dai_usd_price_feed"],
        weth_token: config["networks"][network.show_active()]["eth_usd_price_feed"],
    }
    add_allowed_tokens(token_farm,dict_of_allowed_tokens, account)
    if front_end_update:
        update_front_end()
    return token_farm, dapp_token

def update_front_end():
        # Send the build folder
    copy_folders_t_front_end("./build", "./front_end/src/chain-info")
    # Sending the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
        print("Front end updated!!!")

def copy_folders_t_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)
        return token_farm



def main():
    deploy_token_farm_and_dapp_token(front_end_update=True)