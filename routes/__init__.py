from .auth_routes import register_auth_routes
from .wallet_routes import register_wallet_routes
from .token_routes import register_token_routes
from .transaction_routes import register_transaction_routes
from .swap_routes import register_swap_routes
from .pool_routes import register_pool_routes
from .liquidity_routes import register_liquidity_routes
from .staking_routes import register_staking_routes
from .vote_routes import register_vote_routes
from .multisig_routes import register_multisig_routes
from .loan_routes import register_loan_routes
from .flashloan_routes import register_flashloan_routes
from .reserve_routes import register_reserve_routes
from .admin_routes import register_admin_routes
from .backup_routes import register_backup_routes
from .balance_routes import register_balance_routes
from .price_routes import register_price_routes
from .network_routes import register_network_routes
from .connect_routes import register_connect_routes
from .dapp_routes import register_dapp_routes
from .address_book_routes import register_address_book_routes
from .approval_routes import register_approval_routes
from .broadcast_routes import register_broadcast_routes
from .chain_routes import register_chain_routes
from .export_routes import register_export_routes
from .notification_routes import register_notification_routes
from .portfolio_routes import register_portfolio_routes
from .proposal_routes import register_proposal_routes
from .resource_routes import register_resource_routes
from .security_routes import register_security_routes
from .execute_routes import register_execute_routes
from .multi_chain_ui_routes import register_multi_chain_ui_routes
from .gasless_routes import register_gasless_routes
from .deploy_routes import register_deploy_routes

__all__ = [
    'register_auth_routes',
    'register_wallet_routes',
    'register_token_routes',
    'register_transaction_routes',
    'register_swap_routes',
    'register_pool_routes',
    'register_liquidity_routes',
    'register_staking_routes',
    'register_vote_routes',
    'register_multisig_routes',
    'register_loan_routes',
    'register_flashloan_routes',
    'register_reserve_routes',
    'register_admin_routes',
    'register_backup_routes',
    'register_balance_routes',
    'register_price_routes',
    'register_network_routes',
    'register_connect_routes',
    'register_dapp_routes',
    'register_address_book_routes',
    'register_approval_routes',
    'register_broadcast_routes',
    'register_chain_routes',
    'register_export_routes',
    'register_notification_routes',
    'register_portfolio_routes',
    'register_proposal_routes',
    'register_resource_routes',
    'register_security_routes',
    'register_execute_routes',
    'register_multi_chain_ui_routes',
    'register_gasless_routes',
    'register_deploy_routes'
]