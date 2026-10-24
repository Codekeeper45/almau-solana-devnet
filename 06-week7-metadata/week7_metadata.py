#!/usr/bin/env python3
"""Create a fresh SPL mint and Metaplex Token Metadata on Solana Devnet only."""
import argparse, base64, json, os, time
from pathlib import Path
import requests
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.hash import Hash
from solders.instruction import Instruction, AccountMeta
from solders.system_program import CreateAccountParams, create_account
from solders.transaction import Transaction

HERE = Path(__file__).resolve().parent
RPC = "https://api.devnet.solana.com"
TOKEN = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
METADATA = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
SYSTEM = Pubkey.from_string("11111111111111111111111111111111")
RENT_SYSVAR = Pubkey.from_string("SysvarRent111111111111111111111111111111111")


def rpc(method, params):
    r = requests.post(RPC, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=30)
    r.raise_for_status(); d=r.json()
    if "error" in d: raise RuntimeError(f"RPC {method}: {d['error']}")
    return d["result"]


def secure_key(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists():
        if path.stat().st_mode & 0o077: raise RuntimeError(f"Unsafe key permissions; chmod 600 {path}")
        return Keypair.from_bytes(bytes(json.loads(path.read_text())))
    k=Keypair(); fd=os.open(path, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
    with os.fdopen(fd,"w") as f: json.dump(list(bytes(k)),f)
    return k


def bstr(s):
    b=s.encode("utf-8")
    if len(b)>255: raise ValueError("Metadata string exceeds 255 UTF-8 bytes")
    return len(b).to_bytes(4, "little") + b


def send(payer, signers, instructions):
    bh=rpc("getLatestBlockhash",[{"commitment":"confirmed"}])["value"]["blockhash"]
    tx=Transaction.new_signed_with_payer(instructions,payer.pubkey(),signers,Hash.from_string(bh))
    sig=rpc("sendTransaction",[base64.b64encode(bytes(tx)).decode(),{"encoding":"base64","preflightCommitment":"confirmed"}])
    for _ in range(60):
        st=rpc("getSignatureStatuses",[[sig],{"searchTransactionHistory":True}])["value"][0]
        if st and st.get("confirmationStatus") in ("confirmed","finalized"):
            if st.get("err"): raise RuntimeError(f"Transaction failed: {st['err']}")
            txdata=rpc("getTransaction",[sig,{"encoding":"jsonParsed","commitment":"confirmed","maxSupportedTransactionVersion":0}])
            if not txdata or txdata.get("meta",{}).get("err"): raise RuntimeError("Confirmed transaction could not be independently verified")
            return sig
        time.sleep(1)
    raise RuntimeError(f"Confirmation timeout: {sig}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--metadata-uri",required=True,help="Public HTTPS URI of uploaded metadata JSON")
    ap.add_argument("--payer",type=Path,default=Path.home()/".hermes/secrets/almau-solana-devnet.json")
    ap.add_argument("--keys-dir",type=Path,default=Path.home()/".hermes/secrets/almau-solana-week7")
    ap.add_argument("--name",default="AlmaU Week 7 Demo Token")
    ap.add_argument("--symbol",default="AW7")
    ap.add_argument("--decimals",type=int,default=6)
    ap.add_argument("--supply",type=int,default=1000)
    a=ap.parse_args()
    if not a.metadata_uri.startswith("https://") or "example.invalid" in a.metadata_uri: raise SystemExit("Provide a real public HTTPS metadata URI")
    if not 0<=a.decimals<=9 or a.supply<=0: raise SystemExit("Invalid decimals/supply")
    # This script has no mainnet endpoint option. Explicit guard against accidental edits.
    if RPC != "https://api.devnet.solana.com": raise SystemExit("Safety stop: only Devnet is allowed")
    payer=Keypair.from_bytes(bytes(json.loads(a.payer.read_text())))
    mint=secure_key(a.keys_dir/"week7-mint.json")
    balance=rpc("getBalance",[str(payer.pubkey()),{"commitment":"confirmed"}])["value"]
    if balance<10_000_000: raise SystemExit(f"BLOCKED: payer Devnet balance {balance} lamports; need faucet funding first")
    mint_rent=rpc("getMinimumBalanceForRentExemption",[82])
    meta_pda,_=Pubkey.find_program_address([b"metadata",bytes(METADATA),bytes(mint.pubkey())],METADATA)
    ata,_=Pubkey.find_program_address([bytes(payer.pubkey()),bytes(TOKEN),bytes(mint.pubkey())],ASSOCIATED)
    sigs=[]
    # InitializeMint: tag=0, decimals, mint authority, COption<Pubkey> freeze authority=None.
    init_mint=bytes([0,a.decimals])+bytes(payer.pubkey())+bytes([0])+bytes(32)
    sigs.append(send(payer,[payer,mint],[create_account(CreateAccountParams(from_pubkey=payer.pubkey(),to_pubkey=mint.pubkey(),lamports=mint_rent,space=82,owner=TOKEN)),Instruction(TOKEN,init_mint,[AccountMeta(mint.pubkey(),False,True),AccountMeta(RENT_SYSVAR,False,False)])]))
    sigs.append(send(payer,[payer],[Instruction(ASSOCIATED,bytes([1]),[AccountMeta(payer.pubkey(),True,True),AccountMeta(ata,False,True),AccountMeta(payer.pubkey(),False,False),AccountMeta(mint.pubkey(),False,False),AccountMeta(SYSTEM,False,False),AccountMeta(TOKEN,False,False)])]))
    amount=a.supply*(10**a.decimals)
    sigs.append(send(payer,[payer],[Instruction(TOKEN,bytes([7])+amount.to_bytes(8,"little"),[AccountMeta(mint.pubkey(),False,True),AccountMeta(ata,False,True),AccountMeta(payer.pubkey(),True,False)])]))
    # CreateMetadataAccountV3: discriminator, DataV2 (Borsh strings,
    # seller_fee_basis_points, creators/collection/uses=None), is_mutable,
    # collection_details=None. Borsh string lengths are u32, not u8.
    data=bytes([33])+bstr(a.name)+bstr(a.symbol)+bstr(a.metadata_uri)+(0).to_bytes(2,"little")+bytes([0,0,0,1,0])
    metas=[AccountMeta(meta_pda,False,True),AccountMeta(mint.pubkey(),False,False),AccountMeta(payer.pubkey(),True,True),AccountMeta(payer.pubkey(),True,False),AccountMeta(payer.pubkey(),False,False),AccountMeta(SYSTEM,False,False),AccountMeta(RENT_SYSVAR,False,False)]
    sigs.append(send(payer,[payer],[Instruction(METADATA,data,metas)]))
    # Parse authoritative account state and verify metadata PDA exists under Metaplex program.
    info=rpc("getAccountInfo",[str(meta_pda),{"encoding":"base64","commitment":"confirmed"}])["value"]
    if not info or info["owner"]!=str(METADATA): raise RuntimeError("Metadata account verification failed")
    out={"cluster":"devnet","mint":str(mint.pubkey()),"metadata_account":str(meta_pda),"token_account":str(ata),"metadata_uri":a.metadata_uri,"signatures":sigs,"metadata_owner":info["owner"],"verified":True}
    dest=HERE/"evidence"; dest.mkdir(exist_ok=True)
    (dest/"week7-devnet.json").write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))

if __name__=="__main__": main()
