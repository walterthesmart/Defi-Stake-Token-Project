from brownie import network, exceptions
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_contract, get_account, INITIAL_VALUE
import pytest
from scripts.deploy import deploy_token_farm_and_dapp_token, TokenFarm


def test_setPriceFeedContract():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for unit testing!!!!")
    account = get_account()
    non_Onwner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    price_feed_address = get_contract("eth_usd_price_feed")
    token_farm.setPriceFeedContract(dapp_token.address, price_feed_address, {"from": account})

    # Assert
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == price_feed_address
    with pytest.raises(exceptions.VirtualMachinesError):
       token_farm.setPriceFeedContract(
           dapp_token.address, price_feed_address, {"from": non_Onwner}
       )


def test_stake_tokens(amount_staked):
     # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for unit testing!!!!")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    # Act
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    # Assert
    assert(token_farm.stakingBalance(dapp_token.address, account.address) == amount_staked)
    assert token_farm.uniqueTokenStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token



def test_issue_tokens(amount_staked):
     # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for unit testing!!!!")
    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)
    # Act
    token_farm.issueTokens({"from": account})
    # Assert
    # we are staking 1 dapp token == in price of 1 ETH
    # 
    assert(
        dapp_token.balanceOf(account.address) ==starting_balance +  INITIAL_VALUE
    )
