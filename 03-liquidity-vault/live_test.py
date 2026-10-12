import sys, json, hashlib, struct
from pathlib import Path
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta as M
from solders.transaction import Transaction
from solders.message import Message

sys.path.insert(0, '/home/hermes/projects/almau-solana-rk1')
from devnet_work import rpc, key
from deploy_devnet import send

ROOT = Path('/home/hermes/projects/almau-liquidity-vault')
evidence = ROOT / 'evidence'
evidence.mkdir(exist_ok=True)

payer = key('student')
program_id = Pubkey.from_string('Xu7JJXtKWyA1LfNpc1tcCNfEiZJQQYWn5Ymo96j9vHa')

# We can use our created SPL mint as underlying_mint
underlying_mint = Pubkey.from_string('HzQULeq72G2RQp1wFBk9T3TNvCZ6wBBP3KrqQZVYxgfe')
token_program = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
system_program = Pubkey.from_string('11111111111111111111111111111111')
rent = Pubkey.from_string('SysvarRent111111111111111111111111111111111')

config_pda, _ = Pubkey.find_program_address([b"config", bytes(payer.pubkey())], program_id)
vault_auth_pda, _ = Pubkey.find_program_address([b"vault-authority", bytes(config_pda)], program_id)
share_mint_pda, _ = Pubkey.find_program_address([b"share", bytes(config_pda)], program_id)
token_vault_pda, _ = Pubkey.find_program_address([b"token-vault", bytes(config_pda)], program_id)

disc_create = hashlib.sha256(b"global:create_vault").digest()[:8]

accounts_create = [
    M(config_pda, False, True),
    M(vault_auth_pda, False, False),
    M(underlying_mint, False, False),
    M(share_mint_pda, False, True),
    M(token_vault_pda, False, True),
    M(payer.pubkey(), True, True),
    M(token_program, False, False),
    M(system_program, False, False),
    M(rent, False, False),
]

ix_create = Instruction(program_id, disc_create, accounts_create)

# Check if config already initialized
info = rpc('getAccountInfo', [str(config_pda), {'encoding': 'base64'}])['value']
if not info:
    print('Sending create_vault...')
    sig1 = send([ix_create], [payer])
    print('create_vault tx:', sig1)
    (evidence / 'create_vault.json').write_text(json.dumps({'signature': sig1, 'config': str(config_pda)}, indent=2))
else:
    print('Vault config already created at', config_pda)

# Now test open_position
pos_pda, _ = Pubkey.find_program_address([b"position", bytes(config_pda), bytes(payer.pubkey())], program_id)
disc_open = hashlib.sha256(b"global:open_position").digest()[:8]

accounts_open = [
    M(config_pda, False, False),
    M(pos_pda, False, True),
    M(payer.pubkey(), True, True),
    M(system_program, False, False),
]

ix_open = Instruction(program_id, disc_open, accounts_open)

pos_info = rpc('getAccountInfo', [str(pos_pda), {'encoding': 'base64'}])['value']
if not pos_info:
    print('Sending open_position...')
    sig2 = send([ix_open], [payer])
    print('open_position tx:', sig2)
    (evidence / 'open_position.json').write_text(json.dumps({'signature': sig2, 'position': str(pos_pda)}, indent=2))
else:
    print('User position already created at', pos_pda)

print('SUCCESS: Chapter 8 live tests complete in Devnet')
