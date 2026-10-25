#!/usr/bin/env python3
"""
Full autonomous Devnet pipeline for Week 9 Simple Vault:
1. Setup keypairs in ~/.hermes/secrets/almau-solana-week9/
2. Update declare_id! in lib.rs
3. Build SBF via api.solpg.io
4. Deploy SBF to Devnet using BPFLoaderUpgradeable with fast parallel chunk writing
5. Setup Mint, ATAs, Initialize Vault, Create User Card, Execute Deposit
6. Verify and output Explorer links
"""
import os, sys, json, time, struct, base64, re, hashlib, requests, concurrent.futures
from pathlib import Path
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta as M
from solders.system_program import create_account, CreateAccountParams, transfer, TransferParams
from solders.transaction import Transaction
from solders.hash import Hash

ROOT = Path(__file__).resolve().parent
RPC = 'https://api.devnet.solana.com'
PAYER_FILE = Path('/home/hermes/.hermes/secrets/almau-solana-devnet.json')
SECRETS_DIR = Path('/home/hermes/.hermes/secrets/almau-solana-week9')
SECRETS_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
os.chmod(SECRETS_DIR, 0o700)

LOADER = Pubkey.from_string('BPFLoaderUpgradeab1e11111111111111111111111')
TOKEN = Pubkey.from_string('TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA')
ASSOCIATED = Pubkey.from_string('ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL')
SYSTEM = Pubkey.default()
RENT = Pubkey.from_string('SysvarRent111111111111111111111111111111111')
CLOCK = Pubkey.from_string('SysvarC1ock11111111111111111111111111111111')

def get_key(name):
    p = SECRETS_DIR / f'{name}.json'
    if p.exists():
        return Keypair.from_bytes(bytes(json.loads(p.read_text())))
    kp = Keypair()
    fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(list(bytes(kp)), f)
    return kp

payer = Keypair.from_bytes(bytes(json.load(open(PAYER_FILE))))
program_kp = get_key('program')
buffer_kp = get_key('buffer')
user_kp = get_key('user')
mint_kp = get_key('mint')

print(f"Payer: {payer.pubkey()}")
print(f"Program ID: {program_kp.pubkey()}")
print(f"Buffer: {buffer_kp.pubkey()}")
print(f"User: {user_kp.pubkey()}")
print(f"Mint: {mint_kp.pubkey()}")

def rpc(method, params):
    for attempt in range(6):
        r = requests.post(RPC, json={'jsonrpc':'2.0','id':1,'method':method,'params':params}, timeout=35)
        if r.status_code == 429:
            time.sleep(2 * (attempt + 1))
            continue
        r.raise_for_status()
        d = r.json()
        if 'error' in d:
            raise RuntimeError(f"RPC {method} error: {d['error']}")
        return d['result']
    raise RuntimeError(f"RPC rate limited on {method}")

def get_bh():
    return rpc('getLatestBlockhash', [{'commitment':'confirmed'}])['value']['blockhash']

def send_tx(ixs, signers, payer_kp=payer):
    bh = get_bh()
    tx = Transaction.new_signed_with_payer(ixs, payer_kp.pubkey(), signers, Hash.from_string(bh))
    raw = base64.b64encode(bytes(tx)).decode()
    sig = rpc('sendTransaction', [raw, {'encoding':'base64', 'preflightCommitment':'confirmed'}])
    for _ in range(45):
        st = rpc('getSignatureStatuses', [[sig]])['value'][0]
        if st and st.get('confirmationStatus') in ('confirmed', 'finalized'):
            if st.get('err'):
                raise RuntimeError(f"Tx {sig} failed: {st['err']}")
            return sig
        time.sleep(0.5)
    raise TimeoutError(f"Confirmation timeout for {sig}")

# -------------------------------------------------------------
# STEP 1: Build program with program_kp.pubkey()
# -------------------------------------------------------------
lib_path = ROOT / 'programs/simple_vault/src/lib.rs'
content = lib_path.read_text()
updated = re.sub(r'declare_id!\("[^"]+"\);', f'declare_id!("{program_kp.pubkey()}");', content)
lib_path.write_text(updated)

evidence_dir = ROOT / 'evidence'
evidence_dir.mkdir(exist_ok=True)
so_path = evidence_dir / 'vault.so'

# Check if binary already built for this program ID
manifest_path = evidence_dir / 'manifest.json'
rebuild_needed = True
if manifest_path.exists() and so_path.exists():
    try:
        m = json.loads(manifest_path.read_text())
        if m.get('program_id') == str(program_kp.pubkey()):
            rebuild_needed = False
            print("Binary already built for current program ID.")
    except Exception:
        pass

if rebuild_needed:
    print("Building SBF via api.solpg.io...")
    source_to_build = updated.split('#[cfg(test)]')[0]
    res = requests.post('https://api.solpg.io/build', json={'files':[['/src/lib.rs', source_to_build]], 'flags':{'seedsFeature':True, 'safetyChecks':True}}, timeout=240)
    res.raise_for_status()
    d = res.json()
    if 'error: could not compile' in d.get('stderr', ''):
        raise RuntimeError(f"Solpg compile error: {d.get('stderr')}")
    uuid = d['uuid']
    b = requests.get(f'https://api.solpg.io/deploy/{uuid}', timeout=80)
    b.raise_for_status()
    assert b.content[:4] == b'\x7fELF', "Downloaded file is not ELF"
    so_path.write_bytes(b.content)
    manifest = {
        'program_id': str(program_kp.pubkey()),
        'bytes': len(b.content),
        'sha256': hashlib.sha256(b.content).hexdigest(),
        'uuid': uuid
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"Build verified! Size: {len(b.content)} bytes, sha256: {manifest['sha256']}")

binary = so_path.read_bytes()

# -------------------------------------------------------------
# STEP 2: Deploy to Devnet
# -------------------------------------------------------------
prog_info = rpc('getAccountInfo', [str(program_kp.pubkey()), {'encoding':'base64'}])['value']
if prog_info and prog_info.get('executable'):
    print(f"Program {program_kp.pubkey()} is already deployed and executable!")
else:
    print(f"Deploying program {program_kp.pubkey()} ({len(binary)} bytes)...")
    rent_buffer = rpc('getMinimumBalanceForRentExemption', [37 + len(binary)])
    buf_info = rpc('getAccountInfo', [str(buffer_kp.pubkey()), {'encoding':'base64'}])['value']

    if not buf_info:
        print("Creating buffer account...")
        ix_create_buf = create_account(CreateAccountParams(from_pubkey=payer.pubkey(), to_pubkey=buffer_kp.pubkey(), lamports=rent_buffer, space=37 + len(binary), owner=LOADER))
        ix_init_buf = Instruction(LOADER, struct.pack('<I', 0), [M(buffer_kp.pubkey(), False, True), M(payer.pubkey(), False, False)])
        sig_b = send_tx([ix_create_buf, ix_init_buf], [payer, buffer_kp])
        print(f"Buffer created: {sig_b}")
    else:
        print("Buffer account exists, checking uploaded chunks...")

    # Upload chunks in parallel batches
    chunk_size = 900
    offsets = list(range(0, len(binary), chunk_size))

    def check_missing():
        cur = rpc('getAccountInfo', [str(buffer_kp.pubkey()), {'encoding':'base64'}])['value']
        data = base64.b64decode(cur['data'][0])[37:]
        missing = [off for off in offsets if data[off:off+len(binary[off:off+chunk_size])] != binary[off:off+chunk_size]]
        return missing

    missing = check_missing()
    print(f"Total chunks: {len(offsets)}, missing: {len(missing)}", flush=True)

    batch_size = 20
    round_num = 0
    while missing:
        round_num += 1
        print(f"--- Round {round_num}: {len(missing)} chunks remaining ---", flush=True)
        # Send in parallel batches of 20
        for i in range(0, len(missing), batch_size):
            batch = missing[i:i+batch_size]
            bh = get_bh()
            raw_txs = []
            for off in batch:
                chunk = binary[off:off+chunk_size]
                ix_w = Instruction(LOADER, struct.pack('<IIQ', 1, off, len(chunk)) + chunk, [M(buffer_kp.pubkey(), False, True), M(payer.pubkey(), True, False)])
                tx = Transaction.new_signed_with_payer([ix_w], payer.pubkey(), [payer], Hash.from_string(bh))
                raw_txs.append(base64.b64encode(bytes(tx)).decode())

            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as ex:
                futs = [ex.submit(rpc, 'sendTransaction', [t, {'encoding':'base64', 'preflightCommitment':'confirmed'}]) for t in raw_txs]
                for f in futs:
                    try: f.result()
                    except Exception: pass
            print(f"Sent batch {i//batch_size + 1}/{(len(missing)+batch_size-1)//batch_size}", flush=True)
            time.sleep(1.0)

        print("Batch sweep finished. Waiting 4s for confirmations...", flush=True)
        time.sleep(4.0)
        missing = check_missing()

    print("All chunks confirmed in buffer! Finalizing deploy...", flush=True)
    program_data_pda, _ = Pubkey.find_program_address([bytes(program_kp.pubkey())], LOADER)
    prent = rpc('getMinimumBalanceForRentExemption', [36])

    ix_create_prog = create_account(CreateAccountParams(from_pubkey=payer.pubkey(), to_pubkey=program_kp.pubkey(), lamports=prent, space=36, owner=LOADER))
    ix_deploy = Instruction(LOADER, struct.pack('<IQ', 2, len(binary)), [
        M(payer.pubkey(), True, True),
        M(program_data_pda, False, True),
        M(program_kp.pubkey(), False, True),
        M(buffer_kp.pubkey(), False, True),
        M(RENT, False, False),
        M(CLOCK, False, False),
        M(SYSTEM, False, False),
        M(payer.pubkey(), True, False)
    ])
    sig_deploy = send_tx([ix_create_prog, ix_deploy], [payer, program_kp])
    print(f"PROGRAM DEPLOYED! Tx: {sig_deploy}")

    prog_info = rpc('getAccountInfo', [str(program_kp.pubkey()), {'encoding':'base64'}])['value']
    assert prog_info and prog_info['executable'], "Program is not executable!"

print(f"\nProgram verified on Devnet: https://explorer.solana.com/address/{program_kp.pubkey()}?cluster=devnet\n")

# -------------------------------------------------------------
# STEP 3: Setup Tokens, Vault, Card, and Execute Deposit
# -------------------------------------------------------------
P_ID = program_kp.pubkey()
MINT = mint_kp.pubkey()

# PDAs
vault_state, _ = Pubkey.find_program_address([b'vault', bytes(MINT)], P_ID)
vault_token_acc, _ = Pubkey.find_program_address([b'vault_tokens', bytes(MINT)], P_ID)
share_mint, _ = Pubkey.find_program_address([b'share_mint', bytes(MINT)], P_ID)
user_card, _ = Pubkey.find_program_address([b'user_card', bytes(vault_state), bytes(user_kp.pubkey())], P_ID)

# ATAs
fee_wallet_ata, _ = Pubkey.find_program_address([bytes(payer.pubkey()), bytes(TOKEN), bytes(MINT)], ASSOCIATED)
user_token_ata, _ = Pubkey.find_program_address([bytes(user_kp.pubkey()), bytes(TOKEN), bytes(MINT)], ASSOCIATED)
user_share_ata, _ = Pubkey.find_program_address([bytes(user_kp.pubkey()), bytes(TOKEN), bytes(share_mint)], ASSOCIATED)

print(f"VaultState PDA: {vault_state}")
print(f"VaultToken PDA: {vault_token_acc}")
print(f"ShareMint PDA: {share_mint}")
print(f"UserCard PDA: {user_card}")

# 1. Fund user for rent/fees
u_bal = rpc('getBalance', [str(user_kp.pubkey()), {'commitment':'confirmed'}])['value']
if u_bal < 30_000_000:
    print("Funding user keypair with 0.1 SOL...")
    send_tx([transfer(TransferParams(from_pubkey=payer.pubkey(), to_pubkey=user_kp.pubkey(), lamports=100_000_000))], [payer])

# 2. Create Token Mint
mint_info = rpc('getAccountInfo', [str(MINT), {'encoding':'base64'}])['value']
if not mint_info:
    print("Creating SPL Token Mint...")
    m_rent = rpc('getMinimumBalanceForRentExemption', [82])
    # create_account + InitializeMint2 (tag 20, decimals=6, mint_auth=payer, freeze_auth=None)
    ix_c_mint = create_account(CreateAccountParams(from_pubkey=payer.pubkey(), to_pubkey=MINT, lamports=m_rent, space=82, owner=TOKEN))
    init_mint_data = bytes([20, 6]) + bytes(payer.pubkey()) + bytes([0]) + bytes(32)
    ix_init_m = Instruction(TOKEN, init_mint_data, [M(MINT, False, True)])
    send_tx([ix_c_mint, ix_init_m], [payer, mint_kp])
    print(f"Token Mint created: {MINT}")

# 3. Create fee_wallet ATA and user_token_ata
def ensure_ata(owner, ata_addr, mint_addr, funder_kp=payer):
    info = rpc('getAccountInfo', [str(ata_addr), {'encoding':'base64'}])['value']
    if not info:
        # Create ATA: AssociatedTokenProgram instruction tag 0 or empty bytes
        ix_ata = Instruction(ASSOCIATED, bytes([1]), [
            M(funder_kp.pubkey(), True, True),
            M(ata_addr, False, True),
            M(owner, False, False),
            M(mint_addr, False, False),
            M(SYSTEM, False, False),
            M(TOKEN, False, False)
        ])
        send_tx([ix_ata], [funder_kp], funder_kp)
        print(f"ATA created: {ata_addr} (owner: {owner})")

ensure_ata(payer.pubkey(), fee_wallet_ata, MINT)
ensure_ata(user_kp.pubkey(), user_token_ata, MINT, user_kp)

# Mint 1000 tokens (1000 * 10^6) to user
u_tok_info = rpc('getAccountInfo', [str(user_token_ata), {'encoding':'base64'}])['value']
current_u_tok = 0
if u_tok_info:
    tok_data = base64.b64decode(u_tok_info['data'][0])
    current_u_tok = struct.unpack_from('<Q', tok_data, 64)[0]

if current_u_tok < 100 * 10**6:
    print("Minting 1,000 tokens to user ATA...", flush=True)
    # MintTo: tag 7, amount u64
    amt = 1000 * 10**6
    ix_mint_to = Instruction(TOKEN, bytes([7]) + amt.to_bytes(8, 'little'), [
        M(MINT, False, True),
        M(user_token_ata, False, True),
        M(payer.pubkey(), True, False)
    ])
    send_tx([ix_mint_to], [payer])
    print("Tokens minted to user!", flush=True)

# 4. Initialize Vault FIRST so share_mint is created on-chain!
vault_info = rpc('getAccountInfo', [str(vault_state), {'encoding':'base64'}])['value']
if not vault_info:
    print("Initializing Vault on Devnet...", flush=True)
    sighash = hashlib.sha256(b"global:initialize_vault").digest()[:8]
    ix_init_v = Instruction(P_ID, sighash, [
        M(vault_state, False, True),
        M(vault_token_acc, False, True),
        M(share_mint, False, True),
        M(MINT, False, False),
        M(fee_wallet_ata, False, False),
        M(payer.pubkey(), True, True),
        M(TOKEN, False, False),
        M(SYSTEM, False, False),
        M(RENT, False, False)
    ])
    sig_init_v = send_tx([ix_init_v], [payer])
    print(f"Vault initialized! Tx: {sig_init_v}", flush=True)
else:
    print("Vault already initialized.", flush=True)

# Now share_mint exists, so we can create user's share ATA
ensure_ata(user_kp.pubkey(), user_share_ata, share_mint, user_kp)

# 5. Create User Card
card_info = rpc('getAccountInfo', [str(user_card), {'encoding':'base64'}])['value']
if not card_info:
    print("Creating User Card...")
    sighash = hashlib.sha256(b"global:create_user_card").digest()[:8]
    ix_card = Instruction(P_ID, sighash, [
        M(vault_state, False, False),
        M(user_card, False, True),
        M(user_kp.pubkey(), True, True),
        M(SYSTEM, False, False)
    ])
    sig_card = send_tx([ix_card], [user_kp], user_kp)
    print(f"User card created! Tx: {sig_card}")
else:
    print("User card already exists.")

# 6. Execute DEPOSIT!
print("Executing Deposit on Devnet...")
deposit_amount = 100 * 10**6 # 100 tokens
sighash_dep = hashlib.sha256(b"global:deposit").digest()[:8] + struct.pack('<Q', deposit_amount)
ix_dep = Instruction(P_ID, sighash_dep, [
    M(vault_state, False, True),
    M(user_card, False, True),
    M(MINT, False, False),
    M(fee_wallet_ata, False, True),
    M(vault_token_acc, False, True),
    M(share_mint, False, True),
    M(user_token_ata, False, True),
    M(user_share_ata, False, True),
    M(user_kp.pubkey(), True, True),
    M(TOKEN, False, False)
])
sig_deposit = send_tx([ix_dep], [user_kp], user_kp)
print(f"\n=======================================================")
print(f"SUCCESS! DEPOSIT EXECUTED ON SOLANA DEVNET!")
print(f"Deposit Signature: {sig_deposit}")
print(f"Explorer link: https://explorer.solana.com/tx/{sig_deposit}?cluster=devnet")
print(f"=======================================================\n")

# Read final states
v_acc = rpc('getAccountInfo', [str(vault_state), {'encoding':'base64'}])['value']
v_data = base64.b64decode(v_acc['data'][0])
tot_tokens, tot_shares = struct.unpack_from('<QQ', v_data, 169)

card_acc = rpc('getAccountInfo', [str(user_card), {'encoding':'base64'}])['value']
c_data = base64.b64decode(card_acc['data'][0])
deposited_tokens, card_shares = struct.unpack_from('<QQ', c_data, 80)

summary = {
    'program_id': str(P_ID),
    'token_mint': str(MINT),
    'vault_state': str(vault_state),
    'vault_token_account': str(vault_token_acc),
    'share_mint': str(share_mint),
    'user_card': str(user_card),
    'user': str(user_kp.pubkey()),
    'fee_wallet': str(fee_wallet_ata),
    'deposit_transaction': sig_deposit,
    'deposit_explorer_url': f"https://explorer.solana.com/tx/{sig_deposit}?cluster=devnet",
    'gross_deposit': deposit_amount / 10**6,
    'fee_collected': 1.0,
    'net_tokens_in_vault': tot_tokens / 10**6,
    'total_shares_issued': tot_shares / 10**6,
    'user_shares': card_shares / 10**6
}

out_file = evidence_dir / 'devnet-deposit-verified.json'
out_file.write_text(json.dumps(summary, indent=2))
print("Results saved to:", out_file)
print(json.dumps(summary, indent=2))
